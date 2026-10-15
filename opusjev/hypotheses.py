"""Araştırma döngüsünün sinyal kurucuları. Her biri bir hipotez kartına (research/cards/H*.toml) bağlıdır.

İmza: builder(feats, fund, **params) -> {sembol: Series(+1 long / -1 short / 0)}; Series, feats[sembol] satırlarıyla
hizalıdır. Yalnızca sinyal barının kapanışında bilinen veri kullanılır (tests/test_lab.py nedensellik testi).
Funding kaydı fundingTime anında kesinleşir; kapanışı ondan önce olan bar onu göremez.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

HOUR = 3_600_000


def _last_funding(f: pd.DataFrame, fu: pd.DataFrame, cols=("fundingRate",)) -> pd.DataFrame:
    fu = fu.sort_values("fundingTime")
    m = pd.merge_asof(f[["close_time"]], fu[["fundingTime", *cols]], left_on="close_time", right_on="fundingTime")
    return m.set_index(f.index)


def _sigma(lr: pd.Series) -> pd.Series:
    return lr.rolling(720).std().shift(1)  # son 30 günün saatlik oynaklığı, mevcut bar hariç


def h001_flush_reversal(feats: dict, fund: dict, k: float, vol_mult: float) -> dict:
    """Zorunlu likidasyon sonrası geri dönüş: hacimli, k-sigma'lık saatlik düşüş + pozitif funding -> long (simetriği short)."""
    out = {}
    for s, f in feats.items():
        lr = np.log(f["close"]).diff()
        sig, big_vol = _sigma(lr), f["volume"] >= vol_mult * f["volume"].rolling(168).median().shift(1)
        fr = _last_funding(f, fund[s])["fundingRate"]
        long_ = (lr <= -k * sig) & big_vol & (fr > 0)
        short = (lr >= k * sig) & big_vol & (fr < 0)
        out[s] = pd.Series(np.where(long_, 1, np.where(short, -1, 0)), index=f.index)
    return out


def h002_prefunding(feats: dict, fund: dict, lead: int, q: float, window: int = 90) -> dict:
    """Funding ödemesinden kaçan taşıyıcılar: uç pozitif funding'de ödemeden `lead` saat önce short (simetriği long).

    Sonraki ödeme zamanı geçmişten çıkarılır: son kesinleşme + son aralık (8 saatlik ve 4 saatlik semboller).
    """
    out = {}
    for s, f in feats.items():
        fu = fund[s].sort_values("fundingTime").reset_index(drop=True)
        r = fu["fundingRate"]
        fu["hi"], fu["lo"] = r.rolling(window).quantile(q), r.rolling(window).quantile(1 - q)
        fu["iv"] = (fu["fundingTime"].diff() / HOUR).round() * HOUR
        m = _last_funding(f, fu, ("fundingRate", "hi", "lo", "iv"))
        next_settle = (m["fundingTime"] // HOUR) * HOUR + m["iv"]
        at_lead = (f["close_time"] + 1) == next_settle - lead * HOUR
        short = at_lead & (m["fundingRate"] >= m["hi"]) & (m["fundingRate"] > 0)
        long_ = at_lead & (m["fundingRate"] <= m["lo"]) & (m["fundingRate"] < 0)
        out[s] = pd.Series(np.where(short, -1, np.where(long_, 1, 0)), index=f.index)
    return out


def h003_btc_lead(feats: dict, fund: dict, k: float, lag_frac: float) -> dict:
    """Bilgi önce BTC'ye gelir: BTC'nin k-sigma'lık saatini geride kalan altcoin bir sonraki saatlerde izler."""
    b = feats["BTCUSDT"].set_index("open_time")
    lrb = np.log(b["close"]).diff()
    zb = lrb / _sigma(lrb)
    out = {}
    for s, f in feats.items():
        if s == "BTCUSDT":
            out[s] = pd.Series(0, index=f.index)
            continue
        lr = np.log(f["close"]).diff()
        za = lr / _sigma(lr)
        z = zb.reindex(f["open_time"]).to_numpy()
        long_ = (z >= k) & (za.to_numpy() < lag_frac * z)
        short = (z <= -k) & (za.to_numpy() > lag_frac * z)
        out[s] = pd.Series(np.where(long_, 1, np.where(short, -1, 0)), index=f.index)
    return out
