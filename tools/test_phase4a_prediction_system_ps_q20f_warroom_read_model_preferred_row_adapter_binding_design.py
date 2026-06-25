# path: ./tools/test_phase4a_prediction_system_ps_q20f_warroom_read_model_preferred_row_adapter_binding_design.py
# desc: Focused guard for PS-Q20F WarRoom read-model preferred-row adapter binding design.

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
from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_adapter_binding_design import (  # noqa: E402
    PREFERRED_ROW_BINDING_DESIGN_VERSION,
    build_preferred_row_adapter_binding_design,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
)
from btcts.market_engine.market_state.consumer_integration_design import LANE_WARROOM_READ  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20F_WARROOM_READ_MODEL_PREFERRED_ROW_ADAPTER_BINDING_DESIGN_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/preferred_row_adapter_binding_design.py"

REQUIRED_MARKERS = (
    "ps_q20f_warroom_read_model_preferred_row_adapter_binding_design=true",
    "binding_design_only=true",
    "existing_warroom_read_model_changed=false",
    "existing_market_snapshot_replaced=false",
    "existing_market_state_service_changed=false",
    "existing_warroom_runtime_rewired=false",
    "ps_q19r_scoring_policy_changed=false",
)

FALSE_BOUNDARIES = (
    "component_runtime_binding_allowed=false",
    "ui_code_changed=false",
    "warroom_ui_trigger_enabled=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "view_artifact_write_allowed=false",
    "would_write_warroom_view_artifact=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "collector_ts": "2026-06-25T12:04:14Z",
            "trust_state": "trusted",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 100.0,
            "best_ask": 101.0,
            "spread": 1.0,
            "source_series_id": "series:1",
            "source_stream_session_id": "stream:1",
        }
    return {
        "collector_ts": "2026-06-25T12:04:14Z",
        "trust_state": "quarantined",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 102.0,
        "best_ask": 101.0,
        "spread": -1.0,
        "source_series_id": "series:1",
        "source_stream_session_id": "stream:1",
    }


def _read_model() -> dict:
    return {
        "ok": True,
        "read_model_version": LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
        "market_snapshot": {"source_kind": "market_state_preferred"},
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def test_spec_declares_binding_design_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_binding_design_ready_when_adapter_allows_warroom_read() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=True)], lane=LANE_WARROOM_READ).to_dict()
    packet = build_preferred_row_adapter_binding_design(read_model=_read_model(), preferred_row_adapter_packet=adapter).to_dict()
    assert packet["binding_version"] == PREFERRED_ROW_BINDING_DESIGN_VERSION
    assert packet["binding_state"] == "preferred_row_binding_design_ready"
    assert packet["read_model_present"] is True
    assert packet["adapter_packet_present"] is True
    assert packet["adapter_allowed_for_warroom"] is True
    assert packet["selected_row_available"] is True
    assert packet["proposed_read_model_section_key"] == "preferred_row_adapter_observation"
    assert packet["proposed_market_snapshot_source_kind"] == "market_state_preferred_row_adapter_observed"
    assert packet["existing_warroom_read_model_changed"] is False
    assert packet["existing_market_snapshot_replaced"] is False
    assert packet["would_send_to_broker"] is False


def test_binding_design_observe_only_when_adapter_missing() -> None:
    packet = build_preferred_row_adapter_binding_design(read_model=_read_model(), preferred_row_adapter_packet=None).to_dict()
    assert packet["binding_state"] == "preferred_row_binding_design_observe_only"
    assert packet["adapter_packet_present"] is False
    assert packet["adapter_allowed_for_warroom"] is False
    assert packet["proposed_market_snapshot_source_kind"] == "market_state_existing_snapshot_preserved"
    assert "preferred_row_adapter_packet_not_supplied_for_design_context" in packet["warning_reasons"]


def test_binding_design_blocks_when_adapter_fail_closed() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=False)], lane=LANE_WARROOM_READ).to_dict()
    packet = build_preferred_row_adapter_binding_design(read_model=_read_model(), preferred_row_adapter_packet=adapter).to_dict()
    assert packet["binding_state"] == "preferred_row_binding_design_observe_only"
    assert packet["adapter_packet_present"] is True
    assert packet["adapter_allowed_for_warroom"] is False
    assert "preferred_row_adapter_not_allowed_for_warroom_read" in packet["blocked_reasons"]
    assert "preferred_row_adapter_selected_row_missing" in packet["blocked_reasons"]


def test_module_has_no_io_runtime_binding_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "read_text(",
        "write_text(",
        "open(",
        "Path(",
        "load_latest_market_state(",
        "load_latest_prediction_warroom_read_model(",
        "build_prediction_warroom_preferred_row_adapter(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
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
    test_spec_declares_binding_design_and_safety_boundaries()
    test_binding_design_ready_when_adapter_allows_warroom_read()
    test_binding_design_observe_only_when_adapter_missing()
    test_binding_design_blocks_when_adapter_fail_closed()
    test_module_has_no_io_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
