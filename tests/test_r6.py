import pandas as pd
import pytest

from opusjev import r6

DAY = 86400
T = [1704229200, 1704229200 + 6 * DAY, 1704229200 + 12 * DAY]  # 2024-01-02, 01-08, 01-14 (16:00 New York)


def _rf_nav(daily):
    idx = pd.date_range("2023-12-25", "2024-01-20", freq="D")
    return (1 + pd.Series(daily, index=idx)).cumprod()


def test_chunk_returns_cash_interest_and_stress():
    rf_nav = _rf_nav(0.0001)
    c = {"t": T, "equity": [100.0, 101.0, 101.0], "invested": [0.5, 0.5, 1.0], "traded": [0.0, 50.0, 50.0]}
    r = r6.chunk_returns(c, rf_nav)
    rf6 = 1.0001 ** 6 - 1
    assert r.iloc[0] == pytest.approx(0.01 + 0.5 * rf6)
    assert r.iloc[1] == pytest.approx(0.5 * rf6)  # önceki noktanın nakit oranı
    s = r6.chunk_returns(c, rf_nav, extra=0.001)
    assert s.iloc[0] == pytest.approx(r.iloc[0] - 0.001 * 50 / 100)  # kümülatif hacim farkı
    assert s.iloc[1] == pytest.approx(r.iloc[1])  # aralıkta işlem yok


def test_returns_concatenate_chunks():
    rf_nav = _rf_nav(0.0)
    a = {"t": T[:2], "equity": [100.0, 110.0], "invested": [1, 1], "traded": [0, 0]}
    b = {"t": T[1:], "equity": [100.0, 90.0], "invested": [1, 1], "traded": [0, 0]}
    assert list(r6.returns([b, a], rf_nav)) == pytest.approx([0.10, -0.10])


def test_on_grid_compounds_between_points():
    nav = pd.Series([1.0, 1.1, 1.21], index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]))
    g = r6.on_grid(nav, pd.to_datetime(["2024-01-01", "2024-01-03"]))
    assert g.iloc[1] == pytest.approx(0.21)


def test_combo_is_half_half():
    i = pd.to_datetime(["2024-01-02", "2024-01-03"])
    c = r6.combo(pd.Series([0.02, 0.0], index=i), pd.Series([0.0, 0.04], index=i))
    assert list(c) == pytest.approx([0.01, 0.02])


def test_load_weekly(tmp_path):
    f = tmp_path / "w.txt"
    f.write_text("#2024 20240102,100000,0,0 7,101000,981,969\n")
    (c,) = r6.load_weekly(f)
    assert list(r6._dates(c["t"]).strftime("%Y-%m-%d")) == ["2024-01-02", "2024-01-09"]
    assert c["invested"] == [0.0, 0.981] and c["traded"] == [0.0, 96900.0]
