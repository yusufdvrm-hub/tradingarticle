"""Komut satırı.

    opusjev backtest --source synthetic|binance|csv [--provider baseline|jev] [--days 90]
    opusjev paper    [--provider jev|baseline] [--run-dir runs/paper]   # canlı veri, sahte bakiye
    opusjev report   --run-dir runs/paper
    opusjev jev-ping                                                    # API anahtarı/bağlantı testi
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from opusjev.config import Settings
from opusjev.data import BinanceKlines, load_csv, save_csv, synthetic
from opusjev.decision import BaselineProvider, JevProvider
from opusjev.engine import Engine, run_backtest
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import format_report, go_live_gate, summarize


def make_provider(name: str, settings: Settings):
    if name == "baseline":
        return BaselineProvider()
    if name == "jev":
        if not os.environ.get("TYPESAFE_API_KEY"):
            raise SystemExit("TYPESAFE_API_KEY ortam değişkeni yok. .env.example dosyasına bakın.")
        return JevProvider(settings.jev)
    raise SystemExit(f"bilinmeyen sağlayıcı: {name}")


def cmd_backtest(a: argparse.Namespace) -> int:
    s = Settings()
    syms = tuple(a.symbols.split(",")) if a.symbols else s.strategy.symbols
    s = Settings(strategy=type(s.strategy)(symbols=syms))
    raw = {}
    for sym in syms:
        if a.source == "synthetic":
            raw[sym] = synthetic(sym, bars=a.bars, seed=a.seed)
        elif a.source == "binance":
            cache = Path(a.data_dir) / f"{sym}_{s.strategy.timeframe}_{a.days}d.csv"
            if cache.exists() and not a.refresh:
                raw[sym] = load_csv(cache)
            else:
                raw[sym] = BinanceKlines("futures").history(sym, s.strategy.timeframe, a.days)
                save_csv(raw[sym], cache)
        else:
            raw[sym] = load_csv(Path(a.data_dir) / f"{sym}.csv")
    feats = {sym: compute(df, s.strategy) for sym, df in raw.items()}
    run_dir = Path(a.run_dir or f"runs/backtest_{a.source}_{a.provider}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}")
    results = {}
    names = [a.provider] + (["baseline"] if a.provider != "baseline" else [])
    for name in names:
        eng = Engine(s, make_provider(name, s), Journal(run_dir / f"journal_{name}.jsonl"))
        run_backtest(eng, feats)
        results[name] = summarize(eng.broker.trades, eng.equity_curve, s.starting_equity, eng.provider_cost_usd)
    m = results[a.provider]
    shadow = results.get("baseline") if a.provider != "baseline" else None
    gate = go_live_gate(m, shadow)
    title = f"Backtest ({a.source}, {a.provider}, {','.join(syms)})"
    text = format_report(title, m, gate)
    if shadow:
        text += "\n\n" + format_report("Gölge: jev'siz temel çizgi", shadow, go_live_gate(shadow))
    if a.source == "synthetic":
        text = "> UYARI: sentetik veri. Bu sonuçlar yalnızca sistemin çalıştığını gösterir, stratejinin kârlılığı hakkında bilgi vermez.\n\n" + text
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.md").write_text(text, encoding="utf-8")
    (run_dir / "summary.json").write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(text)
    print(f"\nÇıktılar: {run_dir}")
    return 0


def cmd_paper(a: argparse.Namespace) -> int:
    from opusjev.live import PaperRunner

    s = Settings()
    runner = PaperRunner(s, make_provider(a.provider, s), Path(a.run_dir), shadow=not a.no_shadow)
    if a.once:
        print(f"{runner.poll_once()} bar işlendi")
        return 0
    runner.run_forever()
    return 0


def cmd_report(a: argparse.Namespace) -> int:
    p = Path(a.run_dir) / "report.md"
    print(p.read_text(encoding="utf-8") if p.exists() else f"rapor yok: {p}")
    st = Path(a.run_dir) / "status.json"
    if st.exists():
        data = json.loads(st.read_text(encoding="utf-8"))
        for name, d in data.items():
            print(f"\n[{name}] özsermaye={d['equity']} açık={list(d['open_positions'])} durduruldu={d['halted']} jev_çağrı={d['provider_calls']} maliyet=${d['provider_cost_usd']}")
    return 0


def cmd_jev_ping(a: argparse.Namespace) -> int:
    from opusjev.signals import Candidate

    s = Settings()
    prov = JevProvider(s.jev)
    cand = Candidate("BTCUSDT", "long", "mean_reversion", 0, 60000.0, 59400.0, 61200.0, 500.0, "range", {"rsi": 27.0, "adx": 15.0})
    p = prov.decide(cand, {"equity": 10000})
    print(p.model_dump_json(indent=2))
    return 0 if not p.reason.startswith("error") else 1


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(prog="opusjev")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--source", choices=["synthetic", "binance", "csv"], default="synthetic")
    b.add_argument("--provider", choices=["baseline", "jev"], default="baseline")
    b.add_argument("--symbols", default="")
    b.add_argument("--days", type=int, default=90)
    b.add_argument("--bars", type=int, default=8000)
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--data-dir", default="data")
    b.add_argument("--run-dir", default="")
    b.add_argument("--refresh", action="store_true")
    b.set_defaults(fn=cmd_backtest)
    p = sub.add_parser("paper")
    p.add_argument("--provider", choices=["baseline", "jev"], default="jev")
    p.add_argument("--run-dir", default="runs/paper")
    p.add_argument("--no-shadow", action="store_true")
    p.add_argument("--once", action="store_true")
    p.set_defaults(fn=cmd_paper)
    r = sub.add_parser("report")
    r.add_argument("--run-dir", default="runs/paper")
    r.set_defaults(fn=cmd_report)
    j = sub.add_parser("jev-ping")
    j.set_defaults(fn=cmd_jev_ping)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
