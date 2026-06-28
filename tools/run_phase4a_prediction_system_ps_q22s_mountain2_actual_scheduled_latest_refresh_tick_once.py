# path: ./tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py
# desc: PS-Q22S actual Mountain2 one-tick latest refresh runner. Default no-write. Exact token required. No scheduler action replacement, trigger addition, scheduler enablement, broker, AutoTrade, ledger, or parameter apply.

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import socket
import subprocess
import sys
from typing import Any, Mapping
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement import FUTURE_MOUNTAIN2_TOKEN_CANDIDATE  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q22q_mountain2_final_readiness_no_enablement import run_final_readiness  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    REQUIRED_CONFIRMATION as Q21I_REQUIRED_CONFIRMATION,
    run_one_shot_write,
)
from tools.run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once import (  # noqa: E402
    REQUIRED_STATUS_WRITE_CONFIRMATION as Q22E_REQUIRED_CONFIRMATION,
    run_success_preserving_status_write_once,
)

RUNNER_VERSION = "prediction_warroom.mountain2_actual_scheduled_latest_refresh_tick_once.ps_q22s.v1"
LOCK_RELATIVE_PATH = Path("prediction/runtime/non_ui_scheduler_producer.lock.json")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
LOCK_STALE_AFTER_SEC = 900
Q21IRunner = Callable[..., Mapping[str, Any]]
Q22ERunner = Callable[..., Mapping[str, Any]]
ReadinessProvider = Callable[[], Mapping[str, Any]]


