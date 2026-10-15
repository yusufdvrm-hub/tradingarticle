"""5. tur: hisse/çok varlık günlük stratejiler. Kurallar ve kapılar `research/cards/R5.md` (sonuçlardan önce yazıldı).

Kullanım:  python -m opusjev.macro main   (kapılar, ledger kaydı)
           python -m opusjev.macro ndx    (^NDX 1985'ten, yalnızca rapor)
"""

from __future__ import annotations

import math
import sys

import numpy as np
import pandas as pd

from opusjev import lab
from opusjev.portfolio import _fill

PATH = lab.DATA / "etf" / "close.csv"
COST, SPREAD, PPY = 0.0005, 0.01, 252
START, DEV_END, OOS_START, END = "1999-03-10", "2012-12-31", "2013-01-01", "2026-10-16"
SECTORS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB"]
CTA = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD", "SLV", "DBC", "USO", "UUP", "FXE", "FXY", "VNQ"]


def load():
    c = pd.read_csv(PATH, index_col=0, parse_dates=True)
    c = c[c.index < END]
    rf = c.pop("^IRX").ffill().fillna(0.0) / 100 / PPY
    return c, rf


# ---- simülasyon ----------------------------------------------------------------------------------------------
def simulate(T: pd.DataFrame, C: pd.DataFrame, rf: pd.Series, cost_mult: float = 1.0) -> pd.Series:
    """Hedef D kapanışında; dolum D+1 kapanışı; getiri D+1 → D+2 kapanışı (D+2'ye etiketli). NaN satır = tut.
    Nakit (1 − net ağırlık) risksiz kazanır; negatifse risksiz + SPREAD ile borçlanılır."""
    C = C[T.columns]
    X = C.shift(-1)
    R = X.shift(-1) / X - 1
    rate, w, rets = COST * cost_mult, pd.Series(0.0, index=T.columns), []
    for d in T.index[:-2]:
        new = _fill(w, T.loc[d])
        held = new != 0
        if R.loc[d][held].isna().any():
            raise ValueError(f"{d}: tutulan pozisyonda eksik fiyat {list(R.columns[held & R.loc[d].isna()])}")
        cash, r_f = 1 - float(new.sum()), float(rf.loc[d])
        fin = cash * r_f if cash >= 0 else cash * (r_f + SPREAD / PPY)
        Rd = R.loc[d].fillna(0.0)
        r = float((new * Rd).sum()) - float((new - w).abs().sum()) * rate + fin
        rets.append(r)
        w = new * (1 + Rd) / (1 + r) if 1 + r > 0 else new * 0
    return pd.Series(rets, index=T.index[2:])


def buy_hold(C: pd.DataFrame, rf: pd.Series, sym: str) -> pd.Series:
    T = pd.DataFrame({sym: np.where(C[sym].notna(), 1.0, 0.0)}, index=C.index)
    return simulate(T, C, rf)


# ---- stratejiler ---------------------------------------------------------------------------------------------
def h008(C: pd.DataFrame, L: float, sym: str = "QQQ") -> pd.DataFrame:
    s = C[sym]
    sma = s.rolling(200).mean()
    return pd.DataFrame({sym: np.where(sma.notna() & (s > sma), L, 0.0)}, index=C.index)


