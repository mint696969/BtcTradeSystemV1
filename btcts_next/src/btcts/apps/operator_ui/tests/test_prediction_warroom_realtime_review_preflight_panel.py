# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_realtime_review_preflight_panel.py
# desc: Verify PS-Q13B WarRoom realtime review preflight panel packet remains display-only and non-executing.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_realtime_review_preflight_contract import (  # noqa: E402
    PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION,
    REVIEW_SURFACE_IDS,
)
from btcts.apps.operator_ui.components.prediction_warroom_realtime_review_preflight_panel import (  # noqa: E402
    PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_PANEL_VERSION,
    build_prediction_warroom_realtime_review_preflight_panel_packet,
    prediction_warroom_realtime_review_boundary_rows,
    prediction_warroom_realtime_review_surface_rows,
)


def _latest_panel() -> dict:
    return {
        "adapter_packet": {
            "review_packet_ready": True,
            "session_state_updated": True,
            "blocker_count": 0,
            "warning_count": 1,
            "source_summary": {
                "prediction_run_id": "prediction_system.ps_q13b:BTC_JPY:bitFlyer:unit",
                "generated_at": "2026-06-22T13:00:00Z",
                "market_uid": "BTC_JPY:bitFlyer",
                "signal_strength_percent": 57,
                "signal_strength_band": "medium",
            },
        },
        "read_only": True,
        "non_executing": True,
        "display_only": True,
    }


def _prediction_result() -> dict:
    return {
        "scenario_core": {
            "scenario_trace": {"scenario_switch_trace": {"state": "available"}},
            "gpt_review_digest": {"operator_next_action": "review_only"},
        },
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def main() -> int:
    packet = build_prediction_warroom_realtime_review_preflight_panel_packet(
        latest_prediction_source_panel=_latest_panel(),
        prediction_system_result=_prediction_result(),
    )
    assert packet["panel_version"] == PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_PANEL_VERSION
    assert packet["preflight_version"] == PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION
    assert packet["panel_state"] == "realtime_review_preflight_panel_ready"
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["display_only"] is True
    assert packet["review_only"] is True
    assert packet["warroom_page_mutation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["parameter_mutation_allowed"] is False
    assert packet["parameter_version_append_allowed"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_mutate_live_parameters"] is False
    assert packet["would_append_parameter_version"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["broker_execution_requested"] is False
    assert packet["mode_apply_requested"] is False
    assert packet["command_ledger_append_requested"] is False
    assert packet["decision_ledger_append_requested"] is False
    assert packet["approval_append_requested"] is False
    assert packet["authorization_grant_requested"] is False
    assert packet["autotrade_trigger_enabled"] is False

    preflight = packet["preflight_packet"]
    assert preflight["ready_for_future_warroom_ui_slice"] is True
    assert preflight["prediction_run_id"] == "prediction_system.ps_q13b:BTC_JPY:bitFlyer:unit"
    assert preflight["scenario_trace_present"] is True
    assert preflight["gpt_review_digest_present"] is True

    surface_rows = prediction_warroom_realtime_review_surface_rows(preflight)
    assert [row["surface_id"] for row in surface_rows] == list(REVIEW_SURFACE_IDS)
    assert all(row["read_only"] is True for row in surface_rows)
    assert all(row["execution"] is False for row in surface_rows)
    assert all(row["autotrade"] is False for row in surface_rows)
    assert all(row["broker"] is False for row in surface_rows)

    boundary_rows = prediction_warroom_realtime_review_boundary_rows(preflight)
    boundary_keys = {row["boundary"] for row in boundary_rows}
    assert "prediction_system" in boundary_keys
    assert "warroom" in boundary_keys
    assert "collector" in boundary_keys
    assert "autotrade" in boundary_keys
    assert "silent_live_parameter_mutation" in boundary_keys
    assert "autotrade_trigger_consumption" in boundary_keys
    assert "broker_private_api" in boundary_keys
    assert all(row["read_only"] is True for row in boundary_rows)
    assert all(row["execution"] is False for row in boundary_rows)

    blocked_packet = build_prediction_warroom_realtime_review_preflight_panel_packet()
    assert blocked_packet["panel_state"] == "realtime_review_preflight_panel_review_only_not_ready"
    assert blocked_packet["preflight_packet"]["ready_for_future_warroom_ui_slice"] is False
    assert "latest_prediction_source_panel_missing" in blocked_packet["preflight_packet"]["blocked_reasons"]
    print("ok")
    return 0


def test_prediction_warroom_realtime_review_preflight_panel() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
