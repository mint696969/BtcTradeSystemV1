# path: ./tools/test_phase4a_prediction_system_ps_q20l_disabled_binding_plan_no_runtime_enablement.py
# desc: Focused guard for PS-Q20L disabled binding plan with no runtime enablement.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.apps.operator_ui.prediction_warroom.read_models.disabled_binding_plan_no_runtime_enablement import (  # noqa: E402
    DISABLED_BINDING_PLAN_VERSION,
    build_disabled_binding_plan_no_runtime_enablement,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20L_DISABLED_BINDING_PLAN_NO_RUNTIME_ENABLEMENT_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_binding_plan_no_runtime_enablement.py"

REQUIRED_MARKERS = (
    "ps_q20l_disabled_binding_plan_no_runtime_enablement=true",
    "plan_only=true",
    "disabled_binding_plan_only=true",
    "runtime_enablement_allowed=false",
    "loader_binding_runtime_allowed=false",
    "target_loader_invoked=false",
    "latest_prediction_warroom_read_model_loader_changed=false",
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


def _review_decision() -> dict:
    return {
        "review_state": "disabled_helper_sample_review_passed",
        "binding_decision": "allow_design_only_disabled_binding_plan",
        "runtime_enablement_decision": "runtime_enablement_disallowed",
        "runtime_enablement_allowed": False,
        "loader_binding_runtime_allowed": False,
        "next_allowed_lane": "design_review_only",
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


def test_spec_declares_plan_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_safe_review_decision_produces_plan_only_disabled_binding_plan() -> None:
    plan = build_disabled_binding_plan_no_runtime_enablement(review_decision=_review_decision()).to_dict()
    assert plan["plan_version"] == DISABLED_BINDING_PLAN_VERSION
    assert plan["plan_state"] == "disabled_binding_plan_ready"
    assert plan["plan_decision"] == "plan_disabled_binding_without_runtime_enablement"
    assert plan["review_passed"] is True
    assert plan["design_review_only_lane"] is True
    assert plan["runtime_enablement_disallowed"] is True
    assert plan["loader_binding_runtime_disallowed"] is True
    assert plan["runtime_enablement_allowed"] is False
    assert plan["loader_binding_runtime_allowed"] is False
    assert plan["target_loader_invoked"] is False
    assert plan["latest_prediction_warroom_read_model_loader_changed"] is False
    assert plan["unsafe_true_fields"] == []
    assert plan["blocked_reasons"] == []
    assert "keep_latest_prediction_warroom_read_model_loader_unchanged" in plan["plan_items"]
    assert "review_passed_allows_plan_only_not_runtime_enablement" in plan["warning_reasons"]


def test_plan_blocks_if_review_lane_is_not_design_review_only() -> None:
    decision = _review_decision()
    decision["next_allowed_lane"] = "runtime_binding"
    plan = build_disabled_binding_plan_no_runtime_enablement(review_decision=decision).to_dict()
    assert plan["plan_state"] == "disabled_binding_plan_blocked"
    assert "next_lane_not_design_review_only" in plan["blocked_reasons"]
    assert plan["runtime_enablement_allowed"] is False


def test_plan_blocks_if_any_runtime_or_execution_flag_is_true() -> None:
    decision = _review_decision()
    decision["runtime_enablement_allowed"] = True
    decision["producer_enabled"] = True
    plan = build_disabled_binding_plan_no_runtime_enablement(review_decision=decision).to_dict()
    assert plan["plan_state"] == "disabled_binding_plan_blocked"
    assert sorted(plan["unsafe_true_fields"]) == ["producer_enabled", "runtime_enablement_allowed"]
    assert "unsafe_runtime_or_execution_flag_true" in plan["blocked_reasons"]
    assert plan["would_send_to_broker"] is False


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
        "target_loader_invoked: bool = True",
        "latest_prediction_warroom_read_model_loader_changed: bool = True",
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
    test_spec_declares_plan_and_safety_boundaries()
    test_safe_review_decision_produces_plan_only_disabled_binding_plan()
    test_plan_blocks_if_review_lane_is_not_design_review_only()
    test_plan_blocks_if_any_runtime_or_execution_flag_is_true()
    test_module_has_no_io_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
