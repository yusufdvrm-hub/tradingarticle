import numpy as np
import pandas as pd

from opusjev.config import Settings, StrategyConfig
from opusjev.data import TF_MS, synthetic
from opusjev.decision import BaselineProvider, Proposal
from opusjev.engine import Engine, run_backtest
from opusjev.features import compute
from opusjev.live import PaperRunner
from opusjev.metrics import go_live_gate, summarize


def test_features_have_no_lookahead():
    df = synthetic("BTCUSDT", bars=1200)
    cfg = StrategyConfig()
    full = compute(df, cfg)
    part = compute(df.iloc[:900], cfg)
    cols = ["ema_fast", "atr", "adx", "rsi", "bb_up", "dc_high", "rvol"]
    pd.testing.assert_frame_equal(full[cols].iloc[:900], part[cols])


class SkipAll:
    name = "skipall"

    def decide(self, c, ctx):
        return Proposal(action="skip", take_probability=0.0, provider=self.name)


def _feats(bars=4000):
    s = Settings()
    return s, {sym: compute(synthetic(sym, bars=bars), s.strategy) for sym in s.strategy.symbols}


def test_backtest_runs_and_respects_invariants():
    s, feats = _feats()
    eng = run_backtest(Engine(s, BaselineProvider()), feats)
    trades = eng.broker.trades
    assert len(trades) > 20
    # Hiçbir işlem planlanan riskin (stop kayması dahil) belirgin ötesinde kaybetmemeli (gap hariç küçük pay).
    assert min(t.r_multiple for t in trades) > -1.6
    assert all(t.exit_reason in {"stop", "take_profit", "time_stop"} for t in trades)
    # Sembol başına aynı anda en fazla 1 pozisyon: aynı sembolde işlemler çakışmamalı.
    for sym in s.strategy.symbols:
        ts = sorted((t.entry_time, t.exit_time) for t in trades if t.symbol == sym)
        assert all(a[1] <= b[0] for a, b in zip(ts, ts[1:]))
    # Muhasebe: nakit = başlangıç + net PnL toplamı (açık pozisyon girişi ücretleri hariç)
    open_fees = sum(p.entry_fee for p in eng.broker.positions.values())
    assert np.isclose(eng.broker.cash, s.starting_equity + sum(t.pnl for t in trades) - open_fees)
    m = summarize(trades, eng.equity_curve, s.starting_equity)
    assert m["trades"] == len(trades)
    assert len(go_live_gate(m, m)) == 9


def test_skip_provider_never_trades():
    s, feats = _feats(1500)
    eng = run_backtest(Engine(s, SkipAll()), feats)
    assert eng.broker.trades == [] and eng.provider_calls > 0


class FakeFeed:
    """Canlı Binance yerine sentetik veriden 'şu ana kadar' barları döndürür."""

    def __init__(self, bars=1500):
        self.dfs = {sym: synthetic(sym, bars=bars) for sym in Settings().strategy.symbols}

    def fetch(self, symbol, interval, limit=500, **kw):
        df = self.dfs[symbol]
        return df[df["open_time"] <= self.now - TF_MS[interval]].tail(limit + 1).reset_index(drop=True)


def test_paper_runner_processes_and_resumes(tmp_path):
    feed = FakeFeed()
    df = feed.dfs["BTCUSDT"]
    s = Settings()
    feed.now = int(df["close_time"].iloc[600]) + 1
    r = PaperRunner(s, BaselineProvider(), tmp_path, feed=feed)
    assert r.poll_once(feed.now) == 1  # ilk çalıştırma geçmişi oynatmaz
    for i in range(601, 900):
        feed.now = int(df["close_time"].iloc[i]) + 1
        r.poll_once(feed.now)
    trades_before = len(r.engines["primary"].broker.trades)
    assert (tmp_path / "status.json").exists() and (tmp_path / "report.md").exists()
    r2 = PaperRunner(s, BaselineProvider(), tmp_path, feed=feed)  # diskten devam
    assert len(r2.engines["primary"].broker.trades) == trades_before
    feed.now = int(df["close_time"].iloc[905]) + 1
    assert r2.poll_once(feed.now) == 6  # kaçırılan 900..905 barları yakalanır


def test_paper_runner_catchup_bars_do_not_open_new_entries(tmp_path):
    feed = FakeFeed()
    df = feed.dfs["BTCUSDT"]
    s = Settings()
    feed.now = int(df["close_time"].iloc[600]) + 1
    r = PaperRunner(s, BaselineProvider(), tmp_path, feed=feed)
    r.poll_once(feed.now)
    feed.now = int(df["close_time"].iloc[1400]) + 1
    entries_before = r.engines["primary"].risk.state.last_entry_ms.copy()
    r.poll_once(feed.now)  # 800 bar geride kalınmış: yalnızca son bar taze
    new = {k: v for k, v in r.engines["primary"].risk.state.last_entry_ms.items() if entries_before.get(k) != v}
    assert all(v >= int(df["close_time"].iloc[1399]) for v in new.values())
