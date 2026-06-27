# path: ./tools/diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement.py
# desc: PS-Q22M read-only Mountain2 recurring/trigger preparation preflight. No scheduler enablement, no trigger addition, no recurring execution, no latest/status write, no broker/AutoTrade.

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

from tools.design_phase4a_prediction_system_ps_q21m_scheduler_producer_policy import run_design as run_q21m_policy_design  # noqa: E402
from tools.design_phase4a_prediction_system_ps_q21n_disabled_non_ui_scheduler_producer_dry_run import run_design as run_q21n_dry_run_design  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    PS_Q21V_TOOL,
    TASK_NAME,
    TASK_PATH,
    query_disabled_scheduler_registration,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import run_shadow_preflight  # noqa: E402

HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST = HOT_ROOT / "prediction/latest_prediction_system_result.json"
STATUS = HOT_ROOT / "prediction/status/non_ui_scheduled_producer_status.json"
STATE_ROOT = HOT_ROOT / "state/collector_vnext"
PREP_VERSION = "prediction_warroom.mountain2_recurring_trigger_prep_no_enablement.ps_q22m.v1"
FUTURE_MOUNTAIN2_TOKEN_CANDIDATE = "ENABLE_RECURRING_PRODUCER_LOOP_WITH_TRIGGER_AND_ROLLBACK_PLAN"
Q22E_STATUS_VERSION = "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        return {"_load_error": f"{exc.__class__.__name__}: {exc}"}


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _generated_at(latest: Mapping[str, Any]) -> str:
    batch = _as_mapping(latest.get("forecast_batch"))
    return str(batch.get("generated_at") or latest.get("generated_at") or "")


def _collector_green_packet(state_root: Path = STATE_ROOT) -> dict[str, Any]:
    health = _load_json(state_root / "unified_health.json")
    daemon = _load_json(state_root / "unified_daemon_health.json")
    status = _load_json(state_root / "unified_status.json")
    supervisor = _load_json(state_root / "unified_supervisor_status.json")
    market = _load_json(state_root / "unified_market_state_status.json")
    ws_board = _as_mapping(status.get("ws_board_lane"))
    ws_exec = _as_mapping(status.get("ws_executions_lane"))
    ok = bool(
        supervisor.get("mode") == "RUNNING"
        and health.get("ok") is True
        and daemon.get("ok") is True
        and status.get("mode") == "RUNNING"
        and ws_board.get("ws_state") == "LIVE"
        and ws_board.get("ws_freshness") in {"LIVE", "QUIET"}
        and ws_exec.get("ws_state") == "LIVE"
        and market.get("lane_state") == "live"
        and market.get("would_send_to_broker") is False
    )
    return {
        "ok": ok,
        "supervisor_mode": supervisor.get("mode"),
        "status_mode": status.get("mode"),
        "health_ok": health.get("ok"),
        "daemon_health_ok": daemon.get("ok"),
        "ws_board_state": ws_board.get("ws_state"),
        "ws_board_freshness": ws_board.get("ws_freshness"),
        "ws_executions_state": ws_exec.get("ws_state"),
        "ws_executions_freshness": ws_exec.get("ws_freshness"),
        "market_state_lane": market.get("lane_state"),
        "market_state_last_event_ts": market.get("last_event_ts"),
        "would_send_to_broker": market.get("would_send_to_broker"),
    }


def _task_summary(query: Mapping[str, Any]) -> dict[str, Any]:
    readback = _as_mapping(query.get("task_readback"))
    action = str(readback.get("action_arguments") or "")
    return {
        "query_state": query.get("query_state"),
        "task_recognized_as_ps_q21w": query.get("task_recognized_as_ps_q21w") is True,
        "task_exists": readback.get("task_exists") is True,
        "task_name": readback.get("task_name"),
        "task_path": readback.get("task_path"),
        "task_state": readback.get("state"),
        "task_trigger_count": int(readback.get("trigger_count") or 0),
        "task_action_target": action,
        "task_action_is_q21v_dry_run": str(PS_Q21V_TOOL) in action or "run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py" in action,
        "task_readback_failures": list(query.get("task_readback_failures") or []),
    }