def month_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Ayın ilk işlem günü (nedensel; "son gün" ertesi güne bakmayı gerektirir). Ad tarihsel."""
    m = pd.Series(idx.month, index=idx)
    return idx[m.ne(m.shift(1)).to_numpy()]


def h009(C: pd.DataFrame) -> pd.DataFrame:
    S = C[SECTORS]
    score = sum(S / S.shift(n) - 1 for n in (63, 126, 252)) / 3
    spy, sma = C["SPY"], C["SPY"].rolling(200).mean()
    T = pd.DataFrame(np.nan, index=C.index, columns=SECTORS + ["IEF"])
    for d in month_ends(C.index):
        sc = score.loc[d].dropna()
        if len(sc) < 3 or pd.isna(sma.loc[d]):
            continue
        row = pd.Series(0.0, index=T.columns)
        if spy.loc[d] < sma.loc[d]:
            if pd.notna(C.loc[d, "IEF"]):
                row["IEF"] = 1.0
        else:
            row[sc.nlargest(3).index] = 1 / 3
        T.loc[d] = row
    return T


def h010(C: pd.DataFrame) -> pd.DataFrame:
    A = C[CTA]
    sig = sum(np.sign(A / A.shift(n) - 1) for n in (21, 63, 252)) / 3
    sigma = np.log(A).diff().rolling(60).std() * math.sqrt(PPY)
    ok = sig.notna() & sigma.notna() & (sigma > 0)
    n = ok.sum(axis=1).replace(0, np.nan)
    W = (sig * 0.15 / sigma).where(ok).div(np.sqrt(n), axis=0).fillna(0.0)
    g = W.abs().sum(axis=1)
    return W.div(np.maximum(g / 3, 1.0), axis=0)


def h011(parts: dict[str, pd.Series], rf: pd.Series, target: float, cost_mult: float = 1.0) -> pd.Series:
    """Ters vol ağırlık (252 gün, ay sonu), sonra portföy vol hedefi (63 gün, ≤3); ikisi de 1 gün gecikmeli."""
    R = pd.DataFrame(parts).dropna(how="all").fillna(0.0)
    rfa = rf.reindex(R.index).ffill()
    vol = R.rolling(252).std()
    me = month_ends(R.index)
    iv = (1 / vol.loc[me]).replace(np.inf, np.nan)
    w = iv.div(iv.sum(axis=1), axis=0).reindex(R.index).ffill().shift(1)
    mix = (w * R).sum(axis=1).where(w.notna().all(axis=1))
    ex = mix - rfa
    scale = (target / (ex.rolling(63).std() * math.sqrt(PPY))).clip(upper=3.0).shift(1)
    # ponytail: kaplama maliyeti = |Δ(ölçek x ağırlık)| x COST; alttaki stratejilerin brütü ~1 varsayılıyor
    expo = w.mul(scale, axis=0)
    tc = expo.diff().abs().sum(axis=1) * COST * cost_mult
    r = rfa + scale * ex - (scale - 1).clip(lower=0) * SPREAD / PPY - tc
    return r.dropna()


# ---- ölçüm ---------------------------------------------------------------------------------------------------
def metrics(r: pd.Series, rf: pd.Series) -> dict:
    ex = r - rf.reindex(r.index).fillna(0.0)
    eq = (1 + r).cumprod()
    yrs = len(r) / PPY
    return dict(sharpe=float(ex.mean() / ex.std() * math.sqrt(PPY)) if ex.std() > 0 else 0.0,
                cagr=float(eq.iloc[-1] ** (1 / yrs) - 1), vol=float(r.std() * math.sqrt(PPY)),
                maxdd=float((1 - eq / eq.cummax().clip(lower=1.0)).max()),
                years={str(y): round(float((1 + g).prod() - 1), 3) for y, g in r.groupby(r.index.year)})


def win(r: pd.Series, a: str, b: str) -> pd.Series:
    return r[(r.index >= a) & (r.index <= b)]


def alpha_dsr(r: pd.Series, bench: pd.Series, rf: pd.Series, n: int, var: float) -> tuple[float, float]:
    """OOS'ta vol-eşitlenmiş kıyasa karşı fazla getiri: (günlük SR, DSR)."""
    rfa = rf.reindex(r.index).fillna(0.0)
    a, b = r - rfa, bench.reindex(r.index).fillna(0.0) - rfa
    x = a - a.std() / b.std() * b
    sr = float(x.mean() / x.std())
    return sr, lab.dsr(sr, len(x), float(x.skew()), float(x.kurt() + 3), n, var)


def monthly(r: pd.Series) -> pd.Series:
    return (1 + r).resample("ME").prod() - 1


