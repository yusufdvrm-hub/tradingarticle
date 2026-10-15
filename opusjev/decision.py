"""Karar sağlayıcıları (DecisionProvider).

Sağlayıcı yalnızca `take` / `skip` önerir. Miktar, kaldıraç ve stop fiyatı
belirleyemez; bunlar adayda ve risk yöneticisinde sabittir. Her hata, zaman
aşımı, bütçe aşımı veya belirsiz cevap güvenli varsayılan olan `skip`'e düşer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from opusjev.config import JevConfig
from opusjev.signals import Candidate


class Proposal(BaseModel):
    action: Literal["take", "skip"]
    take_probability: float = Field(ge=0, le=1)
    provider: str
    reason: str = ""
    cost_usd: float = 0.0
    input_tokens: int = 0
    latency_ms: int = 0
    model: str | None = None
    raw: dict[str, Any] | None = None


class DecisionProvider(Protocol):
    name: str

    def decide(self, candidate: Candidate, context: dict) -> Proposal: ...


class BaselineProvider:
    """Her adayı onaylar. jev ablasyonu için gölge temel çizgi."""

    name = "baseline"

    def decide(self, candidate: Candidate, context: dict) -> Proposal:
        return Proposal(action="take", take_probability=1.0, provider=self.name, reason="baseline: always take")


@dataclass
class SpendTracker:
    """Günlük çağrı sayısı ve USD harcama tavanı (UTC gününe göre sıfırlanır)."""

    daily_cap_usd: float
    max_calls: int
    day: str = ""
    spent_usd: float = 0.0
    calls: int = 0
    total_usd: float = field(default=0.0)

    def _roll(self, now: datetime) -> None:
        d = now.strftime("%Y-%m-%d")
        if d != self.day:
            self.day, self.spent_usd, self.calls = d, 0.0, 0

    def allow(self, now: datetime) -> bool:
        self._roll(now)
        return self.calls < self.max_calls and self.spent_usd < self.daily_cap_usd

    def record(self, usd: float, now: datetime) -> None:
        self._roll(now)
        self.calls += 1
        self.spent_usd += usd
        self.total_usd += usd


INSTRUCTIONS = (
    "You are the entry filter of a conservative, short-term crypto trading system. "
    "A deterministic rule engine proposed the trade candidate in the state. The stop-loss and "
    "take-profit are fixed (reward:risk is about 2:1) and position size is set by a risk manager. "
    "Decide only whether this specific entry is likely to reach its take-profit before its stop-loss. "
    "Prefer 'skip' unless the setup is clean: the regime agrees with the setup, momentum is not "
    "strongly against the trade, and volatility is not abnormal. Fees make marginal trades losing trades."
)

CRITERIA = {
    "take": "Enter the trade: the take-profit is more likely than usual to be hit before the stop-loss.",
    "skip": "Do not enter: the setup is marginal, conflicting, or too risky.",
}


class JevProvider:
    """TypeSafe AI jev (System One) üzerinden giriş filtresi."""

    name = "jev"

    def __init__(self, cfg: JevConfig, client: Any | None = None, clock=lambda: datetime.now(timezone.utc)):
        self.cfg = cfg
        self.clock = clock
        self.spend = SpendTracker(cfg.daily_spend_cap_usd, cfg.max_calls_per_day)
        if client is None:
            from typesafe_sdk import TypeSafeClient  # TYPESAFE_API_KEY ortam değişkeninden okunur

            client = TypeSafeClient(timeout=cfg.timeout_s)
        self.client = client

    def _skip(self, reason: str, **kw) -> Proposal:
        return Proposal(action="skip", take_probability=0.0, provider=self.name, reason=reason, **kw)

    def decide(self, candidate: Candidate, context: dict) -> Proposal:
        now = self.clock()
        if not self.spend.allow(now):
            return self._skip("budget: daily jev call/spend cap reached")
        from typesafe_sdk import Choice

        state = {
            "candidate": {
                "symbol": candidate.symbol,
                "side": candidate.side,
                "setup": candidate.setup,
                "regime": candidate.regime,
                "entry_ref_price": candidate.ref_price,
                "stop_loss": round(candidate.stop, 6),
                "take_profit": round(candidate.take_profit, 6),
                "stop_distance_pct": round(100 * candidate.stop_distance / candidate.ref_price, 3),
            },
            "indicators": candidate.features,
            "portfolio": context,
        }
        t0 = time.monotonic()
        try:
            resp = self.client.system_one(
                state=state,
                questions={"entry": Choice(instructions=INSTRUCTIONS, criteria=CRITERIA)},
                model=self.cfg.model,
                timeout=self.cfg.timeout_s,
            )
        except Exception as e:  # ağ, kimlik, oran limiti, doğrulama: hepsi skip
            self.spend.record(0.0, now)
            return self._skip(f"error: {type(e).__name__}: {str(e)[:160]}", latency_ms=int((time.monotonic() - t0) * 1000))
        latency = int((time.monotonic() - t0) * 1000)
        tokens = int(getattr(resp.usage, "input_tokens", 0) or 0)
        cost = tokens * self.cfg.usd_per_input_token
        self.spend.record(cost, now)
        ans = resp.choices.get("entry")
        if ans is None:
            return self._skip("invalid: no 'entry' answer", cost_usd=cost, input_tokens=tokens, latency_ms=latency)
        probs = {str(k).lower(): float(v) for k, v in ans.probabilities.items()}
        p_take = min(max(probs.get("take", 0.0), 0.0), 1.0)
        action = "take" if str(ans.choice).lower() == "take" and p_take >= self.cfg.min_take_probability else "skip"
        return Proposal(
            action=action,
            take_probability=p_take,
            provider=self.name,
            reason=f"jev choice={ans.choice} p_take={p_take:.3f} conf={ans.confidence:.3f}",
            cost_usd=cost,
            input_tokens=tokens,
            latency_ms=latency,
            model=resp.model,
            raw={"choice": ans.choice, "confidence": ans.confidence, "probabilities": probs},
        )
