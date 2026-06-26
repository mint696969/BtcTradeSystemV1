# path: ./tools/test_phase4a_prediction_system_ps_q20k_disabled_helper_sample_result_review_and_binding_decision.py
# desc: Focused guard for PS-Q20K disabled helper sample result review and binding decision.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.apps.operator_ui.prediction_warroom.read_models.disabled_helper_sample_review_decision import (  # noqa: E402
    DISABLED_HELPER_SAMPLE_REVIEW_DECISION_VERSION,
    build_disabled_helper_sample_review_decision,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20K_DISABLED_HELPER_SAMPLE_RESULT_REVIEW_AND_BINDING_DECISION_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_helper_sample_review_decision.py"

REQUIRED_MARKERS = (
    "ps_q20k_disabled_helper_sample_result_review_and_binding_decision=true",
    "review_only=true",
    "decision_contract_only=true",
    "runtime_enablement_allowed=false",
    "loader_binding_runtime_allowed=false",
    "next_allowed_lane=design_review_only",
)

FALSE_BOUNDARIES = (
    "component_runtime_binding_allowed=false",
    "ui_code_changed=false",
    "warroom_ui_trigger_enabled=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "runtime_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "would_write_warroom_view_artifact=false",
    "ps_q19r_scoring_policy_changed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _passing_sample() -> dict:
    return {
        "ok": True,
        "sample_state": "disabled_helper_real_data_dry_run_sample_ready",
        "sample_only": True,
        "hot_data_read_only": True,
        "stdout_only": True,
        "helper_disabled_by_default": True,
        "helper_state": "explicit_read_only_loader_binding_helper_disabled",
        "dry_run_ready": True,
        "enable_explicit_read_only_loader_binding": False,
        "optional_section_attached": False,
        "output_model_has_optional_section": False,
        "adapter_state": "preferred_row_adapter_ready",
        "adapter_allowed_for_requested_lane": True,
        "adapter_selected_row_available": True,
        "adapter_consumer_preferred_count": 191,
        "adapter_diagnostic_transition_count": 9,
        "selected_row_summary": {
            "collector_ts": "2026-06-25T19:27:36Z",
            "trust_state": "trusted",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "spread": 3419.0,
        },
        "warning_reasons": [
            "diagnostic_transition_rows_retained",
            "multiple_consumer_preferred_rows_available",
            "explicit_read_only_loader_binding_disabled_by_default",
        ],
        "target_loader_invoked": False,
        "runtime_loader_invoked": False,
        "latest_prediction_warroom_read_model_loader_changed": False,
        "existing_market_snapshot_replaced": False,
        "existing_market_state_service_changed": False,
        "existing_warroom_runtime_rewired": False,
        "component_runtime_binding_allowed": False,
        "ui_code_changed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "view_artifact_write_allowed": False,
        "would_write_warroom_view_artifact": False,
        "ps_q19r_scoring_policy_changed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_review_decision_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_passing_sample_allows_design_only_next_lane_but_not_runtime_enablement() -> None:
    decision = build_disabled_helper_sample_review_decision(sample_result=_passing_sample()).to_dict()
    assert decision["review_version"] == DISABLED_HELPER_SAMPLE_REVIEW_DECISION_VERSION
    assert decision["review_state"] == "disabled_helper_sample_review_passed"
    assert decision["binding_decision"] == "allow_design_only_disabled_binding_plan"
    assert decision["runtime_enablement_decision"] == "runtime_enablement_disallowed"
    assert decision["next_allowed_lane"] == "design_review_only"
    assert decision["runtime_enablement_allowed"] is False
    assert decision["loader_binding_runtime_allowed"] is False
    assert decision["optional_section_attached_by_default"] is False
    assert decision["adapter_consumer_preferred_count"] == 191
    assert decision["adapter_diagnostic_transition_count"] == 9
    assert decision["selected_row_spread"] == 3419.0
    assert decision["unsafe_true_fields"] == []
    assert decision["blocked_reasons"] == []
    assert "dry_run_ready_does_not_permit_runtime_enablement" in decision["warning_reasons"]
    assert decision["would_send_to_broker"] is False


def test_review_blocks_if_default_sample_attached_optional_section() -> None:
    sample = _passing_sample()
    sample["optional_section_attached"] = True
    decision = build_disabled_helper_sample_review_decision(sample_result=sample).to_dict()
    assert decision["review_state"] == "disabled_helper_sample_review_blocked"
    assert decision["next_allowed_lane"] == "blocked"
    assert "optional_section_attached_in_default_sample" in decision["blocked_reasons"]
    assert decision["runtime_enablement_allowed"] is False


def test_review_blocks_if_any_runtime_or_execution_flag_is_true() -> None:
    sample = _passing_sample()
    sample["would_send_to_broker"] = True
    sample["view_artifact_write_allowed"] = True
    decision = build_disabled_helper_sample_review_decision(sample_result=sample).to_dict()
    assert decision["review_state"] == "disabled_helper_sample_review_blocked"
    assert sorted(decision["unsafe_true_fields"]) == ["view_artifact_write_allowed", "would_send_to_broker"]
    assert "unsafe_runtime_or_execution_flag_true" in decision["blocked_reasons"]
    assert decision["broker_private_api_allowed"] is False


def test_module_has_no_io_runtime_binding_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "read_text(",
        "write_text(",
        "open(",
        "Path(",
        "load_latest_market_state(",
        "load_latest_prediction_warroom_read_model(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
        "runtime_enablement_allowed: bool = True",
        "loader_binding_runtime_allowed: bool = True",
        "component_runtime_binding_allowed: bool = True",
        "ui_code_changed: bool = True",
        "producer_enabled: bool = True",
        "scheduler_enabled: bool = True",
        "warroom_ui_trigger_enabled: bool = True",
        "view_artifact_write_allowed: bool = True",
        "would_write_warroom_view_artifact: bool = True",
        "ps_q19r_scoring_policy_changed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "broker_private_api_allowed: bool = True",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_review_decision_and_safety_boundaries()
    test_passing_sample_allows_design_only_next_lane_but_not_runtime_enablement()
    test_review_blocks_if_default_sample_attached_optional_section()
    test_review_blocks_if_any_runtime_or_execution_flag_is_true()
    test_module_has_no_io_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
