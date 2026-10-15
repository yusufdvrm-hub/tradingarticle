"""Alternatif giriş sinyalleri (araştırma, 2026-10-15). `signals.generate` ile aynı imza.

Her fikir önce vektörel olarak bir `sig` sütunu (+1 long, -1 short, 0 yok) üretir; `from_sig` yalnızca son
kapanmış barı okur. Hepsi geçmiş/kapanmış veriyle hesaplanır (lookahead yok).

- tsmom: zaman serisi momentumu (Moskowitz-Ooi-Pedersen 2012; kripto: Liu-Tsyvinski 2021).
- funding_extreme: funding uç değerlerinde kalabalığın tersine (He-Manela-Ross-von Wachter 2022 perp fiyatlaması).
- xs_momentum: kesitsel momentum (Liu-Tsyvinski-Wu 2022, kripto momentum faktörü).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from opusjev.config import StrategyConfig
from opusjev.signals import Candidate


def tsmom(df: pd.DataFrame, lookback: int, z_th: float) -> pd.Series:
    """L saatlik log getiri / (30 günlük saatlik oynaklık * sqrt(L)); |z| > eşik yönünde."""
    lr = np.log(df["close"]).diff()
    z = (np.log(df["close"]) - np.log(df["close"].shift(lookback))) / (lr.rolling(720).std() * np.sqrt(lookback))
    return np.sign(z).where(z.abs() > z_th, 0).fillna(0)


def funding_extreme(df: pd.DataFrame, funding: pd.DataFrame, window: int, q: float) -> pd.Series:
    """Son kesinleşmiş funding, son `window` kesinleşmenin q/1-q yüzdeliğini aşarsa ters yönde.

    Pozitif uç (kalabalık long) -> short, negatif uç -> long. İşaret şartı: üst uç >0, alt uç <0.
    """
    f = funding.sort_values("fundingTime").reset_index(drop=True)
    r = f["fundingRate"]
    hi, lo = r.rolling(window).quantile(q), r.rolling(window).quantile(1 - q)
    f["s"] = np.where((r >= hi) & (r > 0), -1, np.where((r <= lo) & (r < 0), 1, 0))
    m = pd.merge_asof(df[["close_time"]], f[["fundingTime", "s"]], left_on="close_time", right_on="fundingTime")
    return pd.Series(m["s"].fillna(0).to_numpy(), index=df.index)


def xs_momentum(closes: pd.DataFrame, lookback: int, k: int) -> pd.DataFrame:
    """closes: open_time x sembol. L saatlik getiride en iyi k long, en kötü k short."""
    rank = np.log(closes / closes.shift(lookback)).rank(axis=1)
    n = rank.notna().sum(axis=1)
    sig = pd.DataFrame(0, index=closes.index, columns=closes.columns)
    sig[rank.gt(n - k, axis=0)] = 1
    sig[rank.le(k, axis=0) & rank.notna()] = -1
    return sig


def from_sig(symbol: str, feats: pd.DataFrame, cfg: StrategyConfig, setup: str = "alt") -> Candidate | None:
    row = feats.iloc[-1]
    s = row["sig"]
    if s == 0 or pd.isna(row["atr"]) or row["atr"] <= 0:
        return None
    side = "long" if s > 0 else "short"
    close, a = float(row["close"]), float(row["atr"])
    d = cfg.stop_atr_mult * a * (1 if s > 0 else -1)
    return Candidate(symbol, side, setup, int(row["close_time"]), close, close - d, close + cfg.tp_r_multiple * d, a, setup,
                     {"close": close, "atr": round(a, 6)})


if __name__ == "__main__":
    t = pd.DataFrame({"close_time": np.arange(10) * 10, "close": np.linspace(1, 2, 10)})
    fu = pd.DataFrame({"fundingTime": [0, 30, 60], "fundingRate": [0.0001, 0.001, -0.001]})
    assert list(funding_extreme(t, fu, 2, 0.9)) == [0, 0, 0, -1, -1, -1, 1, 1, 1, 1]
    c = pd.DataFrame({"A": [1, 2, 3], "B": [1, 1, 1], "C": [3, 2, 1]})
    assert xs_momentum(c, 1, 1).iloc[-1].tolist() == [1, 0, -1]
    print("ok")
