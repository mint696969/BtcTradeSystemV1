# path: ./tools/test_phase4a_prediction_system_ps_q20h_read_only_loader_binding_dry_run_contract.py
# desc: Focused guard for PS-Q20H read-only loader binding dry-run contract.

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
from btcts.apps.operator_ui.prediction_warroom.read_models.read_only_loader_binding_dry_run_contract import (  # noqa: E402
    READ_ONLY_LOADER_BINDING_DRY_RUN_VERSION,
    TARGET_LOADER_NAME,
    build_read_only_loader_binding_dry_run_contract,
)
from btcts.market_engine.market_state.consumer_integration_design import LANE_WARROOM_READ  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20H_READ_ONLY_LOADER_BINDING_DRY_RUN_CONTRACT_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/read_only_loader_binding_dry_run_contract.py"

REQUIRED_MARKERS = (
    "ps_q20h_read_only_loader_binding_dry_run_contract=true",
    "dry_run_contract_only=true",
    "supplied_mappings_only=true",
    "target_loader_invoked=false",
    "latest_prediction_artifact_read=false",
    "latest_prediction_warroom_read_model_loader_changed=false",
    "existing_warroom_runtime_rewired=false",
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


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "symbol_raw": "FX_BTC_JPY",
            "collector_ts": "2026-06-25T12:04:14Z",
            "trust_state": "trusted",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 9905261,
            "best_ask": 9907274,
            "spread": 2013,
            "mid_price": 9906267.5,
            "source_series_id": "series:1",
            "source_stream_session_id": "stream:1",
        }
    return {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-25T12:04:14Z",
        "trust_state": "quarantined",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 9906282,
        "best_ask": 9906280,
        "spread": -2,
        "mid_price": 9906281,
        "source_series_id": "series:1",
        "source_stream_session_id": "stream:1",
    }


def _read_model() -> dict:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "market_snapshot": {"source_kind": "market_state_preferred", "market_uid": "bitflyer.fx.FX_BTC_JPY", "spread": 2013},
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def test_spec_declares_dry_run_contract_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_dry_run_ready_when_supplied_mappings_can_build_optional_section() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=True)], lane=LANE_WARROOM_READ).to_dict()
    packet = build_read_only_loader_binding_dry_run_contract(read_model=_read_model(), preferred_row_adapter_packet=adapter).to_dict()
    assert packet["dry_run_version"] == READ_ONLY_LOADER_BINDING_DRY_RUN_VERSION
    assert packet["dry_run_state"] == "read_only_loader_binding_dry_run_ready"
    assert packet["target_loader_name"] == TARGET_LOADER_NAME
    assert packet["read_model_supplied"] is True
    assert packet["adapter_packet_supplied"] is True
    assert packet["optional_section_preview_built"] is True
    assert packet["optional_section_preview_state"] == "preferred_row_observation_section_ready"
    assert packet["optional_section_selected_row_available"] is True
    assert packet["would_attach_optional_section_in_future_slice"] is True
    assert packet["target_loader_invoked"] is False
    assert packet["latest_prediction_artifact_read"] is False
    assert packet["latest_prediction_warroom_read_model_loader_changed"] is False
    assert packet["would_send_to_broker"] is False


def test_dry_run_observe_only_when_adapter_missing() -> None:
    packet = build_read_only_loader_binding_dry_run_contract(read_model=_read_model(), preferred_row_adapter_packet=None).to_dict()
    assert packet["dry_run_state"] == "read_only_loader_binding_dry_run_observe_only"
    assert packet["read_model_supplied"] is True
    assert packet["adapter_packet_supplied"] is False
    assert packet["would_attach_optional_section_in_future_slice"] is False
    assert "preferred_row_adapter_packet_not_supplied_for_dry_run" in packet["warning_reasons"]


def test_dry_run_blocks_future_attach_when_adapter_fail_closed() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=False)], lane=LANE_WARROOM_READ).to_dict()
    packet = build_read_only_loader_binding_dry_run_contract(read_model=_read_model(), preferred_row_adapter_packet=adapter).to_dict()
    assert packet["dry_run_state"] == "read_only_loader_binding_dry_run_observe_only"
    assert packet["adapter_packet_supplied"] is True
    assert packet["optional_section_preview_state"] == "preferred_row_observation_section_blocked"
    assert packet["would_attach_optional_section_in_future_slice"] is False
    assert "optional_preferred_row_observation_section_not_ready_for_future_attach" in packet["blocked_reasons"]
    assert "consumer_preferred_market_overview_row_missing" in packet["blocked_reasons"]


def test_module_has_no_loader_invocation_io_runtime_binding_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "read_text(",
        "write_text(",
        "open(",
        "Path(",
        "load_latest_market_state(",
        "load_latest_prediction_warroom_read_model(",
        "latest_prediction_artifact_path(",
        "load_latest_prediction_payload(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
        "target_loader_invoked: bool = True",
        "latest_prediction_artifact_read: bool = True",
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
    test_spec_declares_dry_run_contract_and_safety_boundaries()
    test_dry_run_ready_when_supplied_mappings_can_build_optional_section()
    test_dry_run_observe_only_when_adapter_missing()
    test_dry_run_blocks_future_attach_when_adapter_fail_closed()
    test_module_has_no_loader_invocation_io_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
