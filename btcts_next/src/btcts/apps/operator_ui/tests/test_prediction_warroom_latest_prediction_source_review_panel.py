# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py
# desc: Verify PS-Q12B latest prediction source review panel helpers and panel packet remain read-only/non-executing.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
    build_prediction_warroom_latest_prediction_source_review_panel_packet,
    latest_prediction_source_boundary_rows,
    latest_prediction_source_status_rows,
)


def _adapter_packet() -> dict:
    return {
        "adapter_state": "latest_prediction_source_ready",
        "source_summary": {
            "prediction_run_id": "run-ps-q12b",
            "generated_at": "2026-06-22T11:00:00Z",
            "market_uid": "bitflyer.spot.BTC_JPY",
            "signal_strength_percent": 66,
            "signal_strength_band": "medium",
        },
        "review_packet_ready": True,
        "session_state_updated": True,
        "q9b_loader_called_by_this_adapter": True,
        "actual_file_read_attempted": True,
        "payload_decode_attempted": True,
    }


def main() -> int:
    status_rows = latest_prediction_source_status_rows(_adapter_packet())
    assert [row["name"] for row in status_rows] == [
        "adapter_state",
        "prediction_run_id",
        "generated_at",
        "market_uid",
        "signal_strength",
        "review_packet_ready",
        "session_state_updated",
    ]
    assert status_rows[1]["value"] == "run-ps-q12b"
    assert status_rows[4]["value"] == "66 / medium"
    assert all(row["read_only"] is True for row in status_rows)
    assert all(row["execution"] == "false" for row in status_rows)

    boundary_rows = latest_prediction_source_boundary_rows(_adapter_packet())
    boundary = {row["boundary"]: row["enabled"] for row in boundary_rows}
    assert boundary["top_default_expanded_review_panel"] is True
    assert boundary["ps_q12a_adapter_called"] is True
    assert boundary["actual_file_read_attempted"] is True
    assert boundary["payload_decode_attempted"] is True
    assert boundary["review_packet_session_handoff"] is True
    assert boundary["warroom_page_mutation"] is False
    assert boundary["runtime_artifact_write"] is False
    assert boundary["approval_or_authorization"] is False
    assert boundary["decision_or_command_ledger_append"] is False
    assert boundary["autotrade_trigger"] is False
    assert boundary["broker_private_api"] is False

    blocked_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state={},
        allow_actual_read=False,
        store_in_session_state=False,
    )
    assert blocked_panel["panel_version"] == PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION
    assert blocked_panel["panel_state"] == "latest_prediction_source_review_panel_blocked"
    assert blocked_panel["top_default_expanded_review_panel_connected"] is True
    assert blocked_panel["q9g_session_state_seed_attempted"] is False
    assert blocked_panel["q9g_session_state_seed_ready"] is False
    assert blocked_panel["read_only"] is True
    assert blocked_panel["non_executing"] is True
    assert blocked_panel["display_only"] is True
    assert blocked_panel["render_intent_only"] is True
    assert blocked_panel["warroom_page_mutation_allowed"] is False
    assert blocked_panel["warroom_panel_mutation_allowed"] is False
    assert blocked_panel["runtime_artifact_write_allowed"] is False
    assert blocked_panel["ledger_append_allowed"] is False
    assert blocked_panel["autotrade_trigger_allowed"] is False
    assert blocked_panel["broker_private_api_allowed"] is False
    assert blocked_panel["would_send_to_broker"] is False
    assert blocked_panel["broker_execution_requested"] is False
    assert blocked_panel["mode_apply_requested"] is False
    assert blocked_panel["command_ledger_append_requested"] is False
    assert blocked_panel["approval_append_requested"] is False
    assert blocked_panel["authorization_grant_requested"] is False
    assert blocked_panel["autotrade_trigger_enabled"] is False
    assert blocked_panel["would_write_runtime_artifact"] is False
    assert blocked_panel["would_write_collector_state"] is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
