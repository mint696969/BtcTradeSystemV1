# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_partial_comparison.py
# desc: MR-F8.13 tests for honest partial comparison and insufficient-evidence governance.

from __future__ import annotations

from btcts.prediction.market_regime.future_shadow_partial_comparison import (
    build_future_shadow_partial_comparison,
)


def test_partial_comparison_is_same_window_and_never_promotes() -> None:
    pairs = []
    rows = []
    for horizon in (300, 900, 1800, 3600, 21600, 43200, 86400):
        active_trace = f"active:{horizon}"
        shadow_trace = f"shadow:{horizon}"
        pairs.append({
            "slot_identity": {
                "origin_timestamp": "2026-07-15T09:12:33Z",
                "feature_snapshot_ref": "snap:1",
                "target_horizon_sec": horizon,
            },
            "candidate_identities": [
                {"parameter_set_id": "active.v1", "registry_role": "active"},
                {"parameter_set_id": "shadow.v1", "registry_role": "shadow"},
            ],
            "forecasts": [
                {"parameter_set_id": "active.v1", "trace_id": active_trace},
                {"parameter_set_id": "shadow.v1", "trace_id": shadow_trace},
            ],
        })
        rows.append({
            "parameter_set_id": "active.v1",
            "trace_id": active_trace,
            "outcome_status": "ABSTAINED",
        })
        rows.append({
            "parameter_set_id": "shadow.v1",
            "trace_id": shadow_trace,
            "outcome_status": "CORRECT" if horizon == 300 else "UNRESOLVED",
        })
    report = build_future_shadow_partial_comparison(
        runtime_preflight_result={"preflight_report": {"pairs": pairs}},
        outcome_intake_report={"outcome_rows": rows},
        evaluated_at="2026-07-15T15:10:00Z",
    )
    assert report["same_window_comparison"] is True
    assert report["same_source_snapshot"] is True
    assert report["candidate_count"] == 2
    assert report["decision"] == "insufficient_evidence"
    assert report["selected_candidate_id"] is None
    assert report["rollback_candidate_id"] == "active.v1"
    assert report["human_approval_required"] is True
    assert report["auto_promotion_allowed"] is False
    assert report["live_parameter_apply_allowed"] is False
    assert report["writes_dhot"] is False
    assert "brier_score" in report["unavailable_metrics"]

    active, shadow = report["candidate_summaries"]
    assert active["coverage_rate"] == 0.0
    assert active["accuracy_on_resolved_non_abstained"] is None
    assert shadow["coverage_rate"] == 1 / 7
    assert shadow["accuracy_on_resolved_non_abstained"] == 1.0
