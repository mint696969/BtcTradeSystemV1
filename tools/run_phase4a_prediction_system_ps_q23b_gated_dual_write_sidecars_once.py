# path: ./tools/run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once.py
# desc: PS-Q23B explicitly gated one-shot distributed sidecar writer. Default is blocked no-write; legacy latest/status untouched.

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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    DIAGNOSTIC_VERSION as Q23A_DIAGNOSTIC_VERSION,
    LATEST_RELATIVE_PATH,
    STATUS_RELATIVE_PATH,
    _file_meta,
    _load_json,
    _records,
    _warning_candidates,
    build_candidate_layout,
)

WRITER_VERSION = "prediction_warroom.distributed_sidecar_writer.ps_q23b.v1"
REQUIRED_CONFIRMATION = "WRITE_D_HOT_DISTRIBUTED_PREDICTION_SIDECARS_ONCE"
LATEST_MANIFEST_RELATIVE_PATH = Path("prediction/latest_manifest.json")
LOCK_RELATIVE_PATH = Path("prediction/runtime/non_ui_scheduler_producer.lock.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")


def _jsonl_bytes(records: list[Any]) -> bytes:
    return b"".join((json.dumps(record, ensure_ascii=False, sort_keys=True, default=str) + "\n").encode("utf-8") for record in records)


