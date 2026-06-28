# path: ./tools/run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once.py
# desc: PS-Q23M gated legacy latest shrink executor. Default is blocked no-write; actual D-hot legacy latest replacement requires explicit confirmation.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    DEFAULT_MAX_RECORDS_PER_HORIZON,
    DEFAULT_SELECTED_HORIZON_SEC,
    LATEST_MANIFEST_RELATIVE_PATH,
    build_latest_prediction_warroom_read_model,
    load_latest_prediction_payload_status_manifest_first,
)
from tools.diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write import run_legacy_latest_shrink_readiness_no_write  # noqa: E402

RUNNER_VERSION = "prediction_warroom.gated_legacy_latest_shrink.ps_q23m.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
LEGACY_LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
BACKUP_ROOT_RELATIVE_PATH = Path("prediction/backups/legacy_latest_shrink")
REQUIRED_CONFIRMATION = "SHRINK_D_HOT_LEGACY_LATEST_TO_COMPACT_READ_MODEL_COMPAT_ONCE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")


def _sha256_prefix_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _file_sha256_prefix(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()[:16]


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "sha256_prefix": "", "mtime_utc": ""}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "sha256_prefix": _file_sha256_prefix(path),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _hot_root_ok(root: Path) -> bool:
    return str(root).rstrip("\\/").lower().replace("/", "\\") == r"d:\btc_ts_hot"


def _backup_relative_path(now_utc: str) -> Path:
    safe = now_utc.replace(":", "").replace("-", "").replace("Z", "Z")
    day = now_utc[:10]
    return BACKUP_ROOT_RELATIVE_PATH / day / f"latest_prediction_system_result.before_ps_q23m_{safe}.json"


def build_compact_legacy_latest_payload(*, distributed_payload: Mapping[str, Any], now_utc: str | None = None) -> dict[str, Any]:
    """Build a compact but existing read-model-compatible legacy latest payload."""
    payload = _as_mapping(distributed_payload)
    batch = _as_mapping(payload.get("forecast_batch"))
    records = _as_list(batch.get("records"))
    generated_at = _clean(batch.get("generated_at") or payload.get("generated_at"))
    read_model = build_latest_prediction_warroom_read_model(
        payload=payload,
        market_state={},
        market_diag={},
        now_utc=now_utc,
        source_path="distributed_manifest_compaction_source",
        selected_horizon_sec=DEFAULT_SELECTED_HORIZON_SEC,
        max_records_per_horizon=DEFAULT_MAX_RECORDS_PER_HORIZON,
    )
    selected_records: list[dict[str, Any]] = []
    selected_by_horizon = _as_mapping(read_model.get("selected_records_by_horizon"))
    for horizon in [str(item) for item in read_model.get("selected_horizon_sec") or []]:
        for row in _as_list(selected_by_horizon.get(horizon)):
            item = dict(_as_mapping(row))
            if not item:
                continue
            item["generated_at"] = item.get("generated_at") or generated_at
            item["read_only"] = True
            item["non_executing"] = True
            item["would_send_to_broker"] = False
            item["would_write_runtime_artifact"] = False
            item["would_append_ledger"] = False
            selected_records.append(item)
    compact_payload = {
        "generated_at": generated_at,
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "legacy_latest_shrunk_by": RUNNER_VERSION,
        "legacy_latest_shrink_mode": "read_model_compatible_selected_records",
        "source_artifact_mode": "distributed_manifest_to_compact_legacy_latest",
        "source_manifest_relative_path": LATEST_MANIFEST_RELATIVE_PATH,
        "original_record_count": len(records),
        "compact_record_count": len(selected_records),
        "forecast_batch": {
            "generated_at": generated_at,
            "read_only": True,
            "non_executing": True,
            "family_count": batch.get("family_count"),
            "horizon_count": batch.get("horizon_count"),
            "record_count": len(selected_records),
            "records": selected_records,
        },
    }
    return compact_payload


