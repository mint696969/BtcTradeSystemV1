# path: ./tools/diagnose_phase4a_prediction_system_ps_q23r_scheduled_compact_legacy_tick_observation.py
# desc: PS-Q23R no-write diagnostic confirming scheduled ticks keep legacy latest compact while sidecars retain full records.

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import build_latest_prediction_warroom_read_model  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model import run_manifest_first_live_read_model_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write import run_legacy_latest_shrink_readiness_no_write  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once import RUNNER_VERSION as Q23M_RUNNER_VERSION  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.scheduled_compact_legacy_tick_observation.ps_q23r.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
LEGACY_LATEST_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
LATEST_MANIFEST_RELATIVE_PATH = Path("prediction/latest_manifest.json")
COMPACT_LEGACY_MAX_BYTES = 1_000_000
EXPECTED_FULL_RECORD_COUNT_MIN = 100


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _sha256_prefix(path: Path) -> str:
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
        "sha256_prefix": _sha256_prefix(path),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _load_json_object(path: Path) -> tuple[dict[str, Any], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        return {}, f"json_load_failed:{exc.__class__.__name__}"
    if not isinstance(data, dict):
        return {}, "json_not_object"
    return data, ""


def _safe_relative_path(path_text: Any) -> str:
    text = "" if path_text is None else str(path_text).replace("\\", "/")
    if not text or text.startswith("/") or ":" in text or ".." in Path(text).parts:
        return ""
    return text


def _line_count(path: Path, *, max_lines: int = 1_000_000) -> int:
    count = 0
    with path.open("rb") as fh:
        for _ in fh:
            count += 1
            if count > max_lines:
                break
    return count


def _false_safety_flags() -> dict[str, Any]:
    return {
        "read_only_diagnostic": True,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "runtime_artifact_write_enabled": False,
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


def run_scheduled_compact_legacy_tick_observation(*, hot_root: Path = DEFAULT_HOT_ROOT) -> dict[str, Any]:
    repo_status = _git_status_short()
    legacy_path = hot_root / LEGACY_LATEST_RELATIVE_PATH
    manifest_path = hot_root / LATEST_MANIFEST_RELATIVE_PATH
    legacy_meta = _file_meta(legacy_path)
    manifest_meta = _file_meta(manifest_path)
    legacy_payload, legacy_parse_error = _load_json_object(legacy_path) if legacy_meta.get("exists") else ({}, "legacy_latest_missing")
    manifest, manifest_parse_error = _load_json_object(manifest_path) if manifest_meta.get("exists") else ({}, "latest_manifest_missing")
    batch = _as_mapping(legacy_payload.get("forecast_batch"))
    compact_records = _as_list(batch.get("records"))
    sidecars = _as_mapping(manifest.get("sidecars"))
    forecast_records_rel = _safe_relative_path(sidecars.get("forecast_records"))
    forecast_records_path = hot_root / forecast_records_rel if forecast_records_rel else Path("")
    forecast_records_meta = _file_meta(forecast_records_path) if forecast_records_rel else {"exists": False, "size_bytes": None, "sha256_prefix": "", "mtime_utc": ""}
    forecast_records_line_count = _line_count(forecast_records_path) if forecast_records_meta.get("exists") else 0
    run_dir_rel = _safe_relative_path(manifest.get("run_dir"))
    run_dir_exists = bool(run_dir_rel and (hot_root / run_dir_rel).exists())

    compact_read_model = build_latest_prediction_warroom_read_model(
        payload=legacy_payload,
        market_state={},
        market_diag={},
        source_path=str(legacy_path),
    ) if legacy_payload else {"ok": False, "blocker_reason_codes": [legacy_parse_error or "legacy_latest_empty"]}
    q23e = run_manifest_first_live_read_model_diagnostic(hot_root=hot_root)
    q23k = run_legacy_latest_shrink_readiness_no_write()

    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status:
        blockers.append("repo_clean_required_for_q23r_closeout")
    if legacy_meta.get("exists") is not True:
        blockers.append("compact_legacy_latest_missing")
    if legacy_parse_error:
        blockers.append("compact_legacy_latest_parse_required")
    if legacy_payload.get("legacy_latest_shrunk_by") != Q23M_RUNNER_VERSION:
        blockers.append("compact_legacy_latest_q23m_marker_required")
    if legacy_payload.get("source_manifest_relative_path") != LATEST_MANIFEST_RELATIVE_PATH.as_posix():
        blockers.append("compact_legacy_latest_source_manifest_marker_required")
    if int(legacy_meta.get("size_bytes") or 0) <= 0:
        blockers.append("compact_legacy_latest_size_required")
    if int(legacy_meta.get("size_bytes") or 0) > COMPACT_LEGACY_MAX_BYTES:
        blockers.append("compact_legacy_latest_size_must_be_small")
    compact_count = int(legacy_payload.get("compact_record_count") or 0)
    original_count = int(legacy_payload.get("original_record_count") or 0)
    if compact_count <= 0:
        blockers.append("compact_legacy_latest_record_count_required")
    if original_count <= compact_count:
        blockers.append("original_record_count_must_be_greater_than_compact")
    if int(batch.get("record_count") or 0) != len(compact_records) or len(compact_records) != compact_count:
        blockers.append("compact_forecast_batch_record_count_mismatch")
    if compact_read_model.get("ok") is not True:
        blockers.append("compact_legacy_latest_read_model_compatible_required")
    if manifest_meta.get("exists") is not True:
        blockers.append("latest_manifest_missing")
    if manifest_parse_error:
        blockers.append("latest_manifest_parse_required")
    if manifest.get("generated_at") != legacy_payload.get("generated_at"):
        blockers.append("manifest_and_compact_legacy_generated_at_must_match")
    if int(manifest.get("record_count") or 0) != original_count:
        blockers.append("manifest_record_count_must_match_original_record_count")
    if int(manifest.get("record_count") or 0) < EXPECTED_FULL_RECORD_COUNT_MIN:
        blockers.append("manifest_record_count_must_remain_full")
    if not run_dir_exists:
        blockers.append("manifest_run_dir_required")
    if forecast_records_meta.get("exists") is not True:
        blockers.append("forecast_records_sidecar_required")
    if forecast_records_line_count != int(manifest.get("record_count") or 0):
        blockers.append("forecast_records_line_count_must_match_manifest_record_count")
    if int(forecast_records_meta.get("size_bytes") or 0) <= int(legacy_meta.get("size_bytes") or 0):
        blockers.append("forecast_records_sidecar_must_be_larger_than_compact_legacy")
    if manifest.get("latest_legacy_size_bytes") != legacy_meta.get("size_bytes"):
        warnings.append("latest_manifest_legacy_size_bytes_is_pre_compaction_expected")
    payload_status = _as_mapping(q23e.get("payload_status"))
    read_model = _as_mapping(q23e.get("read_model"))
    if q23e.get("source_artifact_mode") != "distributed":
        blockers.append("q23e_must_select_distributed")
    if payload_status.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH.as_posix():
        blockers.append("q23e_payload_status_must_use_latest_manifest")
    if read_model.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH.as_posix():
        blockers.append("q23e_read_model_must_use_latest_manifest")
    if q23e.get("distributed_reader_ready") is not True:
        blockers.append("q23e_distributed_reader_ready_required")
    if q23e.get("distributed_stale_vs_legacy") is True:
        blockers.append("q23e_distributed_must_not_be_stale_vs_legacy")
    if q23e.get("legacy_fallback_ready") is not True:
        blockers.append("q23e_legacy_fallback_ready_required")
    q23k_blockers = list(q23k.get("blockers") or [])
    if q23k_blockers and not repo_status:
        blockers.append("q23k_no_write_readiness_blockers_unexpected")
    if q23k.get("q23i", {}).get("scheduled_sidecar_dual_write_enabled_observed") is not True:
        blockers.append("q23k_scheduled_sidecar_dual_write_observed_required")
    if q23k.get("q23j_display_default", {}).get("source_artifact_mode") != "distributed":
        blockers.append("q23k_q23j_display_default_must_remain_distributed")
    if q23k.get("q23j_display_default", {}).get("legacy_fallback_ready") is not True:
        blockers.append("q23k_q23j_legacy_fallback_ready_required")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "scheduled_compact_legacy_tick_observation_ready": ready,
        "observation_state": "scheduled_compact_legacy_tick_observed_ready" if ready else "scheduled_compact_legacy_tick_observation_blocked",
        "blockers": blockers,
        "warnings": warnings,
        "repo_status_short": repo_status,
        "legacy_latest": {
            "relative_path": LEGACY_LATEST_RELATIVE_PATH.as_posix(),
            "meta": legacy_meta,
            "parse_error": legacy_parse_error,
            "generated_at": legacy_payload.get("generated_at"),
            "shrunk_by": legacy_payload.get("legacy_latest_shrunk_by"),
            "shrink_mode": legacy_payload.get("legacy_latest_shrink_mode"),
            "source_manifest_relative_path": legacy_payload.get("source_manifest_relative_path"),
            "original_record_count": original_count,
            "compact_record_count": compact_count,
            "forecast_batch_record_count": batch.get("record_count"),
            "record_count_loaded": len(compact_records),
            "read_model_ok": compact_read_model.get("ok") is True,
            "read_model_record_count": compact_read_model.get("record_count"),
            "read_model_blockers": list(compact_read_model.get("blocker_reason_codes") or []),
            "compact_legacy_max_bytes": COMPACT_LEGACY_MAX_BYTES,
        },
        "latest_manifest": {
            "relative_path": LATEST_MANIFEST_RELATIVE_PATH.as_posix(),
            "meta": manifest_meta,
            "parse_error": manifest_parse_error,
            "generated_at": manifest.get("generated_at"),
            "record_count": manifest.get("record_count"),
            "run_dir": run_dir_rel,
            "run_dir_exists": run_dir_exists,
            "latest_legacy_size_bytes": manifest.get("latest_legacy_size_bytes"),
            "legacy_latest_modified": manifest.get("legacy_latest_modified"),
            "source_artifact_mode": manifest.get("source_artifact_mode"),
        },
        "forecast_records_sidecar": {
            "relative_path": forecast_records_rel,
            "meta": forecast_records_meta,
            "line_count": forecast_records_line_count,
        },
        "q23e": {
            "ok": q23e.get("ok"),
            "source_artifact_mode": q23e.get("source_artifact_mode"),
            "payload_status_source_artifact_relative_path": payload_status.get("source_artifact_relative_path"),
            "read_model_source_artifact_relative_path": read_model.get("source_artifact_relative_path"),
            "distributed_reader_ready": q23e.get("distributed_reader_ready"),
            "distributed_stale_vs_legacy": q23e.get("distributed_stale_vs_legacy"),
            "legacy_fallback_ready": q23e.get("legacy_fallback_ready"),
            "selected_record_count": q23e.get("selected_record_count"),
            "selected_generated_at": q23e.get("selected_generated_at"),
        },
        "q23k": {
            "ok": q23k.get("ok"),
            "legacy_latest_shrink_ready": q23k.get("legacy_latest_shrink_ready"),
            "blockers": q23k_blockers,
            "q23i": q23k.get("q23i"),
            "q23j_display_default": q23k.get("q23j_display_default"),
        },
        **_false_safety_flags(),
    }


def main() -> int:
    result = run_scheduled_compact_legacy_tick_observation()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
