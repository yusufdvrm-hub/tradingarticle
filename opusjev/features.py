"""İndikatörler. Hepsi yalnızca geçmiş ve kapanmış barları kullanır (lookahead yok)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from opusjev.config import StrategyConfig


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def atr(df: pd.DataFrame, n: int) -> pd.Series:
    prev = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df: pd.DataFrame, n: int) -> pd.Series:
    up = df["high"].diff()
    dn = -df["low"].diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(df, n)
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean().fillna(0)


def compute(df: pd.DataFrame, cfg: StrategyConfig) -> pd.DataFrame:
    out = df.copy()
    c = out["close"]
    out["ema_fast"] = ema(c, cfg.ema_fast)
    out["ema_slow"] = ema(c, cfg.ema_slow)
    out["atr"] = atr(out, cfg.atr_period)
    out["adx"] = adx(out, cfg.adx_period)
    out["rsi"] = rsi(c, cfg.rsi_period)
    mid = c.rolling(cfg.bb_period).mean()
    sd = c.rolling(cfg.bb_period).std()
    out["bb_mid"], out["bb_up"], out["bb_dn"] = mid, mid + cfg.bb_std * sd, mid - cfg.bb_std * sd
    # Donchian kanalı: mevcut barı HARİÇ tutar, kırılım mevcut kapanışla ölçülür.
    out["dc_high"] = out["high"].shift(1).rolling(cfg.donchian).max()
    out["dc_low"] = out["low"].shift(1).rolling(cfg.donchian).min()
    out["rvol"] = np.log(c).diff().rolling(96).std()
    out["rvol_p99"] = out["rvol"].rolling(960, min_periods=200).quantile(0.99)
    return out
