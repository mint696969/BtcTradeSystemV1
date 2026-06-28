# path: ./tools/diagnose_phase4a_prediction_system_ps_q23c_distributed_reader_validator.py
# desc: PS-Q23C read-only distributed prediction artifact reader validator. Prefers latest_manifest sidecars and falls back to legacy latest.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    LATEST_RELATIVE_PATH,
    STATUS_RELATIVE_PATH,
    _file_meta,
    _load_json,
    build_candidate_layout,
)
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import LATEST_MANIFEST_RELATIVE_PATH  # noqa: E402

VALIDATOR_VERSION = "prediction_warroom.distributed_reader_validator.ps_q23c.v1"
REQUIRED_SIDECARS = (
    "manifest",
    "summary",
    "forecast_batch_summary",
    "forecast_records",
    "warnings",
    "lineage",
    "timings",
    "safety",
    "checksums",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _relative_path_safe(rel: str) -> bool:
    parts = rel.replace("\\", "/").split("/")
    return bool(rel) and not Path(rel).is_absolute() and ".." not in parts and ":" not in rel and rel.startswith("prediction/")


def _resolve_relative(root: Path, rel: str) -> Path:
    if not _relative_path_safe(rel):
        raise ValueError(f"unsafe relative path: {rel}")
    return root / Path(rel)


def _read_json_file(path: Path) -> tuple[dict[str, Any], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
        return (data if isinstance(data, dict) else {}, "")
    except Exception as exc:  # noqa: BLE001 - diagnostic reports parse failure
        return {}, f"{exc.__class__.__name__}: {exc}"


def _read_jsonl_count_and_samples(path: Path, *, sample_limit: int = 3) -> tuple[int, list[dict[str, Any]], str]:
    count = 0
    samples: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            for line in fh:
                text = line.strip()
                if not text:
                    continue
                count += 1
                if len(samples) < sample_limit:
                    value = json.loads(text)
                    samples.append(value if isinstance(value, dict) else {"value_type": type(value).__name__})
        return count, samples, ""
    except Exception as exc:  # noqa: BLE001 - diagnostic reports parse failure
        return count, samples, f"{exc.__class__.__name__}: {exc}"


def _safe_bool_false(value: Any) -> bool:
    return value is False or value is None


def _parse_utc(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _distributed_stale_vs_legacy(*, distributed_generated_at: Any, legacy_generated_at: Any) -> bool:
    distributed_dt = _parse_utc(distributed_generated_at)
    legacy_dt = _parse_utc(legacy_generated_at)
    if distributed_dt is None or legacy_dt is None:
        return False
    return distributed_dt < legacy_dt


def _validate_safety(safety: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key in (
        "broker_execution_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "would_send_to_broker",
    ):
        if not _safe_bool_false(safety.get(key)):
            blockers.append(f"safety_flag_must_be_false:{key}")
    return blockers


def validate_distributed_reader(*, hot_root: Path) -> dict[str, Any]:
    latest_manifest_path = hot_root / LATEST_MANIFEST_RELATIVE_PATH
    manifest_meta = _file_meta(latest_manifest_path)
    manifest_payload, manifest_error = _read_json_file(latest_manifest_path)
    blockers: list[str] = []
    warnings: list[str] = []
    if manifest_meta.get("exists") is not True:
        blockers.append("latest_manifest_missing")
    if manifest_error:
        blockers.append("latest_manifest_parse_failed")
    run_dir = str(manifest_payload.get("run_dir") or "")
    if run_dir and not _relative_path_safe(run_dir):
        blockers.append("latest_manifest_run_dir_unsafe")
    sidecars = dict(_as_mapping(manifest_payload.get("sidecars")))
    for key in REQUIRED_SIDECARS:
        rel = str(sidecars.get(key) or "")
        if not rel:
            blockers.append(f"sidecar_path_missing:{key}")
        elif not _relative_path_safe(rel):
            blockers.append(f"sidecar_path_unsafe:{key}")
    if blockers:
        return {
            "ok": True,
            "source_artifact_mode": "blocked",
            "distributed_reader_ready": False,
            "distributed_blockers": blockers,
            "distributed_warnings": warnings,
            "latest_manifest_meta": manifest_meta,
            "latest_manifest_parse_error": manifest_error,
        }

    parsed: dict[str, Any] = {}
    sidecar_meta: dict[str, Any] = {}
    for key in REQUIRED_SIDECARS:
        rel = str(sidecars[key])
        path = _resolve_relative(hot_root, rel)
        sidecar_meta[key] = _file_meta(path)
        if sidecar_meta[key].get("exists") is not True:
            blockers.append(f"sidecar_missing:{key}")
            continue
        if key == "forecast_records":
            record_count, samples, error = _read_jsonl_count_and_samples(path)
            parsed[key] = {"record_count": record_count, "samples": samples, "parse_error": error}
            if error:
                blockers.append("forecast_records_jsonl_parse_failed")
        else:
            value, error = _read_json_file(path)
            parsed[key] = value
            if error:
                blockers.append(f"sidecar_parse_failed:{key}")

    summary = _as_mapping(parsed.get("summary"))
    batch_summary = _as_mapping(parsed.get("forecast_batch_summary"))
    run_manifest = _as_mapping(parsed.get("manifest"))
    safety = _as_mapping(parsed.get("safety"))
    forecast_records = _as_mapping(parsed.get("forecast_records"))
    jsonl_count = int(forecast_records.get("record_count") or 0)
    latest_manifest_count = int(manifest_payload.get("record_count") or 0)
    summary_count = int(summary.get("record_count") or 0)
    batch_count = int(batch_summary.get("record_count") or 0)
    run_manifest_count = int(run_manifest.get("record_count") or latest_manifest_count or 0)

    for label, count in (
        ("latest_manifest_record_count", latest_manifest_count),
        ("summary_record_count", summary_count),
        ("forecast_batch_summary_record_count", batch_count),
        ("run_manifest_record_count", run_manifest_count),
    ):
        if count and count != jsonl_count:
            blockers.append(f"record_count_mismatch:{label}")
    if jsonl_count <= 0:
        blockers.append("forecast_records_jsonl_empty")
    blockers.extend(_validate_safety(safety))
    if manifest_payload.get("legacy_latest_retained") is not True:
        warnings.append("legacy_latest_retained_not_true_in_latest_manifest")
    if manifest_payload.get("status_artifact_written") is not False:
        warnings.append("status_artifact_written_not_false_in_latest_manifest")

    generated_at = str(manifest_payload.get("generated_at") or summary.get("generated_at") or batch_summary.get("generated_at") or "")
    return {
        "ok": True,
        "source_artifact_mode": "distributed" if not blockers else "blocked",
        "distributed_reader_ready": not blockers,
        "distributed_blockers": blockers,
        "distributed_warnings": warnings,
        "generated_at": generated_at,
        "record_count": jsonl_count,
        "latest_manifest_meta": manifest_meta,
        "latest_manifest_path": str(LATEST_MANIFEST_RELATIVE_PATH).replace("\\", "/"),
        "run_dir": run_dir,
        "summary_path": str(sidecars.get("summary") or ""),
        "forecast_records_path": str(sidecars.get("forecast_records") or ""),
        "sidecar_meta": sidecar_meta,
        "summary": {
            "family_count": summary.get("family_count"),
            "horizon_count": summary.get("horizon_count"),
            "warning_count": summary.get("warning_count"),
            "records_embedded": summary.get("records_embedded") is True,
        },
        "forecast_record_samples": forecast_records.get("samples", []),
        "safety": dict(safety),
    }


def validate_legacy_fallback(*, hot_root: Path) -> dict[str, Any]:
    latest = hot_root / LATEST_RELATIVE_PATH
    latest_meta = _file_meta(latest)
    payload, parse_error = _load_json(latest)
    blockers: list[str] = []
    if latest_meta.get("exists") is not True:
        blockers.append("legacy_latest_missing")
    if parse_error:
        blockers.append("legacy_latest_parse_failed")
    layout = build_candidate_layout(hot_root=hot_root, payload=payload, latest_meta=latest_meta) if not blockers else {}
    if layout and layout.get("candidate_feasible") is not True:
        blockers.append("legacy_latest_candidate_layout_not_feasible")
    sizes = dict(_as_mapping(layout.get("candidate_sizes"))) if layout else {}
    summary = dict(_as_mapping(layout.get("summary_candidate_not_written"))) if layout else {}
    return {
        "ok": True,
        "source_artifact_mode": "legacy_fallback" if not blockers else "blocked",
        "legacy_fallback_ready": not blockers,
        "legacy_blockers": blockers,
        "legacy_latest_parse_error": parse_error,
        "latest_meta": latest_meta,
        "generated_at": summary.get("generated_at", ""),
        "record_count": int(sizes.get("record_count") or 0),
        "summary_estimated_bytes": sizes.get("summary_estimated_bytes"),
        "forecast_records_jsonl_estimated_bytes": sizes.get("forecast_records_jsonl_estimated_bytes"),
    }


def run_reader_validator(*, hot_root: Path = DEFAULT_HOT_ROOT, disable_distributed_preference: bool = False) -> dict[str, Any]:
    distributed = validate_distributed_reader(hot_root=hot_root) if not disable_distributed_preference else {
        "ok": True,
        "source_artifact_mode": "blocked",
        "distributed_reader_ready": False,
        "distributed_blockers": ["distributed_preference_disabled"],
    }
    legacy = validate_legacy_fallback(hot_root=hot_root)
    stale_vs_legacy = bool(
        distributed.get("distributed_reader_ready") is True
        and legacy.get("legacy_fallback_ready") is True
        and _distributed_stale_vs_legacy(
            distributed_generated_at=distributed.get("generated_at"),
            legacy_generated_at=legacy.get("generated_at"),
        )
    )
    if stale_vs_legacy:
        distributed.setdefault("distributed_warnings", []).append("distributed_artifact_older_than_legacy_latest")
    use_distributed = distributed.get("distributed_reader_ready") is True and not stale_vs_legacy
    use_legacy = (not use_distributed) and legacy.get("legacy_fallback_ready") is True
    source_mode = "distributed" if use_distributed else "legacy_fallback" if use_legacy else "blocked"
    selected = distributed if use_distributed else legacy if use_legacy else {}
    return {
        "ok": True,
        "validator_version": VALIDATOR_VERSION,
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "source_artifact_mode": source_mode,
        "distributed_reader_ready": bool(distributed.get("distributed_reader_ready") is True),
        "legacy_fallback_ready": bool(legacy.get("legacy_fallback_ready") is True),
        "distributed_stale_vs_legacy": stale_vs_legacy,
        "freshness_arbitration": "legacy_newer" if stale_vs_legacy else "distributed_current_or_legacy_unavailable",
        "selected_generated_at": selected.get("generated_at", ""),
        "selected_record_count": int(selected.get("record_count") or 0),
        "distributed": distributed,
        "legacy_fallback": legacy,
        "read_only_validator": True,
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
    parser = argparse.ArgumentParser(description="PS-Q23C read-only distributed reader validator")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--disable-distributed-preference", action="store_true")
    args = parser.parse_args(argv)
    result = run_reader_validator(hot_root=Path(args.hot_root), disable_distributed_preference=bool(args.disable_distributed_preference))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and result.get("source_artifact_mode") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
