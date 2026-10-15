"""Kötümser dolum kurallarıyla paper broker.

Kurallar (spec, kâğıt simülatörü):
- Giriş: sinyal barından SONRAKİ barın açılışında piyasa emri + kayma + taker ücreti.
- Stop: borsada duruyormuş gibi her barda önce kontrol edilir; boşlukta (gap) açılış fiyatından,
  ek kayma ile dolar.
- TP: limit emir; fiyat seviyeyi yalnızca değmekle değil aşmakla dolar, maker ücreti.
- Aynı barda hem stop hem TP mümkünse önce stop varsayılır.
- Zaman stopu: N bar içinde hedefin yarısına ulaşılamazsa kapanışta çıkılır.
"""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass, field

from opusjev.config import CostConfig

_ids = itertools.count(1)


@dataclass
class Position:
    symbol: str
    side: str
    qty: float
    entry_price: float
    stop: float
    take_profit: float
    entry_time: int
    entry_fee: float
    risk_usd: float
    setup: str
    provider: str
    proposal_id: str
    bars_held: int = 0
    mfe: float = 0.0  # en iyi lehte hareket (fiyat birimi)
    id: int = field(default_factory=lambda: next(_ids))

    @property
    def sign(self) -> int:
        return 1 if self.side == "long" else -1

    def notional(self, price: float) -> float:
        return abs(self.qty * price)


@dataclass
class Trade:
    id: int
    symbol: str
    side: str
    setup: str
    provider: str
    proposal_id: str
    qty: float
    entry_time: int
    exit_time: int
    entry_price: float
    exit_price: float
    exit_reason: str
    fees: float
    pnl: float  # ücretler düşülmüş net
    r_multiple: float
    bars_held: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PendingEntry:
    symbol: str
    side: str
    qty: float
    stop_distance: float
    tp_distance: float
    risk_usd: float
    setup: str
    provider: str
    proposal_id: str


class PaperBroker:
    def __init__(self, starting_equity: float, costs: CostConfig, time_stop_bars: int):
        self.cash = starting_equity  # gerçekleşmiş özsermaye
        self.costs = costs
        self.time_stop_bars = time_stop_bars
        self.hard_time_stop = False  # True: `time_stop_bars` dolunca her durumda çık (araştırma kartları)
        self.positions: dict[str, Position] = {}
        self.pending: dict[str, PendingEntry] = {}
        self.last_price: dict[str, float] = {}
        self.trades: list[Trade] = []
        self.fees_paid = 0.0

    # ---- durum -------------------------------------------------------------
    def unrealized(self) -> float:
        return sum(p.sign * p.qty * (self.last_price.get(s, p.entry_price) - p.entry_price) for s, p in self.positions.items())

    def equity(self) -> float:
        return self.cash + self.unrealized()

    def gross_exposure(self) -> float:
        return sum(p.notional(self.last_price.get(s, p.entry_price)) for s, p in self.positions.items())

    # ---- emirler -----------------------------------------------------------
    def submit_entry(self, entry: PendingEntry) -> None:
        if entry.symbol in self.positions or entry.symbol in self.pending:
            raise ValueError(f"{entry.symbol} için zaten açık pozisyon veya bekleyen emir var")
        self.pending[entry.symbol] = entry

    def flatten_all(self, time_ms: int, reason: str = "flatten") -> list[Trade]:
        self.pending.clear()
        out = []
        for sym in list(self.positions):
            px = self.last_price[sym]
            p = self.positions[sym]
            out.append(self._close(p, px * (1 - p.sign * self.costs.slippage), time_ms, reason, self.costs.taker_fee))
        return out

    # ---- bar işleme --------------------------------------------------------
    def on_bar(self, symbol: str, bar: dict) -> list[Trade]:
        """Bir sembolün yeni kapanmış barını işler. Kapanan işlemleri döndürür."""
        o, h, lo, c = bar["open"], bar["high"], bar["low"], bar["close"]
        closed: list[Trade] = []
        pe = self.pending.pop(symbol, None)
        if pe is not None:
            self._fill_entry(pe, o, bar["open_time"])
        p = self.positions.get(symbol)
        if p is not None:
            p.bars_held += 1
            t = self._check_exit(p, o, h, lo, c, bar["close_time"])
            if t is not None:
                closed.append(t)
        self.last_price[symbol] = c
        return closed

    def _fill_entry(self, pe: PendingEntry, open_px: float, t: int) -> None:
        slip = self.costs.slippage
        sign = 1 if pe.side == "long" else -1
        fill = open_px * (1 + sign * slip)
        fee = pe.qty * fill * self.costs.taker_fee
        self.cash -= fee
        self.fees_paid += fee
        self.positions[pe.symbol] = Position(
            symbol=pe.symbol,
            side=pe.side,
            qty=pe.qty,
            entry_price=fill,
            stop=fill - sign * pe.stop_distance,  # stop/TP mesafeleri gerçek dolum fiyatına göre sabitlenir
            take_profit=fill + sign * pe.tp_distance,
            entry_time=t,
            entry_fee=fee,
            risk_usd=pe.risk_usd,
            setup=pe.setup,
            provider=pe.provider,
            proposal_id=pe.proposal_id,
        )

    def _check_exit(self, p: Position, o: float, h: float, lo: float, c: float, t: int) -> Trade | None:
        k = self.costs
        if p.side == "long":
            if lo <= p.stop:
                px = min(p.stop, o) * (1 - k.slippage - k.stop_extra_slippage)
                return self._close(p, px, t, "stop", k.taker_fee)
            if h >= p.take_profit * (1 + k.tp_through):
                return self._close(p, p.take_profit, t, "take_profit", k.maker_fee)
            p.mfe = max(p.mfe, h - p.entry_price)
        else:
            if h >= p.stop:
                px = max(p.stop, o) * (1 + k.slippage + k.stop_extra_slippage)
                return self._close(p, px, t, "stop", k.taker_fee)
            if lo <= p.take_profit * (1 - k.tp_through):
                return self._close(p, p.take_profit, t, "take_profit", k.maker_fee)
            p.mfe = max(p.mfe, p.entry_price - lo)
        half_target = 0.5 * abs(p.take_profit - p.entry_price)
        if p.bars_held >= self.time_stop_bars and (self.hard_time_stop or p.mfe < half_target):
            return self._close(p, c * (1 - p.sign * k.slippage), t, "time_stop", k.taker_fee)
        return None

    def _close(self, p: Position, px: float, t: int, reason: str, fee_rate: float) -> Trade:
        fee = p.qty * px * fee_rate
        gross = p.sign * p.qty * (px - p.entry_price)
        self.cash += gross - fee
        self.fees_paid += fee
        pnl = gross - fee - p.entry_fee
        del self.positions[p.symbol]
        tr = Trade(
            id=p.id,
            symbol=p.symbol,
            side=p.side,
            setup=p.setup,
            provider=p.provider,
            proposal_id=p.proposal_id,
            qty=p.qty,
            entry_time=p.entry_time,
            exit_time=t,
            entry_price=p.entry_price,
            exit_price=px,
            exit_reason=reason,
            fees=fee + p.entry_fee,
            pnl=pnl,
            r_multiple=pnl / p.risk_usd if p.risk_usd > 0 else 0.0,
            bars_held=p.bars_held,
        )
        self.trades.append(tr)
        return tr
