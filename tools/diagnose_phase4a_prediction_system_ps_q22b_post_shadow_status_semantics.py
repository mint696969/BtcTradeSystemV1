# path: ./tools/diagnose_phase4a_prediction_system_ps_q22b_post_shadow_status_semantics.py
# desc: PS-Q22B read-only post-Q22A status semantics diagnostic. No writes, no scheduler/trigger/broker/AutoTrade.

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
Q21ZC_RESTORE_COMMAND = [
    "python",
    ".\\tools\\run_phase4a_prediction_system_ps_q21zc_retry_after_q21zb_export_preflight_ready_once.py",
    "--operator-acknowledged",
    "--execute-retry-once",
    "--allow-retry-after-q21zb-export-preflight-ready",
    "--confirmation",
    "WRITE_D_HOT_LATEST_PREDICTION_ONCE",
]


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


def build_post_shadow_status_semantics_report(*, status_payload: Mapping[str, Any], q21x_packet: Mapping[str, Any], latest_meta: Mapping[str, Any], status_meta: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(status_payload)
    q21x = _as_mapping(q21x_packet)
    producer_state = str(status.get("producer_state") or "")
    warnings = [str(item) for item in status.get("warnings", []) if item] if isinstance(status.get("warnings"), list) else []
    blockers = [str(item) for item in status.get("blockers", []) if item] if isinstance(status.get("blockers"), list) else []
    q21x_blockers = [str(item) for item in q21x.get("shadow_preflight_blockers", []) if item] if isinstance(q21x.get("shadow_preflight_blockers"), list) else []
    q16b_scaffold_detected = bool(
        producer_state == "producer_disabled_status_ready"
        and status.get("last_success_generated_at") in (None, "")
        and status.get("last_prediction_run_id") in (None, "")
        and "latest_prediction_source_adapter_not_supplied_for_design_context" in warnings
        and "producer_status_artifact_not_supplied_yet_expected_before_warroom_status_display" in warnings
    )
    q21x_blocked_by_scaffold = bool(
        q16b_scaffold_detected
        and q21x.get("latest_prediction_non_stale") is True
        and q21x.get("latest_status_success_observed") is False
        and "latest_status_success_required_before_shadow_once" in q21x_blockers
    )
    return {
        "ok": True,
        "diagnostic": "ps_q22b_post_shadow_status_semantics_review",
        "read_only_no_write": True,
        "repo_status_short": _git_status(),
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "producer_state": producer_state,
        "status_last_success_generated_at": status.get("last_success_generated_at"),
        "status_last_prediction_run_id": status.get("last_prediction_run_id"),
        "status_runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled"),
        "status_warnings": warnings,
        "status_blockers": blockers,
        "q16b_status_scaffold_detected": q16b_scaffold_detected,
        "q21x_latest_prediction_non_stale": q21x.get("latest_prediction_non_stale") is True,
        "q21x_latest_status_success_observed": q21x.get("latest_status_success_observed") is True,
        "q21x_disabled_boundary_preserved": q21x.get("disabled_boundary_preserved") is True,
        "q21x_shadow_preflight_ready_for_one_shot": q21x.get("shadow_preflight_ready_for_one_shot") is True,
        "q21x_shadow_preflight_blockers": q21x_blockers,
        "q21x_blocked_by_q16b_scaffold_status": q21x_blocked_by_scaffold,
        "interpretation": "q22a_safely_invoked_existing_disabled_status_runner_but_q16b_status_scaffold_is_not_a_successful_prediction_producer_status" if q16b_scaffold_detected else "post_shadow_status_not_identified_as_q16b_scaffold",
        "recommended_next_action": "restore_latest_success_status_with_gated_q21zc_or_implement_success-preserving_producer_status_runner_before_any_recurring_enablement" if q16b_scaffold_detected else "inspect_post_shadow_status_manually",
        "prepared_restore_command_not_executed": Q21ZC_RESTORE_COMMAND,
        "safety": {
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    report = build_post_shadow_status_semantics_report(
        status_payload=_load(STATUS),
        q21x_packet=run_shadow_preflight(),
        latest_meta=_meta(LATEST),
        status_meta=_meta(STATUS),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
