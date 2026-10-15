import numpy as np
import pandas as pd
import pytest

from opusjev import macro as M


def test_leverage_financing_and_costs():
    idx = pd.bdate_range("2024-01-01", periods=5)
    C = pd.DataFrame({"A": [100.0] * 5}, index=idx)
    rf = pd.Series(0.0001, index=idx)
    T = pd.DataFrame({"A": [2.0] * 5}, index=idx)
    r = M.simulate(T, C, rf)
    # ilk gün: 2x giriş maliyeti + 1 birim borç (rf + SPREAD); fiyat sabit
    assert r.iloc[0] == pytest.approx(-2 * M.COST - (0.0001 + M.SPREAD / M.PPY))
    assert r.index[0] == idx[2]  # D sinyali -> D+2'de gerçekleşir
    T0 = pd.DataFrame({"A": [0.0] * 5}, index=idx)
    assert M.simulate(T0, C, rf).iloc[0] == pytest.approx(0.0001)  # nakit risksiz kazanır


@pytest.mark.parametrize("fn", [lambda C: M.h009(C), lambda C: M.h010(C), lambda C: M.h008(C, 2)])
def test_targets_are_causal(fn):
    rng = np.random.default_rng(1)
    idx = pd.bdate_range("2010-01-01", periods=700)
    cols = sorted(set(M.SECTORS + M.CTA + ["IEF"]))
    C = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, (700, len(cols))), axis=0)), index=idx, columns=cols)
    full, cut = fn(C), fn(C.iloc[:600])
    assert np.allclose(full.iloc[:600].fillna(-9).to_numpy(), cut.fillna(-9).to_numpy())
