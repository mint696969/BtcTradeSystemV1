# path: ./tools/diagnose_phase4a_prediction_system_ps_q25o_warroom_prediction_screenshot_review_intake_readiness.py
# desc: Read-only diagnostic for PS-Q25O WarRoom prediction screenshot review intake readiness.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25o_warroom_prediction_screenshot_review_intake_readiness.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25O_WARROOM_PREDICTION_SCREENSHOT_REVIEW_INTAKE_READINESS_2026-06-30.md"
Q25N_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25N_WARROOM_PREDICTION_DISPLAY_CADENCE_GATE_CLOSEOUT_READINESS_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"

REQUIRED_SCREENSHOT_AREAS = [
    "warroom_page_top_visible",
    "live_market_nowcast_panel_visible",
    "prediction_compact_operator_header_visible",
    "prediction_detail_checks_folded_by_default",
    "prediction_metrics_visible",
    "prediction_rows_visible",
    "reading_guide_folded_by_default",
    "footer_or_debug_markers_not_operator_blocking",
]

ACCEPTANCE_CHECKS = [
    "compact_header_first",
    "detail_checks_not_repeated_as_full_blocks",
    "stale_or_expired_prediction_state_is_understandable",
    "operator_action_guidance_visible_or_accessible",
    "horizon_expiry_visible_or_accessible",
    "metrics_and_prediction_rows_remain_visible",
    "no_horizontal_layout_break",
    "no_nested_expander_runtime_error_observed",
    "no_autotrade_or_broker_control_added",
]


def run_warroom_prediction_screenshot_review_intake_readiness_diagnostic() -> dict:
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    q25n_text = Q25N_DOC.read_text(encoding="utf-8-sig") if Q25N_DOC.exists() else ""
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    blockers: list[str] = []
    for marker in (
        "screenshot_review_intake_packet_added=true",
        "actual_screenshot_supplied=false",
        "actual_screenshot_review_performed=false",
        "actual_screenshot_review_required_before_visual_final=true",
        "q25j_density_tuning_review_target=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for area in REQUIRED_SCREENSHOT_AREAS:
        if area not in doc_text:
            blockers.append(f"screenshot_area_required:{area}")
    for check in ACCEPTANCE_CHECKS:
        if check not in doc_text:
            blockers.append(f"acceptance_check_required:{check}")
    for marker in (
        "ps_q25n_warroom_prediction_display_cadence_gate_closeout_readiness=true",
        "closeout_readiness_packet_added=true",
        "display_lane_closeout_ready=true",
        "cadence_lane_stopped_at_human_gate=true",
        "actual_screenshot_review_performed=false",
        "actual_screenshot_review_required_before_visual_final=true",
    ):
        if marker not in q25n_text:
            blockers.append(f"q25n_marker_required:{marker}")
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
        "screenshot_review_intake_version": "prediction_warroom.screenshot_review_intake_readiness.ps_q25o.v1",
        "actual_screenshot_supplied": False,
        "actual_screenshot_review_performed": False,
        "actual_screenshot_review_required_before_visual_final": True,
        "required_screenshot_areas": REQUIRED_SCREENSHOT_AREAS,
        "required_screenshot_area_count": len(REQUIRED_SCREENSHOT_AREAS),
        "acceptance_checks": ACCEPTANCE_CHECKS,
        "acceptance_check_count": len(ACCEPTANCE_CHECKS),
        "q25j_density_tuning_review_target": True,
        "display_lane_closeout_ready_from_q25n": True,
        "cadence_lane_stopped_at_human_gate": True,
        "safe_default_option_id": "keep_current_300s_context_only_until_gate",
        "production_code_changed": False,
        "read_only_review_intake": True,
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
            "read_only_review_intake",
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
    result = run_warroom_prediction_screenshot_review_intake_readiness_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
