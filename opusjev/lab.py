"""Araştırma döngüsü v1: hipotez kartı -> deneme kaydı -> geliştirme/OOS -> düşürülmüş (deflated) kapı ->
ayrı modelle saldırı incelemesi -> bir kez açılan holdout.

Kullanım (repo kökünden, venv ile):
    python -m opusjev.lab run H001      # dev'de tüm varyantlar, seçilen varyant OOS'ta, kapı raporu
    python -m opusjev.lab review H001   # Codex (ayrı model) sonucu çürütmeye çalışır: KEEP/KILL
    python -m opusjev.lab holdout H001  # yalnızca kapı + KEEP geçtiyse, hipotez başına bir kez
    python -m opusjev.lab status

Dönemler sabittir (aşağıda). Holdout yalnızca ileriye dönük veridir (2026-10-16 ve sonrası): daha önceki tüm aylar
1.-2. turlarda en az bir kez görüldü (Codex incelemesi, 2026-10-15), model bilgi kesimi tek başına yetmez. Hipotezler jev'siz (BaselineProvider) ve kayıp durdurmaları kapalı test edilir; funding PnL'e işlem başına
sonradan eklenir.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import subprocess
import sys
import tomllib
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import partial
from itertools import product
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

import opusjev.engine as E
from opusjev import hypotheses as H
from opusjev.config import RiskConfig, Settings, StrategyConfig
from opusjev.data import load_csv
from opusjev.decision import BaselineProvider
from opusjev.features import compute
from opusjev.journal import Journal
from opusjev.metrics import bootstrap_ci_low, max_drawdown
from opusjev.signals_alt import from_sig


def _ms(d: str) -> int:
    return int(datetime.fromisoformat(d).replace(tzinfo=timezone.utc).timestamp() * 1000)


ROOT = Path(__file__).resolve().parent.parent
DATA, CARDS, REVIEWS = ROOT / "data", ROOT / "research" / "cards", ROOT / "research" / "reviews"
LEDGER = ROOT / "research" / "ledger.jsonl"
SPLITS = {"dev": (_ms("2022-10-16"), _ms("2025-07-01")), "oos": (_ms("2025-07-01"), _ms("2026-10-16"))}
HOLDOUT_START = SPLITS["oos"][1]  # ileriye dönük; veri dosyaları güncellendikçe birikir
MIN_HOLDOUT_DAYS = 60
HARNESS = 2  # v2: kesin zaman stopu, dönem sonunda pozisyon kapatma, ileriye dönük holdout
# 2026-10-15 öncesi aynı veride elle denenen yapılandırmalar: tarama 36 + setup 9 + OOS 3 + alternatif sinyaller 28.
# Kenar arayan herkes gibi biz de bunlar arasından seçtik; düşürülmüş Sharpe bu sayıyı da taşır.
PRIOR_TRIALS = 76
MIN_DEV_TRADES = 40
OOS_GATE = dict(trades=100, pf=1.2, ci_lo=0.0, dsr=0.95)
HOLDOUT_GATE = dict(trades=30, pf=1.1, exp_r=0.0)
TIMEOUT_REVIEW_S = 1200


# ---- kart ve kayıt ------------------------------------------------------------------------------------------
def load_card(hid: str) -> dict:
    p = CARDS / f"{hid}.toml"
    card = tomllib.loads(p.read_text(encoding="utf-8"))
    src = inspect.getsource(getattr(H, card["builder"]))
    card["sha"] = hashlib.sha256(p.read_bytes() + src.encode() + f"harness={HARNESS}".encode()).hexdigest()[:16]
    return card


def variants(card: dict) -> list[dict]:
    g = card.get("grid", {})
    out = [dict(zip(g, v)) | card.get("fixed", {}) for v in product(*g.values())] if g else [dict(card.get("fixed", {}))]
    if len(out) > 8:
        raise ValueError(f"{card['id']}: {len(out)} varyant; v1 sınırı 8 (seçim yanlılığını küçük tutmak için)")
    return out


def ledger(path: Path | None = None) -> list[dict]:
    p = path or LEDGER
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def append(entry: dict, path: Path | None = None) -> dict:
    p = path or LEDGER
    try:
        git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        git = ""
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "git": git} | entry
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=float) + "\n")
    return entry


# ---- veri (holdout kilidi) ----------------------------------------------------------------------------------
def _raw(symbols, until_ms: int, holdout_ok: bool = False):
    """until_ms öncesi barlar ve funding. Holdout barlarını yalnızca holdout() açabilir."""
    if until_ms > HOLDOUT_START and not holdout_ok:
        raise PermissionError("holdout kilitli: bu veriyi yalnızca `lab holdout` okuyabilir")
    raw, fund = {}, {}
    for s in symbols:
        df = load_csv(DATA / f"{s}_1h_1460d.csv")
        raw[s] = df[df["close_time"] < until_ms].reset_index(drop=True)
        f = pd.read_csv(DATA / f"{s}_funding.csv")
        fund[s] = f[f["fundingTime"] < until_ms].reset_index(drop=True)
    return raw, fund


# ---- tek varyant ----------------------------------------------------------------------------------------------
def run_variant(card: dict, prm: dict, start: int, end: int, holdout_ok: bool = False) -> dict:
    syms = tuple(card["symbols"])
    raw, fund = _raw(syms, end, holdout_ok)
    hold = int(prm["hold"] if "hold" in prm else prm[card["hold_param"]])  # kart tutma süresini bir parametreye bağlayabilir
    s = Settings(risk=RiskConfig(daily_loss_limit=1.0, weekly_loss_limit=1.0, peak_drawdown_halt=1.0, time_stop_bars=hold,
                                 max_open_positions=4),
                 strategy=StrategyConfig(timeframe="1h", symbols=syms, stop_atr_mult=prm["stop_atr"], tp_r_multiple=prm["tp_r"]))
    feats = {sy: compute(raw[sy], s.strategy) for sy in syms}
    sigs = getattr(H, card["builder"])(feats, fund, **{k: v for k, v in prm.items() if k not in ("stop_atr", "tp_r", "hold")})
    for sy in syms:
        f = feats[sy].assign(sig=sigs[sy].to_numpy())
        feats[sy] = f[f["open_time"] >= start].reset_index(drop=True)
    E.generate = partial(from_sig, setup=card["id"])
    eng = E.Engine(s, BaselineProvider(), Journal(None))
    eng.broker.hard_time_stop = True  # kartlar "hold bar sonra çık" der; broker'ın koşullu kuralı burada geçersiz
    E.run_backtest(eng, feats)
    if eng.equity_curve:  # dönem sonunda açık kalanları kapat: PF/beklenti ile getiri aynı işlem kümesini kapsasın
        eng.broker.flatten_all(eng.equity_curve[-1][0], "period_end")
    tr = []
    for t in eng.broker.trades:
        fu = fund[t.symbol]
        rates = fu["fundingRate"][(fu["fundingTime"] > t.entry_time) & (fu["fundingTime"] <= t.exit_time)].sum()
        fcost = (1 if t.side == "long" else -1) * t.qty * t.entry_price * rates  # long pozitif funding öder
        risk = t.pnl / t.r_multiple if t.r_multiple else float("nan")
        tr.append(dict(sym=t.symbol, side=t.side, exit=t.exit_time, reason=t.exit_reason, pnl=t.pnl - fcost, fees=t.fees, fund=fcost,
                       r=(t.pnl - fcost) / risk if risk == risk else t.r_multiple))
    eq = pd.Series([e for _, e in eng.equity_curve], index=pd.to_datetime([t for t, _ in eng.equity_curve], unit="ms", utc=True))
    if tr:  # funding'i özsermaye eğrisine çıkış anında yansıt
        f = pd.Series([-x["fund"] for x in tr], index=pd.to_datetime([x["exit"] for x in tr], unit="ms", utc=True)).groupby(level=0).sum().cumsum()
        eq = eq + f.reindex(eq.index.union(f.index)).ffill().reindex(eq.index).fillna(0)
    return stats(tr, eq, s.starting_equity) | {"params": prm}


def _pf(x) -> float:
    x = np.asarray(x, float)
    g, l = x[x > 0].sum(), -x[x <= 0].sum()
    return float(g / l) if l > 0 else (float("inf") if g > 0 else 0.0)


def stats(tr: list[dict], eq: pd.Series, start_equity: float) -> dict:
    r = np.array([t["r"] for t in tr], float)
    daily = eq.resample("1D").last().dropna().pct_change().dropna() if len(eq) else pd.Series(dtype=float)
    sd = daily.std()
    return dict(
        n=len(tr), wr=float(np.mean(r > 0)) if len(r) else 0.0, pf=_pf([t["pnl"] for t in tr]),
        pf_ex_fees=_pf([t["pnl"] + t["fees"] for t in tr]), exp_r=float(r.mean()) if len(r) else 0.0,
        ci_lo=bootstrap_ci_low(r) if len(r) > 1 else float("nan"),
        ret=float(100 * (eq.iloc[-1] / start_equity - 1)) if len(eq) else 0.0, dd=float(100 * max_drawdown(eq)),
        sr=float(daily.mean() / sd) if len(daily) > 2 and sd > 0 else 0.0, T=int(len(daily)),
        skew=float(daily.skew()) if len(daily) > 2 else 0.0, kurt=float(daily.kurt() + 3) if len(daily) > 3 else 3.0,
        by_side={sd_: dict(n=sum(t["side"] == sd_ for t in tr), pf=_pf([t["pnl"] for t in tr if t["side"] == sd_])) for sd_ in ("long", "short")},
        by_symbol={sy: dict(n=sum(t["sym"] == sy for t in tr), pnl=round(sum(t["pnl"] for t in tr if t["sym"] == sy), 2))
                   for sy in sorted({t["sym"] for t in tr})},
    )


# ---- düşürülmüş Sharpe (Bailey & López de Prado 2014) ---------------------------------------------------------
def expected_max_sr(n_trials: int, var_sr: float) -> float:
    """N bağımsız, kenarsız denemenin en iyisinden beklenen Sharpe (günlük birimde)."""
    if n_trials < 2 or var_sr <= 0:
        return 0.0
    g, z = 0.5772156649, NormalDist().inv_cdf
    return math.sqrt(var_sr) * ((1 - g) * z(1 - 1 / n_trials) + g * z(1 - 1 / (n_trials * math.e)))


def dsr(sr: float, T: int, skew: float, kurt: float, n_trials: int, var_sr: float) -> float:
    """Gerçek Sharpe'ın şansla beklenen en iyiden büyük olma olasılığı. >=0.95 anlamlı sayılır."""
    if T < 3:
        return 0.0
    sr0 = expected_max_sr(n_trials, var_sr)
    den = 1 - skew * sr + (kurt - 1) / 4 * sr**2
    return NormalDist().cdf((sr - sr0) * math.sqrt(T - 1) / math.sqrt(max(den, 1e-12)))


