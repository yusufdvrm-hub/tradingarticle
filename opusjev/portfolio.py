"""Günlük portföy stratejileri (4. tur, 2026-10-15). Kurallar `reports/Kanıtlı trading stratejileri ve otomasyon.md`
kartlarından birebir; parametre araması yok.

Zamanlama: gün D'nin kapanışı (00:00 UTC) ile sinyal, D+1 01:00 UTC barının kapanışında dolum; pozisyon bir sonraki
dolum anına kadar tutulur. Perp uygulamasında funding gerçek baskılarla (long pozitif funding öder), spot
uygulamasında funding yok ama ücret iki katı. Tampon: |fark| < %10 x |hedef| ve < %0,5 ise işlem yok.

Kullanım:  python -m opusjev.portfolio main      (2022-10 → 2026-10 ana test, kapılar, ledger kaydı)
           python -m opusjev.portfolio extended  (2020 → 2026 ek test, yalnızca rapor)
           python -m opusjev.portfolio paper     (H005 ileriye dönük paper: veriyi güncelle, günlüğe ekle; 01:05 UTC sonrası)
           python -m opusjev.portfolio forward   (2026-10-16'dan beri paper raporu; ≥60 günde holdout kapısı)
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from opusjev import lab
from opusjev.data import BinanceKlines, closed_only

DATA = lab.DATA
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT")
END = "2026-10-16"
COST = {"perp": 0.0005 + 0.0002, "spot": 0.0010 + 0.0002}  # taraf başına ücret + kayma
WARMUP = 150
DAY = 86_400_000


# ---- veri ---------------------------------------------------------------------------------------------------
def load(suffix: str = "1h_1460d", syms=SYMS, end: str | None = END):
    C, X, F, H = {}, {}, {}, {}
    for s in syms:
        h = pd.read_csv(DATA / f"{s}_{suffix}.csv")
        h = h[h["open_time"] < lab._ms(end)] if end else h
        t = pd.to_datetime(h["open_time"], unit="ms", utc=True)
        c = h[t.dt.hour == 23].set_index(t[t.dt.hour == 23].dt.floor("D"))["close"]
        x = h[t.dt.hour == 0].set_index(t[t.dt.hour == 0].dt.floor("D") - pd.Timedelta(days=1))["close"]
        C[s], X[s], H[s] = c, x, h
        F[s] = pd.read_csv(DATA / f"{s}_funding.csv").sort_values("fundingTime")
    C, X = pd.DataFrame(C), pd.DataFrame(X)
    idx = C.index.intersection(X.index)
    C, X = C.loc[idx], X.loc[idx]
    # zamanında uygunluk: ilk funding baskısından önce perp yok (indirici o dönemi spot ile doldurabiliyor)
    for s in syms:
        first = pd.Timestamp(int(F[s]["fundingTime"].iloc[0]), unit="ms", tz="UTC")
        C.loc[C.index < first, s] = np.nan
        X.loc[X.index < first, s] = np.nan
    # funding: dolum(D) < ft <= dolum(D+1), dolum(D) = D + 1 gün + 1 saat. Miktar dönem boyunca sabit, her baskı
    # o anki fiyatla: Σ oran_i x P_i / X_D (giriş ağırlığı başına). P_i = baskı anında kapanan saatlik barın kapanışı.
    ex = np.array([(d + pd.Timedelta(days=1, hours=1)).value // 1_000_000 for d in idx], dtype="int64")
    fund = {}
    for s in syms:
        fu, h = F[s], H[s]
        ft = fu["fundingTime"].to_numpy()
        j = np.searchsorted((h["open_time"] + 3_600_000).to_numpy(), ft, side="right") - 1
        px = np.where(j >= 0, h["close"].to_numpy()[np.clip(j, 0, None)], np.nan)
        cum = np.concatenate([[0.0], np.nancumsum(fu["fundingRate"].to_numpy() * px)])
        tot = cum[np.searchsorted(ft, ex, side="right")]
        fund[s] = np.append(np.diff(tot), np.nan) / X[s].to_numpy()
    return C, X, pd.DataFrame(fund, index=idx)


def vol(C: pd.DataFrame, n: int = 60) -> pd.DataFrame:
    return np.log(C).diff().rolling(n).std() * math.sqrt(365)


# ---- hedef ağırlıklar ----------------------------------------------------------------------------------------
def donchian(C: pd.DataFrame, Ns=(10, 20, 30, 60, 90, 150), cap=2.0, short=False) -> pd.DataFrame:
    """H004: coin x N durum makineleri; ağırlık (1/K) x (açık/len(Ns)) x min(0,25/σ, cap); Σ|w| <= 1."""
    K, sig = C.shape[1], vol(C)
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    for s in C.columns:
        c = C[s].to_numpy()
        on = np.zeros((len(c), len(Ns)))
        for j, N in enumerate(Ns):
            hi = pd.Series(c).shift(1).rolling(N).max().to_numpy()
            lo = pd.Series(c).shift(1).rolling(N).min().to_numpy()
            pos, stop = False, np.nan
            for t in range(len(c)):
                if np.isnan(hi[t]) or np.isnan(c[t]):
                    continue
                mid = (hi[t] + lo[t]) / 2
                if not pos and ((c[t] > hi[t]) if not short else (c[t] < lo[t])):
                    pos, stop = True, mid
                elif pos:
                    stop = max(stop, mid) if not short else min(stop, mid)
                    if (c[t] < stop) if not short else (c[t] > stop):
                        pos = False
                on[t, j] = pos
        W[s] = (1 / K) * on.mean(axis=1) * np.minimum(0.25 / sig[s].to_numpy(), cap) * (-1 if short else 1)
    return _cap(W.fillna(0.0))


def sma(C: pd.DataFrame, Ns=(20, 50, 100), cap=1.0) -> pd.DataFrame:
    """H005: oran = (#(close > SMA_N))/3; w = (1/K) x oran x min(0,25/σ, cap)."""
    K, sig = C.shape[1], vol(C)
    frac = sum((C > C.rolling(N).mean()).astype(float).where(C.rolling(N).mean().notna()) for N in Ns) / len(Ns)
    return _cap(((1 / K) * frac * np.minimum(0.25 / sig, cap)).fillna(0.0))


def xsmom(C: pd.DataFrame, top=3, lookback=14, long_short=False) -> pd.DataFrame:
    """H007: pazar kapanışında (pazartesi 00:00) 14 günlük getiri sırası; en iyi 3 long, ters vol ağırlık, brüt 1x."""
    sig, ret = vol(C), C / C.shift(lookback) - 1
    W = pd.DataFrame(np.nan, index=C.index, columns=C.columns)
    for d in C.index[C.index.dayofweek == 6]:
        r = ret.loc[d].dropna()
        if len(r) < top * 2 or sig.loc[d, r.index].isna().any():
            continue
        best, worst = r.nlargest(top).index, r.nsmallest(top).index
        w = pd.Series(0.0, index=C.columns)
        iv = 1 / sig.loc[d, best]
        w[best] = iv / iv.sum() * (0.5 if long_short else 1.0)
        if long_short:
            iv2 = 1 / sig.loc[d, worst]
            w[worst] = -iv2 / iv2.sum() * 0.5
        W.loc[d] = w
    return W  # NaN = işlem günü değil (pozisyon korunur)


def always_long(C: pd.DataFrame, cap: float) -> pd.DataFrame:
    return _cap(((1 / C.shape[1]) * np.minimum(0.25 / vol(C), cap)).where(C.notna()).fillna(0.0))


def equal_weight_weekly(C: pd.DataFrame) -> pd.DataFrame:
    W = pd.DataFrame(np.nan, index=C.index, columns=C.columns)
    sun = C.index.dayofweek == 6
    W.loc[sun] = C.loc[sun].notna().astype(float).div(C.loc[sun].notna().sum(axis=1), axis=0).to_numpy()
    return W


def _cap(W: pd.DataFrame) -> pd.DataFrame:
    g = W.abs().sum(axis=1)
    return W.div(np.maximum(g, 1.0), axis=0)


# ---- simülasyon ----------------------------------------------------------------------------------------------
def _fill(w: pd.Series, tgt: pd.Series) -> pd.Series:
    """Dolum anındaki yeni ağırlık. Hedef tümüyle NaN ise pozisyon korunur; tampon altındaki farklar işlenmez."""
    if not tgt.notna().any():
        return w
    tgt = tgt.fillna(0.0)
    diff = tgt - w
    trade = ~((diff.abs() < 0.10 * tgt.abs()) & (diff.abs() < 0.005))
    return w.where(~trade, tgt)


def _hold(d, w: pd.Series, new: pd.Series, R_d: pd.Series, f_d: pd.Series, rate: float, impl: str,
          cost_mult: float = 1.0) -> tuple[pd.Series, pd.Series]:
    """Bir dolum + bir dönem tutuş: (coin başına net getiri, sonraki dolumdaki sürüklenmiş ağırlık)."""
    held = new != 0
    if R_d[held].isna().any() or (impl == "perp" and f_d[held].isna().any()):
        raise ValueError(f"{d}: tutulan pozisyonda eksik fiyat/funding {list(R_d.index[held & R_d.isna()])}")
    tc = (new - w).abs() * rate
    f = 0.0
    if impl == "perp":
        f = new * f_d.fillna(0.0)
        f = f.clip(lower=0) * cost_mult + f.clip(upper=0)  # stres ödenen funding'i katlar, alınanı değil
    pnl_i = new * R_d.fillna(0.0) - tc - f
    gross = 1 + float(pnl_i.sum())
    return pnl_i, (new * (1 + R_d.fillna(0.0)) / gross if gross > 0 else new * 0)


def simulate(T: pd.DataFrame, X: pd.DataFrame, fund: pd.DataFrame, impl: str = "perp", cost_mult: float = 1.0,
             start=None) -> dict:
    rate = COST[impl] * cost_mult
    R = X.shift(-1) / X - 1
    idx = T.index if start is None else T.index[T.index >= start]
    w = pd.Series(0.0, index=T.columns)
    rets, contrib, turnover = [], pd.Series(0.0, index=T.columns), 0.0
    for d in idx[:-1]:
        new = _fill(w, T.loc[d])
        pnl_i, w_next = _hold(d, w, new, R.loc[d], fund.loc[d], rate, impl, cost_mult)
        rets.append(float(pnl_i.sum()))
        contrib += pnl_i
        turnover += float((new - w).abs().sum())
        w = w_next
    if rets:  # dönem sonunda kapanış maliyeti
        last = w.abs() * rate
        rets[-1] -= float(last.sum())
        contrib -= last
    # etiket: getirinin gerçekleştiği an = sonraki dolum (D + 2 gün + 1 saat)
    s = pd.Series(rets, index=idx[:-1] + pd.Timedelta(days=2, hours=1))
    return dict(r=s, contrib=contrib, turnover_ann=turnover * 365 / max(len(s), 1))


def metrics(r: pd.Series) -> dict:
    eq = (1 + r).cumprod()
    yrs = len(r) / 365
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if yrs > 0 and eq.iloc[-1] > 0 else -1.0
    dd = float((1 - eq / eq.cummax().clip(lower=1.0)).max())  # başlangıç NAV'ı 1
    sh = float(r.mean() / r.std() * math.sqrt(365)) if r.std() > 0 else 0.0
    return dict(sharpe=sh, cagr=float(cagr), maxdd=dd, calmar=float(cagr / dd) if dd > 0 else float("inf"),
                years={str(y): round(float((1 + g).prod() - 1), 4) for y, g in r.groupby(r.index.year)})


def block_boot_sharpe_lo(r: pd.Series, block=20, n=2000, seed=7) -> float:
    rng, x = np.random.default_rng(seed), r.to_numpy()
    nb = len(x) // block
    out = []
    for _ in range(n):
        st = rng.integers(0, len(x) - block, nb)
        s = np.concatenate([x[i:i + block] for i in st])
        out.append(s.mean() / s.std() * math.sqrt(365))
    return float(np.quantile(out, 0.025))


def newey_west_t(x: pd.Series, lags: int = 4) -> float:
    """Ortalama için Newey-West t istatistiği."""
    v = x.to_numpy()
    n, mu = len(v), v.mean()
    e = v - mu
    s = (e @ e) / n + 2 * sum((1 - k / (lags + 1)) * (e[k:] @ e[:-k]) / n for k in range(1, lags + 1))
    return float(mu / math.sqrt(s / n)) if s > 0 else 0.0


# ---- değerlendirme ------------------------------------------------------------------------------------------
def evaluate_trend(name: str, T: pd.DataFrame, bench: pd.DataFrame, X, fund, start, per_lookback=None) -> dict:
    out = {"name": name, "impl": {}, "bench": {}}
    for impl in ("perp", "spot"):
        b = out["bench"][impl] = metrics(simulate(bench, X, fund, impl, start=start)["r"])  # aynı piyasa kıyası
        base = simulate(T, X, fund, impl, start=start)
        stress = simulate(T, X, fund, impl, 2.0, start=start)
        m, ms = metrics(base["r"]), metrics(stress["r"])
        half = len(base["r"]) // 2
        h1, h2 = metrics(base["r"].iloc[:half]), metrics(base["r"].iloc[half:])
        coins_pos = int((base["contrib"] > 0).sum())
        g = [
            ("net Sharpe (temel)", round(m["sharpe"], 2), ">= 0.8", m["sharpe"] >= 0.8),
            ("net Sharpe (2x maliyet)", round(ms["sharpe"], 2), ">= 0.5", ms["sharpe"] >= 0.5),
            ("maks. düşüş / kıyas", round(m["maxdd"] / b["maxdd"], 2), "<= 0.6", m["maxdd"] <= 0.6 * b["maxdd"]),
            ("Calmar vs kıyas", f"{m['calmar']:.2f} vs {b['calmar']:.2f}", ">", m["calmar"] > b["calmar"]),
            ("net pozitif coin", coins_pos, f">= 7/{T.shape[1]}" if T.shape[1] == 10 else "hepsi", coins_pos >= (7 if T.shape[1] == 10 else T.shape[1])),
            ("iki yarı pozitif", f"{h1['cagr']:+.1%} / {h2['cagr']:+.1%}", "> 0 ikisi", h1["cagr"] > 0 and h2["cagr"] > 0),
        ]
        if per_lookback is not None:
            pos = sum(metrics(simulate(t_, X, fund, impl, start=start)["r"])["cagr"] > 0 for t_ in per_lookback)
            g.append(("pozitif geriye bakış", pos, f">= 4/{len(per_lookback)}", pos >= 4))
        out["impl"][impl] = dict(metrics=m, stress=ms, h1=h1["cagr"], h2=h2["cagr"], turnover=base["turnover_ann"],
                                 gate=[(a, str(v), t, bool(p)) for a, v, t, p in g], passed=all(p for *_, p in g),
                                 sharpe_lo=block_boot_sharpe_lo(base["r"]), r=base["r"])
    return out


def evaluate_xs(name: str, T: pd.DataFrame, X, fund, start, C) -> dict:
    bench = equal_weight_weekly(C)
    out = {"name": name, "impl": {}}
    for impl in ("perp", "spot"):
        base, stress = simulate(T, X, fund, impl, start=start), simulate(T, X, fund, impl, 2.0, start=start)
        b = simulate(bench, X, fund, impl, start=start)
        ex, ex2 = base["r"] - b["r"], stress["r"] - b["r"]
        wk, wk2 = ex.resample("W").sum(), ex2.resample("W").sum()
        half = len(wk) // 2
        t = newey_west_t(wk)
        g = [
            ("fazla getiri NW t (haftalık)", round(t, 2), ">= 2", t >= 2),
            ("fazla getiri 2x maliyet (yıllık)", f"{wk2.mean() * 52:+.1%}", "> 0", wk2.mean() > 0),
            ("iki yarı pozitif", f"{wk.iloc[:half].mean() * 52:+.1%} / {wk.iloc[half:].mean() * 52:+.1%}", "> 0 ikisi",
             wk.iloc[:half].mean() > 0 and wk.iloc[half:].mean() > 0),
        ]
        out["impl"][impl] = dict(metrics=metrics(base["r"]), bench=metrics(b["r"]), excess_ann=float(wk.mean() * 52),
                                 turnover=base["turnover_ann"], gate=[(a, str(v), tt, bool(p)) for a, v, tt, p in g],
                                 passed=all(p for *_, p in g), r=base["r"])
    return out


def report(res: dict) -> None:
    print(f"\n=== {res['name']}")
    for impl, b in res.get("bench", {}).items():
        print(f"  kıyas [{impl}] (vol-ölçekli hep long): Sharpe {b['sharpe']:.2f} CAGR {b['cagr']:+.1%} DD {b['maxdd']:.1%} yıllar {b['years']}")
    for impl, v in res["impl"].items():
        m = v["metrics"]
        print(f"  [{impl}] Sharpe {m['sharpe']:.2f} CAGR {m['cagr']:+.1%} DD {m['maxdd']:.1%} Calmar {m['calmar']:.2f} "
              f"devir/yıl {v['turnover']:.1f}  yıllar {m['years']}" + (f"  Sharpe %95 alt {v['sharpe_lo']:.2f}" if "sharpe_lo" in v else "")
              + (f"  fazla getiri/yıl {v['excess_ann']:+.1%}" if "excess_ann" in v else ""))
        for a, val, t, p in v["gate"]:
            print(f"     {'GEÇTİ' if p else 'KALDI':>6} {a}: {val} ({t})")
        print(f"     -> {'GEÇTİ' if v['passed'] else 'KALDI'}")


def run_all(suffix: str, record: bool) -> list[dict]:
    C, X, fund = load(suffix)
    start = C.index[0] + pd.Timedelta(days=WARMUP)
    Ns = (10, 20, 30, 60, 90, 150)
    res = [
        evaluate_trend("H004 Donchian ansamblı (long/flat, 10 coin)", donchian(C, Ns), always_long(C, 2.0), X, fund, start,
                       per_lookback=[donchian(C, (n,)) for n in Ns]),
        evaluate_trend("H004-S ayna short (ayrı rapor)", donchian(C, Ns, short=True), always_long(C, 2.0), X, fund, start),
    ]
    bc = ["BTCUSDT", "ETHUSDT"]
    res.append(evaluate_trend("H005 SMA filtresi (BTC+ETH, ana)", sma(C[bc]), always_long(C[bc], 1.0), X[bc], fund[bc], start))
    res.append(evaluate_trend("H005 SMA filtresi (10 coin, ikincil)", sma(C), always_long(C, 1.0), X, fund, start))
    res.append(evaluate_xs("H007 haftalık XS momentum (long-only)", xsmom(C), X, fund, start, C))
    res.append(evaluate_xs("H007-LS (long-short, ayrı rapor)", xsmom(C, long_short=True), X, fund, start, C))
    for r_ in res:
        report(r_)
    if record:
        # DSR: önceki tüm denemeler + portföy yapılandırmaları (ad x uygulama, tekil: hata düzeltmesi yeniden
        # koşusu yeni deneme sayılmaz). Not: DSR kapıyı etkilemez; kapı tanımlayıcı, DSR seçim düzeltmeli kanıt.
        srs = [v["metrics"]["sharpe"] / math.sqrt(365) for r_ in res for v in r_["impl"].values()]
        n = lab.trial_universe(lab.ledger())[0] + len(srs)  # aynı 12 yapılandırma; yeniden koşu N'i artırmaz
        var = float(np.var(srs, ddof=1))
        for r_ in res:
            for impl, v in r_["impl"].items():
                x = v["r"]
                d = lab.dsr(float(x.mean() / x.std()), len(x), float(x.skew()), float(x.kurt() + 3), n, var)
                v["dsr"] = d
                lab.append(dict(kind="portfolio", hyp=r_["name"].split()[0], name=r_["name"], impl=impl, window=suffix,
                                fix="codex-r4", passed=v["passed"],
                                dsr=round(d, 3), metrics=v["metrics"], gate=v["gate"], turnover=v["turnover"]))
                print(f"  DSR {r_['name'].split()[0]} [{impl}] = {d:.3f} (N={n})")
    return res


# ---- ileriye dönük paper (H005, kurallar donuk; gerçek emir yok, anahtar gerekmez) ----------------------------
FWD_D0 = pd.Timestamp("2026-10-15", tz="UTC")  # ilk sinyal günü -> ilk dolum 2026-10-16 01:00 UTC; tüm PnL ileriye dönük
FWD = {"btceth": ("BTCUSDT", "ETHUSDT"), "10coin": SYMS}  # ana, ikincil
JOURNAL = lab.ROOT / "runs" / "forward"
# kural parmak izi: bunlardan biri değişirse günlük devam etmez (yeni kart/günlük gerekir)
RULES = hashlib.sha256("".join(inspect.getsource(f) for f in (load, vol, sma, always_long, _cap, _fill, _hold)).encode()
                       + json.dumps(COST).encode()).hexdigest()[:16]


def update_data(syms=SYMS, now_ms: int | None = None) -> None:
    """data/ dosyalarına kapanmış yeni 1h perp barlarını ve funding baskılarını ekler. Yalnızca fapi: spot yedeği yok."""
    k = BinanceKlines("futures")
    k.endpoints = k.endpoints[:1]
    for s in syms:
        p = DATA / f"{s}_1h_1460d.csv"
        h = pd.read_csv(p)
        n0, start = len(h), int(h["open_time"].iloc[-1]) + 3_600_000
        while True:
            df = closed_only(k.fetch(s, "1h", start_ms=start, limit=1000), now_ms)
            if df.empty:
                break
            h = pd.concat([h, df], ignore_index=True)
            start = int(df["open_time"].iloc[-1]) + 3_600_000
        if (np.diff(h["open_time"].to_numpy()[max(n0 - 1, 0):]) != 3_600_000).any():
            raise ValueError(f"{s}: yeni barlarda boşluk; dosya yazılmadı")
        h.to_csv(p, index=False)
        fp = DATA / f"{s}_funding.csv"
        f = pd.read_csv(fp)
        r = requests.get("https://fapi.binance.com/fapi/v1/fundingRate", timeout=15,
                         params=dict(symbol=s, startTime=int(f["fundingTime"].iloc[-1]) + 1, limit=1000))
        r.raise_for_status()
        new = pd.DataFrame(r.json(), columns=["fundingTime", "fundingRate"]).astype({"fundingTime": "int64", "fundingRate": float})
        pd.concat([f, new], ignore_index=True).to_csv(fp, index=False)


def paper_rows(T: pd.DataFrame, X: pd.DataFrame, fund: pd.DataFrame, start=FWD_D0) -> list[dict]:
    """simulate() ile aynı dolum/tutuş kuralları (perp), gün gün. Son gün yalnızca dolum: getirisi henüz yok."""
    rate, R = COST["perp"], X.shift(-1) / X - 1
    idx = T.index[T.index >= start]
    w, rows = pd.Series(0.0, index=T.columns), []
    for i, d in enumerate(idx):
        new = _fill(w, T.loc[d])
        row = dict(date=str(d.date()), fill_utc=str(d + pd.Timedelta(days=1, hours=1)), px=X.loc[d].dropna().to_dict(),
                   target=T.loc[d].round(6).to_dict(), weight=new.round(6).to_dict(), traded=bool((new != w).any()))
        if i < len(idx) - 1:
            pnl_i, w = _hold(d, w, new, R.loc[d], fund.loc[d], rate, "perp")
            row |= dict(realized_utc=str(d + pd.Timedelta(days=2, hours=1)), ret=float(pnl_i.sum()))
        rows.append(row)
    return rows


def _read(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def paper(fetch: bool = True) -> None:
    """Günlük iş (01:05 UTC sonrası): veriyi güncelle, yeni dolum ve gerçekleşen NAV satırlarını günlüğe ekle.
    Kaçırılan günler sonraki koşuda aynı kurallarla yakalanır; yazılmış satırlar asla değişmez."""
    if fetch:
        update_data()
    C, X, fund = load(end=None)
    JOURNAL.mkdir(parents=True, exist_ok=True)
    for name, syms in FWD.items():
        cs, p = list(syms), JOURNAL / f"H005_{name}.jsonl"
        old = _read(p)
        if old and old[0]["rules"] != RULES:
            raise SystemExit(f"{p.name}: kurallar değişmiş ({old[0]['rules']} -> {RULES}); donuk test bozulur")
        have = {(r["kind"], r["date"]): r for r in old}
        rows = paper_rows(sma(C[cs]), X[cs], fund[cs], FWD_D0)
        bench = paper_rows(always_long(C[cs], 1.0), X[cs], fund[cs], FWD_D0)
        out, nav, bnav = [], 1.0, 1.0
        for r, b in zip(rows, bench):
            if ("fill", r["date"]) not in have:
                out.append(dict(kind="fill", rules=RULES) | {k: r[k] for k in ("date", "fill_utc", "px", "target", "weight", "traded")})
            if "ret" not in r:
                continue
            nav, bnav = nav * (1 + r["ret"]), bnav * (1 + b["ret"])
            prev = have.get(("nav", r["date"]))
            if prev is None:
                out.append(dict(kind="nav", rules=RULES, date=r["date"], realized_utc=r["realized_utc"], ret=r["ret"],
                                nav=nav, bench_ret=b["ret"], bench_nav=bnav))
            elif abs(prev["ret"] - r["ret"]) > 1e-9:
                raise SystemExit(f"{p.name} {r['date']}: yeniden hesap günlükten farklı ({prev['ret']} vs {r['ret']})")
        with p.open("a", encoding="utf-8") as f:
            f.writelines(json.dumps(x, default=float) + "\n" for x in out)
        last = rows[-1] if rows else None
        print(f"H005 {name}: +{len(out)} satır" + (f"; son dolum {last['fill_utc']} ağırlık {last['weight']}" if last else "; henüz dolum yok"))


def forward() -> None:
    """2026-10-16'dan beri paper sonucu, aynı piyasa vol-ölçekli hep-long kıyasıyla. Holdout kapısı ≥60 günde."""
    for name, syms in FWD.items():
        nav = pd.DataFrame([r for r in _read(JOURNAL / f"H005_{name}.jsonl") if r["kind"] == "nav"])
        print(f"\n=== H005 {name} ileriye dönük paper (ilk dolum 2026-10-16 01:00 UTC)")
        if nav.empty:
            print("  henüz gerçekleşen gün yok")
            continue
        t = pd.to_datetime(nav["realized_utc"])
        m, mb = metrics(pd.Series(nav["ret"].to_numpy(), t)), metrics(pd.Series(nav["bench_ret"].to_numpy(), t))
        print(f"  {len(nav)} gün, son {nav['realized_utc'].iloc[-1]}")
        print(f"  H005  NAV {nav['nav'].iloc[-1]:.4f}  Sharpe {m['sharpe']:.2f}  DD {m['maxdd']:.1%}")
        print(f"  kıyas NAV {nav['bench_nav'].iloc[-1]:.4f}  Sharpe {mb['sharpe']:.2f}  DD {mb['maxdd']:.1%}")
        if len(nav) < lab.MIN_HOLDOUT_DAYS:
            print(f"  holdout kapısı: {len(nav)}/{lab.MIN_HOLDOUT_DAYS} gün, değerlendirilmedi")
            continue
        C, X, fund = load(syms=syms, end=None)
        report(evaluate_trend(f"H005 {name} holdout kapısı (4. tur kapıları, ileriye dönük pencere)", sma(C),
                              always_long(C, 1.0), X, fund, FWD_D0))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "main"
    if mode == "paper":
        paper()
    elif mode == "forward":
        forward()
    else:
        run_all("1h_1460d" if mode == "main" else "1h_2020", record=mode == "main")
