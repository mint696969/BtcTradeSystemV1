# path: ./btcts_next/src/btcts/replay/prediction_realized_outcome.py
# desc: Minimal realized-outcome contract for replay-side prediction evaluation.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PredictionRealizedOutcomeBuildInput:
    market_uid: str | None = None
    event_ts: str | None = None
    realized_horizon: str | None = None
    realized_regime_state: str | None = None
    realized_confidence: float | int | str | None = None
    realized_caution_level: str | None = None
    realized_return_bp: float | int | str | None = None
    realized_max_adverse_bp: float | int | str | None = None
    realized_max_favorable_bp: float | int | str | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _clamp_confidence(value: Any) -> float | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None
    if parsed < 0.0:
        return 0.0
    if parsed > 1.0:
        return 1.0
    return round(parsed, 2)


def _round_optional(value: Any) -> float | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None
    return round(parsed, 2)


def build_prediction_realized_outcome(
    inp: PredictionRealizedOutcomeBuildInput,
) -> dict[str, Any]:
    return {
        "outcome_type": "prediction_realized_outcome",
        "outcome_version": "phase3.v1alpha1",
        "market_uid": _safe_str(inp.market_uid),
        "event_ts": _safe_str(inp.event_ts),
        "realized_horizon": _safe_str(inp.realized_horizon),
        "realized_regime_state": _safe_str(inp.realized_regime_state),
        "realized_confidence": _clamp_confidence(inp.realized_confidence),
        "realized_caution_level": _safe_str(inp.realized_caution_level),
        "realized_return_bp": _round_optional(inp.realized_return_bp),
        "realized_max_adverse_bp": _round_optional(inp.realized_max_adverse_bp),
        "realized_max_favorable_bp": _round_optional(inp.realized_max_favorable_bp),
        "diagnostics": {
            "builder_type": "prediction_realized_outcome",
            **dict(inp.diagnostics or {}),
        },
    }