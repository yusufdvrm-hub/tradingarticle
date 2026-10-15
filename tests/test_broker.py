import pytest

from opusjev.broker import PaperBroker, PendingEntry
from opusjev.config import CostConfig

COSTS = CostConfig()


def bar(t, o, h, l, c):
    return {"open_time": t, "close_time": t + 899_999, "open": o, "high": h, "low": l, "close": c}


def entry(side="long", sd=1.0, tp=2.0, qty=1.0):
    return PendingEntry("BTCUSDT", side, qty, sd, tp, sd * qty, "test", "baseline", "p1")


def test_entry_fills_at_next_open_with_slippage_and_fee():
    b = PaperBroker(1000, COSTS, time_stop_bars=100)
    b.submit_entry(entry())
    b.on_bar("BTCUSDT", bar(0, 100, 100.5, 99.5, 100))
    p = b.positions["BTCUSDT"]
    assert p.entry_price == pytest.approx(100 * (1 + COSTS.slippage))
    assert p.stop == pytest.approx(p.entry_price - 1.0)
    assert b.cash == pytest.approx(1000 - p.entry_price * COSTS.taker_fee)


def test_stop_checked_before_take_profit_in_same_bar():
    b = PaperBroker(1000, COSTS, 100)
    b.submit_entry(entry())
    b.on_bar("BTCUSDT", bar(0, 100, 100.1, 99.9, 100))
    trades = b.on_bar("BTCUSDT", bar(1, 100, 105, 95, 100))  # hem stop hem TP aralıkta
    assert trades[0].exit_reason == "stop"
    assert trades[0].pnl < 0


def test_gap_through_stop_fills_at_open_not_stop():
    b = PaperBroker(1000, COSTS, 100)
    b.submit_entry(entry())
    b.on_bar("BTCUSDT", bar(0, 100, 100.1, 99.9, 100))
    stop = b.positions["BTCUSDT"].stop
    t = b.on_bar("BTCUSDT", bar(1, 97, 97.5, 96, 97))[0]
    assert t.exit_price < stop
    assert t.exit_price == pytest.approx(97 * (1 - COSTS.slippage - COSTS.stop_extra_slippage))


def test_take_profit_requires_trade_through():
    b = PaperBroker(1000, COSTS, 100)
    b.submit_entry(entry())
    b.on_bar("BTCUSDT", bar(0, 100, 100.1, 99.9, 100))
    tp = b.positions["BTCUSDT"].take_profit
    assert b.on_bar("BTCUSDT", bar(1, 100, tp, 99.5, 101)) == []  # yalnızca değdi
    t = b.on_bar("BTCUSDT", bar(2, 101, tp * 1.001, 100.5, 101))[0]
    assert t.exit_reason == "take_profit" and t.exit_price == pytest.approx(tp) and t.pnl > 0


def test_short_side_symmetry():
    b = PaperBroker(1000, COSTS, 100)
    b.submit_entry(entry(side="short"))
    b.on_bar("BTCUSDT", bar(0, 100, 100.1, 99.9, 100))
    p = b.positions["BTCUSDT"]
    assert p.stop > p.entry_price > p.take_profit
    t = b.on_bar("BTCUSDT", bar(1, 100, 101.5, 99.8, 101))[0]
    assert t.exit_reason == "stop" and t.pnl < 0


def test_time_stop_when_half_target_not_reached():
    b = PaperBroker(1000, COSTS, time_stop_bars=3)
    b.submit_entry(entry())
    b.on_bar("BTCUSDT", bar(0, 100, 100.2, 99.8, 100))
    assert b.on_bar("BTCUSDT", bar(1, 100, 100.3, 99.8, 100.1)) == []
    t = b.on_bar("BTCUSDT", bar(2, 100, 100.3, 99.8, 100.1))[0]
    assert t.exit_reason == "time_stop"


def test_duplicate_entry_rejected():
    b = PaperBroker(1000, COSTS, 100)
    b.submit_entry(entry())
    with pytest.raises(ValueError):
        b.submit_entry(entry())


def test_round_trip_accounting_matches_cash():
    b = PaperBroker(1000, COSTS, 100)
    b.submit_entry(entry())
    b.on_bar("BTCUSDT", bar(0, 100, 100.1, 99.9, 100))
    t = b.on_bar("BTCUSDT", bar(1, 100, 99.5, 98, 98.5))[0]
    assert b.cash == pytest.approx(1000 + t.pnl)
    assert b.equity() == pytest.approx(b.cash)


@pytest.mark.parametrize("hard,exits", [(False, False), (True, True)])
def test_hard_time_stop_exits_even_after_half_target(hard, exits):
    b = PaperBroker(1000, COSTS, time_stop_bars=2)
    b.hard_time_stop = hard
    b.submit_entry(entry(sd=1.0, tp=4.0))
    b.on_bar("BTCUSDT", bar(0, 100, 102.5, 99.9, 102))  # MFE 2.5 > yarım hedef (2.0)
    trades = b.on_bar("BTCUSDT", bar(1, 102, 102.2, 101.8, 102))
    assert bool(trades) == exits
