# path: ./tools/test_phase4a_prediction_system_ps_q20e_warroom_producer_read_only_preferred_row_adapter.py
# desc: Focused guard for PS-Q20E WarRoom / producer read-only preferred-row adapter.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.apps.operator_ui.components.prediction_warroom_preferred_row_adapter import (  # noqa: E402
    PREFERRED_ROW_ADAPTER_VERSION,
    build_prediction_warroom_preferred_row_adapter,
)
from btcts.market_engine.market_state.consumer_integration_design import (  # noqa: E402
    LANE_AUTOTRADE_TRIGGER,
    LANE_PREDICTION_PRODUCER_INPUT,
    LANE_WARROOM_READ,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20E_WARROOM_PRODUCER_READ_ONLY_PREFERRED_ROW_ADAPTER_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_preferred_row_adapter.py"

REQUIRED_MARKERS = (
    "ps_q20e_warroom_producer_read_only_preferred_row_adapter=true",
    "uses_ps_q20b_consumer_row_selection_contract=true",
    "uses_ps_q20d_lane_policy=true",
    "existing_warroom_runtime_rewired=false",
    "existing_producer_runtime_rewired=false",
    "ps_q19r_scoring_policy_changed=false",
)

FALSE_BOUNDARIES = (
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "runtime_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "collector_runtime_behavior_changed=false",
    "market_state_writer_changed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "collector_ts": "2026-06-25T12:04:14Z",
            "exchange_ts": None,
            "trust_state": "trusted",
            "boundary_reason": "none",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "interpretation_reason": "unit",
            "semantic_observer_status": "healthy",
            "best_bid": 9905261.0,
            "best_ask": 9907274.0,
            "spread": 2013.0,
            "mid_price": 9906267.5,
            "source_series_id": "series:1",
            "source_stream_session_id": "stream:1",
        }
    return {
        "collector_ts": "2026-06-25T12:04:14Z",
        "exchange_ts": None,
        "trust_state": "quarantined",
        "boundary_reason": "profile_rule",
        "continuity_state": "continuous",
        "interpretation_bucket": "reanchor_required",
        "interpretation_reason": "unit",
        "semantic_observer_status": "broken",
        "best_bid": 9906282.0,
        "best_ask": 9906280.0,
        "spread": -2.0,
        "mid_price": 9906281.0,
        "source_series_id": "series:1",
        "source_stream_session_id": "stream:1",
    }


def test_spec_declares_adapter_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_adapter_allows_warroom_read_when_preferred_row_exists_and_retains_diagnostics() -> None:
    packet = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=True)], lane=LANE_WARROOM_READ).to_dict()
    assert packet["adapter_version"] == PREFERRED_ROW_ADAPTER_VERSION
    assert packet["adapter_state"] == "preferred_row_adapter_ready"
    assert packet["requested_lane"] == LANE_WARROOM_READ
    assert packet["allowed_for_requested_lane"] is True
    assert packet["selected_row"]["trust_state"] == "trusted"
    assert packet["selected_row"]["interpretation_bucket"] == "allow_structural_use"
    assert packet["consumer_preferred_count"] == 1
    assert packet["diagnostic_transition_count"] == 1
    assert packet["diagnostic_rows_retained"] is True
    assert packet["lane_policy"]["may_display_diagnostic_rows"] is True
    assert packet["lane_policy"]["may_score_diagnostic_rows"] is False
    assert packet["would_send_to_broker"] is False


def test_adapter_allows_prediction_producer_input_read_only_when_preferred_row_exists() -> None:
    packet = build_prediction_warroom_preferred_row_adapter([_row(ok=True)], lane=LANE_PREDICTION_PRODUCER_INPUT).to_dict()
    assert packet["adapter_state"] == "preferred_row_adapter_ready"
    assert packet["requested_lane"] == LANE_PREDICTION_PRODUCER_INPUT
    assert packet["allowed_for_requested_lane"] is True
    assert packet["producer_enabled"] is False
    assert packet["prediction_artifact_write_allowed"] is False
    assert packet["existing_producer_runtime_rewired"] is False


def test_adapter_fail_closes_without_preferred_row() -> None:
    packet = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=False)], lane=LANE_WARROOM_READ).to_dict()
    assert packet["adapter_state"] == "preferred_row_adapter_blocked"
    assert packet["allowed_for_requested_lane"] is False
    assert packet["selected_row"] is None
    assert "consumer_preferred_market_overview_row_missing" in packet["blocked_reasons"]
    assert packet["diagnostic_rows_retained"] is True


def test_adapter_blocks_unsupported_execution_or_autotrade_lane() -> None:
    packet = build_prediction_warroom_preferred_row_adapter([_row(ok=True)], lane=LANE_AUTOTRADE_TRIGGER).to_dict()
    assert packet["adapter_state"] == "preferred_row_adapter_blocked"
    assert packet["allowed_for_requested_lane"] is False
    assert "preferred_row_adapter_lane_not_supported_for_ps_q20e" in packet["blocked_reasons"]
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False


def test_module_has_no_runtime_io_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "read_text(",
        "write_text(",
        "open(",
        "Path(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
        "broker_private_api_allowed: bool = True",
        "would_send_to_broker: bool = True",
        "producer_enabled: bool = True",
        "scheduler_enabled: bool = True",
        "warroom_ui_trigger_enabled: bool = True",
        "ps_q19r_scoring_policy_changed: bool = True",
        "collector_runtime_behavior_changed: bool = True",
        "market_state_writer_changed: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_adapter_and_safety_boundaries()
    test_adapter_allows_warroom_read_when_preferred_row_exists_and_retains_diagnostics()
    test_adapter_allows_prediction_producer_input_read_only_when_preferred_row_exists()
    test_adapter_fail_closes_without_preferred_row()
    test_adapter_blocks_unsupported_execution_or_autotrade_lane()
    test_module_has_no_runtime_io_or_execution_behavior()
    print('{"ok": true}')