def trial_universe(rows: list[dict], hid: str | None = None) -> tuple[int, float]:
    """N: tüm denemeler (önceki + kayıtlı dev). Varyans: yalnızca bu hipotezin dev varyantları.

    ponytail: Bailey-LdP varyansı tüm denemeler üzerinden alır; ama maliyete boğulan yüksek devirli bir fikir
    (ör. H002, SR/gün -0,6) ortak varyansı şişirip çıtayı geçilmez yapıyordu (SR/gün 0,51). Hipotez içi varyans
    daha düşük bir çıta verir; N küresel kalır. Hipotezler arası seçim yapıldığında küresel varyansa dönülmeli.
    """
    devs = [r for r in rows if r.get("kind") == "trial" and r.get("split") == "dev"]
    own = [r["sr"] for r in devs if hid is None or (r.get("hyp") == hid and r.get("harness") == HARNESS)]
    return PRIOR_TRIALS + len(devs), float(np.var(own, ddof=1)) if len(own) > 1 else 0.0


# ---- kapılar ------------------------------------------------------------------------------------------------
def oos_gate(oos: dict, n_trials: int, var_sr: float, verdict: str | None) -> list[tuple[str, object, str, bool | None]]:
    d = dsr(oos["sr"], oos["T"], oos["skew"], oos["kurt"], n_trials, var_sr)
    return [
        ("işlem sayısı", oos["n"], f">= {OOS_GATE['trades']}", oos["n"] >= OOS_GATE["trades"]),
        ("net PF (funding dahil)", round(oos["pf"], 3), f">= {OOS_GATE['pf']}", oos["pf"] >= OOS_GATE["pf"]),
        ("beklenti R %95 alt sınır", round(oos["ci_lo"], 4), "> 0", bool(oos["ci_lo"] > OOS_GATE["ci_lo"])),
        (f"düşürülmüş Sharpe (N={n_trials})", round(d, 3), f">= {OOS_GATE['dsr']}", d >= OOS_GATE["dsr"]),
        ("saldırı incelemesi (Codex)", verdict or "yok", "KEEP", None if verdict is None else verdict == "KEEP"),
    ]