def _sha256_prefix_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _file_sha256_prefix(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()[:16]


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _hot_root_ok(root: Path) -> bool:
    return str(root).rstrip("\\/").lower().replace("/", "\\") == r"d:\btc_ts_hot"


def _relative_path_safe(rel: str) -> bool:
    path = Path(rel)
    parts = rel.replace("\\", "/").split("/")
    return bool(rel) and not path.is_absolute() and ".." not in parts and ":" not in rel and rel.startswith("prediction/")


def _resolve_sidecar(root: Path, rel: str) -> Path:
    if not _relative_path_safe(rel):
        raise ValueError(f"unsafe relative sidecar path: {rel}")
    return root / Path(rel)


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _write_json(path: Path, value: Any) -> None:
    _write_bytes(path, _json_bytes(value))


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(_json_bytes(value))
    os.replace(tmp, path)


def _sidecar_contents(*, payload: Mapping[str, Any], layout: Mapping[str, Any], latest_meta: Mapping[str, Any], started_at: str) -> dict[str, Any]:
    records = _records(payload)
    warnings = _warning_candidates(payload, records)
    summary = dict(_as_mapping(layout.get("summary_candidate_not_written")))
    safety = dict(_as_mapping(layout.get("safety_candidate_not_written")))
    batch = _as_mapping(payload.get("forecast_batch"))
    generated_at = str(summary.get("generated_at") or batch.get("generated_at") or payload.get("generated_at") or "")
    forecast_batch_summary = {
        "generated_at": generated_at,
        "family_count": summary.get("family_count"),
        "horizon_count": summary.get("horizon_count"),
        "record_count": summary.get("record_count"),
        "families": summary.get("families", {}),
        "horizons": summary.get("horizons", {}),
        "source_records_path": _as_mapping(layout.get("candidate_sidecars")).get("forecast_records"),
        "records_embedded": False,
    }
    warnings_payload = {
        "generated_at": generated_at,
        "warning_count": len(warnings),
        "warnings": warnings,
    }
    lineage = {
        "writer_version": WRITER_VERSION,
        "q23a_diagnostic_version": Q23A_DIAGNOSTIC_VERSION,
        "source_artifact_mode": "legacy_latest_to_distributed_sidecars",
        "legacy_latest_relative_path": str(LATEST_RELATIVE_PATH).replace("\\", "/"),
        "legacy_latest_meta": dict(latest_meta),
    }
    timings = {
        "writer_started_at": started_at,
        "writer_finished_at": _utc_now(),
        "read_only_source_snapshot": True,
    }
    return {
        "summary": summary,
        "forecast_batch_summary": forecast_batch_summary,
        "forecast_records": records,
        "warnings": warnings_payload,
        "lineage": lineage,
        "timings": timings,
        "safety": safety,
    }


def _build_blocked_packet(*, hot_root: Path, reasons: list[str], requested_execute: bool, git_status: str = "") -> dict[str, Any]:
    return {
        "ok": True,
        "success": False,
        "writer_version": WRITER_VERSION,
        "execution_state": "ps_q23b_sidecar_write_blocked_no_write",
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "requested_execute_sidecar_write": bool(requested_execute),
        "blocked_reasons": reasons,
        "git_status_short": git_status,
        "default_execution_is_dry_run_no_write": True,
        "latest_prediction_artifact_written": False,
        "legacy_latest_modified": False,
        "status_artifact_written": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "runtime_artifact_write_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def write_distributed_sidecars_once(*, hot_root: Path, operator_acknowledged: bool, execute_sidecar_write_once: bool, confirmation: str, require_clean_tree: bool = True, allow_test_root: bool = False, allow_overwrite_existing_run: bool = False) -> dict[str, Any]:
    started_at = _utc_now()
    git_status = _git_status_short() if require_clean_tree else ""
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_sidecar_write_once:
        blockers.append("execute_sidecar_write_once_flag_required")
    if confirmation != REQUIRED_CONFIRMATION:
        blockers.append("exact_distributed_sidecar_write_confirmation_required")
    if require_clean_tree and git_status:
        blockers.append("repo_clean_required_before_distributed_sidecar_write")
    if not allow_test_root and not _hot_root_ok(hot_root):
        blockers.append("hot_root_must_be_D_btc_ts_hot")
    if (hot_root / LOCK_RELATIVE_PATH).exists():
        blockers.append("scheduler_producer_lock_must_be_absent_before_sidecar_write")

    latest = hot_root / LATEST_RELATIVE_PATH
    status = hot_root / STATUS_RELATIVE_PATH
    before_latest_meta = _file_meta(latest)
    before_status_meta = _file_meta(status)
    payload, parse_error = _load_json(latest)
    if before_latest_meta.get("exists") is not True:
        blockers.append("legacy_latest_missing")
    if parse_error:
        blockers.append("legacy_latest_parse_failed")
    layout = build_candidate_layout(hot_root=hot_root, payload=payload, latest_meta=before_latest_meta) if not parse_error and before_latest_meta.get("exists") is True else {}
    if layout and layout.get("candidate_feasible") is not True:
        blockers.append("q23a_candidate_layout_must_be_feasible")

    run_dir_rel = str(_as_mapping(layout.get("latest_manifest_candidate")).get("run_dir") or "") if layout else ""
    sidecars = dict(_as_mapping(layout.get("candidate_sidecars"))) if layout else {}
    if run_dir_rel and not _relative_path_safe(run_dir_rel):
        blockers.append("candidate_run_dir_must_be_windows_safe_relative_path")
    for rel in sidecars.values():
        if not _relative_path_safe(str(rel)):
            blockers.append("candidate_sidecar_paths_must_be_windows_safe_relative_paths")
            break

    final_run_dir = _resolve_sidecar(hot_root, run_dir_rel) if run_dir_rel and _relative_path_safe(run_dir_rel) else hot_root / "prediction" / "runs" / "invalid"
    latest_manifest = hot_root / LATEST_MANIFEST_RELATIVE_PATH
    if final_run_dir.exists() and not allow_overwrite_existing_run:
        blockers.append("candidate_run_dir_already_exists")

    if blockers:
        result = _build_blocked_packet(hot_root=hot_root, reasons=blockers, requested_execute=execute_sidecar_write_once, git_status=git_status)
        result.update({
            "before_latest_meta": before_latest_meta,
            "before_status_meta": before_status_meta,
            "legacy_latest_parse_error": parse_error,
            "layout_ready_for_future_dual_write": bool(layout.get("candidate_feasible") is True) if layout else False,
        })
        return result

    tmp_run_dir = final_run_dir.with_name(final_run_dir.name + f".tmp_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    if tmp_run_dir.exists():
        shutil.rmtree(tmp_run_dir)
    tmp_run_dir.mkdir(parents=True, exist_ok=False)

    contents = _sidecar_contents(payload=payload, layout=layout, latest_meta=before_latest_meta, started_at=started_at)
    sidecar_paths_written: dict[str, str] = {}
    try:
        _write_json(tmp_run_dir / "summary.json", contents["summary"])
        sidecar_paths_written["summary"] = str(sidecars["summary"])
        _write_json(tmp_run_dir / "forecast_batch_summary.json", contents["forecast_batch_summary"])
        sidecar_paths_written["forecast_batch_summary"] = str(sidecars["forecast_batch_summary"])
        _write_bytes(tmp_run_dir / "forecast_records.jsonl", _jsonl_bytes(list(contents["forecast_records"])))
        sidecar_paths_written["forecast_records"] = str(sidecars["forecast_records"])
        _write_json(tmp_run_dir / "warnings.json", contents["warnings"])
        sidecar_paths_written["warnings"] = str(sidecars["warnings"])
        _write_json(tmp_run_dir / "lineage.json", contents["lineage"])
        sidecar_paths_written["lineage"] = str(sidecars["lineage"])
        _write_json(tmp_run_dir / "timings.json", contents["timings"])
        sidecar_paths_written["timings"] = str(sidecars["timings"])
        _write_json(tmp_run_dir / "safety.json", contents["safety"])
        sidecar_paths_written["safety"] = str(sidecars["safety"])
        _write_json(tmp_run_dir / "feature_summary.json", {"generated_at": contents["summary"].get("generated_at"), "feature_summary_available": False, "source_note": "PS-Q23B sidecar placeholder; detailed feature extraction is a later slice"})
        sidecar_paths_written["feature_summary"] = str(sidecars["feature_summary"])
        _write_json(tmp_run_dir / "input_refs.json", {"legacy_latest_relative_path": str(LATEST_RELATIVE_PATH).replace("\\", "/"), "status_relative_path": str(STATUS_RELATIVE_PATH).replace("\\", "/")})
        sidecar_paths_written["input_refs"] = str(sidecars["input_refs"])

        checksums: dict[str, Any] = {"writer_version": WRITER_VERSION, "files": {}}
        for child in sorted(tmp_run_dir.iterdir()):
            if child.is_file():
                checksums["files"][child.name] = {"size_bytes": child.stat().st_size, "sha256_prefix": _file_sha256_prefix(child)}
        _write_json(tmp_run_dir / "checksums.json", checksums)
        sidecar_paths_written["checksums"] = str(sidecars["checksums"])

        run_manifest = dict(_as_mapping(layout.get("run_manifest_candidate")))
        run_manifest.update({
            "writer_version": WRITER_VERSION,
            "q23a_diagnostic_version": Q23A_DIAGNOSTIC_VERSION,
            "written_at": _utc_now(),
            "source_legacy_latest_meta": before_latest_meta,
            "sidecar_paths_written": sidecar_paths_written,
            "status_artifact_written": False,
            "legacy_latest_modified": False,
        })
        _write_json(tmp_run_dir / "manifest.json", run_manifest)
        sidecar_paths_written["manifest"] = str(sidecars["manifest"])

        final_run_dir.parent.mkdir(parents=True, exist_ok=True)
        tmp_run_dir.rename(final_run_dir)

        latest_manifest_payload = dict(_as_mapping(layout.get("latest_manifest_candidate")))
        latest_manifest_payload.update({
            "layout_version": WRITER_VERSION,
            "q23a_diagnostic_version": Q23A_DIAGNOSTIC_VERSION,
            "latest_manifest_written_at": _utc_now(),
            "run_manifest_path": str(sidecars["manifest"]),
            "legacy_latest_retained": True,
            "legacy_latest_modified": False,
            "status_artifact_written": False,
            "source_artifact_mode": "distributed_sidecars_with_legacy_latest_retained",
        })
        _write_json_atomic(latest_manifest, latest_manifest_payload)
    except Exception:
        if tmp_run_dir.exists():
            shutil.rmtree(tmp_run_dir)
        raise

    after_latest_meta = _file_meta(latest)
    after_status_meta = _file_meta(status)
    latest_manifest_meta = _file_meta(latest_manifest)
    return {
        "ok": True,
        "success": True,
        "writer_version": WRITER_VERSION,
        "execution_state": "ps_q23b_distributed_sidecars_written_once",
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "run_dir": run_dir_rel,
        "latest_manifest_relative_path": str(LATEST_MANIFEST_RELATIVE_PATH).replace("\\", "/"),
        "sidecar_paths_written": sidecar_paths_written,
        "before_latest_meta": before_latest_meta,
        "after_latest_meta": after_latest_meta,
        "before_status_meta": before_status_meta,
        "after_status_meta": after_status_meta,
        "latest_manifest_meta": latest_manifest_meta,
        "legacy_latest_modified": before_latest_meta.get("sha256_prefix") != after_latest_meta.get("sha256_prefix"),
        "status_artifact_written": False,
        "latest_prediction_artifact_written": False,
        "latest_manifest_written": True,
        "run_sidecars_written": True,
        "runtime_artifact_write_enabled": True,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q23B gated one-shot distributed sidecar writer")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-sidecar-write-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--allow-dirty-tree", action="store_true")
    parser.add_argument("--allow-test-root", action="store_true", help="test-only escape hatch for non-D roots")
    parser.add_argument("--allow-overwrite-existing-run", action="store_true", help="test-only escape hatch; do not use for live D-hot")
    args = parser.parse_args(argv)
    result = write_distributed_sidecars_once(
        hot_root=Path(args.hot_root),
        operator_acknowledged=bool(args.operator_acknowledged),
        execute_sidecar_write_once=bool(args.execute_sidecar_write_once),
        confirmation=str(args.confirmation),
        require_clean_tree=not bool(args.allow_dirty_tree),
        allow_test_root=bool(args.allow_test_root),
        allow_overwrite_existing_run=bool(args.allow_overwrite_existing_run),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_sidecar_write_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