def build_mountain2_prep_packet(
    *,
    repo_status_short: str,
    collector_packet: Mapping[str, Any],
    latest_payload: Mapping[str, Any],
    latest_meta: Mapping[str, Any],
    status_payload: Mapping[str, Any],
    status_meta: Mapping[str, Any],
    q21x_packet: Mapping[str, Any],
    q21m_packet: Mapping[str, Any],
    q21n_packet: Mapping[str, Any],
    scheduler_query_packet: Mapping[str, Any],
) -> dict[str, Any]:
    latest = _as_mapping(latest_payload)
    status = _as_mapping(status_payload)
    q21x = _as_mapping(q21x_packet)
    q21m = _as_mapping(q21m_packet)
    q21n = _as_mapping(q21n_packet)
    task = _task_summary(scheduler_query_packet)
    generated_at = _generated_at(latest)
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short.strip():
        blockers.append("repo_clean_required_before_mountain2_prep")
    if collector_packet.get("ok") is not True:
        blockers.append("collector_green_required_before_mountain2_prep")
    if latest_meta.get("exists") is not True or status_meta.get("exists") is not True:
        blockers.append("latest_and_status_artifacts_required")
    if q21x.get("shadow_preflight_ready_for_one_shot") is not True or q21x.get("shadow_preflight_blockers") not in ([], None):
        blockers.append("q21x_ready_required_after_mountain1")
    if status.get("producer_version") != Q22E_STATUS_VERSION:
        blockers.append("mountain1_q22e_status_observation_required")
    if status.get("producer_state") != "manual_refresh_exported_status_written":
        blockers.append("producer_state_success_marker_required")
    if status.get("last_success_generated_at") != generated_at:
        blockers.append("status_last_success_generated_at_must_match_latest")
    if status.get("producer_enabled") is not False:
        blockers.append("producer_must_still_be_disabled")
    if status.get("scheduler_enabled") is not False:
        blockers.append("scheduler_must_still_be_disabled")
    if q21m.get("ready_for_disabled_dry_run_design_slice") is not True:
        blockers.append("q21m_policy_design_ready_required")
    if q21n.get("dry_run_design_ready") is not True:
        blockers.append("q21n_disabled_dry_run_design_ready_required")
    if task.get("task_recognized_as_ps_q21w") is not True:
        blockers.append("existing_disabled_scheduler_task_must_be_recognized")
    if task.get("task_state") != "Disabled":
        blockers.append("existing_scheduler_task_must_remain_disabled")
    if task.get("task_trigger_count") != 0:
        blockers.append("existing_scheduler_task_must_have_zero_triggers")
    if task.get("task_action_is_q21v_dry_run") is not True:
        blockers.append("existing_scheduler_task_action_must_still_be_q21v_dry_run")
    if status.get("runtime_artifact_write_enabled") is not True:
        warnings.append("status_runtime_artifact_write_enabled_false_or_missing")
    ready = not blockers
    return {
        "ok": True,
        "prep_version": PREP_VERSION,
        "prep_state": "mountain2_recurring_trigger_prep_ready_no_enablement" if ready else "mountain2_recurring_trigger_prep_blocked_no_enablement",
        "prep_ready_for_future_enablement_design": ready,
        "prep_blockers": blockers,
        "prep_warnings": warnings,
        "generated_at": generated_at,
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "status_producer_version": status.get("producer_version"),
        "status_producer_state": status.get("producer_state"),
        "last_success_generated_at": status.get("last_success_generated_at"),
        "last_prediction_run_id": status.get("last_prediction_run_id"),
        "repo_status_short": repo_status_short,
        "collector": dict(collector_packet),
        "q21x_ready": q21x.get("shadow_preflight_ready_for_one_shot") is True,
        "q21x_blockers": list(q21x.get("shadow_preflight_blockers") or []),
        "q21m_policy_design_state": q21m.get("policy_design_state"),
        "q21n_dry_run_design_state": q21n.get("dry_run_design_state"),
        "scheduler_task": task,
        "current_baseline": {
            "task_name": TASK_NAME,
            "task_path": TASK_PATH,
            "task_state": "Disabled",
            "task_trigger_count": 0,
            "task_action": "PS-Q21V dry-run only",
            "producer_status_q22e_observed": status.get("producer_version") == Q22E_STATUS_VERSION,
            "latest_prediction_non_stale": q21x.get("latest_prediction_non_stale") is True,
            "producer_enabled": status.get("producer_enabled") is True,
            "scheduler_enabled": status.get("scheduler_enabled") is True,
        },
        "mountain2_future_enablement_not_executed": {
            "future_token_candidate": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
            "must_stop_for_operator_before_enablement": True,
            "would_need_replace_or_add_future_task_action": True,
            "would_need_add_periodic_trigger": True,
            "would_need_enable_scheduler": True,
            "would_need_enable_latest_prediction_artifact_write_per_tick": True,
            "would_need_non_overlap_lock": True,
            "would_need_stale_lock_recovery": True,
            "would_need_failure_backoff": True,
            "would_need_rollback_disable_scheduler_and_remove_trigger": True,
            "would_need_post_enablement_observation_window": True,
        },
        "next_recommended_action": "Implement Mountain2 no-enable design/runner contract for the future scheduled latest-refresh tick. Stop before actual scheduler trigger/recurring enablement." if ready else "Resolve prep blockers, then re-run PS-Q22M no-enable preflight.",
        "read_only_no_enablement": True,
        "scheduler_enabled": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "periodic_execution_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def run_prep() -> dict[str, Any]:
    return build_mountain2_prep_packet(
        repo_status_short=_git_status_short(),
        collector_packet=_collector_green_packet(),
        latest_payload=_load_json(LATEST),
        latest_meta=_file_meta(LATEST),
        status_payload=_load_json(STATUS),
        status_meta=_file_meta(STATUS),
        q21x_packet=run_shadow_preflight(),
        q21m_packet=run_q21m_policy_design(),
        q21n_packet=run_q21n_dry_run_design(),
        scheduler_query_packet=query_disabled_scheduler_registration(),
    )


def main() -> int:
    result = run_prep()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
