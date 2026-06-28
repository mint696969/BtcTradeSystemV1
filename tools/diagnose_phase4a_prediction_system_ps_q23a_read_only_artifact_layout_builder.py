# path: ./tools/diagnose_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder.py
# desc: PS-Q23A read-only diagnostic that derives a distributed artifact layout plan from legacy latest_prediction_system_result.json. No writes.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import DEFAULT_HOT_ROOT  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.artifact_layout_builder.ps_q23a.v1"
LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
STATUS_RELATIVE_PATH = Path("prediction/status/non_ui_scheduled_producer_status.json")
MAX_SUMMARY_BYTES_TARGET = 1_000_000
MAX_MANIFEST_BYTES_TARGET = 100_000
LEGACY_LATEST_LONG_TERM_TARGET_BYTES = 1_000_000


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size_bytes": None, "mtime_utc": "", "sha256_prefix": ""}
    stat = path.stat()
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sha256_prefix": sha.hexdigest()[:16],
    }


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
        return (data if isinstance(data, dict) else {}, "")
    except Exception as exc:  # noqa: BLE001 - diagnostic reports parse failure
        return {}, f"{exc.__class__.__name__}: {exc}"


def _generated_at(payload: Mapping[str, Any]) -> str:
    batch = _as_mapping(payload.get("forecast_batch"))
    return str(batch.get("generated_at") or payload.get("generated_at") or "")


def _prediction_run_id(payload: Mapping[str, Any]) -> str:
    batch = _as_mapping(payload.get("forecast_batch"))
    return str(payload.get("prediction_run_id") or batch.get("prediction_run_id") or "")


def _safe_slug(text: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.:-]+", "_", text.strip())
    clean = clean.strip("_:")
    return clean[-80:] if len(clean) > 80 else clean


def _parse_generated_at(value: str) -> datetime | None:
    if not value:
        return None
    try:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _run_dir(*, generated_at: str, run_id: str) -> str:
    dt = _parse_generated_at(generated_at) or datetime.now(timezone.utc)
    date_part = dt.strftime("%Y-%m-%d")
    time_part = dt.strftime("%H%M%S")
    slug_source = run_id or generated_at or "unknown_run"
    slug = _safe_slug(slug_source) or "unknown_run"
    return f"prediction/runs/{date_part}/{time_part}_{slug}"


def _records(payload: Mapping[str, Any]) -> list[Any]:
    batch = _as_mapping(payload.get("forecast_batch"))
    records = batch.get("records")
    return list(records) if isinstance(records, list) else []


def _warning_candidates(payload: Mapping[str, Any], records: list[Any]) -> list[str]:
    warnings: list[str] = []
    for key in ("warning_reasons", "warnings"):
        value = payload.get(key)
        if isinstance(value, list):
            warnings.extend(str(item) for item in value if item)
    batch = _as_mapping(payload.get("forecast_batch"))
    for key in ("warning_reasons", "warnings"):
        value = batch.get(key)
        if isinstance(value, list):
            warnings.extend(str(item) for item in value if item)
    for record in records[:250]:
        item = _as_mapping(record)
        value = item.get("warnings")
        if isinstance(value, list):
            warnings.extend(str(w) for w in value if w)
    return sorted(set(warnings))


def _json_size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8"))