def summarize_compact_candidate(*, hot_root: Path, now_utc: str | None = None) -> dict[str, Any]:
    payload_status = load_latest_prediction_payload_status_manifest_first(hot_latest_root_hint=hot_root, prefer_distributed=True)
    selected_payload = _as_mapping(payload_status.get("payload"))
    compact = build_compact_legacy_latest_payload(distributed_payload=selected_payload, now_utc=now_utc) if selected_payload else {}
    compact_bytes = _json_bytes(compact) if compact else b""
    read_model = build_latest_prediction_warroom_read_model(
        payload=compact,
        market_state={},
        market_diag={},
        now_utc=now_utc,
        source_path="compact_legacy_latest_candidate",
    ) if compact else {"ok": False, "blocker_reason_codes": ["compact_payload_not_built"]}
    legacy_path = hot_root / LEGACY_LATEST_RELATIVE_PATH
    legacy_meta = _file_meta(legacy_path)
    before_size = int(legacy_meta.get("size_bytes") or 0)
    after_size = len(compact_bytes)
    shrink_bytes = max(0, before_size - after_size)
    shrink_ratio = (after_size / before_size) if before_size > 0 else None
    return {
        "payload_status_ok": payload_status.get("ok") is True,
        "source_artifact_mode": payload_status.get("source_artifact_mode"),
        "source_artifact_relative_path": payload_status.get("source_artifact_relative_path"),
        "distributed_reader_ready": payload_status.get("distributed_reader_ready") is True,
        "distributed_stale_vs_legacy": payload_status.get("distributed_stale_vs_legacy") is True,
        "legacy_fallback_ready_before_shrink": payload_status.get("legacy_fallback_ready") is True,
        "legacy_latest_meta_before": legacy_meta,
        "candidate_compact_payload": compact,
        "candidate_compact_payload_size_bytes": after_size,
        "candidate_compact_payload_sha256_prefix": _sha256_prefix_bytes(compact_bytes) if compact_bytes else "",
        "candidate_read_model_ok": read_model.get("ok") is True,
        "candidate_read_model_record_count": read_model.get("record_count"),
        "candidate_read_model_blockers": list(read_model.get("blocker_reason_codes") or []),
        "original_record_count": compact.get("original_record_count") if compact else 0,
        "compact_record_count": compact.get("compact_record_count") if compact else 0,
        "estimated_before_size_bytes": before_size,
        "estimated_after_size_bytes": after_size,
        "estimated_shrink_bytes": shrink_bytes,
        "estimated_after_to_before_ratio": shrink_ratio,
    }