# ---- koşu ----------------------------------------------------------------------------------------------------
def run(record: bool) -> None:
    C, rf = load()
    C = C[C.index >= START]
    spy = buy_hold(C, rf, "SPY")
    qqq = buy_hold(C, rf, "QQQ")
    strat = {
        "H008-L1": lambda m: simulate(h008(C, 1), C, rf, m),
        "H008-L2": lambda m: simulate(h008(C, 2), C, rf, m),
        "H008-L3": lambda m: simulate(h008(C, 3), C, rf, m),
        "H009": lambda m: simulate(h009(C), C, rf, m),
        "H010": lambda m: simulate(h010(C), C, rf, m),
    }
    base = {k: f(1.0) for k, f in strat.items()}
    stress = {k: f(2.0) for k, f in strat.items()}
    parts = lambda src: {k: src[k] for k in ("H008-L1", "H009", "H010")}
    for t in (0.12, 0.18, 0.25):
        k = f"H011-{int(t * 100)}"
        base[k] = h011(parts(base), rf, t)
        stress[k] = h011(parts(stress), rf, t, 2.0)

    def M(r, a=START, b=END):
        return metrics(win(r, a, b), rf)

    sd, so, sf = M(spy, START, DEV_END), M(spy, OOS_START), M(spy)
    print(f"SPY al-tut  tüm: Sharpe {sf['sharpe']:.2f} CAGR {sf['cagr']:+.1%} DD {sf['maxdd']:.1%} | dev {sd['sharpe']:.2f} | OOS {so['sharpe']:.2f} CAGR {so['cagr']:+.1%}")
    q = M(qqq)
    print(f"QQQ al-tut  tüm: Sharpe {q['sharpe']:.2f} CAGR {q['cagr']:+.1%} DD {q['maxdd']:.1%} | OOS {M(qqq, OOS_START)['sharpe']:.2f} CAGR {M(qqq, OOS_START)['cagr']:+.1%}")
    spy_m = monthly(spy)
    rows = lab.ledger()
    n = lab.trial_universe(rows)[0] + 12 + len(base)  # önceki denemeler + 4. turun 12 yapılandırması + bu tur
    oos_srs = [alpha_dsr(win(r, OOS_START, END), spy, rf, 1, 0.0)[0] for r in base.values()]
    var = float(np.var(oos_srs, ddof=1))
    for k, r in base.items():
        f, d, o, o2 = M(r), M(r, START, DEV_END), M(r, OOS_START), M(stress[k], OOS_START)
        if k.startswith("H010"):
            corr = float(monthly(r).corr(spy_m))
            g = [("OOS Sharpe", f"{o['sharpe']:.2f}", ">= 0.4", o["sharpe"] >= 0.4),
                 ("SPY ile aylık korelasyon", f"{corr:.2f}", "<= 0.3", corr <= 0.3),
                 ("2x maliyet OOS Sharpe", f"{o2['sharpe']:.2f}", ">= 0.3", o2["sharpe"] >= 0.3)]
        elif k.startswith("H011"):
            g = [("OOS Sharpe vs SPY+0.3", f"{o['sharpe']:.2f} vs {so['sharpe'] + 0.3:.2f}", ">=", o["sharpe"] >= so["sharpe"] + 0.3),
                 ("dev Sharpe vs SPY", f"{d['sharpe']:.2f} vs {sd['sharpe']:.2f}", ">", d["sharpe"] > sd["sharpe"]),
                 ("2x maliyet OOS vs SPY+0.15", f"{o2['sharpe']:.2f} vs {so['sharpe'] + 0.15:.2f}", ">=", o2["sharpe"] >= so["sharpe"] + 0.15)]
        elif k in ("H008-L1", "H009"):
            g = [("OOS Sharpe vs SPY+0.2", f"{o['sharpe']:.2f} vs {so['sharpe'] + 0.2:.2f}", ">=", o["sharpe"] >= so["sharpe"] + 0.2),
                 ("dev Sharpe vs SPY", f"{d['sharpe']:.2f} vs {sd['sharpe']:.2f}", ">", d["sharpe"] > sd["sharpe"]),
                 ("2x maliyet OOS vs SPY", f"{o2['sharpe']:.2f} vs {so['sharpe']:.2f}", ">", o2["sharpe"] > so["sharpe"]),
                 ("tüm dönem maksDD vs SPY", f"{f['maxdd']:.1%} vs {sf['maxdd']:.1%}", "<=", f["maxdd"] <= sf["maxdd"])]
        else:
            g = []
        sr_a, dsr = alpha_dsr(win(r, OOS_START, END), spy, rf, n, var)
        passed = all(p for *_, p in g) if g else None
        print(f"\n=== {k}  tüm: Sharpe {f['sharpe']:.2f} CAGR {f['cagr']:+.1%} vol {f['vol']:.1%} DD {f['maxdd']:.1%} | "
              f"dev {d['sharpe']:.2f} CAGR {d['cagr']:+.1%} | OOS {o['sharpe']:.2f} CAGR {o['cagr']:+.1%} DD {o['maxdd']:.1%}")
        print(f"    yıllar {f['years']}")
        for a, v, t, p in g:
            print(f"    {'GEÇTİ' if p else 'KALDI':>6} {a}: {v} ({t})")
        print(f"    -> {'yalnızca rapor' if passed is None else 'GEÇTİ' if passed else 'KALDI'};"
              f" OOS alfa SR/yıl {sr_a * math.sqrt(PPY):.2f}, DSR {dsr:.3f} (N={n}) -> {'KANITLI' if dsr >= 0.95 else 'kanıt yok'}")
        if record:
            lab.append(dict(kind="r5", hyp=k, card="research/cards/R5.md", passed=passed, dsr=round(dsr, 3),
                            full=f, dev=d, oos=o, oos_2x=o2, gate=g))


def ndx() -> None:
    C, rf = load()
    C = C[C.index >= "1985-10-01"][["^NDX", "^GSPC"]]
    for name, r in [("^GSPC al-tut", buy_hold(C, rf, "^GSPC")), ("^NDX al-tut", buy_hold(C, rf, "^NDX"))] + \
                   [(f"H008-L{L} ^NDX", simulate(h008(C, L, "^NDX"), C, rf)) for L in (1, 2, 3)]:
        m = metrics(r, rf)
        print(f"{name:14} Sharpe {m['sharpe']:.2f} CAGR {m['cagr']:+.1%} vol {m['vol']:.1%} DD {m['maxdd']:.1%}")


if __name__ == "__main__":
    ndx() if (sys.argv[1:] or ["main"])[0] == "ndx" else run(record=True)
