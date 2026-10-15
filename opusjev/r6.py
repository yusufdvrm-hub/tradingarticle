"""6. tur değerlendirmesi: QuantConnect "Export" grafiği, dört parça, haftalık (`data/qc/r6_weekly_H012.txt`,
`r6_weekly_H013.txt`); kapılar `research/cards/R6.md`. Getiriler bu ızgarada, SPY ve risksiz de aynı ızgaraya
bileşiklenir (haftalık örnekleme günlük düşüşü biraz küçük gösterir).
Kullanım: python -m opusjev.r6
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from opusjev import lab, macro

QC = lab.DATA / "qc"
DEV, OOS = ("1999-01-01", "2012-12-31"), ("2013-01-01", macro.END)
STRESS_EXTRA = 0.0010  # 15 bp − 5 bp kayma, işlem tutarı başına


def _dates(t) -> pd.DatetimeIndex:
    return pd.to_datetime(t, unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)


def on_grid(nav: pd.Series, idx: pd.DatetimeIndex) -> pd.Series:
    """Günlük NAV -> ızgara noktalarındaki aralık getirileri (her noktada son bilinen NAV)."""
    g = nav.reindex(nav.index.union(idx)).ffill().reindex(idx)
    return g / g.shift(1) - 1


def chunk_returns(c: dict, rf_nav: pd.Series, extra: float = 0.0) -> pd.Series:
    """Bir parça: aralık getirisi − ek maliyet x aralıktaki hacim / önceki özsermaye + nakit oranı x aralık risksizi."""
    d = pd.DataFrame({k: c[k] for k in ("equity", "invested", "traded")}, index=_dates(c["t"]))
    d = d[~d.index.duplicated(keep="last")]
    prev = d["equity"].shift(1)
    r = d["equity"] / prev - 1 - extra * d["traded"].diff() / prev
    cash = (1 - d["invested"].shift(1)).clip(lower=0)
    return (r + cash * on_grid(rf_nav, d.index)).dropna()


def load_weekly(path) -> list[dict]:
    """`data/qc/r6_weekly_H01x.txt`: satır başına bir parça, "#yıl ilk_tarih,özsermaye,yatırım‰,hacim/100 gün,..."
    (tarayıcıda QC günlük grafiğinden haftanın son işlem günü; sağlama toplamlarıyla doğrulandı)."""
    chunks = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        _, *rows = line.split(" ")
        day, t, eq, inv, tr = None, [], [], [], []
        for r in rows:
            a0, e, i, x = r.split(",")
            day = pd.Timestamp(a0) if day is None else day + pd.Timedelta(days=int(a0))
            t.append(int((day + pd.Timedelta(hours=20)).timestamp()))  # 20:00 UTC = New York aynı gün
            eq.append(float(e)); inv.append(int(i) / 1000); tr.append(int(x) * 100.0)
        chunks.append({"t": t, "equity": eq, "invested": inv, "traded": tr})
    return chunks


def returns(chunks: list[dict], rf_nav: pd.Series, extra: float = 0.0) -> pd.Series:
    r = pd.concat([chunk_returns(c, rf_nav, extra) for c in sorted(chunks, key=lambda c: c["t"][0])])
    return r[~r.index.duplicated(keep="first")]


def combo(a: pd.Series, b: pd.Series) -> pd.Series:
    x = pd.concat([a, b], axis=1).dropna()
    return 0.5 * x.iloc[:, 0] + 0.5 * x.iloc[:, 1]


def metrics(r: pd.Series, rf: pd.Series) -> dict:
    """Izgara getirileri; yıllıklandırma gerçek takvim süresiyle."""
    yrs = (r.index[-1] - r.index[0]).days / 365.25 + 6 / 365.25
    ppy = len(r) / yrs
    ex = r - rf.reindex(r.index).fillna(0.0)
    eq = (1 + r).cumprod()
    return dict(sharpe=float(ex.mean() / ex.std() * math.sqrt(ppy)) if ex.std() > 0 else 0.0,
                cagr=float(eq.iloc[-1] ** (1 / yrs) - 1), vol=float(r.std() * math.sqrt(ppy)), ppy=ppy,
                maxdd=float((1 - eq / eq.cummax().clip(lower=1.0)).max()),
                years={str(y): round(float((1 + g).prod() - 1), 3) for y, g in r.groupby(r.index.year)})


def run(record: bool = True) -> None:
    C, rf_d = macro.load()
    rf_nav = (1 + rf_d).cumprod()
    spy_nav = (1 + macro.buy_hold(C[C.index >= "1998-01-01"], rf_d, "SPY")).cumprod()
    res = {h: load_weekly(QC / f"r6_weekly_{h}.txt") for h in ("H012", "H013")}
    r = {(h, lab_): returns(res[h], rf_nav, STRESS_EXTRA if lab_ == "stress" else 0.0)
         for h in ("H012", "H013") for lab_ in ("base", "stress")}
    for lab_ in ("base", "stress"):
        r[("H014", lab_)] = combo(r[("H012", lab_)], r[("H013", lab_)])
    grid = r[("H012", "base")].index
    spy, rf = on_grid(spy_nav, grid).dropna(), on_grid(rf_nav, grid).dropna()

    def M(x, w=None):
        a, b = w or (DEV[0], OOS[1])
        return metrics(x[(x.index >= a) & (x.index <= b)], rf)

    sd, so, sf = M(spy, DEV), M(spy, OOS), M(spy)
    print(f"Izgara: {len(grid)} nokta, yılda ~{sf['ppy']:.0f}")
    print(f"SPY al-tut  tüm: Sharpe {sf['sharpe']:.2f} CAGR {sf['cagr']:+.1%} DD {sf['maxdd']:.1%} | dev {sd['sharpe']:.2f} | OOS {so['sharpe']:.2f} CAGR {so['cagr']:+.1%}")
    print(f"H012-H013 korelasyon: {r[('H012', 'base')].corr(r[('H013', 'base')]):.2f}; ortak nokta "
          f"{len(r[('H014', 'base')])}/{len(grid)}")
    rows = lab.ledger()
    n = lab.trial_universe(rows)[0] + 20 + 3
    oos = lambda x: x[x.index >= OOS[0]]
    srs = [macro.alpha_dsr(oos(r[(h, 'base')]), spy, rf, 1, 0.0)[0] for h in ("H012", "H013", "H014")]
    var = float(np.var(srs, ddof=1))
    for h in ("H012", "H013", "H014"):
        b, s = r[(h, "base")], r[(h, "stress")]
        f, d, o, o2 = M(b), M(b, DEV), M(b, OOS), M(s, OOS)
        if h == "H014":
            g = [("OOS Sharpe vs SPY+0.3", f"{o['sharpe']:.2f} vs {so['sharpe'] + 0.3:.2f}", o["sharpe"] >= so["sharpe"] + 0.3),
                 ("dev Sharpe vs SPY", f"{d['sharpe']:.2f} vs {sd['sharpe']:.2f}", d["sharpe"] > sd["sharpe"]),
                 ("stres OOS vs SPY+0.15", f"{o2['sharpe']:.2f} vs {so['sharpe'] + 0.15:.2f}", o2["sharpe"] >= so["sharpe"] + 0.15)]
        else:
            g = [("OOS Sharpe vs SPY+0.2", f"{o['sharpe']:.2f} vs {so['sharpe'] + 0.2:.2f}", o["sharpe"] >= so["sharpe"] + 0.2),
                 ("dev Sharpe vs SPY", f"{d['sharpe']:.2f} vs {sd['sharpe']:.2f}", d["sharpe"] > sd["sharpe"]),
                 ("stres OOS vs SPY", f"{o2['sharpe']:.2f} vs {so['sharpe']:.2f}", o2["sharpe"] > so["sharpe"]),
                 ("tüm dönem maksDD vs SPY", f"{f['maxdd']:.1%} vs {sf['maxdd']:.1%}", f["maxdd"] <= sf["maxdd"])]
        sr_a, dsr = macro.alpha_dsr(oos(b), spy, rf, n, var)
        passed = all(p for *_, p in g)
        print(f"\n=== {h}  tüm: Sharpe {f['sharpe']:.2f} CAGR {f['cagr']:+.1%} vol {f['vol']:.1%} DD {f['maxdd']:.1%} | "
              f"dev {d['sharpe']:.2f} CAGR {d['cagr']:+.1%} | OOS {o['sharpe']:.2f} CAGR {o['cagr']:+.1%} DD {o['maxdd']:.1%}")
        print(f"    yıllar {f['years']}")
        for a, v, p in g:
            print(f"    {'GEÇTİ' if p else 'KALDI':>6} {a}: {v}")
        print(f"    -> {'GEÇTİ' if passed else 'KALDI'}; OOS alfa SR/yıl {sr_a * math.sqrt(o['ppy']):.2f}, "
              f"DSR {dsr:.3f} (N={n}) -> {'KANITLI' if dsr >= 0.95 else 'kanıt yok'}")
        if record:
            lab.append(dict(kind="r6", hyp=h, card="research/cards/R6.md", passed=passed, dsr=round(dsr, 3),
                            full=f, dev=d, oos=o, oos_stress=o2, gate=g))


if __name__ == "__main__":
    run()
