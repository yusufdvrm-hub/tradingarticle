import numpy as np
import pandas as pd
import pytest

from opusjev import portfolio as P


def _prices(n=400, seed=3):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=n, freq="D", tz="UTC")
    C = pd.DataFrame({s: 100 * np.exp(np.cumsum(rng.normal(0.001, 0.03, n))) for s in ("A", "B", "C", "D", "E", "F", "G")}, index=idx)
    return C


@pytest.mark.parametrize("fn", [lambda C: P.donchian(C, (10, 30)), lambda C: P.sma(C), lambda C: P.xsmom(C)])
def test_targets_are_causal(fn):
    C = _prices()
    full, cut = fn(C), fn(C.iloc[:300])
    a, b = full.iloc[:300], cut
    assert np.allclose(a.fillna(-9).to_numpy(), b.fillna(-9).to_numpy())


def test_simulate_costs_and_funding():
    idx = pd.date_range("2024-01-01", periods=4, freq="D", tz="UTC")
    X = pd.DataFrame({"A": [100.0, 110.0, 110.0, 110.0]}, index=idx)
    fund = pd.DataFrame({"A": [0.001, 0.0, 0.0, np.nan]}, index=idx)
    T = pd.DataFrame({"A": [1.0, 1.0, 0.0, 0.0]}, index=idx)
    r = P.simulate(T, X, fund, "perp")["r"]
    # gün 0: alım maliyeti 0.0007 + %10 getiri - funding 0.001 (long öder)
    assert r.iloc[0] == pytest.approx(0.10 - 0.0007 - 0.001)
    # gün 1: hedef aynı, sürüklenme tamponun altında -> işlem yok; gün 2: satış, maliyet |w| x 0.0007
    w1 = 1.1 / (1 + r.iloc[0])
    assert r.iloc[1] == pytest.approx(0.0)
    assert r.iloc[2] == pytest.approx(-w1 * 0.0007)
    assert P.simulate(T, X, fund, "spot")["r"].iloc[0] == pytest.approx(0.10 - 0.0012)


def test_buffer_skips_small_trades():
    idx = pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")
    X = pd.DataFrame({"A": [100.0, 100.0, 100.0]}, index=idx)
    fund = pd.DataFrame({"A": [0.0, 0.0, 0.0]}, index=idx)
    T = pd.DataFrame({"A": [0.5, 0.503, 0.503]}, index=idx)  # fark 0.003 < 0.005 ve < 0.05 -> işlem yok
    r = P.simulate(T, X, fund, "perp")["r"]
    assert r.iloc[1] == pytest.approx(-0.5 * 0.0007, rel=1e-2)  # yalnızca dönem sonu kapanışı; 0.003'lük işlem atlandı


def test_load_alignment_and_price_weighted_funding(tmp_path, monkeypatch):
    t0 = pd.Timestamp("2024-01-01", tz="UTC")
    times = pd.date_range(t0, periods=72, freq="h")
    close = np.arange(72, dtype=float) + 100  # saat i'nin kapanışı = 100 + i
    ms = (times - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(milliseconds=1)
    pd.DataFrame({"open_time": ms, "open": close, "high": close, "low": close, "close": close, "volume": 1.0,
                  "close_time": ms + 3_599_999}).to_csv(tmp_path / "A_t.csv", index=False)
    ft = (pd.date_range(t0, periods=9, freq="8h") - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(milliseconds=1)
    pd.DataFrame({"fundingTime": ft, "fundingRate": 0.001}).to_csv(tmp_path / "A_funding.csv", index=False)
    monkeypatch.setattr(P, "DATA", tmp_path)
    C, X, fund = P.load("t", syms=("A",))
    d0 = t0
    assert C.loc[d0, "A"] == 123  # gün D'nin 23:00 barı (D+1 00:00'da kapanır) -> sinyal
    assert X.loc[d0, "A"] == 124  # D+1'in 00:00 barı (01:00'da kapanır) -> dolum
    # dolum(D) = 2 Ocak 01:00, sonraki 3 Ocak 01:00; arada saat 32, 40, 48 baskıları,
    # fiyat = o anda kapanan barın (açılış 31, 39, 47) kapanışı
    px = [100 + 31, 100 + 39, 100 + 47]
    assert fund.loc[d0, "A"] == pytest.approx(0.001 * sum(px) / 124)


def test_paper_daily_step_matches_simulate_and_is_append_only(tmp_path, monkeypatch):
    C = _prices(260)[["A", "B"]]
    X = C * 1.001
    fund = pd.DataFrame(0.0001, index=C.index, columns=C.columns)
    start = C.index[200]
    monkeypatch.setattr(P, "load", lambda **k: (C, X, fund))
    monkeypatch.setattr(P, "JOURNAL", tmp_path)
    monkeypatch.setattr(P, "FWD", {"t": ("A", "B")})
    monkeypatch.setattr(P, "FWD_D0", start)
    P.paper(fetch=False)
    rows = P._read(tmp_path / "H005_t.jsonl")
    fills, navs = [r for r in rows if r["kind"] == "fill"], [r for r in rows if r["kind"] == "nav"]
    assert len(fills) == 60 and len(navs) == 59  # son gün yalnızca dolum, getirisi yarın
    sim = P.simulate(P.sma(C), X, fund, "perp", start=start)["r"]
    # simulate dönem sonunda kapanış maliyeti düşer; paper devam ettiği için düşmez -> son gün hariç birebir
    assert np.allclose([r["ret"] for r in navs][:-1], sim.to_numpy()[:-1])
    assert navs[-1]["nav"] == pytest.approx(np.prod([1 + r["ret"] for r in navs]))
    P.paper(fetch=False)  # ikinci koşu: yeni veri yok -> hiçbir şey eklenmez
    assert P._read(tmp_path / "H005_t.jsonl") == rows
