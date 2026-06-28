# path: ./tools/diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model.py
# desc: PS-Q23E read-only opt-in live diagnostic for Q23D manifest-first WarRoom read-model adapter.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    load_latest_prediction_payload_status_manifest_first,
    load_latest_prediction_warroom_read_model_manifest_first,
)

DIAGNOSTIC_VERSION = "prediction_warroom.manifest_first_live_read_model.ps_q23e.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _compact_payload_status(status: Mapping[str, Any]) -> dict[str, Any]:
    distributed = _as_mapping(status.get("distributed_status"))
    legacy = _as_mapping(status.get("legacy_status"))
    manifest = _as_mapping(status.get("manifest_status"))
    return {
        "ok": status.get("ok") is True,
        "source_artifact_mode": str(status.get("source_artifact_mode") or ""),
        "source_artifact_relative_path": str(status.get("source_artifact_relative_path") or ""),
        "source_artifact_path": str(status.get("source_artifact_path") or ""),
        "distributed_reader_ready": status.get("distributed_reader_ready") is True,
        "legacy_fallback_ready": status.get("legacy_fallback_ready") is True,
        "distributed_stale_vs_legacy": status.get("distributed_stale_vs_legacy") is True,
        "distributed_generated_at": str(status.get("distributed_generated_at") or ""),
        "legacy_generated_at": str(status.get("legacy_generated_at") or ""),
        "warning_reason_codes": [str(item) for item in _as_list(status.get("warning_reason_codes"))[:20]],
        "blocked_reason": str(status.get("blocked_reason") or ""),
        "distributed_blocked_reasons": [str(item) for item in _as_list(distributed.get("blocked_reasons"))[:20]],
        "legacy_blocked_reason": str(legacy.get("blocked_reason") or ""),
        "manifest_blocked_reason": str(manifest.get("blocked_reason") or ""),
        "latest_manifest_written": status.get("latest_manifest_written") is True,
        "run_sidecars_written": status.get("run_sidecars_written") is True,
        "latest_prediction_artifact_written": status.get("latest_prediction_artifact_written") is True,
        "status_artifact_written": status.get("status_artifact_written") is True,
        "runtime_artifact_write_enabled": status.get("runtime_artifact_write_enabled") is True,
        "would_send_to_broker": status.get("would_send_to_broker") is True,
        "broker_private_api_allowed": status.get("broker_private_api_allowed") is True,
        "autotrade_trigger_allowed": status.get("autotrade_trigger_allowed") is True,
    }


def _compact_read_model(model: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": model.get("ok") is True,
        "payload_load_ok": model.get("payload_load_ok") is True,
        "read_model_state": str(model.get("read_model_state") or ""),
        "source_artifact_mode": str(model.get("source_artifact_mode") or ""),
        "source_artifact_relative_path": str(model.get("source_artifact_relative_path") or ""),
        "generated_at": str(model.get("generated_at") or ""),
        "record_count": model.get("record_count"),
        "freshness_state": str(model.get("freshness_state") or ""),
        "age_sec": model.get("age_sec"),
        "warning_reason_codes": [str(item) for item in _as_list(model.get("warning_reason_codes"))[:20]],
        "blocker_reason_codes": [str(item) for item in _as_list(model.get("blocker_reason_codes"))[:20]],
        "read_only": model.get("read_only") is True,
        "non_executing": model.get("non_executing") is True,
        "display_only": model.get("display_only") is True,
        "runtime_artifact_write_allowed": model.get("runtime_artifact_write_allowed") is True,
        "status_artifact_write_allowed": model.get("status_artifact_write_allowed") is True,
        "prediction_artifact_write_allowed": model.get("prediction_artifact_write_allowed") is True,
        "view_artifact_write_allowed": model.get("view_artifact_write_allowed") is True,
        "would_send_to_broker": model.get("would_send_to_broker") is True,
        "broker_private_api_allowed": model.get("broker_private_api_allowed") is True,
        "autotrade_trigger_allowed": model.get("autotrade_trigger_allowed") is True,
    }


def run_manifest_first_live_read_model_diagnostic(*, hot_root: Path = DEFAULT_HOT_ROOT, prefer_distributed: bool = True, now_utc: str | None = None) -> dict[str, Any]:
    payload_status = load_latest_prediction_payload_status_manifest_first(
        hot_latest_root_hint=hot_root,
        prefer_distributed=prefer_distributed,
    )
    read_model = load_latest_prediction_warroom_read_model_manifest_first(
        hot_latest_root_hint=hot_root,
        prefer_distributed=prefer_distributed,
        now_utc=now_utc,
    )
    compact_status = _compact_payload_status(_as_mapping(payload_status))
    compact_model = _compact_read_model(_as_mapping(read_model))
    blockers: list[str] = []
    if compact_status["ok"] is not True:
        blockers.append("payload_status_not_ok")
    if compact_model["payload_load_ok"] is not True:
        blockers.append("read_model_payload_load_not_ok")
    for key in (
        "latest_manifest_written",
        "run_sidecars_written",
        "latest_prediction_artifact_written",
        "status_artifact_written",
        "runtime_artifact_write_enabled",
        "would_send_to_broker",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
    ):
        if compact_status.get(key) is True:
            blockers.append(f"payload_status_forbidden_true:{key}")
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "would_send_to_broker",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
    ):
        if compact_model.get(key) is True:
            blockers.append(f"read_model_forbidden_true:{key}")
    if compact_status["source_artifact_mode"] not in {"distributed", "legacy_fallback"}:
        blockers.append("unexpected_source_artifact_mode")
    return {
        "ok": not blockers,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "prefer_distributed": bool(prefer_distributed),
        "source_artifact_mode": compact_status["source_artifact_mode"],
        "selected_generated_at": compact_model["generated_at"],
        "selected_record_count": compact_model["record_count"],
        "distributed_reader_ready": compact_status["distributed_reader_ready"],
        "legacy_fallback_ready": compact_status["legacy_fallback_ready"],
        "distributed_stale_vs_legacy": compact_status["distributed_stale_vs_legacy"],
        "blockers": blockers,
        "payload_status": compact_status,
        "read_model": compact_model,
        "read_only_diagnostic": True,
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
    parser = argparse.ArgumentParser(description="PS-Q23E manifest-first live WarRoom read-model diagnostic")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--now-utc", default=None)
    parser.add_argument("--legacy-only", action="store_true", help="Disable distributed preference and force legacy fallback path")
    args = parser.parse_args(argv)
    result = run_manifest_first_live_read_model_diagnostic(
        hot_root=Path(args.hot_root),
        prefer_distributed=not bool(args.legacy_only),
        now_utc=args.now_utc,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