def _jsonl_size(records: list[Any]) -> int:
    total = 0
    for record in records:
        total += len(json.dumps(record, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")) + 1
    return total


def _safety(payload: Mapping[str, Any]) -> dict[str, Any]:
    batch = _as_mapping(payload.get("forecast_batch"))
    return {
        "read_only": payload.get("read_only") is True or batch.get("read_only") is True,
        "non_executing": payload.get("non_executing") is True or batch.get("non_executing") is True,
        "broker_execution_requested": payload.get("broker_execution_requested") is True,
        "command_ledger_append_requested": payload.get("command_ledger_append_requested") is True,
        "approval_append_requested": payload.get("approval_append_requested") is True,
        "would_send_to_broker": payload.get("would_send_to_broker") is True or batch.get("would_send_to_broker") is True,
    }


def _summary_candidate(payload: Mapping[str, Any], records: list[Any], warnings: list[str]) -> dict[str, Any]:
    batch = _as_mapping(payload.get("forecast_batch"))
    families: dict[str, int] = {}
    horizons: dict[str, int] = {}
    for record in records:
        item = _as_mapping(record)
        family = str(item.get("family") or item.get("prediction_family") or "unknown")
        horizon = str(item.get("horizon_key") or item.get("horizon_sec") or "unknown")
        families[family] = families.get(family, 0) + 1
        horizons[horizon] = horizons.get(horizon, 0) + 1
    return {
        "generated_at": _generated_at(payload),
        "prediction_run_id": _prediction_run_id(payload),
        "family_count": int(batch.get("family_count") or len(families)),
        "horizon_count": int(batch.get("horizon_count") or len(horizons)),
        "record_count": int(batch.get("record_count") or len(records)),
        "families": dict(sorted(families.items())[:50]),
        "horizons": dict(sorted(horizons.items())[:50]),
        "warning_count": len(warnings),
        "warning_samples": warnings[:20],
        "read_only": payload.get("read_only") is True or batch.get("read_only") is True,
        "non_executing": payload.get("non_executing") is True or batch.get("non_executing") is True,
        "records_embedded": False,
    }


def build_candidate_layout(*, hot_root: Path, payload: Mapping[str, Any], latest_meta: Mapping[str, Any]) -> dict[str, Any]:
    records = _records(payload)
    warnings = _warning_candidates(payload, records)
    generated_at = _generated_at(payload)
    run_id = _prediction_run_id(payload) or f"generated_at:{generated_at}"
    run_dir = _run_dir(generated_at=generated_at, run_id=run_id)
    summary = _summary_candidate(payload, records, warnings)
    safety = _safety(payload)
    sidecars = {
        "manifest": f"{run_dir}/manifest.json",
        "summary": f"{run_dir}/summary.json",
        "forecast_batch_summary": f"{run_dir}/forecast_batch_summary.json",
        "forecast_records": f"{run_dir}/forecast_records.jsonl",
        "feature_summary": f"{run_dir}/feature_summary.json",
        "input_refs": f"{run_dir}/input_refs.json",
        "warnings": f"{run_dir}/warnings.json",
        "lineage": f"{run_dir}/lineage.json",
        "timings": f"{run_dir}/timings.json",
        "safety": f"{run_dir}/safety.json",
        "checksums": f"{run_dir}/checksums.json",
    }
    forecast_records_jsonl_estimated_bytes = _jsonl_size(records)
    summary_estimated_bytes = _json_size(summary)
    latest_manifest_candidate = {
        "layout_version": DIAGNOSTIC_VERSION,
        "generated_at": generated_at,
        "prediction_run_id": run_id,
        "run_dir": run_dir,
        "legacy_latest_path": str(LATEST_RELATIVE_PATH).replace("\\", "/"),
        "sidecars": sidecars,
        "record_count": len(records),
        "latest_legacy_size_bytes": latest_meta.get("size_bytes"),
        "source_artifact_mode": "legacy_read_only_diagnostic",
    }
    manifest_estimated_bytes = _json_size(latest_manifest_candidate)
    warnings_out: list[str] = []
    if not generated_at:
        warnings_out.append("generated_at_missing_or_unparseable")
    if not records:
        warnings_out.append("forecast_records_missing_or_empty")
    if int(latest_meta.get("size_bytes") or 0) > LEGACY_LATEST_LONG_TERM_TARGET_BYTES:
        warnings_out.append("legacy_latest_exceeds_long_term_target_bytes")
    if summary_estimated_bytes > MAX_SUMMARY_BYTES_TARGET:
        warnings_out.append("summary_candidate_exceeds_target_bytes")
    if manifest_estimated_bytes > MAX_MANIFEST_BYTES_TARGET:
        warnings_out.append("latest_manifest_candidate_exceeds_target_bytes")
    if safety.get("broker_execution_requested") or safety.get("command_ledger_append_requested") or safety.get("approval_append_requested") or safety.get("would_send_to_broker"):
        warnings_out.append("safety_boundary_requested_in_legacy_payload")
    feasible = bool(generated_at and manifest_estimated_bytes <= MAX_MANIFEST_BYTES_TARGET and summary_estimated_bytes <= MAX_SUMMARY_BYTES_TARGET)
    return {
        "candidate_feasible": feasible,
        "candidate_warnings": warnings_out,
        "latest_manifest_candidate": latest_manifest_candidate,
        "run_manifest_candidate": {
            "layout_version": DIAGNOSTIC_VERSION,
            "run_dir": run_dir,
            "sidecars": sidecars,
            "write_order": [
                "sidecars_tmp_dir",
                "summary",
                "forecast_batch_summary",
                "forecast_records_jsonl",
                "warnings",
                "lineage",
                "timings",
                "safety",
                "checksums",
                "run_manifest_last",
                "latest_manifest_atomic_replace",
                "legacy_latest_compatibility_update",
                "status_last",
            ],
            "atomic_latest_manifest_replace_required": True,
            "legacy_latest_retained": True,
        },
        "candidate_sidecars": sidecars,
        "candidate_sizes": {
            "legacy_latest_size_bytes": latest_meta.get("size_bytes"),
            "latest_manifest_estimated_bytes": manifest_estimated_bytes,
            "summary_estimated_bytes": summary_estimated_bytes,
            "forecast_records_jsonl_estimated_bytes": forecast_records_jsonl_estimated_bytes,
            "record_count": len(records),
            "warning_count": len(warnings),
        },
        "summary_candidate_not_written": summary,
        "safety_candidate_not_written": safety,
    }


def run_layout_diagnostic(*, hot_root: Path = DEFAULT_HOT_ROOT) -> dict[str, Any]:
    latest = hot_root / LATEST_RELATIVE_PATH
    status = hot_root / STATUS_RELATIVE_PATH
    latest_meta = _file_meta(latest)
    status_meta = _file_meta(status)
    payload, parse_error = _load_json(latest)
    blockers: list[str] = []
    if latest_meta.get("exists") is not True:
        blockers.append("legacy_latest_missing")
    if parse_error:
        blockers.append("legacy_latest_parse_failed")
    layout = build_candidate_layout(hot_root=hot_root, payload=payload, latest_meta=latest_meta) if not blockers else {}
    ok = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "read_only_diagnostic": True,
        "layout_ready_for_future_dual_write": bool(ok and layout.get("candidate_feasible") is True),
        "layout_blockers": blockers,
        "legacy_latest_parse_error": parse_error,
        "latest_meta": latest_meta,
        "status_meta": status_meta,
        "layout": layout,
        "latest_prediction_artifact_written": False,
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q23A read-only distributed artifact layout builder")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    args = parser.parse_args(argv)
    result = run_layout_diagnostic(hot_root=Path(args.hot_root))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
