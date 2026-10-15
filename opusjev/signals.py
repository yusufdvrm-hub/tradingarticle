"""Deterministik aday üretici: rejim filtreli ortalamaya dönüş + trend kırılımı.

Aday yalnızca bir önermedir; jev onaylamazsa ve risk yöneticisi izin vermezse
hiçbir emir oluşmaz.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from opusjev.config import StrategyConfig


@dataclass(frozen=True)
class Candidate:
    symbol: str
    side: str  # "long" | "short"
    setup: str  # "mean_reversion" | "breakout"
    bar_time: int  # sinyal barının kapanış zamanı (ms)
    ref_price: float  # sinyal barının kapanışı
    stop: float
    take_profit: float
    atr: float
    regime: str
    features: dict

    @property
    def stop_distance(self) -> float:
        return abs(self.ref_price - self.stop)

    def to_dict(self) -> dict:
        return asdict(self)


def regime_of(row: pd.Series, cfg: StrategyConfig) -> str:
    if row["adx"] >= cfg.adx_trend:
        return "trend_up" if row["ema_fast"] > row["ema_slow"] else "trend_down"
    if row["adx"] <= cfg.adx_range:
        return "range"
    return "neutral"


def generate(symbol: str, feats: pd.DataFrame, cfg: StrategyConfig) -> Candidate | None:
    """Son kapanmış bar için en fazla bir aday döndürür."""
    if len(feats) < cfg.warmup_bars:
        return None
    row = feats.iloc[-1]
    if row[["atr", "bb_up", "bb_dn", "dc_high", "dc_low"]].isna().any() or row["atr"] <= 0:
        return None
    # R11 (kısmi): aşırı volatilitede yeni aday yok.
    if pd.notna(row["rvol_p99"]) and row["rvol"] > row["rvol_p99"]:
        return None
    regime = regime_of(row, cfg)
    close, a = float(row["close"]), float(row["atr"])
    side = setup = None
    if regime == "range":
        if close < row["bb_dn"] and row["rsi"] < 30:
            side, setup = "long", "mean_reversion"
        elif close > row["bb_up"] and row["rsi"] > 70:
            side, setup = "short", "mean_reversion"
    elif regime == "trend_up" and close > row["dc_high"]:
        side, setup = "long", "breakout"
    elif regime == "trend_down" and close < row["dc_low"]:
        side, setup = "short", "breakout"
    if side is None:
        return None
    d = cfg.stop_atr_mult * a
    if side == "long":
        stop, tp = close - d, close + cfg.tp_r_multiple * d
    else:
        stop, tp = close + d, close - cfg.tp_r_multiple * d
    features = {
        k: round(float(row[k]), 6)
        for k in ("close", "ema_fast", "ema_slow", "atr", "adx", "rsi", "bb_up", "bb_mid", "bb_dn", "dc_high", "dc_low", "rvol")
        if pd.notna(row[k])
    }
    recent = feats["close"].iloc[-8:].pct_change().dropna()
    features["last_8_bar_returns_pct"] = [round(x * 100, 3) for x in recent]
    return Candidate(symbol, side, setup, int(row["close_time"]), close, stop, tp, a, regime, features)