def holdout_gate(h: dict) -> list[tuple[str, object, str, bool]]:
    return [
        ("işlem sayısı", h["n"], f">= {HOLDOUT_GATE['trades']}", h["n"] >= HOLDOUT_GATE["trades"]),
        ("net PF (funding dahil)", round(h["pf"], 3), f">= {HOLDOUT_GATE['pf']}", h["pf"] >= HOLDOUT_GATE["pf"]),
        ("beklenti R", round(h["exp_r"], 4), "> 0", h["exp_r"] > HOLDOUT_GATE["exp_r"]),
    ]


def _latest(rows: list[dict], hid: str, kind: str) -> dict | None:
    return next((r for r in reversed(rows) if r.get("hyp") == hid and r.get("kind") == kind), None)


# ---- komutlar -----------------------------------------------------------------------------------------------
def _dev_job(hid: str, prm: dict) -> dict:
    return run_variant(load_card(hid), prm, *SPLITS["dev"])


def run(hid: str) -> None:
    card = load_card(hid)
    vs = variants(card)
    with ProcessPoolExecutor(max_workers=min(6, len(vs))) as ex:
        dev = list(ex.map(partial(_dev_job, hid), vs))
    for d in dev:
        append(dict(kind="trial", hyp=hid, sha=card["sha"], harness=HARNESS, split="dev") | d)
        print(_line("dev", d))
    ok = [d for d in dev if d["n"] >= MIN_DEV_TRADES]
    if not ok:
        append(dict(kind="selection", hyp=hid, sha=card["sha"], chosen=None, reason=f"hiçbir varyant dev'de >= {MIN_DEV_TRADES} işlem yapmadı"))
        print("seçim yok: yetersiz işlem")
        return
    best = max(ok, key=lambda d: d["pf"])
    append(dict(kind="selection", hyp=hid, sha=card["sha"], chosen=best["params"], rule=f"dev net PF en yüksek, n >= {MIN_DEV_TRADES}"))
    oos = run_variant(card, best["params"], *SPLITS["oos"])
    append(dict(kind="oos", hyp=hid, sha=card["sha"], harness=HARNESS) | oos)
    print(_line("OOS", oos))
    _print_gate(hid)


