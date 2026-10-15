"""Performans metrikleri ve spec'teki canlıya geçiş kapısı."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from opusjev.broker import Trade


def max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    return float(((equity - peak) / peak).min() * -1)


def bootstrap_ci_low(x: np.ndarray, n: int = 2000, alpha: float = 0.05, seed: int = 7) -> float:
    if len(x) < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.quantile(means, alpha / 2))


def summarize(trades: list[Trade], equity_curve: list[tuple[int, float]], starting_equity: float, provider_cost_usd: float = 0.0) -> dict:
    eq = pd.Series([e for _, e in equity_curve], index=pd.to_datetime([t for t, _ in equity_curve], unit="ms", utc=True), dtype=float)
    pnl = np.array([t.pnl for t in trades], dtype=float)
    r = np.array([t.r_multiple for t in trades], dtype=float)
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    gross_win, gross_loss = wins.sum(), -losses.sum()
    net_after_llm = pnl.sum() - provider_cost_usd
    pf = (gross_win / (gross_loss + provider_cost_usd)) if (gross_loss + provider_cost_usd) > 0 else (math.inf if gross_win > 0 else 0.0)
    daily = eq.resample("1D").last().dropna().pct_change().dropna() if len(eq) else pd.Series(dtype=float)
    sharpe = float(daily.mean() / daily.std() * math.sqrt(365)) if len(daily) > 2 and daily.std() > 0 else float("nan")
    days = (eq.index[-1] - eq.index[0]).total_seconds() / 86400 if len(eq) > 1 else 0.0
    reasons = pd.Series([t.exit_reason for t in trades]).value_counts().to_dict() if trades else {}
    return {
        "trades": len(trades),
        "days": round(days, 1),
        "win_rate": float(len(wins) / len(pnl)) if len(pnl) else float("nan"),
        "profit_factor": float(pf),
        "net_pnl": float(net_after_llm),
        "return_pct": float(100 * net_after_llm / starting_equity),
        "expectancy_usd": float(pnl.mean()) if len(pnl) else float("nan"),
        "expectancy_r": float(r.mean()) if len(r) else float("nan"),
        "expectancy_r_ci95_low": bootstrap_ci_low(r),
        "avg_win_r": float(r[r > 0].mean()) if (r > 0).any() else float("nan"),
        "avg_loss_r": float(r[r <= 0].mean()) if (r <= 0).any() else float("nan"),
        "worst_trade_r": float(r.min()) if len(r) else float("nan"),
        "max_drawdown_pct": 100 * max_drawdown(eq),
        "sharpe_daily_ann": sharpe,
        "fees_usd": float(sum(t.fees for t in trades)),
        "llm_cost_usd": float(provider_cost_usd),
        "exit_reasons": reasons,
    }


@dataclass
class GateResult:
    name: str
    value: object
    threshold: str
    passed: bool


def go_live_gate(m: dict, shadow: dict | None = None, ops_ok: bool = True) -> list[GateResult]:
    """Spec 'Canlıya geçiş kapısı'. Hepsi geçmeden gerçek paraya geçilmez."""
    g = [
        GateResult("örneklem: işlem sayısı", m["trades"], ">= 200", m["trades"] >= 200),
        GateResult("örneklem: gün", m["days"], ">= 28", m["days"] >= 28),
        GateResult("kâr faktörü (net, LLM dahil)", round(m["profit_factor"], 3), ">= 1.3", m["profit_factor"] >= 1.3),
        GateResult("beklenti R %95 alt sınır", round(m["expectancy_r_ci95_low"], 4), "> 0", bool(m["expectancy_r_ci95_low"] > 0)),
        GateResult("maks. düşüş %", round(m["max_drawdown_pct"], 2), "<= 10", m["max_drawdown_pct"] <= 10),
        GateResult("Sharpe (günlük, yıllık)", round(m["sharpe_daily_ann"], 2), ">= 1", bool(m["sharpe_daily_ann"] >= 1)),
        GateResult("en kötü işlem R", round(m["worst_trade_r"], 2), ">= -1.5", bool(m["worst_trade_r"] >= -1.5)),
        GateResult("operasyon (mutabakat/limit ihlali yok)", ops_ok, "True", ops_ok),
    ]
    if shadow is not None:
        better = m["profit_factor"] > shadow["profit_factor"] and m["expectancy_r"] > shadow["expectancy_r"]
        g.append(
            GateResult(
                "jev ablasyonu (jev > jev'siz gölge)",
                f"PF {m['profit_factor']:.2f} vs {shadow['profit_factor']:.2f}",
                "PF ve beklenti gölgeden yüksek",
                bool(better),
            )
        )
    return g


def format_report(title: str, m: dict, gate: list[GateResult]) -> str:
    lines = [f"## {title}", "", "| metrik | değer |", "|---|---|"]
    for k, v in m.items():
        lines.append(f"| {k} | {round(v, 4) if isinstance(v, float) else v} |")
    lines += ["", "### Canlıya geçiş kapısı", "", "| kriter | değer | eşik | sonuç |", "|---|---|---|---|"]
    for r in gate:
        lines.append(f"| {r.name} | {r.value} | {r.threshold} | {'GEÇTİ' if r.passed else 'KALDI'} |")
    verdict = all(r.passed for r in gate)
    lines += ["", f"**Karar: {'kapı geçildi (canlı pilot için insan onayı gerekir)' if verdict else 'kapı geçilmedi, gerçek paraya geçilmez'}**"]
    return "\n".join(lines)
