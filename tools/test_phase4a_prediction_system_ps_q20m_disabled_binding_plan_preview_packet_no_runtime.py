# path: ./tools/test_phase4a_prediction_system_ps_q20m_disabled_binding_plan_preview_packet_no_runtime.py
# desc: Focused guard for PS-Q20M disabled binding plan preview packet with no runtime.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.apps.operator_ui.components.prediction_warroom_preferred_row_adapter import (  # noqa: E402
    build_prediction_warroom_preferred_row_adapter,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.disabled_binding_plan_no_runtime_enablement import (  # noqa: E402
    build_disabled_binding_plan_no_runtime_enablement,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.disabled_binding_plan_preview_packet_no_runtime import (  # noqa: E402
    DISABLED_BINDING_PLAN_PREVIEW_PACKET_VERSION,
    build_disabled_binding_plan_preview_packet_no_runtime,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (  # noqa: E402
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
)
from btcts.market_engine.market_state.consumer_integration_design import LANE_WARROOM_READ  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20M_DISABLED_BINDING_PLAN_PREVIEW_PACKET_NO_RUNTIME_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_binding_plan_preview_packet_no_runtime.py"

REQUIRED_MARKERS = (
    "ps_q20m_disabled_binding_plan_preview_packet_no_runtime=true",
    "preview_packet_only=true",
    "supplied_mappings_only=true",
    "default_disabled_preview=true",
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


def _plan() -> dict:
    review_decision = {
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
    return build_disabled_binding_plan_no_runtime_enablement(review_decision=review_decision).to_dict()


def _read_model() -> dict:
    return {
        "ok": True,
        "read_model_state": "latest_prediction_warroom_read_model_ready",
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "market_snapshot": {"market_uid": "bitflyer.fx.FX_BTC_JPY", "spread": 3419.0},
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "symbol_raw": "FX_BTC_JPY",
            "collector_ts": "2026-06-25T19:27:36Z",
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 9590239.0,
            "best_ask": 9593658.0,
            "spread": 3419.0,
            "mid_price": 9591948.5,
            "source_series_id": "collector_main-stream-bitflyer-unified_board_ws:series:2",
            "source_stream_session_id": "collector_main-stream-bitflyer-unified_board_ws",
        }
    return {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-25T19:27:35Z",
        "trust_state": "quarantined",
        "continuity_state": "transition",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 9593659.0,
        "best_ask": 9593658.0,
        "spread": -1.0,
        "mid_price": 9593658.5,
        "source_series_id": "collector_main-stream-bitflyer-unified_board_ws:series:1",
        "source_stream_session_id": "collector_main-stream-bitflyer-unified_board_ws",
    }


def _adapter() -> dict:
    return build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=True)], lane=LANE_WARROOM_READ).to_dict()


def test_spec_declares_preview_packet_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_preview_packet_is_ready_but_keeps_helper_disabled_and_section_unattached() -> None:
    model = _read_model()
    packet = build_disabled_binding_plan_preview_packet_no_runtime(
        disabled_binding_plan=_plan(),
        read_model=model,
        preferred_row_adapter_packet=_adapter(),
    ).to_dict()
    output = packet["preview_output_read_model"]
    assert packet["preview_version"] == DISABLED_BINDING_PLAN_PREVIEW_PACKET_VERSION
    assert packet["preview_state"] == "disabled_binding_plan_preview_packet_ready"
    assert packet["preview_packet_only"] is True
    assert packet["supplied_mappings_only"] is True
    assert packet["default_disabled_preview"] is True
    assert packet["plan_ready"] is True
    assert packet["helper_state"] == "explicit_read_only_loader_binding_helper_disabled"
    assert packet["helper_dry_run_ready"] is True
    assert packet["optional_section_attached"] is False
    assert packet["output_model_has_optional_section"] is False
    assert PREFERRED_ROW_OBSERVATION_SECTION_KEY not in output
    assert output["market_snapshot"] == model["market_snapshot"]
    assert packet["runtime_enablement_allowed"] is False
    assert packet["target_loader_invoked"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["blocked_reasons"] == []


def test_preview_blocks_if_plan_is_not_ready() -> None:
    plan = _plan()
    plan["plan_state"] = "disabled_binding_plan_blocked"
    packet = build_disabled_binding_plan_preview_packet_no_runtime(
        disabled_binding_plan=plan,
        read_model=_read_model(),
        preferred_row_adapter_packet=_adapter(),
    ).to_dict()
    assert packet["preview_state"] == "disabled_binding_plan_preview_packet_blocked"
    assert "disabled_binding_plan_not_ready" in packet["blocked_reasons"]
    assert packet["runtime_enablement_allowed"] is False


def test_preview_blocks_if_any_runtime_or_execution_flag_is_true() -> None:
    plan = _plan()
    plan["runtime_enablement_allowed"] = True
    plan["producer_enabled"] = True
    packet = build_disabled_binding_plan_preview_packet_no_runtime(
        disabled_binding_plan=plan,
        read_model=_read_model(),
        preferred_row_adapter_packet=_adapter(),
    ).to_dict()
    assert packet["preview_state"] == "disabled_binding_plan_preview_packet_blocked"
    assert sorted(packet["unsafe_true_fields"]) == ["producer_enabled", "runtime_enablement_allowed"]
    assert "unsafe_runtime_or_execution_flag_true" in packet["blocked_reasons"]
    assert packet["broker_private_api_allowed"] is False


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
    test_spec_declares_preview_packet_and_safety_boundaries()
    test_preview_packet_is_ready_but_keeps_helper_disabled_and_section_unattached()
    test_preview_blocks_if_plan_is_not_ready()
    test_preview_blocks_if_any_runtime_or_execution_flag_is_true()
    test_module_has_no_io_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
