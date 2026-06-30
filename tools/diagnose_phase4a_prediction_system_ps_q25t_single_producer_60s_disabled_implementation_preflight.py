# path: ./tools/diagnose_phase4a_prediction_system_ps_q25t_single_producer_60s_disabled_implementation_preflight.py
# desc: Read-only diagnostic for PS-Q25T single producer 60s disabled implementation preflight.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25t_single_producer_60s_disabled_implementation_preflight.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25T_SINGLE_PRODUCER_60S_DISABLED_IMPLEMENTATION_PREFLIGHT_2026-06-30.md"
Q25S_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25S_WARROOM_PREDICTION_SINGLE_PRODUCER_60S_IMPLEMENTATION_PLANNING_2026-06-30.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"
RUNNER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py"
MANUAL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py"
WRAPPER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py"
CHECKER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py"
PLAN = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py"
STATUS_PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py"

SELECTED = "single_producer_60s_candidate"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_single_producer_60s_disabled_implementation_preflight_diagnostic() -> dict:
    doc_text = _read(DOC)
    q25s_text = _read(Q25S_DOC)
    contract_text = _read(CONTRACT)
    runner_text = _read(RUNNER)
    manual_text = _read(MANUAL)
    wrapper_text = _read(WRAPPER)
    checker_text = _read(CHECKER)
    plan_text = _read(PLAN)
    status_panel_text = _read(STATUS_PANEL)
    blockers: list[str] = []
    for marker in (
        "ps_q25t_single_producer_60s_disabled_implementation_preflight=true",
        f"selected_option_id={SELECTED}",
        "selected_target_cadence_sec=60",
        "disabled_implementation_preflight_added=true",
        "preflight_only=true",
        "structural_candidate_mapping_added=true",
        "implementation_allowed_by_this_packet=false",
        "production_code_changed=false",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "scheduler_enabled=false",
        "manual_one_shot_run_allowed=false",
        "scheduler_enablement_allowed=false",
        "broker_private_api_allowed=false",
        "future_disabled_runner_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py",
        "future_bounded_manual_refresh_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py",
        "future_disabled_scheduler_wrapper_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
        "future_disabled_once_run_checker_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py",
        "future_guarded_once_run_plan_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "ps_q25s_warroom_prediction_single_producer_60s_implementation_planning=true",
        f"selected_option_id={SELECTED}",
        "selected_target_cadence_sec=60",
        "implementation_planning_only=true",
        "implementation_allowed_by_this_packet=false",
        "requires_next_slice_for_disabled_implementation_preflight=true",
        "production_code_changed=false",
    ):
        if marker not in q25s_text:
            blockers.append(f"q25s_marker_required:{marker}")
    source_expectations = (
        (CONTRACT, contract_text, ("MINIMUM_CADENCE_SEC = 60", "RECOMMENDED_CADENCE_SEC = 300", "PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH", "LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH")),
        (RUNNER, runner_text, ("PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION", "producer_enabled", "scheduler_enabled", "runtime_artifact_write_enabled", "latest_prediction_artifact_write_enabled", "ready_for_scheduler_enablement")),
        (MANUAL, manual_text, ("PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION", "bounded_manual_run_only", "allow_runtime_artifact_write", "allow_status_artifact_write", "ready_for_scheduler_enablement")),
        (WRAPPER, wrapper_text, ("DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION", "overlap_policy=never_overlap_runs", "lock_relative_path=prediction/status/non_ui_scheduled_producer.lock", "manual_refresh_invoked_by_this_skeleton")),
        (CHECKER, checker_text, ("DISABLED_ONCE_RUN_CHECKER_VERSION", "ps_q16f_preflight_report_required", "would_skip_due_to_existing_lock", "ready_for_future_disabled_once_run_checker_implementation")),
        (PLAN, plan_text, ("GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION", "future_step_04_check_lock_absent_before_start", "future_step_10_do_not_register_scheduler_or_enable_loop", "future_step_11_do_not_trigger_warroom_ui_autotrade_broker_ledger_or_parameters")),
        (STATUS_PANEL, status_panel_text, ("PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION", "producer_runner_invoked", "scheduler_enabled_by_this_panel", "would_write_status_artifact")),
    )
    for path, text, markers in source_expectations:
        if not path.exists():
            blockers.append(f"source_missing:{path.relative_to(REPO_ROOT)}")
            continue
        for marker in markers:
            if marker not in text:
                blockers.append(f"source_marker_required:{path.relative_to(REPO_ROOT)}:{marker}")
    packet = {
        "single_producer_60s_disabled_preflight_version": "prediction_warroom.single_producer_60s_disabled_implementation_preflight.ps_q25t.v1",
        "selected_option_id": SELECTED,
        "selected_target_cadence_sec": 60,
        "disabled_implementation_preflight_added": True,
        "preflight_only": True,
        "structural_candidate_mapping_added": True,
        "source_candidate_count": 7,
        "future_disabled_runner_candidate": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py",
        "future_bounded_manual_refresh_candidate": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py",
        "future_disabled_scheduler_wrapper_candidate": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
        "future_disabled_once_run_checker_candidate": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py",
        "future_guarded_once_run_plan_candidate": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py",
        "future_status_panel_observer_candidate": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py",
        "required_future_shape": {
            "default_enabled": False,
            "scheduler_enabled_initially": False,
            "producer_enabled_initially": False,
            "runtime_artifact_write_initially": False,
            "status_artifact_write_initially": False,
            "latest_prediction_artifact_write_initially": False,
            "warroom_ui_trigger": False,
            "no_overlap_runs": True,
            "single_run_lock_required": True,
            "on_existing_lock": "skip_and_report_status",
            "status_visibility_required_before_enablement": True,
            "rollback_disable_path_required": True,
            "manual_one_shot_requires_separate_gate": True,
            "scheduler_enablement_requires_separate_gate": True,
        },
        "implementation_allowed_by_this_packet": False,
        "manual_one_shot_run_allowed": False,
        "scheduler_enablement_allowed": False,
        "production_code_changed": False,
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
            "implementation_allowed_by_this_packet",
            "manual_one_shot_run_allowed",
            "scheduler_enablement_allowed",
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
    result = run_single_producer_60s_disabled_implementation_preflight_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
