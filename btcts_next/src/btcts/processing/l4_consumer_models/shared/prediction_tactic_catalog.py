# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_catalog.py
# desc: Shared tactic catalog metadata for Phase 4-A operating stance proposals.

from __future__ import annotations

from typing import Final

TACTIC_CATALOG: Final[dict[str, dict[str, str]]] = {
    "observe_only": {
        "tactic_label": "observe_only",
        "stance_bias": "no_trade_watch",
        "readiness": "hold",
    },
    "tighten_entry_gate": {
        "tactic_label": "tighten_entry_gate",
        "stance_bias": "entry_gate_tightening",
        "readiness": "watch",
    },
    "cautious_probe": {
        "tactic_label": "cautious_probe",
        "stance_bias": "balanced_entry",
        "readiness": "watch",
    },
    "continuation_follow": {
        "tactic_label": "continuation_follow",
        "stance_bias": "continuation_bias",
        "readiness": "ready",
    },
    "reversal_prepare": {
        "tactic_label": "reversal_prepare",
        "stance_bias": "reversal_bias",
        "readiness": "watch",
    },
    "defensive_reduce_risk": {
        "tactic_label": "defensive_reduce_risk",
        "stance_bias": "defensive_bias",
        "readiness": "ready",
    },
    "maintain_no_trade": {
        "tactic_label": "maintain_no_trade",
        "stance_bias": "no_trade_bias",
        "readiness": "avoid",
    },
}


def get_tactic_shape(tactic_key: str) -> tuple[str, str, str]:
    row = TACTIC_CATALOG.get(tactic_key)
    if row is None:
        return (tactic_key, "unknown", "hold")
    return (
        row["tactic_label"],
        row["stance_bias"],
        row["readiness"],
    )