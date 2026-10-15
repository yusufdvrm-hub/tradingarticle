"""Veto yetkili deterministik risk yöneticisi (spec R1–R14).

Risk yöneticisi bir öneriyi yalnızca küçültebilir veya reddedebilir; asla büyütmez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from opusjev.broker import PaperBroker, PendingEntry, Trade
from opusjev.config import CostConfig, RiskConfig
from opusjev.decision import Proposal
from opusjev.signals import Candidate

MIN_NOTIONAL = 10.0
FUNDING_HOURS_UTC = (0, 8, 16)
FUNDING_BLACKOUT_MIN = 20


def _dt(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


@dataclass
class RiskDecision:
    approved: bool
    qty: float = 0.0
    risk_usd: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass
class RiskState:
    peak_equity: float
    day: str = ""
    day_start_equity: float = 0.0
    week: str = ""
    week_start_equity: float = 0.0
    entries_today: int = 0
    last_entry_ms: dict[str, int] = field(default_factory=dict)
    consecutive_losses: int = 0
    cooldown_until_ms: int = 0
    half_size: bool = False
    halted: bool = False  # zirveden düşüş: yalnızca insan sıfırlar
    halt_reason: str = ""


class RiskManager:
    def __init__(self, cfg: RiskConfig, costs: CostConfig, whitelist: tuple[str, ...], starting_equity: float):
        self.cfg = cfg
        self.costs = costs
        self.whitelist = set(whitelist)
        self.state = RiskState(peak_equity=starting_equity)

    # ---- zaman ve sonuç güncellemeleri ------------------------------------
    def on_time(self, now_ms: int, equity: float) -> None:
        s = self.state
        now = _dt(now_ms)
        day = now.strftime("%Y-%m-%d")
        week = "%d-W%02d" % now.isocalendar()[:2]
        if day != s.day:
            s.day, s.day_start_equity, s.entries_today = day, equity, 0
        if week != s.week:
            s.week, s.week_start_equity = week, equity
        s.peak_equity = max(s.peak_equity, equity)
        if not s.halted and equity <= s.peak_equity * (1 - self.cfg.peak_drawdown_halt):
            s.halted = True
            s.halt_reason = f"R6: zirveden -%{self.cfg.peak_drawdown_halt*100:.0f} düşüş; insan incelemesi gerekli"

    def on_trade_closed(self, trade: Trade) -> None:
        s = self.state
        if trade.pnl < 0:
            s.consecutive_losses += 1
            if s.consecutive_losses >= self.cfg.max_consecutive_losses:
                s.cooldown_until_ms = trade.exit_time + self.cfg.cooldown_minutes * 60_000
                s.half_size = True
                s.consecutive_losses = 0
        else:
            s.consecutive_losses = 0
            if trade.pnl > 0:
                s.half_size = False

    def human_reset_halt(self) -> None:
        self.state.halted = False
        self.state.halt_reason = ""
        self.state.peak_equity = 0.0  # bir sonraki on_time'da güncel özsermayeye ayarlanır

    # ---- giriş kapıları ---------------------------------------------------
    def entries_blocked(self, now_ms: int, equity: float) -> list[str]:
        s, c = self.state, self.cfg
        r = []
        if s.halted:
            r.append(s.halt_reason)
        if s.day_start_equity and equity <= s.day_start_equity * (1 - c.daily_loss_limit):
            r.append("R5: günlük kayıp limiti")
        if s.week_start_equity and equity <= s.week_start_equity * (1 - c.weekly_loss_limit):
            r.append("R6: haftalık kayıp limiti")
        if now_ms < s.cooldown_until_ms:
            r.append("R7: ardışık kayıp soğuması")
        if s.entries_today >= c.max_entries_per_day:
            r.append("R10: günlük giriş tavanı")
        return r

    def evaluate(
        self,
        cand: Candidate,
        proposal: Proposal,
        broker: PaperBroker,
        now_ms: int,
        last_price: float,
        data_age_s: float = 0.0,
    ) -> RiskDecision:
        c = self.cfg
        equity = broker.equity()
        reasons = self.entries_blocked(now_ms, equity)
        if proposal.action != "take":
            reasons.append(f"provider skip ({proposal.reason})")
        if cand.symbol not in self.whitelist:
            reasons.append("R12: sembol beyaz listede değil")
        if cand.symbol in broker.positions or cand.symbol in broker.pending:
            reasons.append("R8: sembolde zaten pozisyon var")
        if len(broker.positions) + len(broker.pending) >= c.max_open_positions:
            reasons.append("R8: azami açık pozisyon")
        same_side = sum(1 for p in broker.positions.values() if p.side == cand.side) + sum(
            1 for p in broker.pending.values() if p.side == cand.side
        )
        if same_side >= 2:
            reasons.append("R8: korelasyon kümesi (aynı yönde en fazla 2)")
        last = self.state.last_entry_ms.get(cand.symbol)
        if last is not None and now_ms - last < c.min_minutes_between_entries * 60_000:
            reasons.append("R10: aynı sembolde giriş aralığı")
        entry_dt = _dt(now_ms + 1)
        minute_of_day = entry_dt.hour * 60 + entry_dt.minute
        if any(abs(minute_of_day - h * 60) <= FUNDING_BLACKOUT_MIN or abs(minute_of_day - h * 60 - 1440) <= FUNDING_BLACKOUT_MIN for h in FUNDING_HOURS_UTC):
            reasons.append("R11: funding zamanı penceresi")
        sd = cand.stop_distance
        tp_d = abs(cand.take_profit - cand.ref_price)
        if sd <= 0:
            reasons.append("R12: stop mesafesi sıfır")
        elif (cand.side == "long" and cand.stop >= cand.ref_price) or (cand.side == "short" and cand.stop <= cand.ref_price):
            reasons.append("R12: stop yanlış tarafta")
        elif tp_d / sd < c.min_reward_risk:
            reasons.append("R3: ödül/risk oranı düşük")
        if abs(last_price / cand.ref_price - 1) > c.max_entry_deviation:
            reasons.append("R12: fiyat referanstan çok uzak")
        if data_age_s > c.max_data_age_seconds:
            reasons.append("R13: veri bayat")
        if reasons:
            return RiskDecision(False, reasons=reasons)

        # R1: boyutlandırma (stop kayması ve çift yönlü maliyet dahil)
        k = self.costs
        risk_frac = c.risk_per_trade * (0.5 if self.state.half_size else 1.0)
        risk_usd = equity * risk_frac
        per_unit_loss = sd + cand.ref_price * (2 * k.taker_fee + 2 * k.slippage + k.stop_extra_slippage)
        qty = risk_usd / per_unit_loss
        notional = qty * cand.ref_price
        # R9 + R8: kaldıraç ve brüt maruziyet tavanı (yalnızca küçültür)
        cap = min(c.max_leverage * equity, c.max_gross_exposure * equity - broker.gross_exposure())
        notes = []
        if notional > cap:
            qty = max(cap, 0.0) / cand.ref_price
            notes.append("R8/R9: boyut tavana küçültüldü")
        if qty * cand.ref_price < MIN_NOTIONAL:
            return RiskDecision(False, reasons=["min notional altında"])
        qty = float(f"{qty:.6g}")
        return RiskDecision(True, qty=qty, risk_usd=qty * per_unit_loss, reasons=notes)

    def to_pending(self, cand: Candidate, decision: RiskDecision, proposal: Proposal, proposal_id: str, now_ms: int) -> PendingEntry:
        self.state.entries_today += 1
        self.state.last_entry_ms[cand.symbol] = now_ms
        return PendingEntry(
            symbol=cand.symbol,
            side=cand.side,
            qty=decision.qty,
            stop_distance=cand.stop_distance,
            tp_distance=abs(cand.take_profit - cand.ref_price),
            risk_usd=decision.risk_usd,
            setup=cand.setup,
            provider=proposal.provider,
            proposal_id=proposal_id,
        )

