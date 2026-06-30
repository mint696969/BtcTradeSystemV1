# path: ./tools/diagnose_phase4a_prediction_system_ps_q25p_warroom_prediction_actual_screenshot_review_record.py
# desc: Read-only diagnostic for PS-Q25P WarRoom prediction actual screenshot review record.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25p_warroom_prediction_actual_screenshot_review_record.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25P_WARROOM_PREDICTION_ACTUAL_SCREENSHOT_REVIEW_RECORD_2026-06-30.md"
Q25O_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25O_WARROOM_PREDICTION_SCREENSHOT_REVIEW_INTAKE_READINESS_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"

REQUIRED_REVIEW_MARKERS = [
    "actual_screenshot_supplied=true",
    "actual_screenshot_review_performed=true",
    "actual_screenshot_count=6",
    "visual_review_result=pass_for_operator_review_not_trade_decision",
    "visual_final_candidate=true",
    "q25j_density_tuning_reviewed=true",
    "compact_header_first=true",
    "detail_checks_folded_by_default=true",
    "detail_checks_expandable=true",
    "reading_guide_folded_by_default=true",
    "prediction_metrics_visible=true",
    "prediction_rows_visible=true",
    "operator_action_guidance_visible_or_accessible=true",
    "horizon_expiry_visible_or_accessible=true",
    "no_nested_expander_runtime_error_observed=true",
    "no_autotrade_or_broker_control_added=true",
]


def run_warroom_prediction_actual_screenshot_review_record_diagnostic() -> dict:
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    q25o_text = Q25O_DOC.read_text(encoding="utf-8-sig") if Q25O_DOC.exists() else ""
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    blockers: list[str] = []
    for marker in (
        "ps_q25p_warroom_prediction_actual_screenshot_review_record=true",
        "actual_screenshot_review_record_added=true",
        "production_code_changed=false",
        "read_only_review_record=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in REQUIRED_REVIEW_MARKERS:
        if marker not in doc_text:
            blockers.append(f"review_marker_required:{marker}")
    for marker in (
        "ps_q25o_warroom_prediction_screenshot_review_intake_readiness=true",
        "screenshot_review_intake_packet_added=true",
        "actual_screenshot_review_required_before_visual_final=true",
        "q25j_density_tuning_review_target=true",
    ):
        if marker not in q25o_text:
            blockers.append(f"q25o_marker_required:{marker}")
    for marker in (
        "WARROOM_PREDICTION_DENSITY_TUNING_VERSION",
        "_render_prediction_detail_checks_foldout",
        "density_tuning_rendered",
        'with st.expander(_t(lang, "reading_title"), expanded=False)',
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
        "actual_screenshot_review_record_version": "prediction_warroom.actual_screenshot_review_record.ps_q25p.v1",
        "actual_screenshot_supplied": True,
        "actual_screenshot_review_performed": True,
        "actual_screenshot_count": 6,
        "visual_review_result": "pass_for_operator_review_not_trade_decision",
        "visual_final_candidate": True,
        "visual_final_blocker_count": 0,
        "followup_visual_polish_optional": True,
        "q25j_density_tuning_reviewed": True,
        "compact_header_first": True,
        "detail_checks_folded_by_default": True,
        "detail_checks_expandable": True,
        "reading_guide_folded_by_default": True,
        "prediction_metrics_visible": True,
        "prediction_rows_visible": True,
        "operator_action_guidance_visible_or_accessible": True,
        "horizon_expiry_visible_or_accessible": True,
        "no_nested_expander_runtime_error_observed": True,
        "no_autotrade_or_broker_control_added": True,
        "cadence_lane_stopped_at_human_gate": True,
        "safe_default_option_id": "keep_current_300s_context_only_until_gate",
        "production_code_changed": False,
        "read_only_review_record": True,
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
            "read_only_review_record",
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
    result = run_warroom_prediction_actual_screenshot_review_record_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
