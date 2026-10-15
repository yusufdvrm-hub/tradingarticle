# Each setup run in isolation (other setup's candidates dropped), 1h, stop 2.5xATR, halts off.
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

import opusjev.engine as E
from opusjev.config import RiskConfig, Settings, StrategyConfig
from opusjev.data import load_csv
from opusjev.decision import BaselineProvider
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import summarize
from opusjev.signals import generate

SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
raw = {s: load_csv(Path("data") / f"{s}_1h_365d.csv") for s in SYMS}


def pf(x):
    x = np.asarray(x, float)
    g, l = x[x > 0].sum(), -x[x <= 0].sum()
    return g / l if l > 0 else float("inf")


def stats(tr):
    pnl = [t.pnl for t in tr]
    exits = defaultdict(int)
    for t in tr:
        exits[t.exit_reason] += 1
    return dict(n=len(tr), wr=np.mean([p > 0 for p in pnl]) if tr else 0, pf=pf(pnl),
                pf_gross=pf([t.pnl + t.fees for t in tr]), exp_r=np.mean([t.r_multiple for t in tr]) if tr else 0,
                pnl=sum(pnl), exits=dict(exits))


rows = []
for only in ("mean_reversion", "breakout", None):
    for tp in (1.5, 2.0, 3.0):
        E.generate = (lambda sym, f, cfg, only=only: (c if (c := generate(sym, f, cfg)) and (only is None or c.setup == only) else None))
        s = Settings(risk=RiskConfig(daily_loss_limit=1.0, weekly_loss_limit=1.0, peak_drawdown_halt=1.0, time_stop_bars=16),
                     strategy=StrategyConfig(timeframe="1h", stop_atr_mult=2.5, tp_r_multiple=tp))
        feats = {sym: compute(raw[sym], s.strategy) for sym in SYMS}
        eng = E.Engine(s, BaselineProvider(), Journal(Path("runs/setups") / f"{only}_{tp}.jsonl"))
        E.run_backtest(eng, feats)
        tr = eng.broker.trades
        m = summarize(tr, eng.equity_curve, s.starting_equity, 0.0)
        mid = sorted(t.exit_time for t in tr)[len(tr) // 2] if tr else 0
        row = dict(setup=only or "both", tp=tp, ci_lo=m["expectancy_r_ci95_low"], ret=m["return_pct"], dd=m["max_drawdown_pct"],
                   pf_h1=pf([t.pnl for t in tr if t.exit_time <= mid]), pf_h2=pf([t.pnl for t in tr if t.exit_time > mid]),
                   **stats(tr))
        row["by_side"] = {sd: stats([t for t in tr if t.side == sd]) for sd in ("long", "short")}
        row["by_symbol"] = {sy: stats([t for t in tr if t.symbol == sy]) for sy in SYMS}
        rows.append(row)
        print(f"{row['setup']:>14} tp={tp} n={row['n']} pf={row['pf']:.2f} gross={row['pf_gross']:.2f} ret={row['ret']:.1f}%", flush=True)

Path("runs/setups.json").write_text(json.dumps(rows, indent=2, default=float), encoding="utf-8")
