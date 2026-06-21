# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_adapter.py
# desc: Verify PS-Q12A WarRoom latest prediction source adapter reads allowed latest JSON as read-only and hands off a review packet without execution surfaces.

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import (  # noqa: E402
    DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_adapter import (  # noqa: E402
    LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
    build_prediction_warroom_latest_prediction_source_adapter,
)
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import (  # noqa: E402
    LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
)


def _payload() -> dict:
    return {
        "prediction_run_id": "real_ps_q12a_run_001",
        "generated_at": "2026-06-22T09:00:00Z",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "headline_ja": "PS-Q12A latest prediction source smoke",
        "primary_signal_summary": {
            "estimated_signal_strength_percent": 64,
            "estimated_reference_hit_rate_percent": 61,
            "signal_strength_band": "medium",
            "signal_strength_band_label_ja": "中",
            "signal_strength_cap_reasons": [],
            "prediction_unavailable_reasons": [],
        },
        "horizon_cards": [
            {
                "horizon_group": "short",
                "display_label_ja": "短期",
                "estimated_signal_strength_percent": 64,
                "signal_strength_band": "medium",
                "scenario_lite": {
                    "scenario_balance_state": "continuation",
                    "turning_point_risk": "medium",
                },
            }
        ],
        "family_cards": [
            {
                "family": "scenario_core_closeout_candidate",
                "horizon_sec": 300,
                "primary_label": "monitor_watch_path",
                "estimated_signal_strength_percent": 64,
                "source_quality_gate_state": "trusted",
                "source_contribution_ledger": [],
            }
        ],
        "source_quality_panel": {
            "tier0_source_quality_gate": {"gate_state": "trusted"},
            "source_artifact_input_coverage_state": "available",
        },
        "warning_panel": {
            "blockers": [],
            "warnings": [],
        },
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
        "would_append_ledger": False,
        "would_write_runtime_artifact": False,
    }


def _write_latest(root: Path) -> None:
    prediction_dir = root / "prediction"
    prediction_dir.mkdir(parents=True, exist_ok=True)
    (prediction_dir / "latest_prediction_system_result.json").write_text(
        json.dumps(_payload(), ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    blocked = build_prediction_warroom_latest_prediction_source_adapter()
    assert blocked.adapter_version == LATEST_PREDICTION_SOURCE_ADAPTER_VERSION
    assert blocked.adapter_state == "latest_prediction_source_blocked"
    assert blocked.allow_actual_read_requested is False
    assert blocked.q9b_loader_called_by_this_adapter is False
    assert "allow_actual_read_false" in blocked.blocked_reasons
    assert blocked.would_send_to_broker is False
    assert blocked.would_write_runtime_artifact is False
    assert blocked.autotrade_trigger_enabled is False

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_latest(root)
        session_state: dict = {}
        ready = build_prediction_warroom_latest_prediction_source_adapter(
            hot_latest_root_hint=str(root),
            allow_actual_read=True,
            session_state=session_state,
            store_in_session_state=True,
        )

    assert ready.adapter_state == "latest_prediction_source_ready"
    assert ready.allow_actual_read_requested is True
    assert ready.q9b_loader_called_by_this_adapter is True
    assert ready.q9o_composition_harness_called is True
    assert ready.q10k_session_state_handoff_called is True
    assert ready.actual_file_read_attempted is True
    assert ready.actual_file_read_succeeded is True
    assert ready.payload_decode_attempted is True
    assert ready.payload_decode_succeeded is True
    assert ready.loaded_payload_count == 1
    assert ready.review_packet_ready is True
    assert ready.ready_for_warroom_review_panel is True
    assert ready.ready_for_warroom_top_display is False
    assert ready.session_state_updated is True
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in session_state
    assert ready.blocker_count == 0
    assert ready.review_packet["contract_version"] == (
        LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
    )
    assert ready.review_packet["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert ready.source_summary["prediction_run_id"] == "real_ps_q12a_run_001"
    assert ready.source_summary["generated_at"] == "2026-06-22T09:00:00Z"
    assert ready.source_summary["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert ready.source_summary["signal_strength_percent"] == 64
    assert ready.read_only is True
    assert ready.non_executing is True
    assert ready.ui_controls_added is False
    assert ready.ui_triggered_loader_execution is False
    assert ready.warroom_page_mutation_allowed is False
    assert ready.warroom_panel_mutation_allowed is False
    assert ready.runtime_artifact_write_allowed is False
    assert ready.ledger_append_allowed is False
    assert ready.autotrade_trigger_allowed is False
    assert ready.broker_private_api_allowed is False
    assert ready.would_send_to_broker is False
    assert ready.broker_execution_requested is False
    assert ready.mode_apply_requested is False
    assert ready.command_ledger_append_requested is False
    assert ready.approval_append_requested is False
    assert ready.authorization_grant_requested is False
    assert ready.autotrade_trigger_enabled is False
    assert ready.would_write_runtime_artifact is False
    assert ready.would_write_collector_state is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