def _print_gate(hid: str) -> bool:
    rows = ledger()
    oos, rev = _latest(rows, hid, "oos"), _latest(rows, hid, "review")
    if oos is None:
        print(f"{hid}: OOS sonucu yok")
        return False
    n, v = trial_universe(rows, hid)
    g = oos_gate(oos, n, v, rev and rev["verdict"])
    print(f"\n{hid} OOS kapısı")
    for name, val, thr, ok in g:
        print(f"  {'GEÇTİ' if ok else ('BEKLİYOR' if ok is None else 'KALDI'):>8}  {name}: {val} ({thr})")
    return all(ok for *_, ok in g)


def _line(tag: str, d: dict) -> str:
    return (f"{tag:>4} {d['params']} n={d['n']} wr={d['wr']:.0%} pf={d['pf']:.2f} ücretsiz={d['pf_ex_fees']:.2f} "
            f"R={d['exp_r']:+.3f} ci={d['ci_lo']:+.3f} SR/gün={d['sr']:+.3f} getiri={d['ret']:.1f}% dd={d['dd']:.1f}%")


REVIEW_PROMPT = """You are the adversarial reviewer of a trading-research result. Another model (Claude) wrote the
hypothesis, the signal code and the backtest harness. Your job is to find reasons the result is wrong or misleading,
NOT to improve the strategy. You have read-only access to the repository in the current directory.

Check, with file:line evidence where possible:
1. Lookahead: does the signal in opusjev/hypotheses.py (function `{builder}`) use any bar, volume or funding value that
   was not known at the close of the signal bar? Entries fill at the next bar's open (opusjev/broker.py).
2. Harness errors in opusjev/lab.py: split boundaries, holdout leakage, funding sign, cost model, selection rule.
3. Whether the reported result (below) could come from a few trades, one symbol, one side or one regime.
4. Whether the hypothesis card's mechanism is actually what the code tests.

Do not edit files. End your answer with exactly one line:
VERDICT: KEEP - <one-sentence reason>   or   VERDICT: KILL - <one-sentence reason>
KEEP means "I found no reason this result is invalid", independent of whether the strategy is profitable.

## Portfolio policy applied to every card (not repeated in each card)
Engine risk manager with loss halts disabled: max 4 open positions, max 2 on the same side, max 12 entries/day,
no new entry within 20 min of 00/08/16 UTC, 4 consecutive losses -> 60 min cooldown and half size, candidates
processed in the card's symbol order, hard time stop at `hold` bars, open positions closed at period end.
Historical dev/OOS months were all seen by earlier research rounds; only forward data (>= 2026-10-16) is untouched.

## Hypothesis card
{card}

## Ledger rows for this hypothesis (dev trials, selection, OOS)
{rows}
"""


