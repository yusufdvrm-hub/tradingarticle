"""Motor: geri test ve canlı paper için aynı kod yolu.

Her zaman damgasında sıra:
1. Broker yeni barı işler (bekleyen girişler açılışta dolar, stop/TP/zaman stopu kontrol edilir).
2. Risk durumu güncellenir (günlük/haftalık/zirve limitleri).
3. Kapanmış bardan aday üretilir -> ucuz risk ön kontrolü -> sağlayıcı (jev) -> risk vetosu ->
   bir sonraki barın açılışında dolacak giriş emri.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import pandas as pd

from opusjev.broker import PaperBroker
from opusjev.config import Settings
from opusjev.decision import DecisionProvider, Proposal
from opusjev.journal import Journal
from opusjev.risk import RiskManager
from opusjev.signals import generate


@dataclass
class BarInput:
    bar: dict
    feats: pd.DataFrame  # bu bar dahil geçmiş özellikler


@dataclass
class Engine:
    settings: Settings
    provider: DecisionProvider
    journal: Journal = field(default_factory=lambda: Journal(None))
    broker: PaperBroker = field(init=False)
    risk: RiskManager = field(init=False)
    equity_curve: list[tuple[int, float]] = field(default_factory=list)
    provider_calls: int = 0
    provider_cost_usd: float = 0.0

    def __post_init__(self) -> None:
        s = self.settings
        self.broker = PaperBroker(s.starting_equity, s.costs, s.risk.time_stop_bars)
        self.risk = RiskManager(s.risk, s.costs, s.strategy.symbols, s.starting_equity)
        self._seq = itertools.count(1)

    def process(self, now_ms: int, inputs: dict[str, BarInput], data_age_s: float = 0.0) -> None:
        for sym, inp in inputs.items():
            for tr in self.broker.on_bar(sym, inp.bar):
                self.risk.on_trade_closed(tr)
                self.journal.write("trade", **tr.to_dict())
        equity = self.broker.equity()
        self.risk.on_time(now_ms, equity)
        self.equity_curve.append((now_ms, equity))

        for sym, inp in inputs.items():
            cand = generate(sym, inp.feats, self.settings.strategy)
            if cand is None:
                continue
            last_price = float(inp.bar["close"])
            # Ücretsiz ön kontrol: risk zaten reddedecekse jev kredisi harcanmaz.
            pre = self.risk.evaluate(
                cand, Proposal(action="take", take_probability=1.0, provider="precheck"), self.broker, now_ms, last_price, data_age_s
            )
            if not pre.approved:
                self.journal.write("veto", provider=self.provider.name, stage="precheck", candidate=cand.to_dict(), reasons=pre.reasons)
                continue
            context = {
                "equity": round(equity, 2),
                "open_positions": [{"symbol": p.symbol, "side": p.side} for p in self.broker.positions.values()],
                "consecutive_losses": self.risk.state.consecutive_losses,
            }
            proposal = self.provider.decide(cand, context)
            self.provider_calls += 1
            self.provider_cost_usd += proposal.cost_usd
            pid = f"{self.provider.name}-{now_ms}-{sym}-{next(self._seq)}"
            decision = self.risk.evaluate(cand, proposal, self.broker, now_ms, last_price, data_age_s)
            self.journal.write(
                "decision",
                proposal_id=pid,
                candidate=cand.to_dict(),
                proposal=proposal.model_dump(),
                risk={"approved": decision.approved, "qty": decision.qty, "risk_usd": decision.risk_usd, "reasons": decision.reasons},
            )
            if decision.approved:
                self.broker.submit_entry(self.risk.to_pending(cand, decision, proposal, pid, now_ms))


def run_backtest(engine: Engine, feats_by_symbol: dict[str, pd.DataFrame]) -> Engine:
    """Tüm sembolleri ortak zaman ekseninde bar bar oynatır."""
    indexed = {s: f.set_index("open_time", drop=False) for s, f in feats_by_symbol.items()}
    positions = {s: {t: i for i, t in enumerate(f["open_time"])} for s, f in feats_by_symbol.items()}
    times = sorted(set().union(*[set(f["open_time"]) for f in feats_by_symbol.values()]))
    for t in times:
        inputs = {}
        now_ms = 0
        for s, f in feats_by_symbol.items():
            i = positions[s].get(t)
            if i is None:
                continue
            row = indexed[s].iloc[i]
            bar = {k: float(row[k]) for k in ("open", "high", "low", "close")}
            bar["open_time"], bar["close_time"] = int(row["open_time"]), int(row["close_time"])
            now_ms = max(now_ms, bar["close_time"])
            inputs[s] = BarInput(bar=bar, feats=f.iloc[: i + 1])
        engine.process(now_ms, inputs)
    return engine
