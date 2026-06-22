# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py
# desc: Verify PS-Q12B/PS-Q12G latest prediction source review panel helpers and panel packet remain read-only/non-executing.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION,
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION,
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
    build_prediction_warroom_latest_prediction_source_review_panel_packet,
    build_prediction_warroom_latest_prediction_source_uicheck_snapshot,
    latest_prediction_source_boundary_rows,
    latest_prediction_source_issue_rows,
    latest_prediction_source_readability_rows,
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
        "ready_for_warroom_review_panel": True,
        "session_state_updated": True,
        "q9b_loader_called_by_this_adapter": True,
        "actual_file_read_attempted": True,
        "actual_file_read_succeeded": True,
        "payload_decode_attempted": True,
        "payload_decode_succeeded": True,
        "loaded_payload_count": 1,
        "blocker_count": 0,
        "warning_count": 2,
        "blocked_reasons": [],
        "warning_reasons": ["schema_validation_deferred_to_ps_q9c", "operator_review_warning"],
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

    readability_rows = latest_prediction_source_readability_rows(_adapter_packet())
    readability = {row["item"]: row for row in readability_rows}
    assert [row["item"] for row in readability_rows] == [
        "source_panel",
        "payload_load_decode",
        "q9g_review_handoff",
        "warnings",
        "blockers",
        "signal",
    ]
    assert readability["source_panel"]["severity"] == "ok"
    assert readability["payload_load_decode"]["severity"] == "ok"
    assert readability["q9g_review_handoff"]["severity"] == "ok"
    assert readability["warnings"]["severity"] == "warning"
    assert readability["warnings"]["state"] == "2"
    assert readability["blockers"]["severity"] == "ok"
    assert readability["signal"]["severity"] == "review_only"
    assert all(row["read_only"] is True for row in readability_rows)
    assert all(row["execution"] == "false" for row in readability_rows)

    snapshot_panel = {
        "panel_version": PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
        "readability_polish_version": PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION,
        "panel_state": "latest_prediction_source_review_panel_ready",
        "adapter_packet": _adapter_packet(),
        "q9g_session_state_seed_ready": True,
        "readability_rows": readability_rows,
        "issue_rows": [
            {"severity": "warning", "reason": "schema_validation_deferred_to_ps_q9c"},
            {"severity": "warning", "reason": "operator_review_warning"},
        ],
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "warroom_page_mutation_allowed": False,
        "warroom_panel_mutation_allowed": False,
        "runtime_artifact_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }
    snapshot = build_prediction_warroom_latest_prediction_source_uicheck_snapshot(snapshot_panel)
    assert snapshot["snapshot_version"] == PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION
    assert snapshot["panel_state"] == "latest_prediction_source_review_panel_ready"
    assert snapshot["adapter_state"] == "latest_prediction_source_ready"
    assert snapshot["prediction_run_id"] == "run-ps-q12b"
    assert snapshot["loaded_payload_count"] == 1
    assert snapshot["actual_file_read_succeeded"] is True
    assert snapshot["payload_decode_succeeded"] is True
    assert snapshot["review_packet_ready"] is True
    assert snapshot["session_state_updated"] is True
    assert snapshot["q9g_session_state_seed_ready"] is True
    assert snapshot["blocker_count"] == 0
    assert snapshot["warning_count"] == 2
    assert snapshot["readability_row_count"] == 6
    assert snapshot["issue_row_count"] == 2
    assert all(snapshot["safe_boundary"].values())

    issue_rows = latest_prediction_source_issue_rows(_adapter_packet())
    assert [row["severity"] for row in issue_rows] == ["warning", "warning"]
    assert issue_rows[0]["reason"] == "schema_validation_deferred_to_ps_q9c"
    assert all(row["read_only"] is True for row in issue_rows)
    assert all(row["execution"] == "false" for row in issue_rows)

    blocked_sample = dict(_adapter_packet())
    blocked_sample.update(
        {
            "review_packet_ready": False,
            "session_state_updated": False,
            "actual_file_read_succeeded": False,
            "payload_decode_succeeded": False,
            "loaded_payload_count": 0,
            "blocker_count": 1,
            "blocked_reasons": ["freshness_status_stale_before_actual_read"],
        }
    )
    blocked_readability = {row["item"]: row for row in latest_prediction_source_readability_rows(blocked_sample)}
    assert blocked_readability["source_panel"]["severity"] == "blocker"
    assert blocked_readability["payload_load_decode"]["severity"] == "blocker"
    assert blocked_readability["q9g_review_handoff"]["severity"] == "blocker"
    assert blocked_readability["blockers"]["severity"] == "blocker"
    blocked_issues = latest_prediction_source_issue_rows(blocked_sample)
    assert blocked_issues[0]["severity"] == "blocker"
    assert blocked_issues[0]["reason"] == "freshness_status_stale_before_actual_read"

    blocked_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state={},
        allow_actual_read=False,
        store_in_session_state=False,
    )
    assert blocked_panel["panel_version"] == PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION
    assert blocked_panel["readability_polish_version"] == PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION
    assert blocked_panel["panel_state"] == "latest_prediction_source_review_panel_blocked"
    assert blocked_panel["top_default_expanded_review_panel_connected"] is True
    assert blocked_panel["q9g_session_state_seed_attempted"] is False
    assert blocked_panel["q9g_session_state_seed_ready"] is False
    assert blocked_panel["warning_readability_polish"] is True
    assert isinstance(blocked_panel["readability_rows"], list)
    assert isinstance(blocked_panel["issue_rows"], list)
    assert blocked_panel["uicheck_snapshot"]["snapshot_version"] == PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION
    assert blocked_panel["uicheck_snapshot"]["safe_boundary"]["read_only"] is True
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
