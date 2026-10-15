from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from opusjev.config import JevConfig
from opusjev.decision import JevProvider
from opusjev.signals import Candidate

CAND = Candidate("BTCUSDT", "long", "mean_reversion", 0, 100.0, 99.0, 102.0, 1.0, "range", {"rsi": 25.0})


class FakeClient:
    def __init__(self, choice="take", p_take=0.8, tokens=800, exc=None):
        self.choice, self.p_take, self.tokens, self.exc = choice, p_take, tokens, exc
        self.calls = []

    def system_one(self, state, questions, model=None, timeout=None):
        self.calls.append({"state": state, "questions": questions, "model": model})
        if self.exc:
            raise self.exc
        ans = SimpleNamespace(choice=self.choice, confidence=0.7, probabilities={"take": self.p_take, "skip": 1 - self.p_take})
        return SimpleNamespace(model="jev-1.13", usage=SimpleNamespace(input_tokens=self.tokens), choices={"entry": ans})


def test_take_above_threshold():
    c = FakeClient(p_take=0.8)
    p = JevProvider(JevConfig(), client=c).decide(CAND, {"equity": 1})
    assert p.action == "take" and p.take_probability == pytest.approx(0.8)
    assert p.cost_usd == pytest.approx(800 * 0.042 / 1e6)
    q = c.calls[0]["questions"]["entry"]
    assert q.type == "choice" and set(q.criteria) == {"take", "skip"}
    assert c.calls[0]["state"]["candidate"]["stop_loss"] == 99.0


def test_take_below_threshold_becomes_skip():
    p = JevProvider(JevConfig(), client=FakeClient(p_take=0.55)).decide(CAND, {})
    assert p.action == "skip"


def test_choice_case_insensitive_and_skip_choice():
    assert JevProvider(JevConfig(), client=FakeClient(choice="TAKE", p_take=0.9)).decide(CAND, {}).action == "take"
    assert JevProvider(JevConfig(), client=FakeClient(choice="skip", p_take=0.3)).decide(CAND, {}).action == "skip"


def test_errors_fail_safe_to_skip():
    p = JevProvider(JevConfig(), client=FakeClient(exc=TimeoutError("slow"))).decide(CAND, {})
    assert p.action == "skip" and p.reason.startswith("error")


def test_missing_answer_is_skip():
    c = FakeClient()
    c.system_one = lambda **kw: SimpleNamespace(model="x", usage=SimpleNamespace(input_tokens=1), choices={})
    assert JevProvider(JevConfig(), client=c).decide(CAND, {}).action == "skip"


def test_daily_call_cap_and_reset():
    day = [datetime(2026, 10, 14, tzinfo=timezone.utc)]
    c = FakeClient()
    prov = JevProvider(JevConfig(max_calls_per_day=2), client=c, clock=lambda: day[0])
    assert [prov.decide(CAND, {}).action for _ in range(3)] == ["take", "take", "skip"]
    assert len(c.calls) == 2
    day[0] = datetime(2026, 10, 15, tzinfo=timezone.utc)
    assert prov.decide(CAND, {}).action == "take"


def test_spend_cap():
    c = FakeClient(tokens=10_000_000)  # 0.42$ / çağrı
    prov = JevProvider(JevConfig(daily_spend_cap_usd=0.5), client=c)
    assert [prov.decide(CAND, {}).action for _ in range(3)] == ["take", "take", "skip"]
