# path: ./tools/diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py
# desc: No-write diagnostic for PS-Q23R closeout and room/steady-state guard sync.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23r_scheduled_compact_legacy_tick_observation import (  # noqa: E402
    run_scheduled_compact_legacy_tick_observation,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q23r_closeout_steady_state_guard_sync.v1"
ROOM_ROOT = REPO_ROOT / "tmp" / "gpt_room"
EXPECTED_PRE_CLOSEOUT_GATE = "PS_Q23R_AFTER_SCHEDULED_COMPACT_LEGACY_STEADY_STATE"
EXPECTED_PRE_CLOSEOUT_FOCUS = "ps_q23r_room_sync_after_scheduled_compact_legacy_steady_state"
EXPECTED_PRE_CLOSEOUT_SLICE = "PS-Q23R_SCHEDULED_COMPACT_LEGACY_TICK_OBSERVATION"
EXPECTED_POST_CLOSEOUT_GATE = "PS_Q23R_CLOSEOUT_STEADY_STATE_GUARD_SYNCED"
EXPECTED_POST_CLOSEOUT_FOCUS = "ps_q23r_closeout_steady_state_guard_sync_completed"
EXPECTED_POST_CLOSEOUT_SLICE = "PS-Q23R_CLOSEOUT_AND_STEADY_STATE_GUARD_SYNC"
EXPECTED_Q23T_GATE = "PS_Q23T_MANIFEST_FIRST_STEADY_STATE_GUARD_HARDENED"
EXPECTED_Q23T_FOCUS = "ps_q23t_manifest_first_steady_state_guard_hardening_completed"
EXPECTED_Q23T_SLICE = "PS-Q23T_MANIFEST_FIRST_STEADY_STATE_GUARD_HARDENING"
EXPECTED_Q24A_GATE = "PS_Q24A_AUTOTRADE_READ_ONLY_PREDICTION_CONSUMPTION_PLANNED"
EXPECTED_Q24A_FOCUS = "ps_q24a_autotrade_read_only_prediction_consumption_planning_completed"
EXPECTED_Q24A_SLICE = "PS-Q24A_AUTOTRADE_READ_ONLY_PREDICTION_CONSUMPTION_PLANNING"
EXPECTED_Q24B_GATE = "PS_Q24B_AUTOTRADE_READ_ONLY_PREDICTION_STATUS_DISPLAY_COMPAT_GUARDED"
EXPECTED_Q24B_FOCUS = "ps_q24b_autotrade_read_only_prediction_status_display_compat_guard_completed"
EXPECTED_Q24B_SLICE = "PS-Q24B_AUTOTRADE_READ_ONLY_PREDICTION_STATUS_DISPLAY_COMPAT_GUARD"
EXPECTED_Q24C_GATE = "PS_Q24C_AUTOTRADE_READ_ONLY_STATUS_PAGE_PLANNING_NO_RUNTIME_WIRING_DONE"
EXPECTED_Q24C_FOCUS = "ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring_completed"
EXPECTED_Q24C_SLICE = "PS-Q24C_AUTOTRADE_READ_ONLY_STATUS_PAGE_PLANNING_NO_RUNTIME_WIRING"
EXPECTED_Q24D_GATE = "PS_Q24D_AUTOTRADE_READ_ONLY_STATUS_PAGE_DISPLAY_PACKET_DESIGNED"
EXPECTED_Q24D_FOCUS = "ps_q24d_autotrade_read_only_status_page_display_packet_design_completed"
EXPECTED_Q24D_SLICE = "PS-Q24D_AUTOTRADE_READ_ONLY_STATUS_PAGE_DISPLAY_PACKET_DESIGN"
EXPECTED_Q24E_GATE = "PS_Q24E_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDER_PLAN_NO_COMMANDS_DONE"
EXPECTED_Q24E_FOCUS = "ps_q24e_autotrade_read_only_status_page_render_plan_no_commands_completed"
EXPECTED_Q24E_SLICE = "PS-Q24E_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDER_PLAN_NO_COMMANDS"
EXPECTED_Q24F_GATE = "PS_Q24F_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDERER_COMPONENT_DRY_RUN_NO_PAGE_WIRING_DONE"
EXPECTED_Q24F_FOCUS = "ps_q24f_autotrade_read_only_status_page_renderer_component_dry_run_no_page_wiring_completed"
EXPECTED_Q24F_SLICE = "PS-Q24F_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDERER_COMPONENT_DRY_RUN_NO_PAGE_WIRING"
EXPECTED_Q24G_GATE = "PS_Q24G_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_NO_PAGE_CHANGE_DONE"
EXPECTED_Q24G_FOCUS = "ps_q24g_autotrade_read_only_status_page_actual_render_wiring_plan_no_page_change_completed"
EXPECTED_Q24G_SLICE = "PS-Q24G_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_RENDER_WIRING_PLAN_NO_PAGE_CHANGE"
EXPECTED_Q24H_GATE = "PS_Q24H_AUTOTRADE_READ_ONLY_STATUS_PAGE_PAGE_WIRING_READINESS_NO_CHANGE_DONE"
EXPECTED_Q24H_FOCUS = "ps_q24h_autotrade_read_only_status_page_page_wiring_readiness_no_change_completed"
EXPECTED_Q24H_SLICE = "PS-Q24H_AUTOTRADE_READ_ONLY_STATUS_PAGE_PAGE_WIRING_READINESS_NO_CHANGE"
EXPECTED_Q24I_GATE = "PS_Q24I_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDERER_ACTUAL_PAGE_WIRING_GATE_READINESS_DONE"
EXPECTED_Q24I_FOCUS = "ps_q24i_autotrade_read_only_status_page_renderer_actual_page_wiring_gate_readiness_completed"
EXPECTED_Q24I_SLICE = "PS-Q24I_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDERER_ACTUAL_PAGE_WIRING_GATE_READINESS"
EXPECTED_Q24J_GATE = "PS_Q24J_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_GATE_REQUIRED_DONE"
EXPECTED_Q24J_FOCUS = "ps_q24j_autotrade_read_only_status_page_actual_page_wiring_explicit_gate_required_completed"
EXPECTED_Q24J_SLICE = "PS-Q24J_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_GATE_REQUIRED"
EXPECTED_Q24K_GATE = "PS_Q24K_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_HUMAN_GATE_DECISION_DONE"
EXPECTED_Q24K_FOCUS = "ps_q24k_autotrade_read_only_status_page_actual_page_wiring_human_gate_decision_completed"
EXPECTED_Q24K_SLICE = "PS-Q24K_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_HUMAN_GATE_DECISION"
EXPECTED_Q24L_GATE = "PS_Q24L_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_HUMAN_GATE_REQUIRED_DONE"
EXPECTED_Q24L_FOCUS = "ps_q24l_autotrade_read_only_status_page_actual_page_wiring_explicit_human_gate_required_completed"
EXPECTED_Q24L_SLICE = "PS-Q24L_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_HUMAN_GATE_REQUIRED"
EXPECTED_Q24M_GATE = "PS_Q24M_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_HUMAN_GATE_DECISION_REQUIRED_DONE"
EXPECTED_Q24M_FOCUS = "ps_q24m_autotrade_read_only_status_page_actual_page_wiring_explicit_human_gate_decision_required_completed"
EXPECTED_Q24M_SLICE = "PS-Q24M_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_EXPLICIT_HUMAN_GATE_DECISION_REQUIRED"
ALLOWED_ROOM_GATES = {EXPECTED_PRE_CLOSEOUT_GATE, EXPECTED_POST_CLOSEOUT_GATE, EXPECTED_Q23T_GATE, EXPECTED_Q24A_GATE, EXPECTED_Q24B_GATE, EXPECTED_Q24C_GATE, EXPECTED_Q24D_GATE, EXPECTED_Q24E_GATE, EXPECTED_Q24F_GATE, EXPECTED_Q24G_GATE, EXPECTED_Q24H_GATE, EXPECTED_Q24I_GATE, EXPECTED_Q24J_GATE, EXPECTED_Q24K_GATE, EXPECTED_Q24L_GATE, EXPECTED_Q24M_GATE}
ALLOWED_ROOM_FOCUSES = {EXPECTED_PRE_CLOSEOUT_FOCUS, EXPECTED_POST_CLOSEOUT_FOCUS, EXPECTED_Q23T_FOCUS, EXPECTED_Q24A_FOCUS, EXPECTED_Q24B_FOCUS, EXPECTED_Q24C_FOCUS, EXPECTED_Q24D_FOCUS, EXPECTED_Q24E_FOCUS, EXPECTED_Q24F_FOCUS, EXPECTED_Q24G_FOCUS, EXPECTED_Q24H_FOCUS, EXPECTED_Q24I_FOCUS, EXPECTED_Q24J_FOCUS, EXPECTED_Q24K_FOCUS, EXPECTED_Q24L_FOCUS, EXPECTED_Q24M_FOCUS}
ALLOWED_ROOM_SLICES = {EXPECTED_PRE_CLOSEOUT_SLICE, EXPECTED_POST_CLOSEOUT_SLICE, EXPECTED_Q23T_SLICE, EXPECTED_Q24A_SLICE, EXPECTED_Q24B_SLICE, EXPECTED_Q24C_SLICE, EXPECTED_Q24D_SLICE, EXPECTED_Q24E_SLICE, EXPECTED_Q24F_SLICE, EXPECTED_Q24G_SLICE, EXPECTED_Q24H_SLICE, EXPECTED_Q24I_SLICE, EXPECTED_Q24J_SLICE, EXPECTED_Q24K_SLICE, EXPECTED_Q24L_SLICE, EXPECTED_Q24M_SLICE}
DIRTY_ONLY_BLOCKERS = {
    "repo_clean_required_for_q23r_closeout",
    "q23k_no_write_readiness_blockers_unexpected",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        return {}, f"json_load_failed:{exc.__class__.__name__}"
    if not isinstance(data, dict):
        return {}, "json_not_object"
    return data, ""


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8-sig"), ""
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        return "", f"text_load_failed:{exc.__class__.__name__}"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def run_ps_q23r_closeout_steady_state_guard_sync() -> dict[str, Any]:
    head = _git(["rev-parse", "--short", "HEAD"])
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q23r = run_scheduled_compact_legacy_tick_observation()
    q23r_blockers = list(q23r.get("blockers") or [])
    q23r_non_dirty_blockers = [item for item in q23r_blockers if item not in DIRTY_ONLY_BLOCKERS]

    status_text, status_error = _read_text(ROOM_ROOT / "08_STATUS.md")
    focus, focus_error = _load_json(ROOM_ROOT / "09_FOCUS.json")
    state, state_error = _load_json(ROOM_ROOT / "11_STATE.json")
    handoff_path = ROOM_ROOT / "memory" / "handoffs" / "2026-06-29_ps_q23r_room_sync_after_scheduled_compact_legacy_steady_state.md"
    handoff_text, handoff_error = _read_text(handoff_path)

    room_blockers: list[str] = []
    if status_error:
        room_blockers.append("room_status_read_required")
    if focus_error:
        room_blockers.append("room_focus_json_read_required")
    if state_error:
        room_blockers.append("room_state_json_read_required")
    if handoff_error:
        room_blockers.append("room_q23r_handoff_read_required")
    status_has_pre_closeout_marker = "PS-Q23R after scheduled compact legacy steady-state" in status_text
    status_has_post_closeout_marker = "PS-Q23R closeout steady-state guard synced" in status_text
    status_has_q23t_marker = "PS-Q23T manifest-first steady-state guard hardened" in status_text
    status_has_q24a_marker = "PS-Q24A AutoTrade read-only prediction consumption planning completed" in status_text
    status_has_q24b_marker = "PS-Q24B AutoTrade read-only prediction status display compat guard completed" in status_text
    status_has_q24c_marker = "PS-Q24C AutoTrade read-only status page planning / no runtime wiring completed" in status_text
    status_has_q24d_marker = "PS-Q24D AutoTrade read-only status page display packet design completed" in status_text
    status_has_q24e_marker = "PS-Q24E AutoTrade read-only status page render plan / no commands completed" in status_text
    status_has_q24f_marker = "PS-Q24F AutoTrade read-only status page renderer component dry-run / no page wiring completed" in status_text
    status_has_q24g_marker = "PS-Q24G AutoTrade read-only status page actual render wiring plan / no page change completed" in status_text
    status_has_q24h_marker = "PS-Q24H AutoTrade read-only status page page-wiring readiness / no change completed" in status_text
    status_has_q24i_marker = "PS-Q24I AutoTrade read-only status page renderer actual page-wiring gate readiness completed" in status_text
    status_has_q24j_marker = "PS-Q24J AutoTrade read-only status page actual page wiring explicit gate required completed" in status_text
    status_has_q24k_marker = "PS-Q24K AutoTrade read-only status page actual page wiring human gate decision completed" in status_text
    status_has_q24l_marker = "PS-Q24L AutoTrade read-only status page actual page wiring explicit human gate required completed" in status_text
    status_has_q24m_marker = "PS-Q24M AutoTrade read-only status page actual page wiring explicit human gate decision required completed" in status_text
    if not (status_has_pre_closeout_marker or status_has_post_closeout_marker or status_has_q23t_marker or status_has_q24a_marker or status_has_q24b_marker or status_has_q24c_marker or status_has_q24d_marker or status_has_q24e_marker or status_has_q24f_marker or status_has_q24g_marker or status_has_q24h_marker or status_has_q24i_marker or status_has_q24j_marker or status_has_q24k_marker or status_has_q24l_marker or status_has_q24m_marker):
        room_blockers.append("room_status_q23r_or_later_safe_marker_required")
    if "PS-Q22T danger boundary" in status_text:
        room_blockers.append("room_status_must_not_be_old_q22t_entry")
    if focus.get("current_focus") not in ALLOWED_ROOM_FOCUSES:
        room_blockers.append("room_focus_current_focus_q23r_or_closeout_required")
    if focus.get("latest_slice") not in ALLOWED_ROOM_SLICES:
        room_blockers.append("room_focus_latest_slice_q23r_or_closeout_required")
    if _mapping(focus.get("work_policy")).get("default_method") != "one_shot_patch_runner":
        room_blockers.append("room_focus_one_shot_patch_runner_policy_required")
    if state.get("current_gate") not in ALLOWED_ROOM_GATES:
        room_blockers.append("room_state_current_gate_q23r_or_closeout_required")
    if state.get("latest_completed_slice") not in ALLOWED_ROOM_SLICES:
        room_blockers.append("room_state_latest_completed_slice_q23r_or_closeout_required")
    prediction_status = _mapping(state.get("prediction_status"))
    if prediction_status.get("latest_manifest_record_count") != 110:
        room_blockers.append("room_state_latest_manifest_record_count_110_required")
    if prediction_status.get("legacy_latest_compact_record_count") != 24:
        room_blockers.append("room_state_compact_record_count_24_required")
    if prediction_status.get("legacy_latest_original_record_count") != 110:
        room_blockers.append("room_state_original_record_count_110_required")
    if prediction_status.get("would_send_to_broker") is not False:
        room_blockers.append("room_state_would_send_to_broker_false_required")
    if EXPECTED_PRE_CLOSEOUT_GATE not in handoff_text and EXPECTED_POST_CLOSEOUT_GATE not in status_text and EXPECTED_Q23T_GATE not in status_text and EXPECTED_Q24A_GATE not in status_text and EXPECTED_Q24B_GATE not in status_text and EXPECTED_Q24C_GATE not in status_text and EXPECTED_Q24D_GATE not in status_text and EXPECTED_Q24E_GATE not in status_text and EXPECTED_Q24F_GATE not in status_text and EXPECTED_Q24G_GATE not in status_text and EXPECTED_Q24H_GATE not in status_text and EXPECTED_Q24I_GATE not in status_text and EXPECTED_Q24J_GATE not in status_text and EXPECTED_Q24K_GATE not in status_text and EXPECTED_Q24L_GATE not in status_text and EXPECTED_Q24M_GATE not in status_text:
        room_blockers.append("room_handoff_or_status_expected_gate_required")

    q23r_legacy = _mapping(q23r.get("legacy_latest"))
    q23r_manifest = _mapping(q23r.get("latest_manifest"))
    q23r_sidecar = _mapping(q23r.get("forecast_records_sidecar"))
    q23r_q23e = _mapping(q23r.get("q23e"))

    artifact_blockers: list[str] = []
    if q23r_legacy.get("compact_record_count") != 24:
        artifact_blockers.append("live_compact_legacy_record_count_24_required")
    if q23r_legacy.get("original_record_count") != 110:
        artifact_blockers.append("live_original_record_count_110_required")
    if q23r_manifest.get("record_count") != 110:
        artifact_blockers.append("live_manifest_record_count_110_required")
    if q23r_sidecar.get("line_count") != 110:
        artifact_blockers.append("live_forecast_records_line_count_110_required")
    if q23r_q23e.get("source_artifact_mode") != "distributed":
        artifact_blockers.append("live_manifest_first_reader_distributed_required")
    if q23r_q23e.get("legacy_fallback_ready") is not True:
        artifact_blockers.append("live_legacy_fallback_ready_required")

    blockers = q23r_non_dirty_blockers + room_blockers + artifact_blockers
    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {
            "branch": branch,
            "head": head,
            "status_short": status_short,
            "dirty_only_q23r_blockers_allowed_while_uncommitted": sorted(DIRTY_ONLY_BLOCKERS),
        },
        "ready": ready,
        "state": "ps_q23r_closeout_steady_state_guard_sync_ready" if ready else "ps_q23r_closeout_steady_state_guard_sync_blocked",
        "blockers": blockers,
        "q23r_blockers": q23r_blockers,
        "q23r_non_dirty_blockers": q23r_non_dirty_blockers,
        "room_blockers": room_blockers,
        "artifact_blockers": artifact_blockers,
        "room": {
            "status_marker_present": status_has_pre_closeout_marker or status_has_post_closeout_marker or status_has_q23t_marker or status_has_q24a_marker or status_has_q24b_marker or status_has_q24c_marker or status_has_q24d_marker or status_has_q24e_marker or status_has_q24f_marker or status_has_q24g_marker or status_has_q24h_marker or status_has_q24i_marker or status_has_q24j_marker or status_has_q24k_marker or status_has_q24l_marker or status_has_q24m_marker,
            "status_pre_closeout_marker_present": status_has_pre_closeout_marker,
            "status_post_closeout_marker_present": status_has_post_closeout_marker,
            "status_q23t_marker_present": status_has_q23t_marker,
            "status_q24a_marker_present": status_has_q24a_marker,
            "status_q24b_marker_present": status_has_q24b_marker,
            "status_q24c_marker_present": status_has_q24c_marker,
            "status_q24d_marker_present": status_has_q24d_marker,
            "status_q24e_marker_present": status_has_q24e_marker,
            "status_q24f_marker_present": status_has_q24f_marker,
            "status_q24g_marker_present": status_has_q24g_marker,
            "status_q24h_marker_present": status_has_q24h_marker,
            "status_q24i_marker_present": status_has_q24i_marker,
            "status_q24j_marker_present": status_has_q24j_marker,
            "status_q24k_marker_present": status_has_q24k_marker,
            "status_q24l_marker_present": status_has_q24l_marker,
            "status_q24m_marker_present": status_has_q24m_marker,
            "focus_current_focus": focus.get("current_focus"),
            "focus_latest_slice": focus.get("latest_slice"),
            "state_current_gate": state.get("current_gate"),
            "state_latest_completed_slice": state.get("latest_completed_slice"),
            "allowed_room_gates": sorted(ALLOWED_ROOM_GATES),
            "allowed_room_focuses": sorted(ALLOWED_ROOM_FOCUSES),
            "allowed_room_slices": sorted(ALLOWED_ROOM_SLICES),
            "work_policy_default_method": _mapping(focus.get("work_policy")).get("default_method"),
            "handoff_exists": handoff_path.exists(),
        },
        "artifact_summary": {
            "legacy_compact_record_count": q23r_legacy.get("compact_record_count"),
            "legacy_original_record_count": q23r_legacy.get("original_record_count"),
            "manifest_record_count": q23r_manifest.get("record_count"),
            "forecast_records_line_count": q23r_sidecar.get("line_count"),
            "manifest_first_source_artifact_mode": q23r_q23e.get("source_artifact_mode"),
            "legacy_fallback_ready": q23r_q23e.get("legacy_fallback_ready"),
        },
        "safety": {
            "read_only_diagnostic": True,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "latest_manifest_written": False,
            "run_sidecars_written": False,
            "runtime_artifact_write_enabled": False,
            "scheduler_action_changed": False,
            "scheduler_enabled_by_this_tool": False,
            "trigger_added": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "approval_or_ledger_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_ps_q23r_closeout_steady_state_guard_sync()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
