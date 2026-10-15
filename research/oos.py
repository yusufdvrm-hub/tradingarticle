# Out-of-sample check: mean reversion only, 1h, stop 2.5xATR, params untouched,
# on the ~3 years BEFORE the 365-day window used for the sweep.
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import opusjev.engine as E
from opusjev.config import RiskConfig, Settings, StrategyConfig
from opusjev.data import BinanceKlines, load_csv, save_csv
from opusjev.decision import BaselineProvider
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import summarize
from opusjev.signals import generate

SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
YEAR_MS = 365 * 86_400_000

full, oos = {}, {}
boundary = min(int(load_csv(Path("data") / f"{s}_1h_365d.csv")["open_time"].iloc[0]) for s in SYMS)
for s in SYMS:
    p = Path("data") / f"{s}_1h_1460d.csv"
    if not p.exists():
        save_csv(BinanceKlines("futures").history(s, "1h", 1460), p)
    df = load_csv(p)
    oos[s] = df[df["open_time"] < boundary].reset_index(drop=True)


def pf(x):
    x = np.asarray(x, float)
    g, l = x[x > 0].sum(), -x[x <= 0].sum()
    return g / l if l > 0 else float("inf")


def st(tr):
    return dict(n=len(tr), wr=float(np.mean([t.pnl > 0 for t in tr])) if tr else 0.0, pf=pf([t.pnl for t in tr]),
                pf_gross=pf([t.pnl + t.fees for t in tr]), exp_r=float(np.mean([t.r_multiple for t in tr])) if tr else 0.0,
                pnl=float(sum(t.pnl for t in tr)))


fmt = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")
start = max(int(oos[s]["open_time"].iloc[0]) for s in SYMS)
print("OOS window:", fmt(start), "->", fmt(boundary))

E.generate = lambda sym, f, cfg: (c if (c := generate(sym, f, cfg)) and c.setup == "mean_reversion" else None)
rows = []
for tp in (1.5, 2.0, 3.0):
    s = Settings(risk=RiskConfig(daily_loss_limit=1.0, weekly_loss_limit=1.0, peak_drawdown_halt=1.0, time_stop_bars=16),
                 strategy=StrategyConfig(timeframe="1h", stop_atr_mult=2.5, tp_r_multiple=tp))
    feats = {sym: compute(oos[sym], s.strategy) for sym in SYMS}
    eng = E.Engine(s, BaselineProvider(), Journal(Path("runs/oos") / f"mr_{tp}.jsonl"))
    E.run_backtest(eng, feats)
    tr = eng.broker.trades
    m = summarize(tr, eng.equity_curve, s.starting_equity, 0.0)
    # yearly slices counted back from the boundary: Y-1 is the year just before the in-sample window
    years = {}
    for k in (3, 2, 1):
        lo, hi = boundary - k * YEAR_MS, boundary - (k - 1) * YEAR_MS
        years[f"Y-{k} ({fmt(max(lo, start))[:7]}..)"] = st([t for t in tr if lo <= t.exit_time < hi])
    row = dict(tp=tp, **st(tr), ci_lo=m["expectancy_r_ci95_low"], ret=m["return_pct"], dd=m["max_drawdown_pct"],
               by_year=years,
               by_side={sd: st([t for t in tr if t.side == sd]) for sd in ("long", "short")},
               by_symbol={sy: st([t for t in tr if t.symbol == sy]) for sy in SYMS},
               sol_short=st([t for t in tr if t.symbol == "SOLUSDT" and t.side == "short"]))
    rows.append(row)

Path("runs/oos_mr.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
for r in rows:
    print(f"\nTP={r['tp']} n={r['n']} wr={r['wr']:.0%} pf={r['pf']:.2f} gross={r['pf_gross']:.2f} expR={r['exp_r']:+.3f} ci={r['ci_lo']:+.3f} ret={r['ret']:.1f}% dd={r['dd']:.1f}%")
    for g in ("by_year", "by_side", "by_symbol"):
        print("   ", "  ".join(f"{k}: n={v['n']} pf={v['pf']:.2f} pnl={v['pnl']:+.0f}" for k, v in r[g].items()))
    v = r["sol_short"]
    print(f"    SOL short: n={v['n']} pf={v['pf']:.2f} pnl={v['pnl']:+.0f}")
