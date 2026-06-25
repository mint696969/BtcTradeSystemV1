# path: ./tools/test_phase4a_prediction_system_ps_q19y_actual_point_selection_decision_lock.py
# desc: Focused guard for PS-Q19Y actual-point selection policy decision lock.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19Y_ACTUAL_POINT_SELECTION_DECISION_LOCK_2026-06-25.md"
PS_Q19R_TOOL = REPO_ROOT / "tools/review_prediction_vs_actual_market_ps_q19r.py"
PS_Q19X_TOOL = REPO_ROOT / "tools/compare_actual_point_selection_policy_ps_q19x.py"

REQUIRED_MARKERS = (
    "ps_q19y_actual_point_selection_decision_lock=true",
    "policy_decision_locked=true",
    "phase_boundary_observation_diagnosis_complete=true",
    "next_thread_starts_collector_reanchor_crossed_book_repair=true",
    "ps_q19r_current_policy=strict_nearest_then_fail_closed_quality_gate",
    "ps_q19r_behavior_change_allowed_now=false",
    "nearest_quality_ok_within_tolerance_candidate_status=deferred",
    "collector_reanchor_crossed_book_repair_preferred_next=true",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_decision_lock=false",
    "status_artifact_write_performed_by_decision_lock=false",
    "prediction_artifact_write_performed_by_decision_lock=false",
    "view_artifact_write_performed_by_decision_lock=false",
    "collector_state_write_performed_by_decision_lock=false",
    "ps_q19r_behavior_changed_by_decision_lock=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)

NEXT_THREAD_MARKERS = (
    "next_slice=PS-Q20A_COLLECTOR_REANCHOR_CROSSED_BOOK_REPAIR_DIAGNOSIS",
    "start_from=PS-Q19W_AND_PS_Q19X_EVIDENCE",
    "primary_question=why_same_second_market_overview_contains_quarantined_crossed_rows_and_trusted_rows",
    "avoid_first_step=changing_ps_q19r_selection_policy",
)


def test_spec_locks_policy_and_next_thread_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker
    for marker in NEXT_THREAD_MARKERS:
        assert marker in text, marker


def test_decision_lock_does_not_modify_ps_q19r_behavior() -> None:
    q19r = PS_Q19R_TOOL.read_text(encoding="utf-8")
    assert "def _nearest(" in q19r
    assert "def _actual_quality_reasons(" in q19r
    assert "nearest_quality_ok_within_tolerance" not in q19r
    assert "ps_q19r_behavior_changed_by_decision_lock" not in q19r


def test_ps_q19x_remains_read_only_comparison_only() -> None:
    q19x = PS_Q19X_TOOL.read_text(encoding="utf-8")
    assert "read_only_policy_compare" in q19x
    assert "ps_q19r_behavior_changed_by_policy_compare" in q19x
    assert "operator_policy_decision_required_before_ps_q19r_change" in q19x
    assert "quality_ok_candidate_does_not_imply_auto_rewrite" in q19x


def test_decision_lock_contains_completed_evidence_chain() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for token in ("PS-Q19R", "PS-Q19S", "PS-Q19T", "PS-Q19U", "PS-Q19V", "PS-Q19W", "PS-Q19X", "PS-Q19Y"):
        assert token in text, token


def test_no_behavior_or_runtime_markers_in_decision_doc() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    forbidden = (
        "ps_q19r_behavior_change_allowed_now=true",
        "scheduler_enabled=true",
        "producer_enabled=true",
        "warroom_ui_trigger_enabled=true",
        "would_send_to_broker=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_locks_policy_and_next_thread_boundary()
    test_decision_lock_does_not_modify_ps_q19r_behavior()
    test_ps_q19x_remains_read_only_comparison_only()
    test_decision_lock_contains_completed_evidence_chain()
    test_no_behavior_or_runtime_markers_in_decision_doc()
    print('{"ok": true}')
