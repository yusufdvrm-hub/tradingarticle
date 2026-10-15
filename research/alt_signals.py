# Alternative entry signals (opusjev/signals_alt.py), no jev, 1h, 10 USDⓈ-M perps.
# Tune on the last 365 days (IS), then run every config untouched on the 3 years before (OOS).
# Same pessimistic broker; halts off. Funding is not in broker PnL, so it is added post hoc per trade.
# Usage (repo root, venv): python research/alt_signals.py
import json
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import partial
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import requests

import opusjev.engine as E
from opusjev import signals_alt as A
from opusjev.config import RiskConfig, Settings, StrategyConfig
from opusjev.data import BinanceKlines, load_csv, save_csv
from opusjev.decision import BaselineProvider
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import bootstrap_ci_low, max_drawdown

SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT")
YEAR_MS = 365 * 86_400_000
D = Path("data")

# grids: kept small on purpose (fewer configs = less selection bias)
GRID = {
    "tsmom": [dict(lookback=L, z_th=z, stop=st, hold=L) for L, z, st in product((24, 72, 168), (0.5, 1.0), (3.0, 6.0))],
    "funding": [dict(window=90, q=q, stop=st, hold=h) for q, st, h in product((0.9, 0.97), (3.0, 6.0), (24, 72))],
    "xsmom": [dict(lookback=L, k=k, stop=st, hold=L) for L, k, st in product((72, 168), (1, 2), (3.0, 6.0))],
}
TP = 3.0


def funding_history(sym):
    p = D / f"{sym}_funding.csv"
    if p.exists():
        return pd.read_csv(p)
    rows, start = [], 1_600_000_000_000
    while True:
        r = requests.get("https://fapi.binance.com/fapi/v1/fundingRate", params=dict(symbol=sym, startTime=start, limit=1000), timeout=15)
        r.raise_for_status()
        b = r.json()
        if not b:
            break
        rows += b
        start = b[-1]["fundingTime"] + 1
        if len(b) < 1000:
            break
        time.sleep(0.3)
    df = pd.DataFrame(rows)[["fundingTime", "fundingRate"]].astype({"fundingTime": "int64", "fundingRate": float})
    df.to_csv(p, index=False)
    return df


def load():
    end = int(load_csv(D / "BTCUSDT_1h_1460d.csv")["open_time"].iloc[-1])
    raw = {}
    for s in SYMS:
        p = D / f"{s}_1h_1460d.csv"
        if not p.exists():
            save_csv(BinanceKlines("futures").history(s, "1h", 1460), p)
        df = load_csv(p)
        raw[s] = df[df["open_time"] <= end].reset_index(drop=True)
    return raw, {s: funding_history(s) for s in SYMS}


RAW = FUND = None


def _init():
    global RAW, FUND
    RAW, FUND = load()


def pf(x):
    x = np.asarray(x, float)
    g, l = x[x > 0].sum(), -x[x <= 0].sum()
    return float(g / l) if l > 0 else float("inf")


def st(tr):
    if not tr:
        return dict(n=0)
    r = np.array([t["r"] for t in tr])
    rf = np.array([t["r_f"] for t in tr])
    return dict(n=len(tr), wr=float(np.mean(r > 0)), pf=pf([t["pnl"] for t in tr]), pf_gross=pf([t["pnl"] + t["fees"] for t in tr]),
                pf_f=pf([t["pnl_f"] for t in tr]), exp_r=float(r.mean()), ci_lo=bootstrap_ci_low(r),
                exp_r_f=float(rf.mean()), ci_lo_f=bootstrap_ci_low(rf), pnl_f=float(sum(t["pnl_f"] for t in tr)))


