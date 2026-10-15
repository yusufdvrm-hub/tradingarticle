"""Canlı paper döngüsü: gerçek Binance verisi, sahte bakiye.

Her 15 dakikalık bar kapandıktan birkaç saniye sonra son klines çekilir, yeni
kapanmış barlar motora verilir. Birincil motor (jev) ile jev'siz gölge motor
aynı barları işler (spec: jev ablasyonu). Durum her barda diske yazılır;
yeniden başlatmada kaldığı yerden devam eder.
"""

from __future__ import annotations

import json
import logging
import pickle
import signal
import time
from pathlib import Path

from opusjev.config import Settings
from opusjev.data import TF_MS, BinanceKlines, closed_only
from opusjev.decision import BaselineProvider, DecisionProvider
from opusjev.engine import BarInput, Engine
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import format_report, go_live_gate, summarize

log = logging.getLogger("opusjev.live")
HISTORY_BARS = 500


class PaperRunner:
    def __init__(self, settings: Settings, provider: DecisionProvider, run_dir: Path, shadow: bool = True, feed: BinanceKlines | None = None):
        self.s = settings
        self.run_dir = run_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        self.feed = feed or BinanceKlines("futures")
        self.state_path = run_dir / "state.pkl"
        self.engines: dict[str, Engine] = {}
        self.last_bar: dict[str, int] = {}
        if self.state_path.exists():
            saved = pickle.loads(self.state_path.read_bytes())
            self.last_bar = saved["last_bar"]
            for name, eng_state in saved["engines"].items():
                prov = provider if name == "primary" else BaselineProvider()
                eng = Engine(settings, prov, Journal(run_dir / f"journal_{name}.jsonl"))
                eng.broker, eng.risk, eng.equity_curve = eng_state["broker"], eng_state["risk"], eng_state["equity_curve"]
                eng.provider_calls, eng.provider_cost_usd = eng_state["calls"], eng_state["cost"]
                self.engines[name] = eng
            log.info("Durum yüklendi: %s", {k: v for k, v in self.last_bar.items()})
        else:
            self.engines["primary"] = Engine(settings, provider, Journal(run_dir / "journal_primary.jsonl"))
            if shadow and provider.name != "baseline":
                self.engines["shadow"] = Engine(settings, BaselineProvider(), Journal(run_dir / "journal_shadow.jsonl"))
        self._stop = False

    def save(self) -> None:
        data = {
            "last_bar": self.last_bar,
            "engines": {
                n: {"broker": e.broker, "risk": e.risk, "equity_curve": e.equity_curve, "calls": e.provider_calls, "cost": e.provider_cost_usd}
                for n, e in self.engines.items()
            },
        }
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_bytes(pickle.dumps(data))
        tmp.replace(self.state_path)

    def poll_once(self, now_ms: int | None = None) -> int:
        """Yeni kapanmış barları işler; işlenen zaman damgası sayısını döndürür."""
        now_ms = now_ms if now_ms is not None else int(time.time() * 1000)
        frames = {}
        for sym in self.s.strategy.symbols:
            df = closed_only(self.feed.fetch(sym, self.s.strategy.timeframe, limit=HISTORY_BARS), now_ms)
            frames[sym] = compute(df, self.s.strategy)
        new_times = sorted(
            {int(t) for sym, f in frames.items() for t in f["open_time"] if t > self.last_bar.get(sym, 0)}
        )
        # İlk çalıştırmada geçmişi oynatma: yalnızca en son kapanmış bardan itibaren işlem yap.
        if not self.last_bar:
            new_times = new_times[-1:]
        for t in new_times:
            inputs = {}
            close_ms = 0
            for sym, f in frames.items():
                idx = f.index[f["open_time"] == t]
                if len(idx) == 0:
                    continue
                i = int(idx[0])
                row = f.iloc[i]
                bar = {k: float(row[k]) for k in ("open", "high", "low", "close")}
                bar["open_time"], bar["close_time"] = int(row["open_time"]), int(row["close_time"])
                close_ms = max(close_ms, bar["close_time"])
                inputs[sym] = BarInput(bar=bar, feats=f.iloc[: i + 1])
                self.last_bar[sym] = t
            # Gecikmiş (catch-up) barlarda yeni giriş açılmasın diye bayatlık yaşı gerçek zamana göre ölçülür.
            age_s = max(0.0, (now_ms - close_ms) / 1000)
            for eng in self.engines.values():
                eng.process(close_ms, inputs, data_age_s=age_s)
        if new_times:
            self.save()
            self.write_status()
        return len(new_times)

    def write_status(self) -> None:
        sums = {n: summarize(e.broker.trades, e.equity_curve, self.s.starting_equity, e.provider_cost_usd) for n, e in self.engines.items()}
        status = {
            n: {
                "equity": round(e.broker.equity(), 2),
                "open_positions": {s: {"side": p.side, "entry": p.entry_price, "stop": p.stop, "tp": p.take_profit} for s, p in e.broker.positions.items()},
                "halted": e.risk.state.halted,
                "provider_calls": e.provider_calls,
                "provider_cost_usd": round(e.provider_cost_usd, 6),
                "summary": sums[n],
            }
            for n, e in self.engines.items()
        }
        (self.run_dir / "status.json").write_text(json.dumps(status, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
        gate = go_live_gate(sums["primary"], sums.get("shadow"))
        (self.run_dir / "report.md").write_text(format_report("Paper (canlı veri) - birincil", sums["primary"], gate), encoding="utf-8")

    def run_forever(self) -> None:
        signal.signal(signal.SIGTERM, lambda *_: setattr(self, "_stop", True))
        step = TF_MS[self.s.strategy.timeframe]
        backoff = 5
        while not self._stop:
            try:
                n = self.poll_once()
                backoff = 5
                if n:
                    eq = {k: round(e.broker.equity(), 2) for k, e in self.engines.items()}
                    log.info("%d yeni bar işlendi; özsermaye %s", n, eq)
            except Exception as e:  # ağ hatası: stoplar paper broker'da bar bazında kontrol edildiği için güvenli bekle
                log.warning("poll hatası: %s; %ss sonra tekrar", e, backoff)
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)
                continue
            now = int(time.time() * 1000)
            next_close = (now // step + 1) * step
            time.sleep(max(1.0, (next_close - now) / 1000 + 3))
        self.save()
