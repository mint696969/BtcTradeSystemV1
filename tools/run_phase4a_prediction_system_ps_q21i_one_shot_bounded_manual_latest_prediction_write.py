# path: ./tools/run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write.py
# desc: PS-Q21I explicitly gated one-shot bounded manual latest prediction artifact write. Writes only D-hot prediction/latest_prediction_system_result.json and producer status when all CLI gates and clean-tree checks pass; no scheduler/producer/UI trigger/AutoTrade/broker.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
    build_prediction_warroom_bounded_manual_refresh_runner,
)

RUNNER_VERSION = "prediction_warroom.one_shot_bounded_manual_latest_prediction_write.ps_q21i.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
REQUIRED_CONFIRMATION = "WRITE_D_HOT_LATEST_PREDICTION_ONCE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _hot_root_ok(root: Path) -> bool:
    return str(root).rstrip("\\/").lower().replace("/", "\\") == r"d:\btc_ts_hot"


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return proc.stdout.strip()


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def summarize_one_shot_write_packet(*, packet: Mapping[str, Any] | Any, before_latest_meta: Mapping[str, Any], before_status_meta: Mapping[str, Any], after_latest_meta: Mapping[str, Any], after_status_meta: Mapping[str, Any], git_status_before: str, requested_execute: bool) -> dict[str, Any]:
    data = _as_mapping(packet)
    status_payload = _as_mapping(data.get("status_payload"))
    safe_flags = _as_mapping(status_payload.get("safe_flags"))
    blockers = [str(item) for item in data.get("blocked_reasons", []) if item] if isinstance(data.get("blocked_reasons"), list | tuple) else []
    warnings = [str(item) for item in data.get("warning_reasons", []) if item] if isinstance(data.get("warning_reasons"), list | tuple) else []
    latest_written = data.get("latest_prediction_artifact_written") is True
    status_written = data.get("status_artifact_written") is True
    success = bool(latest_written and status_written and not blockers)
    return {
        "ok": True,
        "runner_version": RUNNER_VERSION,
        "bounded_manual_refresh_runner_version": PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
        "runner_state": str(data.get("runner_state") or ""),
        "success": success,
        "requested_execute_one_shot_write": bool(requested_execute),
        "git_status_before_clean": git_status_before == "",
        "latest_prediction_artifact_written": latest_written,
        "status_artifact_written": status_written,
        "latest_prediction_artifact_path": str(data.get("latest_prediction_artifact_path") or ""),
        "status_artifact_path": str(data.get("status_artifact_path") or ""),
        "before_latest_meta": dict(before_latest_meta),
        "after_latest_meta": dict(after_latest_meta),
        "before_status_meta": dict(before_status_meta),
        "after_status_meta": dict(after_status_meta),
        "prediction_run_id": str(data.get("prediction_run_id") or ""),
        "generated_at": str(data.get("generated_at") or ""),
        "exported_at": str(data.get("exported_at") or ""),
        "latest_prediction_artifact_size_bytes": data.get("latest_prediction_artifact_size_bytes"),
        "status_artifact_size_bytes": data.get("status_artifact_size_bytes"),
        "blocker_count": int(data.get("blocker_count") or len(blockers)),
        "warning_count": int(data.get("warning_count") or len(warnings)),
        "blocked_reasons": blockers,
        "warning_reasons": warnings,
        "producer_state": str(status_payload.get("producer_state") or ""),
        "producer_enabled": status_payload.get("producer_enabled") is True,
        "scheduler_enabled": status_payload.get("scheduler_enabled") is True,
        "runtime_artifact_write_enabled": status_payload.get("runtime_artifact_write_enabled") is True,
        "safe_flags": dict(safe_flags),
        "one_shot_manual_write_only": True,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "scheduled_loop_enabled": False,
        "warroom_ui_trigger_allowed": False,
        "ui_triggered_runner_execution": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def build_blocked_packet(*, reasons: list[str], hot_root: Path, requested_execute: bool, git_status_before: str = "") -> dict[str, Any]:
    return summarize_one_shot_write_packet(
        packet={
            "runner_state": "ps_q21i_one_shot_write_blocked_before_runner",
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "latest_prediction_artifact_path": str(hot_root / LATEST_RELATIVE_PATH),
            "status_artifact_path": str(hot_root / STATUS_RELATIVE_PATH),
            "blocker_count": len(reasons),
            "blocked_reasons": reasons,
            "warning_count": 0,
            "warning_reasons": [],
            "status_payload": {"producer_enabled": False, "scheduler_enabled": False, "runtime_artifact_write_enabled": False, "safe_flags": {}},
        },
        before_latest_meta=_file_meta(hot_root / LATEST_RELATIVE_PATH),
        before_status_meta=_file_meta(hot_root / STATUS_RELATIVE_PATH),
        after_latest_meta=_file_meta(hot_root / LATEST_RELATIVE_PATH),
        after_status_meta=_file_meta(hot_root / STATUS_RELATIVE_PATH),
        git_status_before=git_status_before,
        requested_execute=requested_execute,
    )


def run_one_shot_write(*, hot_root: Path, operator_acknowledged: bool, execute_one_shot_write: bool, confirmation: str, require_clean_tree: bool = True) -> dict[str, Any]:
    git_status = _git_status_short() if require_clean_tree else ""
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_one_shot_write:
        blockers.append("execute_one_shot_write_required")
    if confirmation != REQUIRED_CONFIRMATION:
        blockers.append("confirmation_token_required")
    if not _hot_root_ok(hot_root):
        blockers.append("hot_root_must_be_D_btc_ts_hot")
    if require_clean_tree and git_status:
        blockers.append("working_tree_must_be_clean_before_one_shot_write")
    if blockers:
        return build_blocked_packet(reasons=blockers, hot_root=hot_root, requested_execute=execute_one_shot_write, git_status_before=git_status)
    latest = hot_root / LATEST_RELATIVE_PATH
    status = hot_root / STATUS_RELATIVE_PATH
    before_latest = _file_meta(latest)
    before_status = _file_meta(status)
    packet = build_prediction_warroom_bounded_manual_refresh_runner(
        hot_latest_root_hint=str(hot_root),
        operator_acknowledged=True,
        execute_manual_refresh=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_export_preflight=True,
        allow_latest_payload_export=True,
        allow_runtime_artifact_write=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=False,
        request_scheduler_enable=False,
        request_warroom_ui_trigger=False,
        request_parameter_apply=False,
        request_parameter_staging_write=False,
        request_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()
    after_latest = _file_meta(latest)
    after_status = _file_meta(status)
    result = summarize_one_shot_write_packet(
        packet=packet,
        before_latest_meta=before_latest,
        before_status_meta=before_status,
        after_latest_meta=after_latest,
        after_status_meta=after_status,
        git_status_before=git_status,
        requested_execute=execute_one_shot_write,
    )
    result["finished_at_utc"] = _utc_now()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q21I one-shot bounded manual latest prediction write")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-one-shot-write", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--allow-dirty-tree", action="store_true", help="diagnostic escape hatch; do not use for live one-shot write")
    args = parser.parse_args(argv)
    result = run_one_shot_write(
        hot_root=Path(args.hot_root),
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_one_shot_write=bool(args.execute_one_shot_write),
        confirmation=str(args.confirmation),
        require_clean_tree=not bool(args.allow_dirty_tree),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_one_shot_write) else 1


if __name__ == "__main__":
    raise SystemExit(main())
