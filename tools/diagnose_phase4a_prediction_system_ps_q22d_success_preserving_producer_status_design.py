# path: ./tools/diagnose_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design.py
# desc: PS-Q22D read-only success-preserving producer status design. No writes, no scheduler/trigger/broker/AutoTrade.

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

from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import run_shadow_preflight  # noqa: E402

HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST = HOT_ROOT / "prediction/latest_prediction_system_result.json"
STATUS = HOT_ROOT / "prediction/status/non_ui_scheduled_producer_status.json"
DESIGN_VERSION = "prediction_warroom.success_preserving_producer_status_design.ps_q22d.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def _meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _git_status() -> str:
    return subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False).stdout.strip()


def _copy_safe_flags(status: Mapping[str, Any]) -> dict[str, Any]:
    safe = status.get("safe_flags") if isinstance(status.get("safe_flags"), Mapping) else {}
    out = dict(safe)
    for key in (
        "producer_enabled_false",
        "scheduler_enabled_false",
        "scheduled_loop_enabled_false",
        "warroom_ui_trigger_false",
        "autotrade_trigger_allowed_false",
        "broker_private_api_allowed_false",
        "would_send_to_broker_false",
        "would_write_collector_state_false",
    ):
        out[key] = True
    return out


def build_success_preserving_status_design(*, latest_meta: Mapping[str, Any], status_payload: Mapping[str, Any], status_meta: Mapping[str, Any], q21x_packet: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(status_payload)
    q21x = _as_mapping(q21x_packet)
    blockers: list[str] = []
    if q21x.get("latest_status_success_observed") is not True:
        blockers.append("current_latest_status_success_required")
    if q21x.get("disabled_boundary_preserved") is not True:
        blockers.append("current_disabled_boundary_preserved_required")
    if q21x.get("shadow_preflight_ready_for_one_shot") is not True:
        blockers.append("current_q21x_shadow_ready_required")
    if status.get("producer_state") != "manual_refresh_exported_status_written":
        blockers.append("manual_refresh_exported_status_required")
    if not status.get("last_success_generated_at"):
        blockers.append("last_success_generated_at_required")
    if not status.get("last_prediction_run_id"):
        blockers.append("last_prediction_run_id_required")
    if latest_meta.get("exists") is not True or status_meta.get("exists") is not True:
        blockers.append("latest_and_status_artifacts_required")
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    proposed = dict(status)
    proposed.update({
        "producer_version": "prediction_warroom.success_preserving_producer_status_design.ps_q22d.v1",
        "producer_state": "producer_shadow_status_success_preserved_no_write_design",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": bool(status.get("runtime_artifact_write_enabled") is True),
        "last_run_started_at": now,
        "last_run_finished_at": now,
        "last_success_at": status.get("last_success_at"),
        "last_failure_at": None,
        "last_success_generated_at": status.get("last_success_generated_at"),
        "last_prediction_run_id": status.get("last_prediction_run_id"),
        "last_target_file_size_bytes": status.get("last_target_file_size_bytes") or latest_meta.get("size_bytes"),
        "last_warning_count": int(status.get("last_warning_count") or len(status.get("warnings") if isinstance(status.get("warnings"), list) else [])),
        "last_blocker_count": 0,
        "consecutive_failure_count": 0,
        "safe_flags": _copy_safe_flags(status),
        "blockers": [],
        "disable_rollback_state": "success_preserving_shadow_status_design_no_scheduler_no_trigger_no_latest_write",
        "q22d_design_note": "No artifact was written. Future status-only producer must preserve last_success_generated_at and last_prediction_run_id.",
    })
    preserves = bool(
        not blockers
        and proposed.get("last_success_generated_at") == status.get("last_success_generated_at")
        and proposed.get("last_prediction_run_id") == status.get("last_prediction_run_id")
        and proposed.get("producer_enabled") is False
        and proposed.get("scheduler_enabled") is False
        and proposed.get("blockers") == []
    )
    return {
        "ok": True,
        "design_version": DESIGN_VERSION,
        "read_only_no_write": True,
        "repo_status_short": _git_status(),
        "design_state": "success_preserving_producer_status_design_ready_no_write" if preserves else "success_preserving_producer_status_design_blocked",
        "design_blockers": blockers,
        "current_producer_state": status.get("producer_state"),
        "current_last_success_generated_at": status.get("last_success_generated_at"),
        "current_last_prediction_run_id": status.get("last_prediction_run_id"),
        "q21x_shadow_preflight_ready_for_one_shot": q21x.get("shadow_preflight_ready_for_one_shot") is True,
        "q21x_latest_status_success_observed": q21x.get("latest_status_success_observed") is True,
        "q21x_disabled_boundary_preserved": q21x.get("disabled_boundary_preserved") is True,
        "preserves_last_success_generated_at": proposed.get("last_success_generated_at") == status.get("last_success_generated_at") and bool(status.get("last_success_generated_at")),
        "preserves_last_prediction_run_id": proposed.get("last_prediction_run_id") == status.get("last_prediction_run_id") and bool(status.get("last_prediction_run_id")),
        "preserves_last_target_file_size_bytes": proposed.get("last_target_file_size_bytes") == (status.get("last_target_file_size_bytes") or latest_meta.get("size_bytes")),
        "proposed_status_payload_not_written": proposed,
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "next_recommended_action": "implement_exact_token_success_preserving_status_write_wrapper_after_no_write_design_review" if preserves else "restore_manual_success_status_before_design_review",
        "safety": {
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "warroom_ui_trigger_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
            "would_write_collector_state": False,
        },
    }


def main() -> int:
    report = build_success_preserving_status_design(
        latest_meta=_meta(LATEST),
        status_payload=_load(STATUS),
        status_meta=_meta(STATUS),
        q21x_packet=run_shadow_preflight(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
