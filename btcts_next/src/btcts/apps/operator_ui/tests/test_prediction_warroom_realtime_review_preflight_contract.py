# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_realtime_review_preflight_contract.py
# desc: Verify PS-Q13A WarRoom real-time prediction review preflight remains contract-only, review-only, and responsibility-separated.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_realtime_review_preflight_contract import (  # noqa: E402
    FORBIDDEN_NEXT_BEHAVIOR,
    PARAMETER_REVIEW_STATES,
    PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION,
    RESPONSIBILITY_BOUNDARY,
    REVIEW_SURFACE_IDS,
    build_prediction_warroom_realtime_review_preflight,
)


def _latest_panel() -> dict:
    return {
        "panel_state": "latest_prediction_source_review_panel_ready",
        "adapter_packet": {
            "adapter_state": "latest_prediction_source_ready",
            "review_packet_ready": True,
            "session_state_updated": True,
            "blocker_count": 0,
            "warning_count": 2,
            "source_summary": {
                "prediction_run_id": "prediction_system.ps_q13a:BTC_JPY:bitFlyer:unit",
                "generated_at": "2026-06-22T12:00:00Z",
                "market_uid": "BTC_JPY:bitFlyer",
                "signal_strength_percent": 55,
                "signal_strength_band": "medium",
            },
        },
        "read_only": True,
        "non_executing": True,
        "display_only": True,
    }


def _prediction_result() -> dict:
    return {
        "prediction_run_id": "prediction_system.ps_q13a:BTC_JPY:bitFlyer:unit",
        "generated_at": "2026-06-22T12:00:00Z",
        "market_uid": "BTC_JPY:bitFlyer",
        "scenario_core": {
            "scenario_trace": {
                "evidence_weighting_trace": {"state": "available"},
                "invalidation_rewrite_trace": {"state": "available"},
                "scenario_switch_trace": {"state": "available"},
            },
            "gpt_review_digest": {
                "primary_story": "unit digest",
                "operator_next_action": "review_only",
            },
        },
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def main() -> int:
    blocked = build_prediction_warroom_realtime_review_preflight()
    assert blocked.preflight_version == PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION
    assert blocked.preflight_state == "blocked_waiting_for_latest_prediction_source"
    assert blocked.latest_prediction_source_panel_present is False
    assert "latest_prediction_source_panel_missing" in blocked.blocked_reasons
    assert blocked.ready_for_future_warroom_ui_slice is False
    assert blocked.read_only is True
    assert blocked.non_executing is True
    assert blocked.contract_only is True
    assert blocked.preflight_only is True
    assert blocked.display_only is True
    assert blocked.streamlit_import_required is False
    assert blocked.streamlit_render_performed_by_this_contract is False
    assert blocked.ui_controls_added is False
    assert blocked.would_read_runtime_file is False
    assert blocked.would_decode_payload is False
    assert blocked.would_write_runtime_artifact is False
    assert blocked.would_mutate_live_parameters is False
    assert blocked.would_append_parameter_version is False
    assert blocked.command_ledger_append_requested is False
    assert blocked.decision_ledger_append_requested is False
    assert blocked.autotrade_trigger_enabled is False
    assert blocked.broker_execution_requested is False
    assert blocked.mode_apply_requested is False
    assert blocked.would_send_to_broker is False

    ready = build_prediction_warroom_realtime_review_preflight(
        latest_prediction_source_panel=_latest_panel(),
        prediction_system_result=_prediction_result(),
    )
    payload = ready.to_dict()
    assert ready.preflight_state == "ready_for_future_warroom_ui_slice"
    assert ready.ready_for_future_warroom_ui_slice is True
    assert ready.latest_prediction_review_ready is True
    assert ready.latest_prediction_blocker_count == 0
    assert ready.latest_prediction_warning_count == 2
    assert ready.prediction_run_id == "prediction_system.ps_q13a:BTC_JPY:bitFlyer:unit"
    assert ready.generated_at == "2026-06-22T12:00:00Z"
    assert ready.market_uid == "BTC_JPY:bitFlyer"
    assert ready.signal_strength_percent == 55
    assert ready.signal_strength_band == "medium"
    assert ready.scenario_trace_present is True
    assert ready.gpt_review_digest_present is True
    assert ready.blocker_count == 0

    assert tuple(payload["surface_ids"]) == REVIEW_SURFACE_IDS
    surface_by_id = {row["surface_id"]: row for row in payload["review_surfaces"]}
    assert set(surface_by_id) == set(REVIEW_SURFACE_IDS)
    assert surface_by_id["latest_prediction_source"]["state"] == "ready"
    assert surface_by_id["realtime_prediction_delta_review"]["state"] == "declared_check_only"
    assert surface_by_id["scenario_trace_review"]["state"] == "present"
    assert surface_by_id["gpt_assisted_explanation_context"]["state"] == "present"
    assert surface_by_id["parameter_adjustment_candidate_review"]["state"] == "proposal_only_declared"
    assert all(row["read_only"] is True for row in payload["review_surfaces"])
    assert all(row["execution"] is False for row in payload["review_surfaces"])
    assert all(row["autotrade"] is False for row in payload["review_surfaces"])
    assert all(row["broker"] is False for row in payload["review_surfaces"])

    assert payload["responsibility_boundary"] == dict(RESPONSIBILITY_BOUNDARY)
    assert "proposal_only" in PARAMETER_REVIEW_STATES
    assert "human_review_required" in PARAMETER_REVIEW_STATES
    assert "versioned_policy_required_before_apply" in PARAMETER_REVIEW_STATES
    assert "silent_live_parameter_mutation" in FORBIDDEN_NEXT_BEHAVIOR
    assert "autotrade_trigger_consumption" in FORBIDDEN_NEXT_BEHAVIOR
    assert "broker_private_api" in FORBIDDEN_NEXT_BEHAVIOR
    assert "warroom_runtime_artifact_write" in FORBIDDEN_NEXT_BEHAVIOR

    assert payload["would_mutate_live_parameters"] is False
    assert payload["would_append_parameter_version"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["command_ledger_append_requested"] is False
    assert payload["decision_ledger_append_requested"] is False
    assert payload["approval_append_requested"] is False
    assert payload["autotrade_trigger_enabled"] is False
    assert payload["broker_execution_requested"] is False
    assert payload["would_send_to_broker"] is False
    return 0


def test_prediction_warroom_realtime_review_preflight_contract() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
