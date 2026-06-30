# path: ./tools/diagnose_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff.py
# desc: Read-only diagnostic for PS-Q25Q WarRoom prediction display closeout handoff.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25q_warroom_prediction_display_closeout_handoff.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25Q_WARROOM_PREDICTION_DISPLAY_CLOSEOUT_HANDOFF_2026-06-30.md"
Q25P_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25P_WARROOM_PREDICTION_ACTUAL_SCREENSHOT_REVIEW_RECORD_2026-06-30.md"
Q25M_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25M_WARROOM_PREDICTION_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"


def run_warroom_prediction_display_closeout_handoff_diagnostic() -> dict:
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    q25p_text = Q25P_DOC.read_text(encoding="utf-8-sig") if Q25P_DOC.exists() else ""
    q25m_text = Q25M_DOC.read_text(encoding="utf-8-sig") if Q25M_DOC.exists() else ""
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    blockers: list[str] = []
    for marker in (
        "ps_q25q_warroom_prediction_display_closeout_handoff=true",
        "display_closeout_handoff_added=true",
        "display_lane_closed_out=true",
        "visual_review_recorded=true",
        "visual_review_result=pass_for_operator_review_not_trade_decision",
        "visual_final_for_operator_review=true",
        "trade_decision_approved=false",
        "execution_approval=false",
        "production_code_changed=false",
        "read_only_closeout_handoff=true",
        "cadence_lane_stopped_at_human_gate=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "scheduler_enabled=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "actual_screenshot_review_record_added=true",
        "actual_screenshot_supplied=true",
        "actual_screenshot_review_performed=true",
        "visual_review_result=pass_for_operator_review_not_trade_decision",
        "visual_final_candidate=true",
        "visual_final_blockers=[]",
        "q25j_density_tuning_reviewed=true",
    ):
        if marker not in q25p_text:
            blockers.append(f"q25p_marker_required:{marker}")
    for marker in (
        "ps_q25m_warroom_prediction_producer_cadence_gate_awaiting_human=true",
        "human_decision_recorded=false",
        "implementation_allowed_by_this_packet=false",
        "must_stop_before_implementation=true",
        "safe_default_option_id=keep_current_300s_context_only_until_gate",
    ):
        if marker not in q25m_text:
            blockers.append(f"q25m_marker_required:{marker}")
    for marker in (
        "WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION",
        "WARROOM_PREDICTION_DENSITY_TUNING_VERSION",
        "_render_prediction_detail_checks_foldout",
        "density_tuning_rendered",
    ):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION",
        "implementation_allowed_by_this_packet",
        "keep_current_300s_context_only_until_gate",
    ):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    packet = {
        "display_closeout_handoff_version": "prediction_warroom.display_closeout_handoff.ps_q25q.v1",
        "display_lane_closed_out": True,
        "visual_review_recorded": True,
        "visual_review_result": "pass_for_operator_review_not_trade_decision",
        "visual_final_for_operator_review": True,
        "trade_decision_approved": False,
        "execution_approval": False,
        "safe_stop_here": True,
        "optional_next_display_only_polish": True,
        "scenario_prediction_core_strengthening_allowed_as_separate_non_execution_work": True,
        "producer_cadence_implementation_requires_explicit_human_option_and_gate_token": True,
        "autotrade_actual_page_wiring_still_requires_separate_human_gate": True,
        "cadence_lane_stopped_at_human_gate": True,
        "safe_default_option_id": "keep_current_300s_context_only_until_gate",
        "production_code_changed": False,
        "read_only_closeout_handoff": True,
        "planning_only": True,
        "non_executing": True,
        "producer_cadence_changed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "safety": {key: packet[key] for key in (
            "production_code_changed",
            "read_only_closeout_handoff",
            "planning_only",
            "trade_decision_approved",
            "execution_approval",
            "producer_cadence_changed",
            "scheduler_action_changed",
            "scheduler_enabled",
            "producer_enabled",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "prediction_artifact_write_allowed",
            "view_artifact_write_allowed",
            "latest_manifest_written",
            "run_sidecars_written",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "ledger_append_allowed",
            "mode_apply_allowed",
            "parameter_apply_allowed",
            "would_send_to_broker",
        )},
    }


def main() -> int:
    result = run_warroom_prediction_display_closeout_handoff_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
