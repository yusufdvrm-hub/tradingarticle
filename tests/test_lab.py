import math
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest

from opusjev import hypotheses as H
from opusjev import lab

HOUR = 3_600_000


def _synthetic(n=1500, syms=("BTCUSDT", "ETHUSDT", "SOLUSDT"), seed=1):
    rng = np.random.default_rng(seed)
    t0 = 1_700_000_000_000 // HOUR * HOUR
    feats, fund = {}, {}
    btc_ret = rng.normal(0, 0.004, n)
    for j, s in enumerate(syms):
        r = rng.normal(0, 0.004, n) + (0.5 * btc_ret if s != "BTCUSDT" else btc_ret)
        vol = rng.lognormal(3, 0.2, n)
        for i in range(800 + j * 37, n, 97):  # hacimli k-sigma şoklar
            r[i] = -0.05 if (i // 97) % 2 else 0.05
            vol[i] *= 10
        if s == "BTCUSDT":
            btc_ret[:] = r
        close = 100 * np.exp(np.cumsum(r))
        ot = t0 + np.arange(n) * HOUR
        feats[s] = pd.DataFrame(dict(open_time=ot, close_time=ot + HOUR - 1, close=close, volume=vol))
        ft = t0 + np.arange(0, n, 8) * HOUR + 3  # 8 saatte bir kesinleşme, ms kayması ile
        fund[s] = pd.DataFrame(dict(fundingTime=ft, fundingRate=rng.normal(0, 0.0003, len(ft))))
    return feats, fund


BUILDERS = [
    (H.h001_flush_reversal, dict(k=3.0, vol_mult=3.0)),
    (H.h002_prefunding, dict(lead=1, q=0.8, window=30)),
    (H.h003_btc_lead, dict(k=2.5, lag_frac=0.5)),
]


@pytest.mark.parametrize("builder,prm", BUILDERS)
def test_builders_are_causal_and_fire(builder, prm):
    feats, fund = _synthetic()
    full = builder(feats, fund, **prm)
    cut = 1100
    end = feats["BTCUSDT"]["close_time"].iloc[cut - 1]
    short = builder({s: f.iloc[:cut] for s, f in feats.items()},
                    {s: f[f["fundingTime"] <= end] for s, f in fund.items()}, **prm)
    for s in feats:
        assert (full[s].iloc[:cut].to_numpy() == short[s].to_numpy()).all(), f"{builder.__name__} uses future data on {s}"
    assert sum(int((x != 0).sum()) for x in full.values()) > 0, f"{builder.__name__} never fires on synthetic shocks"


def test_dsr_properties():
    # N=1: düşürme yok, olasılıksal Sharpe ile aynı
    assert lab.dsr(0.1, 365, 0.0, 3.0, 1, 0.01) == pytest.approx(NormalDist().cdf(0.1 * math.sqrt(364) / math.sqrt(1 + 0.5 * 0.01)))
    # daha çok deneme -> daha yüksek çıta -> daha düşük olasılık
    vals = [lab.dsr(0.1, 365, 0.0, 3.0, n, 0.002) for n in (2, 10, 100, 1000)]
    assert vals == sorted(vals, reverse=True)
    # gözlenen Sharpe şansla beklenen en iyiye eşitse 0.5
    sr0 = lab.expected_max_sr(50, 0.002)
    assert lab.dsr(sr0, 365, 0.0, 3.0, 50, 0.002) == pytest.approx(0.5)


def test_raw_refuses_holdout_without_lock():
    with pytest.raises(PermissionError):
        lab._raw(["BTCUSDT"], lab.HOLDOUT_START + HOUR)


def _passing_ledger(tmp_path, sha):
    p = tmp_path / "ledger.jsonl"
    chosen = {"k": 3.0, "hold": 6, "stop_atr": 3.0, "tp_r": 3.0, "vol_mult": 3.0}
    lab.append(dict(kind="selection", hyp="H001", sha=sha, chosen=chosen), p)
    lab.append(dict(kind="oos", hyp="H001", sha=sha, n=200, pf=2.0, ci_lo=0.1, sr=0.3, T=365, skew=0.0, kurt=3.0), p)
    lab.append(dict(kind="review", hyp="H001", sha=sha, verdict="KEEP"), p)
    return p


def test_holdout_waits_for_forward_data_without_spending_lock(tmp_path, monkeypatch):
    card = lab.load_card("H001")
    p = _passing_ledger(tmp_path, card["sha"])
    monkeypatch.setattr(lab, "HOLDOUT_START", lab._ms("2099-01-01"))
    with pytest.raises(PermissionError, match="kilit harcanmadı"):
        lab.holdout("H001", p, runner=lambda *a, **k: dict(n=40, pf=1.5, exp_r=0.1))
    assert "holdout_open" not in [r["kind"] for r in lab.ledger(p)]


def test_holdout_opens_once(tmp_path, monkeypatch):
    monkeypatch.setattr(lab, "HOLDOUT_START", lab._ms("2020-01-01"))
    card = lab.load_card("H001")
    p = _passing_ledger(tmp_path, card["sha"])
    stub = lambda *a, **k: dict(n=40, pf=1.5, exp_r=0.1)
    lab.holdout("H001", p, runner=stub)
    kinds = [r["kind"] for r in lab.ledger(p)]
    assert kinds[-2:] == ["holdout_open", "holdout"]
    with pytest.raises(PermissionError, match="zaten"):
        lab.holdout("H001", p, runner=stub)


def test_holdout_refuses_changed_card_or_failed_gate(tmp_path):
    stub = lambda *a, **k: dict(n=40, pf=1.5, exp_r=0.1)
    with pytest.raises(PermissionError, match="değişmiş"):
        lab.holdout("H001", _passing_ledger(tmp_path, "stale-sha"), runner=stub)
    card = lab.load_card("H001")
    p = tmp_path / "kill.jsonl"
    _passing_ledger(tmp_path, card["sha"]).rename(p)
    lab.append(dict(kind="review", hyp="H001", sha=card["sha"], verdict="KILL"), p)
    with pytest.raises(PermissionError, match="geçilmedi"):
        lab.holdout("H001", p, runner=stub)