def review(hid: str) -> None:
    card = load_card(hid)
    rows = [r for r in ledger() if r.get("hyp") == hid and r.get("sha") == card["sha"] and r.get("kind") in ("trial", "selection", "oos")]
    if not rows:
        raise SystemExit(f"{hid}: önce `lab run {hid}`")
    REVIEWS.mkdir(parents=True, exist_ok=True)
    out = REVIEWS / f"{hid}.md"
    prompt = REVIEW_PROMPT.format(builder=card["builder"], card=(CARDS / f"{hid}.toml").read_text(encoding="utf-8"),
                                  rows="\n".join(json.dumps(r, default=float) for r in rows))
    cmd = ["codex", "exec", "-s", "read-only", "-C", str(ROOT), "--ephemeral", "-o", str(out), "-"]
    subprocess.run(cmd if sys.platform != "win32" else ["cmd", "/c", *cmd], input=prompt, text=True, encoding="utf-8",
                   capture_output=True, timeout=TIMEOUT_REVIEW_S, check=True)
    text = out.read_text(encoding="utf-8")
    last = next((x for x in reversed(text.splitlines()) if x.strip().upper().startswith("VERDICT:")), "")
    verdict = "KEEP" if "KEEP" in last.upper() else "KILL" if "KILL" in last.upper() else "UNCLEAR"
    append(dict(kind="review", hyp=hid, sha=card["sha"], reviewer="codex", verdict=verdict, line=last.strip(), file=str(out.relative_to(ROOT))))
    print(f"{hid}: {last.strip() or 'karar satırı yok -> UNCLEAR'}")
    _print_gate(hid)


def holdout(hid: str, ledger_path: Path | None = None, runner=None) -> dict:
    """Hipotez başına bir kez. Önce kilit kaydı yazılır, sonra veri açılır (çökse bile ikinci kez açılmaz)."""
    card = load_card(hid)
    rows = ledger(ledger_path)
    if _latest(rows, hid, "holdout_open"):
        raise PermissionError(f"{hid}: holdout zaten açıldı; ikinci kez açılamaz")
    sel, oos, rev = _latest(rows, hid, "selection"), _latest(rows, hid, "oos"), _latest(rows, hid, "review")
    if not (sel and sel.get("chosen") and oos):
        raise PermissionError(f"{hid}: seçim/OOS kaydı yok")
    if sel["sha"] != card["sha"]:
        raise PermissionError(f"{hid}: kart veya sinyal kodu OOS'tan sonra değişmiş ({sel['sha']} -> {card['sha']}); yeni hipotez açın")
    n, v = trial_universe(rows, hid)
    if not all(ok for *_, ok in oos_gate(oos, n, v, rev and rev["verdict"])):
        raise PermissionError(f"{hid}: OOS kapısı veya saldırı incelemesi geçilmedi; holdout açılmaz")
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    have = int(load_csv(DATA / f"{card['symbols'][0]}_1h_1460d.csv")["close_time"].iloc[-1]) if runner is None else now
    if have - HOLDOUT_START < MIN_HOLDOUT_DAYS * 86_400_000:
        raise PermissionError(f"{hid}: ileriye dönük veri {MIN_HOLDOUT_DAYS} günden az; kilit harcanmadı, veriyi güncelleyip sonra deneyin")
    append(dict(kind="holdout_open", hyp=hid, sha=card["sha"]), ledger_path)
    h = (runner or run_variant)(card, sel["chosen"], HOLDOUT_START, now, holdout_ok=True)
    g = holdout_gate(h)
    append(dict(kind="holdout", hyp=hid, sha=card["sha"], passed=all(ok for *_, ok in g)) | h, ledger_path)
    for name, val, thr, ok in g:
        print(f"  {'GEÇTİ' if ok else 'KALDI':>6}  {name}: {val} ({thr})")
    return h


def status() -> None:
    rows = ledger()
    n, v = trial_universe(rows)
    print(f"deneme evreni N={n} (önceki {PRIOR_TRIALS} + kayıtlı dev); kapı her hipotezde kendi dev varyansını kullanır")
    for p in sorted(CARDS.glob("H*.toml")):
        hid = p.stem
        oos, rev, ho = _latest(rows, hid, "oos"), _latest(rows, hid, "review"), _latest(rows, hid, "holdout")
        state = ("holdout " + ("GEÇTİ" if ho["passed"] else "KALDI")) if ho else (
            f"OOS pf={oos['pf']:.2f} n={oos['n']}" if oos else "çalıştırılmadı")
        _, v = trial_universe(rows, hid)
        print(f"  {hid}: {state}; inceleme={rev['verdict'] if rev else '-'}; şansla beklenen en iyi SR/gün={expected_max_sr(n, v):.3f}")


if __name__ == "__main__":
    cmds = dict(run=run, review=review, holdout=holdout, status=status)
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        raise SystemExit(__doc__)
    cmds[sys.argv[1]](*sys.argv[2:])
