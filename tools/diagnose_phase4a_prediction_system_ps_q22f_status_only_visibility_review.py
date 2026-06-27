# path: ./tools/diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review.py
# desc: PS-Q22F read-only review of Q22E status-only visibility semantics. No writes, no scheduler/trigger/broker/AutoTrade.

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
REVIEW_VERSION = "prediction_warroom.status_only_visibility_review.ps_q22f.v1"
Q22E_STATUS_VERSION = "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1"


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


def build_status_only_visibility_review(*, latest_meta: Mapping[str, Any], status_meta: Mapping[str, Any], status_payload: Mapping[str, Any], q21x_packet: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(status_payload)
    q21x = _as_mapping(q21x_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    repo_status = _git_status()
    if repo_status.strip():
        warnings.append("repo_dirty_q21x_shadow_ready_may_be_false_until_commit")
    if status.get("producer_version") != Q22E_STATUS_VERSION:
        blockers.append("q22e_status_version_required")
    if status.get("producer_state") != "manual_refresh_exported_status_written":
        blockers.append("q21x_success_marker_producer_state_required")
    if not status.get("last_success_generated_at"):
        blockers.append("last_success_generated_at_required")
    if not status.get("last_prediction_run_id"):
        blockers.append("last_prediction_run_id_required")
    if status.get("producer_enabled") is not False or status.get("scheduler_enabled") is not False:
        blockers.append("producer_scheduler_disabled_required")
    if status.get("blockers") not in ([], None):
        blockers.append("status_blockers_must_be_empty")
    latest_exists = latest_meta.get("exists") is True
    status_exists = status_meta.get("exists") is True
    if not latest_exists or not status_exists:
        blockers.append("latest_and_status_artifacts_required")
    status_mtime = str(status_meta.get("mtime_utc") or "")
    latest_mtime = str(latest_meta.get("mtime_utc") or "")
    status_only_observed = bool(status_exists and latest_exists and status_mtime >= latest_mtime and status.get("producer_version") == Q22E_STATUS_VERSION)
    q21x_ready_when_clean = bool(q21x.get("shadow_preflight_ready_for_one_shot") is True and q21x.get("shadow_preflight_blockers") == [])
    review_ready = bool(not blockers and (q21x_ready_when_clean or repo_status.strip()))
    return {
        "ok": True,
        "review_version": REVIEW_VERSION,
        "read_only_no_write": True,
        "repo_status_short": repo_status,
        "review_state": "q22e_status_only_visibility_review_ready_no_write" if review_ready else "q22e_status_only_visibility_review_blocked",
        "review_blockers": blockers,
        "review_warnings": warnings,
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "status_only_write_observed": status_only_observed,
        "status_producer_version": status.get("producer_version"),
        "status_producer_state": status.get("producer_state"),
        "last_success_generated_at": status.get("last_success_generated_at"),
        "last_prediction_run_id": status.get("last_prediction_run_id"),
        "last_target_file_size_bytes": status.get("last_target_file_size_bytes"),
        "preserves_q21x_success_marker": status.get("producer_state") == "manual_refresh_exported_status_written" and bool(status.get("last_success_generated_at")) and bool(status.get("last_prediction_run_id")),
        "q21x_shadow_preflight_ready_for_one_shot": q21x.get("shadow_preflight_ready_for_one_shot") is True,
        "q21x_shadow_preflight_blockers": list(q21x.get("shadow_preflight_blockers") or []),
        "q21x_latest_prediction_non_stale": q21x.get("latest_prediction_non_stale") is True,
        "q21x_latest_status_success_observed": q21x.get("latest_status_success_observed") is True,
        "q21x_disabled_boundary_preserved": q21x.get("disabled_boundary_preserved") is True,
        "next_recommended_action": "wire_future_producer_shadow_once_to_success_preserving_status_writer_no_scheduler_enablement" if review_ready else "restore_status_or_commit_review_files_before_next_step",
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
    report = build_status_only_visibility_review(
        latest_meta=_meta(LATEST),
        status_meta=_meta(STATUS),
        status_payload=_load(STATUS),
        q21x_packet=run_shadow_preflight(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
