"""Sabit risk ve strateji parametreleri.

Risk değerleri spec'teki R1–R14 tablosundan gelir. jev veya Claude bunları
değiştiremez; yalnızca insan bu dosyayı düzenleyerek değiştirir.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RiskConfig:
    risk_per_trade: float = 0.005  # R1: özsermayenin %0,5'i
    min_reward_risk: float = 1.5  # R3: TP mesafesi >= 1.5 x stop mesafesi
    time_stop_bars: int = 16  # R4: 16 x 15dk = 4 saat
    daily_loss_limit: float = 0.02  # R5
    weekly_loss_limit: float = 0.05  # R6
    peak_drawdown_halt: float = 0.10  # R6: insan incelemesi gerekir
    max_consecutive_losses: int = 4  # R7
    cooldown_minutes: int = 60  # R7
    max_open_positions: int = 3  # R8
    max_gross_exposure: float = 1.5  # R8: brüt maruziyet / özsermaye
    max_leverage: float = 2.0  # R9
    max_entries_per_day: int = 12  # R10
    min_minutes_between_entries: int = 30  # R10: aynı sembolde
    max_entry_deviation: float = 0.003  # R12: son fiyattan ±%0,3
    max_data_age_seconds: int = 60  # R13: kapanmış bar kapanıştan en fazla 60 sn sonra işlenmeli


@dataclass(frozen=True)
class CostConfig:
    """Kötümser dolum modeli (spec: kâğıt simülatörü kuralları)."""

    taker_fee: float = 0.0005  # Binance USDⓈ-M, kötümser taraf
    maker_fee: float = 0.0002
    slippage: float = 0.0002  # her piyasa/stop emrine ek 2 bps
    stop_extra_slippage: float = 0.0003  # stoplar ek 3 bps daha kötü
    tp_through: float = 0.0001  # limit TP, fiyat seviyeyi 1 bps aşınca dolar


@dataclass(frozen=True)
class StrategyConfig:
    timeframe: str = "15m"
    symbols: tuple[str, ...] = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    atr_period: int = 14
    stop_atr_mult: float = 1.2
    tp_r_multiple: float = 2.0  # TP = 2R (asimetrik hedef)
    adx_period: int = 14
    adx_trend: float = 25.0
    adx_range: float = 20.0
    bb_period: int = 20
    bb_std: float = 2.0
    rsi_period: int = 14
    donchian: int = 20
    ema_fast: int = 50
    ema_slow: int = 200
    warmup_bars: int = 220


@dataclass(frozen=True)
class JevConfig:
    model: str = "jev-latest"
    timeout_s: float = 15.0
    min_take_probability: float = 0.6  # altı otomatik skip
    # TypeSafe yayınlanmış fiyat: girdi tokeni başına $0.042 / 1M; çıktı ücretsiz.
    usd_per_input_token: float = 0.042 / 1_000_000
    daily_spend_cap_usd: float = 0.50  # 5$ bakiye için muhafazakâr tavan
    max_calls_per_day: int = 60


@dataclass(frozen=True)
class Settings:
    risk: RiskConfig = field(default_factory=RiskConfig)
    costs: CostConfig = field(default_factory=CostConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    jev: JevConfig = field(default_factory=JevConfig)
    starting_equity: float = 10_000.0
