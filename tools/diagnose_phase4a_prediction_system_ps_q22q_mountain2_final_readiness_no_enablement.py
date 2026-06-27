# path: ./tools/diagnose_phase4a_prediction_system_ps_q22q_mountain2_final_readiness_no_enablement.py
# desc: PS-Q22Q final no-enable Mountain2 readiness / danger-boundary review. Aggregates PS-Q22M/N/O/P and executes no scheduler/trigger/recurring/runtime write.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import (  # noqa: E402
    FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
    run_prep as run_q22m_prep,
)
from tools.design_phase4a_prediction_system_ps_q22n_mountain2_scheduled_tick_contract_no_enablement import run_contract as run_q22n_contract  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22o_mountain2_scheduled_latest_refresh_tick_once import run_mountain2_tick_runner_skeleton  # noqa: E402
from tools.design_phase4a_prediction_system_ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement import run_contract as run_q22p_contract  # noqa: E402

READINESS_VERSION = "prediction_warroom.mountain2_final_readiness_no_enablement.ps_q22q.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def build_final_readiness_packet(
    *,
    repo_status_short: str,
    q22m_packet: Mapping[str, Any],
    q22n_packet: Mapping[str, Any],
    q22o_packet: Mapping[str, Any],
    q22p_packet: Mapping[str, Any],
) -> dict[str, Any]:
    q22m = _as_mapping(q22m_packet)
    q22n = _as_mapping(q22n_packet)
    q22o = _as_mapping(q22o_packet)
    q22p = _as_mapping(q22p_packet)
    blockers: list[str] = []
    runtime_blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_final_readiness")
    if q22m.get("prep_ready_for_future_enablement_design") is not True:
        runtime_blockers.append("q22m_prep_not_ready")
    if q22n.get("contract_ready_for_future_no_enable_runner_skeleton") is not True:
        runtime_blockers.append("q22n_tick_contract_not_runtime_ready")
    if q22o.get("runner_ready_for_future_danger_boundary_review") is not True:
        runtime_blockers.append("q22o_tick_skeleton_not_ready")
    if q22p.get("contract_ready_for_future_enablement_review") is not True:
        runtime_blockers.append("q22p_failure_backoff_contract_not_ready")
    for label, packet in (("q22m", q22m), ("q22n", q22n), ("q22o", q22o), ("q22p", q22p)):
        if packet.get("scheduler_enabled") is not False or packet.get("trigger_added") is not False:
            blockers.append(f"{label}_must_preserve_no_scheduler_no_trigger")
        if packet.get("recurring_enablement_allowed_now") is not False:
            blockers.append(f"{label}_must_not_allow_recurring_now")
        if packet.get("latest_prediction_artifact_written") is not False or packet.get("status_artifact_written") is not False:
            blockers.append(f"{label}_must_preserve_no_runtime_writes")
        if packet.get("would_send_to_broker") is not False:
            blockers.append(f"{label}_must_preserve_no_broker_send")
    if runtime_blockers:
        warnings.append("runtime_not_ready_yet_most_likely_latest_freshness_or_clean_tree_observation")
    safe_to_stop_before_danger = not blockers
    return {
        "ok": True,
        "readiness_version": READINESS_VERSION,
        "readiness_state": "mountain2_final_pre_danger_boundary_ready_no_enablement" if safe_to_stop_before_danger else "mountain2_final_pre_danger_boundary_blocked_no_enablement",
        "safe_to_stop_before_danger_boundary": safe_to_stop_before_danger,
        "ready_to_execute_mountain2_now": False,
        "must_stop_before_actual_mountain2": True,
        "operator_confirmation_required_before_actual_mountain2": True,
        "generated_at": _utc_now(),
        "repo_status_short": repo_status_short,
        "readiness_blockers": blockers,
        "runtime_readiness_blockers": runtime_blockers,
        "readiness_warnings": warnings,
        "q22m_prep_state": q22m.get("prep_state"),
        "q22m_blockers": list(q22m.get("prep_blockers") or []),
        "q22n_contract_state": q22n.get("contract_state"),
        "q22n_blockers": list(q22n.get("contract_blockers") or []),
        "q22o_runner_state": q22o.get("runner_state"),
        "q22o_blocked_reasons": list(q22o.get("blocked_reasons") or []),
        "q22p_contract_state": q22p.get("contract_state"),
        "q22p_blockers": list(q22p.get("contract_blockers") or []),
        "dangerous_operations_not_executed": {
            "scheduler_action_replacement": False,
            "periodic_trigger_addition": False,
            "scheduler_enablement": False,
            "recurring_or_periodic_execution": False,
            "per_tick_latest_prediction_artifact_write_enablement": False,
            "per_tick_lock_acquire_enablement": False,
            "rollback_execution_against_scheduler": False,
        },
        "future_enablement_token_candidate": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "future_enablement_token_used": False,
        "next_human_stop_message": "Actual Mountain2 begins at scheduler action replacement / trigger addition / scheduler enablement / recurring execution. Stop here and ask operator before those steps.",
        "read_only_review_only": True,
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "periodic_execution_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "lock_file_created": False,
        "lock_file_written": False,
        "lock_acquire_attempted": False,
        "rollback_executed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def run_final_readiness() -> dict[str, Any]:
    return build_final_readiness_packet(
        repo_status_short=_git_status_short(),
        q22m_packet=run_q22m_prep(),
        q22n_packet=run_q22n_contract(),
        q22o_packet=run_mountain2_tick_runner_skeleton(),
        q22p_packet=run_q22p_contract(),
    )


def main() -> int:
    result = run_final_readiness()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
