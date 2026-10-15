"""Piyasa verisi: Binance USDⓈ-M herkese açık kline uç noktaları (anahtar gerekmez).

Ayrıca ağ erişimi olmadan test için deterministik sentetik veri üreticisi içerir.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

FAPI_BASES = ("https://fapi.binance.com",)
SPOT_BASES = ("https://data-api.binance.vision", "https://api.binance.com")
TF_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000}
COLUMNS = ["open_time", "open", "high", "low", "close", "volume", "close_time"]


def _parse(rows: list[list]) -> pd.DataFrame:
    df = pd.DataFrame([r[:7] for r in rows], columns=COLUMNS)
    for c in ("open", "high", "low", "close", "volume"):
        df[c] = df[c].astype(float)
    df["open_time"] = df["open_time"].astype("int64")
    df["close_time"] = df["close_time"].astype("int64")
    return df


class BinanceKlines:
    """USDⓈ-M klines; erişilemezse spot kline aynasına düşer (fiyat çok yakındır)."""

    def __init__(self, market: str = "futures", session: requests.Session | None = None, timeout: float = 10.0):
        self.session = session or requests.Session()
        self.timeout = timeout
        if market == "futures":
            self.endpoints = [(b, "/fapi/v1/klines") for b in FAPI_BASES] + [(b, "/api/v3/klines") for b in SPOT_BASES]
        else:
            self.endpoints = [(b, "/api/v3/klines") for b in SPOT_BASES]

    def _get(self, params: dict) -> list[list]:
        last_err: Exception | None = None
        for base, path in self.endpoints:
            try:
                r = self.session.get(base + path, params=params, timeout=self.timeout)
                if r.status_code in (418, 429):
                    time.sleep(int(r.headers.get("Retry-After", "5")))
                    continue
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                last_err = e
        raise ConnectionError(f"Hiçbir Binance uç noktasına erişilemedi: {last_err}")

    def fetch(self, symbol: str, interval: str, start_ms: int | None = None, end_ms: int | None = None, limit: int = 1000) -> pd.DataFrame:
        params: dict = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_ms is not None:
            params["startTime"] = start_ms
        if end_ms is not None:
            params["endTime"] = end_ms
        return _parse(self._get(params))

    def history(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        step = TF_MS[interval]
        end = int(time.time() * 1000)
        start = end - days * 86_400_000
        frames = []
        while start < end:
            df = self.fetch(symbol, interval, start_ms=start, limit=1000)
            if df.empty:
                break
            frames.append(df)
            start = int(df["open_time"].iloc[-1]) + step
            time.sleep(0.2)
        out = pd.concat(frames).drop_duplicates("open_time").reset_index(drop=True)
        return closed_only(out)


def closed_only(df: pd.DataFrame, now_ms: int | None = None) -> pd.DataFrame:
    """Henüz kapanmamış son barı at; özellikler yalnızca kapanmış barlarda hesaplanır."""
    now_ms = now_ms if now_ms is not None else int(time.time() * 1000)
    return df[df["close_time"] < now_ms].reset_index(drop=True)


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def synthetic(symbol: str, bars: int = 3000, interval: str = "15m", seed: int = 0, start_price: float = 100.0) -> pd.DataFrame:
    """Rejim değiştiren sentetik fiyat serisi (yatay / trend / şok).

    YALNIZCA sistem tesisatını test etmek içindir; buradan çıkan PnL
    stratejinin gerçek performansı hakkında hiçbir şey söylemez.
    """
    rng = np.random.default_rng(seed + sum(map(ord, symbol)))
    step = TF_MS[interval]
    rets = np.empty(bars)
    i = 0
    while i < bars:
        n = int(rng.integers(150, 500))
        regime = rng.choice(["range", "up", "down", "shock"], p=[0.45, 0.25, 0.25, 0.05])
        vol = rng.uniform(0.002, 0.006)
        if regime == "range":
            seg = rng.normal(0, vol, n)
            seg -= 0.08 * np.cumsum(seg) / np.arange(1, n + 1)  # hafif ortalamaya dönüş
        elif regime == "up":
            seg = rng.normal(vol * 0.15, vol, n)
        elif regime == "down":
            seg = rng.normal(-vol * 0.15, vol, n)
        else:
            seg = rng.normal(0, vol * 3, n)
        rets[i : i + n] = seg[: bars - i]
        i += n
    close = start_price * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[start_price], close[:-1]])
    wick = np.abs(rng.normal(0, 0.0015, bars))
    high = np.maximum(open_, close) * (1 + wick)
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.0015, bars)))
    t0 = 1_700_000_000_000 - (1_700_000_000_000 % step)
    open_time = t0 + np.arange(bars, dtype=np.int64) * step
    return pd.DataFrame(
        {
            "open_time": open_time,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": rng.uniform(100, 1000, bars),
            "close_time": open_time + step - 1,
        }
    )
