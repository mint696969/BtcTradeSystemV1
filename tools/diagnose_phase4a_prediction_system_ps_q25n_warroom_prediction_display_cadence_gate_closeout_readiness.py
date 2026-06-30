# path: ./tools/diagnose_phase4a_prediction_system_ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness.py
# desc: Read-only diagnostic for PS-Q25N WarRoom prediction display/cadence-gate closeout readiness.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25N_WARROOM_PREDICTION_DISPLAY_CADENCE_GATE_CLOSEOUT_READINESS_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"
REQUIRED_DOCS = [
    "PREDICTION_SYSTEM_PS_Q25B_WARROOM_LIVE_MARKET_NOWCAST_HIGH_FREQUENCY_VISIBILITY_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25C_WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_ATTENTION_CLASSIFICATION_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25D_WARROOM_LIVE_NOWCAST_SOURCE_IMPORTANCE_SIGNAL_LAYERING_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25E_WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_HISTORY_MINI_TREND_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25F_WARROOM_LIVE_NOWCAST_HORIZON_READINESS_PREDICTION_INPUT_HANDOFF_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25G_WARROOM_PREDICTION_ARTIFACT_HORIZON_FRESHNESS_EXPIRY_VISIBILITY_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25H_WARROOM_PREDICTION_DATA_AGE_SEVERITY_OPERATOR_ACTION_GUIDANCE_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25I_WARROOM_PREDICTION_PANEL_SECTION_ORDER_COMPACT_LAYOUT_POLISH_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25J_WARROOM_PREDICTION_PANEL_VISUAL_REVIEW_DENSITY_TUNING_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25K_WARROOM_PREDICTION_PRODUCER_CADENCE_GAP_PLANNING_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25L_WARROOM_PREDICTION_PRODUCER_CADENCE_OPTIONS_HUMAN_GATE_2026-06-30.md",
    "PREDICTION_SYSTEM_PS_Q25M_WARROOM_PREDICTION_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_2026-06-30.md",
]


def run_warroom_prediction_display_cadence_gate_closeout_readiness_diagnostic() -> dict:
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    docs_dir = REPO_ROOT / "docs" / "strategy"
    existing_docs = [name for name in REQUIRED_DOCS if (docs_dir / name).exists()]
    missing_docs = [name for name in REQUIRED_DOCS if name not in existing_docs]
    blockers: list[str] = []
    for marker in (
        "WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION",
        "WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION",
        "WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION",
        "WARROOM_PREDICTION_DENSITY_TUNING_VERSION",
        "_render_prediction_detail_checks_foldout",
        "density_tuning_rendered",
    ):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in (
        "PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION",
        "PREDICTION_WARROOM_PRODUCER_CADENCE_OPTION_DECISION_VERSION",
        "PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION",
        "implementation_allowed_by_this_packet",
        "must_stop_before_implementation",
        "keep_current_300s_context_only_until_gate",
    ):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    for marker in (
        "closeout_readiness_packet_added=true",
        "production_code_changed=false",
        "read_only_closeout=true",
        "display_lane_closeout_ready=true",
        "cadence_lane_stopped_at_human_gate=true",
        "actual_screenshot_review_performed=false",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    if missing_docs:
        blockers.append("q25b_to_q25m_docs_missing")
    for forbidden in ("Set-ScheduledTask", "Enable-ScheduledTask", "Disable-ScheduledTask", "Register-ScheduledTask", "New-ScheduledTaskTrigger", "append_decision_jsonl", "run_shadow_decision_from_snapshot", "submit_mode_change_command_request", "validate_and_append_command", "send_order(", "place_order(", "create_order(", ".write_text(", ".write_bytes(", "os.replace", "shutil.copy2"):
        if forbidden in panel_text or forbidden in contract_text:
            blockers.append(f"forbidden_marker_present:{forbidden}")
    packet = {
        "closeout_readiness_version": "prediction_warroom.display_cadence_gate_closeout_readiness.ps_q25n.v1",
        "display_lane_closeout_ready": True,
        "cadence_lane_stopped_at_human_gate": True,
        "safe_default_option_id": "keep_current_300s_context_only_until_gate",
        "actual_screenshot_review_performed": False,
        "actual_screenshot_review_required_before_visual_final": True,
        "q25b_to_q25m_required_doc_count": len(REQUIRED_DOCS),
        "q25b_to_q25m_existing_doc_count": len(existing_docs),
        "missing_docs": missing_docs,
        "production_code_changed": False,
        "read_only_closeout": True,
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
            "read_only_closeout",
            "planning_only",
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
    result = run_warroom_prediction_display_cadence_gate_closeout_readiness_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