def _utc_now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _utc_now_dt()).astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _repo_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:  # noqa: BLE001 - status visibility only
        return {"_load_error": f"{exc.__class__.__name__}: {exc}"}


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)
    return int(path.stat().st_size)


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {"exists": True, "size_bytes": int(stat.st_size), "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}


def _false_scheduler_boundary() -> dict[str, Any]:
    return {
        "scheduler_action_replacement_executed": False,
        "scheduler_enabled": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "periodic_execution_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def _base_packet(*, run_id: str, requested_execute: bool, confirmation_ok: bool, hot_root: Path) -> dict[str, Any]:
    return {
        "ok": True,
        "runner_version": RUNNER_VERSION,
        "run_id": run_id,
        "generated_at": _iso(),
        "requested_execute_tick_once": bool(requested_execute),
        "confirmation_ok": bool(confirmation_ok),
        "required_confirmation": FUTURE_MOUNTAIN2_TOKEN_CANDIDATE,
        "hot_root": str(hot_root),
        "lock_artifact_path": str(hot_root / LOCK_RELATIVE_PATH),
        "status_artifact_path": str(hot_root / STATUS_RELATIVE_PATH),
        "default_execution_is_dry_run_no_write": True,
        **_false_scheduler_boundary(),
    }


def _lock_payload(*, run_id: str, started: datetime, reason: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "pid": None,
        "host": socket.gethostname(),
        "started_at_utc": _iso(started),
        "expires_at_utc": _iso(started + timedelta(seconds=LOCK_STALE_AFTER_SEC)),
        "reason": reason,
        "runner_version": RUNNER_VERSION,
    }


def _active_lock(lock_payload: Mapping[str, Any], *, now: datetime) -> bool:
    expires = _parse_utc(lock_payload.get("expires_at_utc"))
    started = _parse_utc(lock_payload.get("started_at_utc"))
    if expires is not None:
        return now < expires
    if started is not None:
        return (now - started).total_seconds() < LOCK_STALE_AFTER_SEC
    return True


def _acquire_lock(lock_path: Path, *, run_id: str) -> dict[str, Any]:
    now = _utc_now_dt()
    stale_lock_deleted = False
    existing_payload: dict[str, Any] = {}
    if lock_path.exists():
        existing_payload = _load_json(lock_path)
        if _active_lock(existing_payload, now=now):
            return {"acquired": False, "lock_active": True, "stale_lock_deleted": False, "existing_lock": existing_payload}
        lock_path.unlink()
        stale_lock_deleted = True
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _lock_payload(run_id=run_id, started=now, reason="mountain2_scheduled_latest_refresh_tick_once")
    try:
        with lock_path.open("x", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    except FileExistsError:
        return {"acquired": False, "lock_active": True, "stale_lock_deleted": stale_lock_deleted, "existing_lock": _load_json(lock_path)}
    return {"acquired": True, "lock_active": False, "stale_lock_deleted": stale_lock_deleted, "lock_payload": payload}


def _release_lock(lock_path: Path, *, run_id: str) -> dict[str, Any]:
    if not lock_path.exists():
        return {"released": True, "lock_missing_before_release": True}
    payload = _load_json(lock_path)
    if payload.get("run_id") != run_id:
        return {"released": False, "lock_owner_mismatch": True, "existing_lock": payload}
    lock_path.unlink()
    return {"released": True, "lock_owner_mismatch": False}


def _status_payload(*, hot_root: Path, run_id: str, state: str, blockers: list[str], warning_reasons: list[str] | None = None) -> dict[str, Any]:
    current = _load_json(hot_root / STATUS_RELATIVE_PATH)
    safe_flags = _as_mapping(current.get("safe_flags"))
    now = _iso()
    previous_count = int(current.get("consecutive_failure_count") or 0)
    is_failure = state.endswith("failed") or "failure" in state
    payload = dict(current)
    payload.update({
        "producer_version": RUNNER_VERSION,
        "producer_state": state,
        "producer_enabled": False,
        "scheduler_enabled": False,
        "last_run_started_at": now,
        "last_run_finished_at": now,
        "last_failure_at": now if is_failure else current.get("last_failure_at"),
        "last_blocker_count": len(blockers),
        "consecutive_failure_count": previous_count + 1 if is_failure else 0,
        "blockers": blockers,
        "warnings": list(warning_reasons or current.get("warnings") or []),
        "last_tick_run_id": run_id,
        "q22s_tick_note": "Mountain2 actual one-tick runner status visibility; scheduler/trigger/recurring enablement is outside PS-Q22S.",
        "safe_flags": {
            **dict(safe_flags),
            "producer_enabled_false": True,
            "scheduler_enabled_false": True,
            "scheduled_loop_enabled_false": True,
            "warroom_ui_trigger_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
        },
    })
    return payload


def _write_tick_status(*, hot_root: Path, run_id: str, state: str, blockers: list[str], warning_reasons: list[str] | None = None) -> dict[str, Any]:
    path = hot_root / STATUS_RELATIVE_PATH
    before = _file_meta(path)
    payload = _status_payload(hot_root=hot_root, run_id=run_id, state=state, blockers=blockers, warning_reasons=warning_reasons)
    size = _write_json_atomic(path, payload)
    return {"status_artifact_written": True, "status_artifact_size_bytes": size, "before_status_meta": before, "after_status_meta": _file_meta(path), "written_status_payload": payload}


def _post_refresh_q22e_design_packet(*, hot_root: Path) -> dict[str, Any]:
    """Build a Q22E-compatible design packet from the just-written Q21I success status.

    Q22S runs in the narrow interval immediately after Q21I refreshed latest/status.
    At that point Q22E's normal Q22D path can be cyclic because Q21X may still
    depend on the Q22E status marker. This recovery packet preserves the Q21I
    success fields and lets Q22E write the status-only marker without weakening
    standalone Q22E validation.
    """
    status_path = hot_root / STATUS_RELATIVE_PATH
    latest_path = hot_root / "prediction/latest_prediction_system_result.json"
    status = _load_json(status_path)
    latest_meta = _file_meta(latest_path)
    status_meta = _file_meta(status_path)
    safe_flags = _as_mapping(status.get("safe_flags"))
    now = _iso()
    proposed = dict(status)
    proposed.update({
        "producer_version": "prediction_warroom.success_preserving_producer_status_design.ps_q22d.v1",
        "producer_state": "producer_shadow_status_success_preserved_no_write_design",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "last_run_started_at": now,
        "last_run_finished_at": now,
        "last_failure_at": None,
        "last_blocker_count": 0,
        "consecutive_failure_count": 0,
        "blockers": [],
        "safe_flags": {
            **dict(safe_flags),
            "producer_enabled_false": True,
            "scheduler_enabled_false": True,
            "scheduled_loop_enabled_false": True,
            "warroom_ui_trigger_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
            "would_write_collector_state_false": True,
        },
        "q22d_design_note": "No artifact was written. Q22S post-refresh recovery preserves Q21I success fields before Q22E status-only write.",
    })
    last_success = status.get("last_success_generated_at")
    last_run_id = status.get("last_prediction_run_id")
    ready = bool(
        status.get("producer_state") == "manual_refresh_exported_status_written"
        and last_success
        and last_run_id
        and status.get("producer_enabled") is False
        and status.get("scheduler_enabled") is False
        and status.get("blockers") in ([], None)
        and latest_meta.get("exists") is True
        and status_meta.get("exists") is True
    )
    blockers: list[str] = []
    if not ready:
        blockers.append("post_refresh_q21i_success_status_required")
    return {
        "ok": True,
        "design_version": "prediction_warroom.success_preserving_producer_status_design.ps_q22d.v1",
        "read_only_no_write": True,
        "repo_status_short": _repo_status_short(),
        "design_state": "success_preserving_producer_status_design_ready_no_write" if ready else "success_preserving_producer_status_design_blocked",
        "design_blockers": blockers,
        "current_producer_state": status.get("producer_state"),
        "current_last_success_generated_at": last_success,
        "current_last_prediction_run_id": last_run_id,
        "q21x_shadow_preflight_ready_for_one_shot": None,
        "q21x_latest_status_success_observed": True if ready else False,
        "q21x_disabled_boundary_preserved": True if ready else False,
        "preserves_last_success_generated_at": bool(last_success),
        "preserves_last_prediction_run_id": bool(last_run_id),
        "preserves_last_target_file_size_bytes": True,
        "proposed_status_payload_not_written": proposed,
        "latest_meta": latest_meta,
        "status_meta": status_meta,
        "next_recommended_action": "q22s_post_refresh_q22e_status_restore" if ready else "inspect_q21i_status_before_q22e_restore",
        "safety": _false_scheduler_boundary(),
    }


def _readiness_green(packet: Mapping[str, Any]) -> bool:
    return bool(
        packet.get("readiness_state") == "mountain2_final_pre_danger_boundary_ready_no_enablement"
        and packet.get("readiness_blockers") in ([], None)
        and packet.get("runtime_readiness_blockers") in ([], None)
        and packet.get("safe_to_stop_before_danger_boundary") is True
        and packet.get("repo_status_short") == ""
    )


def run_mountain2_actual_scheduled_latest_refresh_tick_once(
    *,
    operator_acknowledged: bool = False,
    execute_tick_once: bool = False,
    confirmation: str = "",
    hot_root: Path = DEFAULT_HOT_ROOT,
    readiness_provider: ReadinessProvider | None = None,
    q21i_runner: Q21IRunner | None = None,
    q22e_runner: Q22ERunner | None = None,
    repo_status_short: str | None = None,
) -> dict[str, Any]:
    run_id = f"mountain2.tick.ps_q22s:{_iso()}:{uuid.uuid4().hex[:8]}"
    confirmation_ok = confirmation == FUTURE_MOUNTAIN2_TOKEN_CANDIDATE
    base = _base_packet(run_id=run_id, requested_execute=execute_tick_once, confirmation_ok=confirmation_ok, hot_root=hot_root)
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_tick_once:
        blockers.append("execute_tick_once_flag_required")
    if not confirmation_ok:
        blockers.append("exact_mountain2_enablement_confirmation_required")
    repo_status = _repo_status_short() if repo_status_short is None else str(repo_status_short)
    if repo_status:
        blockers.append("repo_clean_required_before_mountain2_tick")
    readiness_provider = readiness_provider or run_final_readiness
    readiness = dict(readiness_provider())
    if not _readiness_green(readiness):
        blockers.append("q22q_final_readiness_green_required")
    if blockers:
        return {**base, "tick_state": "mountain2_actual_tick_blocked_no_write", "success": False, "blocked_reasons": blockers, "repo_status_short": repo_status, "q22q_final_readiness": readiness, "lock_acquire_attempted": False, "lock_acquired": False, "latest_prediction_artifact_written": False, "status_artifact_written": False}

    lock_path = hot_root / LOCK_RELATIVE_PATH
    lock_result = _acquire_lock(lock_path, run_id=run_id)
    if lock_result.get("acquired") is not True:
        status_packet = _write_tick_status(hot_root=hot_root, run_id=run_id, state="mountain2_tick_skipped_active_lock", blockers=["active_lock_present_skip_tick"], warning_reasons=[])
        return {**base, "tick_state": "mountain2_actual_tick_skipped_active_lock", "success": False, "blocked_reasons": ["active_lock_present_skip_tick"], "q22q_final_readiness": readiness, "lock_acquire_attempted": True, "lock_acquired": False, "lock_active": True, "lock_result": lock_result, "latest_prediction_artifact_written": False, **status_packet}

    release_result: dict[str, Any] = {"released": False}
    try:
        q21i_runner = q21i_runner or run_one_shot_write
        q22e_runner = q22e_runner or run_success_preserving_status_write_once
        refresh = dict(q21i_runner(hot_root=hot_root, operator_acknowledged=True, execute_one_shot_write=True, confirmation=Q21I_REQUIRED_CONFIRMATION, require_clean_tree=True))
        if refresh.get("success") is not True or refresh.get("latest_prediction_artifact_written") is not True or refresh.get("status_artifact_written") is not True:
            status_packet = _write_tick_status(hot_root=hot_root, run_id=run_id, state="mountain2_tick_failed", blockers=["bounded_latest_refresh_failed_or_incomplete"], warning_reasons=list(refresh.get("warning_reasons") or []))
            release_result = _release_lock(lock_path, run_id=run_id)
            return {**base, "tick_state": "mountain2_actual_tick_failed", "success": False, "blocked_reasons": ["bounded_latest_refresh_failed_or_incomplete"], "q22q_final_readiness": readiness, "lock_acquire_attempted": True, "lock_acquired": True, "lock_result": lock_result, "lock_release_attempted": True, "lock_released": release_result.get("released") is True, "lock_release_result": release_result, "q21i_result": refresh, "latest_prediction_artifact_written": refresh.get("latest_prediction_artifact_written") is True, **status_packet}
        q22e_design = _post_refresh_q22e_design_packet(hot_root=hot_root)
        q22e = dict(q22e_runner(operator_acknowledged=True, execute_status_write_once=True, confirmation=Q22E_REQUIRED_CONFIRMATION, design_packet=q22e_design))
        q22e_success = q22e.get("success") is True and q22e.get("status_artifact_written") is True and q22e.get("latest_prediction_artifact_written") is False
        if not q22e_success:
            status_packet = _write_tick_status(hot_root=hot_root, run_id=run_id, state="mountain2_tick_failed", blockers=["q22e_status_visibility_restore_failed"], warning_reasons=[])
            release_result = _release_lock(lock_path, run_id=run_id)
            return {**base, "tick_state": "mountain2_actual_tick_failed", "success": False, "blocked_reasons": ["q22e_status_visibility_restore_failed"], "q22q_final_readiness": readiness, "lock_acquire_attempted": True, "lock_acquired": True, "lock_result": lock_result, "lock_release_attempted": True, "lock_released": release_result.get("released") is True, "lock_release_result": release_result, "q21i_result": refresh, "q22e_design": q22e_design, "q22e_result": q22e, "latest_prediction_artifact_written": refresh.get("latest_prediction_artifact_written") is True, **status_packet}
        release_result = _release_lock(lock_path, run_id=run_id)
        success = bool(release_result.get("released") is True)
        return {
            **base,
            "tick_state": "mountain2_actual_tick_completed_one_bounded_refresh" if success else "mountain2_actual_tick_completed_but_lock_release_failed",
            "success": success,
            "blocked_reasons": [] if success else ["lock_release_failed"],
            "q22q_final_readiness": readiness,
            "lock_acquire_attempted": True,
            "lock_acquired": True,
            "lock_result": lock_result,
            "lock_release_attempted": True,
            "lock_released": success,
            "lock_release_result": release_result,
            "q21i_result": refresh,
            "q22e_design": q22e_design,
            "q22e_result": q22e,
            "latest_prediction_artifact_written": True,
            "status_artifact_written": True,
            "bounded_manual_refresh_invoked": True,
            "actual_export_runner_invoked": True,
        }
    except Exception as exc:  # noqa: BLE001 - status visibility and lock release must be best effort
        status_packet = _write_tick_status(hot_root=hot_root, run_id=run_id, state="mountain2_tick_failed", blockers=[f"exception:{exc.__class__.__name__}"], warning_reasons=[str(exc)])
        release_result = _release_lock(lock_path, run_id=run_id)
        return {**base, "tick_state": "mountain2_actual_tick_failed", "success": False, "blocked_reasons": [f"exception:{exc.__class__.__name__}"], "exception_message": str(exc), "lock_acquire_attempted": True, "lock_acquired": True, "lock_release_attempted": True, "lock_released": release_result.get("released") is True, "lock_release_result": release_result, "latest_prediction_artifact_written": False, **status_packet}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22S actual Mountain2 one-tick latest refresh runner")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-tick-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    args = parser.parse_args(argv)
    result = run_mountain2_actual_scheduled_latest_refresh_tick_once(
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_tick_once=bool(args.execute_tick_once),
        confirmation=str(args.confirmation),
        hot_root=Path(args.hot_root),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_tick_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
