# Baseline (no jev) parameter sweep. Loss halts off so every config trades the full window.
# Run from repo root with the repo venv.
import json, sys, tempfile
from itertools import product
from pathlib import Path

import numpy as np

from opusjev.config import RiskConfig, Settings, StrategyConfig
from opusjev.data import BinanceKlines, load_csv, save_csv
from opusjev.decision import BaselineProvider
from opusjev.engine import Engine, run_backtest
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import summarize

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 365
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TFS = ("15m", "1h", "4h")
STOPS = (1.2, 2.0, 2.5, 3.0)
TPS = (1.5, 2.0, 3.0)
TIME_STOP_HOURS = 16  # same wall-clock hold limit on every timeframe
TF_H = {"15m": 0.25, "1h": 1, "4h": 4}

raw = {}
for tf in TFS:
    for s in SYMS:
        p = Path("data") / f"{s}_{tf}_{DAYS}d.csv"
        if p.exists():
            raw[tf, s] = load_csv(p)
        else:
            raw[tf, s] = BinanceKlines("futures").history(s, tf, DAYS)
            p.parent.mkdir(exist_ok=True)
            save_csv(raw[tf, s], p)


def pf(x):
    g, l = x[x > 0].sum(), -x[x <= 0].sum()
    return g / l if l > 0 else float("inf")


rows = []
tmp = Path(tempfile.mkdtemp())
for tf, sm, tp in product(TFS, STOPS, TPS):
    risk = RiskConfig(daily_loss_limit=1.0, weekly_loss_limit=1.0, peak_drawdown_halt=1.0,
                      time_stop_bars=max(1, int(TIME_STOP_HOURS / TF_H[tf])))
    s = Settings(risk=risk, strategy=StrategyConfig(timeframe=tf, stop_atr_mult=sm, tp_r_multiple=tp))
    feats = {sym: compute(raw[tf, sym], s.strategy) for sym in SYMS}
    jp = tmp / f"{tf}_{sm}_{tp}.jsonl"
    eng = Engine(s, BaselineProvider(), Journal(jp))
    run_backtest(eng, feats)
    tr = eng.broker.trades
    m = summarize(tr, eng.equity_curve, s.starting_equity, 0.0)
    pnl = np.array([t.pnl for t in tr])
    gross = np.array([t.pnl + t.fees for t in tr])
    # cost share of stop distance, from the candidates that became trades
    dec = {}
    for line in jp.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["kind"] == "decision":
            dec[r["proposal_id"]] = r["candidate"]
    c = s.costs
    share = [dec[t.proposal_id]["ref_price"] * (2 * c.taker_fee + 2 * c.slippage + c.stop_extra_slippage)
             / abs(dec[t.proposal_id]["ref_price"] - dec[t.proposal_id]["stop"]) for t in tr if t.proposal_id in dec]
    mid = sorted(t.exit_time for t in tr)[len(tr) // 2] if tr else 0
    h1 = np.array([t.pnl for t in tr if t.exit_time <= mid])
    h2 = np.array([t.pnl for t in tr if t.exit_time > mid])
    rows.append(dict(tf=tf, stop=sm, tp=tp, n=len(tr), wr=m["win_rate"], pf=m["profit_factor"],
                     pf_gross=pf(gross), pf_h1=pf(h1), pf_h2=pf(h2), exp_r=m["expectancy_r"],
                     ci_lo=m["expectancy_r_ci95_low"], ret=m["return_pct"], dd=m["max_drawdown_pct"],
                     cost_share=float(np.median(share)) if share else float("nan")))
    r = rows[-1]
    print(f"{tf:>3} stop={sm} tp={tp} n={r['n']} pf={r['pf']:.2f} gross={r['pf_gross']:.2f} ret={r['ret']:.1f}%", flush=True)

Path("runs").mkdir(exist_ok=True)
Path(f"runs/sweep_{DAYS}d.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