def _blocked_packet(*, hot_root: Path, reasons: list[str], requested_execute: bool, git_status: str) -> dict[str, Any]:
    return {
        "ok": True,
        "success": False,
        "runner_version": RUNNER_VERSION,
        "execution_state": "ps_q23m_legacy_latest_shrink_blocked_no_write",
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "requested_execute_legacy_latest_shrink": bool(requested_execute),
        "blocked_reasons": reasons,
        "git_status_short": git_status,
        "default_execution_is_dry_run_no_write": True,
        "legacy_latest_shrink_executed": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "runtime_artifact_write_enabled": False,
        "backup_written": False,
        "scheduler_action_changed": False,
        "scheduler_enabled_by_this_tool": False,
        "trigger_added": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def run_legacy_latest_shrink_once(*, hot_root: Path, operator_acknowledged: bool, execute_legacy_latest_shrink_once: bool, confirmation: str, require_clean_tree: bool = True, allow_test_root: bool = False, allow_dirty_tree_for_test: bool = False) -> dict[str, Any]:
    git_status = _git_status_short() if require_clean_tree else ""
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_legacy_latest_shrink_once:
        blockers.append("execute_legacy_latest_shrink_once_flag_required")
    if confirmation != REQUIRED_CONFIRMATION:
        blockers.append("exact_legacy_latest_shrink_confirmation_required")
    if require_clean_tree and git_status:
        blockers.append("repo_clean_required_before_legacy_latest_shrink")
    if not allow_test_root and not _hot_root_ok(hot_root):
        blockers.append("hot_root_must_be_D_btc_ts_hot")

    readiness = run_legacy_latest_shrink_readiness_no_write() if not allow_test_root else {"legacy_latest_shrink_ready": True, "blockers": []}
    if readiness.get("legacy_latest_shrink_ready") is not True and not allow_dirty_tree_for_test:
        blockers.append("q23k_legacy_latest_shrink_readiness_required")

    candidate: dict[str, Any] = {}
    try:
        candidate = summarize_compact_candidate(hot_root=hot_root)
    except Exception as exc:  # noqa: BLE001 - diagnostic/gated runner
        candidate = {"candidate_exception": exc.__class__.__name__, "candidate_exception_message": str(exc)[:240]}
        blockers.append("compact_candidate_build_failed")
    if candidate.get("source_artifact_mode") != "distributed":
        blockers.append("source_artifact_mode_must_be_distributed")
    if candidate.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH:
        blockers.append("source_artifact_relative_path_must_be_latest_manifest")
    if candidate.get("distributed_stale_vs_legacy") is True:
        blockers.append("distributed_must_not_be_stale_vs_legacy")
    if candidate.get("candidate_read_model_ok") is not True:
        blockers.append("compact_candidate_must_be_read_model_compatible")
    if int(candidate.get("compact_record_count") or 0) <= 0:
        blockers.append("compact_candidate_records_required")
    if int(candidate.get("estimated_after_size_bytes") or 0) <= 0:
        blockers.append("compact_candidate_size_required")

    legacy_path = hot_root / LEGACY_LATEST_RELATIVE_PATH
    now = _utc_now()
    backup_rel = _backup_relative_path(now)
    backup_path = hot_root / backup_rel

    if blockers:
        result = _blocked_packet(hot_root=hot_root, reasons=sorted(set(blockers)), requested_execute=execute_legacy_latest_shrink_once, git_status=git_status)
        result.update({"readiness": readiness, "candidate": {k: v for k, v in candidate.items() if k != "candidate_compact_payload"}, "backup_relative_path_candidate": str(backup_rel).replace("\\", "/")})
        return result

    before_meta = _file_meta(legacy_path)
    compact_payload = _as_mapping(candidate.get("candidate_compact_payload"))
    compact_bytes = _json_bytes(compact_payload)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(legacy_path, backup_path)
    tmp_path = legacy_path.with_name(legacy_path.name + ".ps_q23m_tmp")
    tmp_path.write_bytes(compact_bytes)
    os.replace(tmp_path, legacy_path)
    after_meta = _file_meta(legacy_path)
    backup_meta = _file_meta(backup_path)
    return {
        "ok": True,
        "success": True,
        "runner_version": RUNNER_VERSION,
        "execution_state": "ps_q23m_legacy_latest_shrunk_once",
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "legacy_latest_relative_path": str(LEGACY_LATEST_RELATIVE_PATH).replace("\\", "/"),
        "backup_relative_path": str(backup_rel).replace("\\", "/"),
        "before_latest_meta": before_meta,
        "after_latest_meta": after_meta,
        "backup_meta": backup_meta,
        "candidate": {k: v for k, v in candidate.items() if k != "candidate_compact_payload"},
        "legacy_latest_shrink_executed": True,
        "latest_prediction_artifact_written": True,
        "status_artifact_written": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "runtime_artifact_write_enabled": True,
        "backup_written": True,
        "scheduler_action_changed": False,
        "scheduler_enabled_by_this_tool": False,
        "trigger_added": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q23M gated legacy latest shrink executor")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-legacy-latest-shrink-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--allow-dirty-tree", action="store_true")
    parser.add_argument("--allow-test-root", action="store_true")
    parser.add_argument("--allow-dirty-tree-for-test", action="store_true")
    args = parser.parse_args(argv)
    result = run_legacy_latest_shrink_once(
        hot_root=Path(args.hot_root),
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_legacy_latest_shrink_once=bool(args.execute_legacy_latest_shrink_once),
        confirmation=str(args.confirmation),
        require_clean_tree=not bool(args.allow_dirty_tree),
        allow_test_root=bool(args.allow_test_root),
        allow_dirty_tree_for_test=bool(args.allow_dirty_tree_for_test),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_legacy_latest_shrink_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
