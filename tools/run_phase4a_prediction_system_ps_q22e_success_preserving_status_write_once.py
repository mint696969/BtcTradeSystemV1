# path: ./tools/run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once.py
# desc: PS-Q22E exact-token success-preserving D-hot status-only write wrapper. Default no-write; no latest write/scheduler/trigger/broker/AutoTrade.

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design import (  # noqa: E402
    HOT_ROOT,
    LATEST,
    STATUS,
    _load,
    _meta,
    build_success_preserving_status_design,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import run_shadow_preflight  # noqa: E402

WRITE_VERSION = "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1"
REQUIRED_STATUS_WRITE_CONFIRMATION = "WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE"
StatusWriter = Callable[[Path, Mapping[str, Any]], int]


def _repo_clean() -> bool:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip() == ""


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _write_json_atomic(target: Path, payload: Mapping[str, Any]) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    body = json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(target)
    return int(target.stat().st_size)


def _false_boundary() -> dict[str, Any]:
    return {
        "latest_prediction_artifact_written": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "scheduled_loop_enabled": False,
        "scheduler_enabled": False,
        "scheduler_enablement_allowed_now": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def build_current_design() -> dict[str, Any]:
    return build_success_preserving_status_design(
        latest_meta=_meta(LATEST),
        status_payload=_load(STATUS),
        status_meta=_meta(STATUS),
        q21x_packet=run_shadow_preflight(),
    )


def _q21x_compatible_payload(design: Mapping[str, Any]) -> dict[str, Any]:
    proposed = design.get("proposed_status_payload_not_written") if isinstance(design.get("proposed_status_payload_not_written"), Mapping) else {}
    payload = dict(proposed)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload.update({
        "producer_version": WRITE_VERSION,
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "last_run_started_at": now,
        "last_run_finished_at": now,
        "last_failure_at": None,
        "last_blocker_count": 0,
        "consecutive_failure_count": 0,
        "blockers": [],
        "disable_rollback_state": "success_preserving_status_write_once_no_scheduler_no_trigger_no_latest_write",
        "q22e_write_note": "Q21X-compatible status-only write; preserves latest success fields and does not write latest prediction.",
    })
    return payload


def run_success_preserving_status_write_once(
    *,
    operator_acknowledged: bool = False,
    execute_status_write_once: bool = False,
    confirmation: str = "",
    design_packet: Mapping[str, Any] | None = None,
    status_writer: StatusWriter | None = None,
    repo_clean: bool | None = None,
    status_path: Path | None = None,
) -> dict[str, Any]:
    design = dict(design_packet) if design_packet is not None else build_current_design()
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_status_write_once:
        blockers.append("execute_status_write_once_flag_required")
    if confirmation != REQUIRED_STATUS_WRITE_CONFIRMATION:
        blockers.append("exact_status_write_confirmation_token_required")
    repo_is_clean = _repo_clean() if repo_clean is None else bool(repo_clean)
    if not repo_is_clean:
        blockers.append("repo_clean_required_before_status_write_once")
    if design.get("design_state") != "success_preserving_producer_status_design_ready_no_write":
        blockers.append("q22d_design_ready_required")
    if design.get("design_blockers") not in ([], None):
        blockers.append("q22d_design_blockers_must_be_empty")
    if design.get("preserves_last_success_generated_at") is not True:
        blockers.append("last_success_generated_at_preservation_required")
    if design.get("preserves_last_prediction_run_id") is not True:
        blockers.append("last_prediction_run_id_preservation_required")
    if blockers:
        return {
            "ok": True,
            "write_version": WRITE_VERSION,
            "write_state": "success_preserving_status_write_blocked_no_write",
            "success": False,
            "blocked_reasons": blockers,
            "q22d_design": design,
            "status_artifact_written": False,
            "status_write_invoked": False,
            "required_status_write_confirmation": REQUIRED_STATUS_WRITE_CONFIRMATION,
            **_false_boundary(),
        }
    target = status_path or STATUS
    before = _file_meta(target)
    payload = _q21x_compatible_payload(design)
    writer = status_writer or _write_json_atomic
    size = writer(target, payload)
    after = _file_meta(target)
    success = bool(size and payload.get("producer_state") == "manual_refresh_exported_status_written" and payload.get("last_success_generated_at") and payload.get("last_prediction_run_id"))
    return {
        "ok": True,
        "write_version": WRITE_VERSION,
        "write_state": "success_preserving_status_written_once" if success else "success_preserving_status_write_failed_or_incomplete",
        "success": success,
        "blocked_reasons": [],
        "q22d_design": design,
        "status_artifact_written": bool(success),
        "status_write_invoked": True,
        "status_artifact_path": str(target),
        "status_artifact_size_bytes": int(size or 0),
        "before_status_meta": before,
        "after_status_meta": after,
        "written_status_payload": payload,
        "required_status_write_confirmation": REQUIRED_STATUS_WRITE_CONFIRMATION,
        **_false_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22E success-preserving status-only write once")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-status-write-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_success_preserving_status_write_once(
        operator_acknowledged=args.operator_acknowledged,
        execute_status_write_once=args.execute_status_write_once,
        confirmation=args.confirmation,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_status_write_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
