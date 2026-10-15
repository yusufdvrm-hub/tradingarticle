import pytest

from opusjev.broker import PaperBroker, Trade
from opusjev.config import CostConfig, RiskConfig
from opusjev.decision import Proposal
from opusjev.risk import RiskManager
from opusjev.signals import Candidate

# 2026-10-14 10:00 UTC: funding pencerelerinden uzak
NOW = 1_791_972_000_000
TAKE = Proposal(action="take", take_probability=0.9, provider="t")


def cand(symbol="BTCUSDT", side="long", ref=100.0, stop=99.0, tp=102.0):
    return Candidate(symbol, side, "mean_reversion", NOW, ref, stop, tp, 1.0, "range", {})


def setup(equity=10_000.0, **kw):
    rcfg = RiskConfig(**kw)
    rm = RiskManager(rcfg, CostConfig(), ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"), equity)
    br = PaperBroker(equity, CostConfig(), 16)
    rm.on_time(NOW, equity)
    return rm, br


def loss_trade(t=NOW, pnl=-10.0):
    return Trade(1, "BTCUSDT", "long", "s", "p", "id", 1, t, t, 100, 99, "stop", 0.1, pnl, -1.0, 2)


def test_sizing_risks_half_percent_including_costs():
    rm, br = setup()
    d = rm.evaluate(cand(), TAKE, br, NOW, 100.0)
    assert d.approved
    assert d.risk_usd == pytest.approx(50.0, rel=0.01)
    assert d.qty * 100 < 20_000  # kaldıraç tavanı içinde


def test_provider_skip_is_vetoed():
    rm, br = setup()
    d = rm.evaluate(cand(), Proposal(action="skip", take_probability=0.2, provider="t"), br, NOW, 100.0)
    assert not d.approved


def test_stop_wrong_side_and_bad_reward_risk():
    rm, br = setup()
    assert not rm.evaluate(cand(stop=101.0), TAKE, br, NOW, 100.0).approved
    assert not rm.evaluate(cand(tp=101.0), TAKE, br, NOW, 100.0).approved


def test_not_whitelisted_and_price_deviation():
    rm, br = setup()
    assert not rm.evaluate(cand(symbol="DOGEUSDT"), TAKE, br, NOW, 100.0).approved
    assert not rm.evaluate(cand(), TAKE, br, NOW, 100.5).approved


def test_daily_loss_limit_blocks_entries():
    rm, br = setup()
    br.cash = 9_790.0
    d = rm.evaluate(cand(), TAKE, br, NOW, 100.0)
    assert not d.approved and any("R5" in r for r in d.reasons)


def test_peak_drawdown_halts_until_human_reset():
    rm, br = setup()
    rm.on_time(NOW + 86_400_000 * 8, 8_900.0)
    assert rm.state.halted
    br.cash = 8_900.0
    rm.on_time(NOW + 86_400_000 * 9, 8_900.0)
    assert not rm.evaluate(cand(), TAKE, br, NOW + 86_400_000 * 9, 100.0).approved
    rm.human_reset_halt()
    rm.on_time(NOW + 86_400_000 * 9 + 1, 8_900.0)
    assert not rm.state.halted


def test_consecutive_losses_cooldown_then_half_size():
    rm, br = setup()
    for _ in range(4):
        rm.on_trade_closed(loss_trade())
    assert not rm.evaluate(cand(), TAKE, br, NOW + 30 * 60_000, 100.0).approved
    d = rm.evaluate(cand(), TAKE, br, NOW + 61 * 60_000, 100.0)
    assert d.approved and d.risk_usd == pytest.approx(25.0, rel=0.01)


def test_max_positions_and_correlation_cluster():
    rm, br = setup()
    for sym in ("BTCUSDT", "ETHUSDT"):
        d = rm.evaluate(cand(symbol=sym), TAKE, br, NOW, 100.0)
        br.submit_entry(rm.to_pending(cand(symbol=sym), d, TAKE, sym, NOW))
    d = rm.evaluate(cand(symbol="SOLUSDT"), TAKE, br, NOW, 100.0)
    assert not d.approved and any("korelasyon" in r for r in d.reasons)
    d = rm.evaluate(cand(symbol="SOLUSDT", side="short", stop=101.0, tp=98.0), TAKE, br, NOW, 100.0)
    assert d.approved
    br.submit_entry(rm.to_pending(cand(symbol="SOLUSDT", side="short", stop=101.0, tp=98.0), d, TAKE, "s", NOW))
    d = rm.evaluate(cand(symbol="XRPUSDT", side="short", stop=101.0, tp=98.0), TAKE, br, NOW, 100.0)
    assert not d.approved and any("azami" in r for r in d.reasons)


def test_same_symbol_spacing_and_daily_entry_cap():
    rm, br = setup(max_entries_per_day=1)
    d = rm.evaluate(cand(), TAKE, br, NOW, 100.0)
    rm.to_pending(cand(), d, TAKE, "a", NOW)
    d2 = rm.evaluate(cand(symbol="ETHUSDT"), TAKE, br, NOW, 100.0)
    assert not d2.approved and any("R10" in r for r in d2.reasons)


def test_funding_window_blocked():
    rm, br = setup()
    funding_eve = 1_791_936_000_000 - 10 * 60_000  # 2026-10-14 00:00 UTC'den 10 dk önce
    rm.on_time(funding_eve, 10_000)
    d = rm.evaluate(cand(), TAKE, br, funding_eve, 100.0)
    assert not d.approved and any("R11" in r for r in d.reasons)


def test_stale_data_blocked():
    rm, br = setup()
    assert not rm.evaluate(cand(), TAKE, br, NOW, 100.0, data_age_s=120).approved


def test_leverage_cap_shrinks_never_grows():
    rm, br = setup()
    tight = cand(stop=99.99, tp=100.02)  # çok dar stop -> devasa boyut isterdi
    d = rm.evaluate(tight, TAKE, br, NOW, 100.0)
    assert d.approved and d.qty * 100 <= 15_000 + 1e-6