def run(idea, prm, window, boundary):
    s = Settings(risk=RiskConfig(daily_loss_limit=1.0, weekly_loss_limit=1.0, peak_drawdown_halt=1.0, time_stop_bars=prm["hold"],
                                 max_open_positions=4),
                 strategy=StrategyConfig(timeframe="1h", symbols=SYMS, stop_atr_mult=prm["stop"], tp_r_multiple=TP))
    feats = {}
    if idea == "xsmom":
        closes = pd.DataFrame({sy: RAW[sy].set_index("open_time")["close"] for sy in SYMS})
        xs = A.xs_momentum(closes, prm["lookback"], prm["k"])
    for sy in SYMS:
        f = compute(RAW[sy], s.strategy)
        if idea == "tsmom":
            f["sig"] = A.tsmom(f, prm["lookback"], prm["z_th"])
        elif idea == "funding":
            f["sig"] = A.funding_extreme(f, FUND[sy], prm["window"], prm["q"])
        else:
            f["sig"] = f["open_time"].map(xs[sy]).fillna(0)
        f = f[(f["open_time"] >= boundary) if window == "IS" else (f["open_time"] < boundary)]
        feats[sy] = f.reset_index(drop=True)
    E.generate = partial(A.from_sig, setup=idea)
    eng = E.Engine(s, BaselineProvider(), Journal(None))
    E.run_backtest(eng, feats)
    out = []
    for t in eng.broker.trades:
        fu = FUND[t.symbol]
        rates = fu["fundingRate"][(fu["fundingTime"] > t.entry_time) & (fu["fundingTime"] <= t.exit_time)].sum()
        sign = 1 if t.side == "long" else -1
        fcost = sign * t.qty * t.entry_price * rates  # long pays positive funding
        risk = t.pnl / t.r_multiple if t.r_multiple else np.nan
        out.append(dict(sym=t.symbol, side=t.side, exit=t.exit_time, reason=t.exit_reason, pnl=t.pnl, fees=t.fees, r=t.r_multiple,
                        pnl_f=t.pnl - fcost, r_f=(t.pnl - fcost) / risk if risk == risk else t.r_multiple))
    eq = pd.Series([e for _, e in eng.equity_curve], dtype=float)
    return dict(idea=idea, prm=prm, window=window, trades=out, dd=100 * max_drawdown(eq), ret=100 * (eq.iloc[-1] / s.starting_equity - 1))


def summarize(res, boundary, start):
    tr = res["trades"]
    row = dict(idea=res["idea"], prm=res["prm"], window=res["window"], **st(tr), ret=res["ret"], dd=res["dd"])
    row["exits"] = pd.Series([t["reason"] for t in tr]).value_counts().to_dict() if tr else {}
    row["by_side"] = {sd: st([t for t in tr if t["side"] == sd]) for sd in ("long", "short")}
    if res["window"] == "OOS":
        row["by_year"] = {}
        for k in (3, 2, 1):
            lo, hi = boundary - k * YEAR_MS, boundary - (k - 1) * YEAR_MS
            row["by_year"][datetime.fromtimestamp(max(lo, start) / 1000, timezone.utc).strftime("%Y-%m")] = st(
                [t for t in tr if lo <= t["exit"] < hi])
    else:
        mid = sorted(t["exit"] for t in tr)[len(tr) // 2] if tr else 0
        row["pf_h1"], row["pf_h2"] = pf([t["pnl_f"] for t in tr if t["exit"] <= mid]), pf([t["pnl_f"] for t in tr if t["exit"] > mid])
    return row


def line(r):
    if not r["n"]:
        return f"{r['idea']:>8} {r['window']:>3} {r['prm']} n=0"
    return (f"{r['idea']:>8} {r['window']:>3} {r['prm']} n={r['n']} wr={r['wr']:.0%} pf={r['pf']:.2f} gross={r['pf_gross']:.2f} "
            f"pf_f={r['pf_f']:.2f} expR_f={r['exp_r_f']:+.3f} ci={r['ci_lo_f']:+.3f} ret={r['ret']:.1f}% dd={r['dd']:.1f}%")


if __name__ == "__main__":
    _init()
    boundary = int(load_csv(D / "BTCUSDT_1h_365d.csv")["open_time"].iloc[0])
    start = max(int(RAW[s]["open_time"].iloc[0]) for s in SYMS)
    jobs = [(i, p, w) for i, ps in GRID.items() for p in ps for w in ("IS", "OOS")]
    with ProcessPoolExecutor(max_workers=6, initializer=_init) as ex:
        futs = [ex.submit(run, i, p, w, boundary) for i, p, w in jobs]
        rows = []
        for f in futs:
            rows.append(summarize(f.result(), boundary, start))
            print(line(rows[-1]), flush=True)
    # selection: per idea, best IS net PF incl. funding among configs with >=40 trades; OOS judged on that config only
    verdict = {}
    for idea in GRID:
        IS = [r for r in rows if r["idea"] == idea and r["window"] == "IS" and r["n"] >= 40]
        best = max(IS, key=lambda r: r["pf_f"]) if IS else None
        oos = next(r for r in rows if r["idea"] == idea and r["window"] == "OOS" and best and r["prm"] == best["prm"]) if best else None
        verdict[idea] = dict(chosen=best and best["prm"], IS=best, OOS=oos,
                             passes=bool(oos and oos["pf_f"] >= 1.2 and oos["ci_lo_f"] > 0))
    Path("runs/alt_signals.json").write_text(json.dumps(dict(rows=rows, verdict=verdict), indent=1, default=float), encoding="utf-8")
    print("\nVERDICT")
    for idea, v in verdict.items():
        print(idea, v["chosen"], "passes" if v["passes"] else "FAILS")
        for k in ("IS", "OOS"):
            if v[k]:
                print("  ", line(v[k]))
        if v["OOS"]:
            print("   years:", {y: (s.get("n"), round(s.get("pf_f", 0), 2)) for y, s in v["OOS"]["by_year"].items()})
