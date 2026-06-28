# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/latest_prediction_warroom_read_model.py
# desc: PS-Q19C read-only WarRoom read model for latest prediction artifact plus current market snapshot. Pure mapping/read-only load helpers; no UI mount, artifact writes, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (
    FRESHNESS_MAX_AGE_SEC,
    FRESHNESS_WARNING_AGE_SEC,
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
)
from btcts.apps.operator_ui.market_state_service import (
    load_latest_market_state,
    market_state_diagnostics,
)
from btcts.core import paths as core_paths

LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION = "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1"
LATEST_PREDICTION_WARROOM_VIEW_RELATIVE_PATH = "prediction/status/latest_prediction_warroom_view.json"
DEFAULT_SELECTED_HORIZON_SEC = (15, 60, 300, 900)
DEFAULT_MAX_RECORDS_PER_HORIZON = 6
DEFAULT_MAX_ARTIFACT_BYTES = 12_000_000

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "warroom_read_model_only",
    "latest_prediction_payload_consumed",
    "market_state_snapshot_consumed",
    "freshness_policy_applied",
    "selected_horizons_summarized",
    "safety_flags_preserved",
    "view_artifact_schema_declared_not_written",
)

FALSE_BOUNDARIES = (
    "ui_mount_allowed",
    "ui_code_changed",
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "refresh_invocation_allowed",
    "scheduler_enabled",
    "producer_enabled",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "prediction_artifact_write_allowed",
    "view_artifact_write_allowed",
    "would_write_runtime_artifact",
    "would_write_status_artifact",
    "would_write_prediction_artifact",
    "would_write_warroom_view_artifact",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _to_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except Exception:
        return None


def _parse_utc(value: Any) -> datetime | None:
    text = _clean(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _now_utc(value: str | None = None) -> datetime:
    parsed = _parse_utc(value)
    if parsed is not None:
        return parsed
    return datetime.now(timezone.utc)


def _age_seconds(generated_at: str, *, now_utc: str | None = None) -> int | None:
    generated = _parse_utc(generated_at)
    if generated is None:
        return None
    return max(0, int((_now_utc(now_utc) - generated).total_seconds()))


def _freshness_state(age_sec: int | None) -> str:
    if age_sec is None:
        return "unknown"
    if age_sec <= FRESHNESS_WARNING_AGE_SEC:
        return "fresh"
    if age_sec <= FRESHNESS_MAX_AGE_SEC:
        return "delayed"
    return "stale"


def _safe_flag_summary(payload: Mapping[str, Any], forecast_batch: Mapping[str, Any], records: list[Any]) -> dict[str, Any]:
    record_maps = [_as_mapping(item) for item in records]
    record_count = len(record_maps)
    all_records_safe = all(
        row.get("read_only") is True
        and row.get("non_executing") is True
        and row.get("would_send_to_broker") is False
        and row.get("would_write_runtime_artifact") is False
        and row.get("would_append_ledger") is False
        for row in record_maps
    ) if record_maps else False

    return {
        "read_only": payload.get("read_only") is True and forecast_batch.get("read_only") is True,
        "non_executing": payload.get("non_executing") is True and forecast_batch.get("non_executing") is True,
        "broker_execution_requested": payload.get("broker_execution_requested") is True,
        "command_ledger_append_requested": payload.get("command_ledger_append_requested") is True,
        "approval_append_requested": payload.get("approval_append_requested") is True,
        "records_all_safe": all_records_safe,
        "record_count_checked": record_count,
        "would_send_to_broker": False,
        "would_write_runtime_artifact": False,
        "would_append_ledger": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
    }


def _record_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    values = _as_mapping(row.get("values_snapshot"))
    return {
        "family": _clean(row.get("family")),
        "horizon_sec": _to_int(row.get("horizon_sec")),
        "horizon_key": _clean(row.get("horizon_key") or row.get("horizon_label")),
        "primary_label": _clean(row.get("primary_label")),
        "confidence": _clean(row.get("confidence")),
        "score": _to_float(row.get("score")),
        "usable": row.get("usable") is True,
        "warning_count": len(_as_list(row.get("warnings"))),
        "warnings": [str(item) for item in _as_list(row.get("warnings"))[:4]],
        "drivers": [str(item) for item in _as_list(row.get("drivers"))[:4]],
        "estimated_signal_strength_percent": values.get("estimated_signal_strength_percent"),
        "estimated_reference_hit_rate_percent": values.get("estimated_reference_hit_rate_percent"),
        "read_only": row.get("read_only") is True,
        "non_executing": row.get("non_executing") is True,
        "would_send_to_broker": row.get("would_send_to_broker") is True,
        "would_write_runtime_artifact": row.get("would_write_runtime_artifact") is True,
        "would_append_ledger": row.get("would_append_ledger") is True,
    }


def _selected_records_by_horizon(records: list[Any], *, selected_horizon_sec: tuple[int, ...], max_records_per_horizon: int) -> dict[str, list[dict[str, Any]]]:
    selected: dict[str, list[dict[str, Any]]] = {str(h): [] for h in selected_horizon_sec}
    for item in records:
        row = _as_mapping(item)
        horizon = _to_int(row.get("horizon_sec"))
        if horizon not in selected_horizon_sec:
            continue
        key = str(horizon)
        selected[key].append(_record_summary(row))

    for key, rows in selected.items():
        rows.sort(
            key=lambda r: (
                0 if r.get("usable") else 1,
                -abs(float(r.get("score") or 0.0)),
                str(r.get("family") or ""),
            )
        )
        selected[key] = rows[: max(1, int(max_records_per_horizon))]
    return selected


def _market_snapshot(market_state: Mapping[str, Any] | None, market_diag: Mapping[str, Any] | None) -> dict[str, Any]:
    row = _as_mapping(market_state)
    diag = _as_mapping(market_diag)
    return {
        "source_kind": "market_state_preferred" if row else "missing",
        "market_uid": _clean(row.get("market_uid") or row.get("symbol_raw") or row.get("symbol")),
        "collector_ts": _clean(row.get("collector_ts") or row.get("exchange_ts")),
        "freshness": _clean(diag.get("preferred_row_freshness") or "UNKNOWN"),
        "age_sec": diag.get("preferred_row_age_sec"),
        "trust_state": _clean(row.get("trust_state") or diag.get("preferred_row_trust_state")),
        "continuity_state": _clean(row.get("continuity_state") or diag.get("preferred_row_continuity_state")),
        "interpretation_bucket": _clean(row.get("interpretation_bucket") or diag.get("preferred_row_interpretation_bucket")),
        "best_bid": row.get("best_bid") or row.get("last_best_bid"),
        "best_ask": row.get("best_ask") or row.get("last_best_ask"),
        "spread": row.get("spread") or row.get("last_spread"),
        "source_series_id": _clean(row.get("source_series_id") or diag.get("preferred_row_source_series_id")),
    }


def build_latest_prediction_warroom_read_model(
    *,
    payload: Mapping[str, Any],
    market_state: Mapping[str, Any] | None = None,
    market_diag: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
    source_path: str = "",
    selected_horizon_sec: tuple[int, ...] = DEFAULT_SELECTED_HORIZON_SEC,
    max_records_per_horizon: int = DEFAULT_MAX_RECORDS_PER_HORIZON,
) -> dict[str, Any]:
    data = _as_mapping(payload)
    forecast_batch = _as_mapping(data.get("forecast_batch"))
    records = _as_list(forecast_batch.get("records"))
    generated_at = _clean(forecast_batch.get("generated_at"))
    age_sec = _age_seconds(generated_at, now_utc=now_utc)
    freshness_state = _freshness_state(age_sec)

    warning_reason_codes: list[str] = []
    blocker_reason_codes: list[str] = []
    if not data:
        blocker_reason_codes.append("prediction_payload_missing")
    if not forecast_batch:
        blocker_reason_codes.append("forecast_batch_missing")
    if not generated_at:
        blocker_reason_codes.append("forecast_batch_generated_at_missing")
    if age_sec is None:
        warning_reason_codes.append("forecast_batch_generated_at_unparseable")
    elif freshness_state == "delayed":
        warning_reason_codes.append("source_generated_at_delayed")
    elif freshness_state == "stale":
        warning_reason_codes.append("source_generated_at_stale")
    if not records:
        blocker_reason_codes.append("forecast_records_missing")

    safety_flags = _safe_flag_summary(data, forecast_batch, records)
    if safety_flags["broker_execution_requested"]:
        blocker_reason_codes.append("broker_execution_requested_true")
    if safety_flags["command_ledger_append_requested"]:
        blocker_reason_codes.append("command_ledger_append_requested_true")
    if safety_flags["approval_append_requested"]:
        blocker_reason_codes.append("approval_append_requested_true")
    if not safety_flags["records_all_safe"]:
        warning_reason_codes.append("record_safety_flags_not_all_safe_or_no_records")

    selected = _selected_records_by_horizon(
        records,
        selected_horizon_sec=selected_horizon_sec,
        max_records_per_horizon=max_records_per_horizon,
    )
    market_snapshot = _market_snapshot(market_state, market_diag)

    ok = bool(data and forecast_batch and records and not blocker_reason_codes)
    read_model = {
        "ok": ok,
        "read_model_version": LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
        "read_model_state": "latest_prediction_warroom_read_model_ready" if ok else "latest_prediction_warroom_read_model_blocked",
        "source_artifact_relative_path": LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
        "source_artifact_path": source_path,
        "declared_view_artifact_relative_path": LATEST_PREDICTION_WARROOM_VIEW_RELATIVE_PATH,
        "view_artifact_write_allowed": False,
        "generated_at": generated_at,
        "age_sec": age_sec,
        "freshness_state": freshness_state,
        "freshness_warning_age_sec": FRESHNESS_WARNING_AGE_SEC,
        "freshness_max_age_sec": FRESHNESS_MAX_AGE_SEC,
        "warning_reason_codes": warning_reason_codes,
        "blocker_reason_codes": blocker_reason_codes,
        "family_count": forecast_batch.get("family_count"),
        "horizon_count": forecast_batch.get("horizon_count"),
        "record_count": forecast_batch.get("record_count") or len(records),
        "selected_horizon_sec": list(selected_horizon_sec),
        "selected_records_by_horizon": selected,
        "market_snapshot": market_snapshot,
        "safety_flags": safety_flags,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
    }
    read_model.update({key: True for key in TRUE_BOUNDARIES})
    read_model.update({key: False for key in FALSE_BOUNDARIES})
    return read_model


def latest_prediction_artifact_path(*, hot_latest_root_hint: str | Path | None = None) -> Path:
    root = Path(str(hot_latest_root_hint).rstrip("\\/")) if hot_latest_root_hint else core_paths.runtime_root(ensure=False)
    return root / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH


def load_latest_prediction_payload_status(*, path: Path | None = None, max_bytes: int = DEFAULT_MAX_ARTIFACT_BYTES) -> dict[str, Any]:
    target = path or latest_prediction_artifact_path()
    status: dict[str, Any] = {
        "ok": False,
        "path": str(target),
        "max_bytes": int(max_bytes),
        "artifact_size_bytes": None,
        "blocked_reason": "",
        "payload": {},
    }
    try:
        stat = target.stat()
    except Exception as exc:  # noqa: BLE001 - read-only diagnostic
        status["blocked_reason"] = "latest_prediction_artifact_stat_failed:" + exc.__class__.__name__
        return status
    status["artifact_size_bytes"] = int(stat.st_size)
    if stat.st_size > int(max_bytes):
        status["blocked_reason"] = "latest_prediction_artifact_exceeds_read_model_max_bytes"
        return status
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - read-only diagnostic
        status["blocked_reason"] = "latest_prediction_artifact_json_load_failed:" + exc.__class__.__name__
        return status
    if not isinstance(data, dict):
        status["blocked_reason"] = "latest_prediction_artifact_not_json_object"
        return status
    status["ok"] = True
    status["payload"] = data
    return status


def load_latest_prediction_payload(*, path: Path | None = None, max_bytes: int = DEFAULT_MAX_ARTIFACT_BYTES) -> dict[str, Any]:
    status = load_latest_prediction_payload_status(path=path, max_bytes=max_bytes)
    payload = status.get("payload")
    return payload if isinstance(payload, dict) else {}


def load_latest_prediction_warroom_read_model(
    *,
    now_utc: str | None = None,
    prediction_path: Path | None = None,
    hot_latest_root_hint: str | Path | None = None,
) -> dict[str, Any]:
    target = prediction_path or latest_prediction_artifact_path(hot_latest_root_hint=hot_latest_root_hint)
    payload_status = load_latest_prediction_payload_status(path=target)
    payload = payload_status.get("payload") if isinstance(payload_status.get("payload"), dict) else {}
    market_state = load_latest_market_state(exchange="bitflyer", symbol_raw="FX_BTC_JPY")
    market_diag = market_state_diagnostics(exchange="bitflyer", symbol_raw="FX_BTC_JPY")
    read_model = build_latest_prediction_warroom_read_model(
        payload=payload,
        market_state=market_state,
        market_diag=market_diag,
        now_utc=now_utc,
        source_path=str(target),
    )
    read_model["artifact_size_bytes"] = payload_status.get("artifact_size_bytes")
    read_model["artifact_max_bytes"] = payload_status.get("max_bytes")
    read_model["payload_load_ok"] = payload_status.get("ok") is True
    blocked_reason = str(payload_status.get("blocked_reason") or "")
    read_model["payload_load_blocked_reason"] = blocked_reason
    if blocked_reason:
        read_model.setdefault("blocker_reason_codes", []).append(blocked_reason)
    return read_model

# PS-Q23D manifest-first distributed read adapter
LATEST_MANIFEST_RELATIVE_PATH = "prediction/latest_manifest.json"
DISTRIBUTED_FORECAST_RECORDS_MAX_BYTES = 50_000_000


def _q23d_read_json_object_status(path: Path, *, max_bytes: int) -> dict[str, Any]:
    status: dict[str, Any] = {
        "ok": False,
        "path": str(path),
        "artifact_size_bytes": None,
        "blocked_reason": "",
        "payload": {},
    }
    try:
        stat = path.stat()
    except Exception as exc:  # noqa: BLE001 - read-only diagnostic
        status["blocked_reason"] = "json_artifact_stat_failed:" + exc.__class__.__name__
        return status
    status["artifact_size_bytes"] = int(stat.st_size)
    if stat.st_size > int(max_bytes):
        status["blocked_reason"] = "json_artifact_exceeds_max_bytes"
        return status
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - read-only diagnostic
        status["blocked_reason"] = "json_artifact_load_failed:" + exc.__class__.__name__
        return status
    if not isinstance(data, dict):
        status["blocked_reason"] = "json_artifact_not_object"
        return status
    status["ok"] = True
    status["payload"] = data
    return status


def _q23d_relative_path_safe(rel: str) -> bool:
    parts = rel.replace("\\", "/").split("/")
    return bool(rel) and not Path(rel).is_absolute() and ".." not in parts and ":" not in rel and rel.startswith("prediction/")


def _q23d_resolve_relative(root: Path, rel: str) -> Path:
    if not _q23d_relative_path_safe(rel):
        raise ValueError(f"unsafe prediction artifact relative path: {rel}")
    return root / Path(rel)


def _q23d_read_jsonl_records_status(path: Path, *, max_bytes: int = DISTRIBUTED_FORECAST_RECORDS_MAX_BYTES) -> dict[str, Any]:
    status: dict[str, Any] = {
        "ok": False,
        "path": str(path),
        "artifact_size_bytes": None,
        "blocked_reason": "",
        "records": [],
        "record_count": 0,
    }
    try:
        stat = path.stat()
    except Exception as exc:  # noqa: BLE001 - read-only diagnostic
        status["blocked_reason"] = "forecast_records_stat_failed:" + exc.__class__.__name__
        return status
    status["artifact_size_bytes"] = int(stat.st_size)
    if stat.st_size > int(max_bytes):
        status["blocked_reason"] = "forecast_records_exceeds_max_bytes"
        return status
    records: list[Any] = []
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            for line in fh:
                text = line.strip()
                if not text:
                    continue
                records.append(json.loads(text))
    except Exception as exc:  # noqa: BLE001 - read-only diagnostic
        status["blocked_reason"] = "forecast_records_jsonl_load_failed:" + exc.__class__.__name__
        status["record_count"] = len(records)
        status["records"] = records
        return status
    status["ok"] = True
    status["record_count"] = len(records)
    status["records"] = records
    return status


def _q23d_legacy_generated_at(payload: Mapping[str, Any]) -> str:
    batch = _as_mapping(payload.get("forecast_batch"))
    return _clean(batch.get("generated_at") or payload.get("generated_at"))


def _q23d_distributed_payload_from_sidecars(*, root: Path, manifest_payload: Mapping[str, Any], max_bytes: int) -> dict[str, Any]:
    sidecars = _as_mapping(manifest_payload.get("sidecars"))
    required = ("summary", "forecast_batch_summary", "forecast_records", "safety")
    blockers: list[str] = []
    for key in required:
        rel = _clean(sidecars.get(key))
        if not rel:
            blockers.append(f"sidecar_path_missing:{key}")
        elif not _q23d_relative_path_safe(rel):
            blockers.append(f"sidecar_path_unsafe:{key}")
    if blockers:
        return {"ok": False, "blocked_reasons": blockers, "payload": {}}

    summary_status = _q23d_read_json_object_status(_q23d_resolve_relative(root, _clean(sidecars.get("summary"))), max_bytes=max_bytes)
    batch_status = _q23d_read_json_object_status(_q23d_resolve_relative(root, _clean(sidecars.get("forecast_batch_summary"))), max_bytes=max_bytes)
    safety_status = _q23d_read_json_object_status(_q23d_resolve_relative(root, _clean(sidecars.get("safety"))), max_bytes=max_bytes)
    records_status = _q23d_read_jsonl_records_status(_q23d_resolve_relative(root, _clean(sidecars.get("forecast_records"))))
    for label, status in (
        ("summary", summary_status),
        ("forecast_batch_summary", batch_status),
        ("safety", safety_status),
        ("forecast_records", records_status),
    ):
        if status.get("ok") is not True:
            blockers.append(f"sidecar_load_failed:{label}:{status.get('blocked_reason')}")
    if blockers:
        return {"ok": False, "blocked_reasons": blockers, "payload": {}}

    summary = _as_mapping(summary_status.get("payload"))
    batch_summary = _as_mapping(batch_status.get("payload"))
    safety = _as_mapping(safety_status.get("payload"))
    records = _as_list(records_status.get("records"))
    record_count = len(records)
    for label, value in (
        ("latest_manifest", manifest_payload.get("record_count")),
        ("summary", summary.get("record_count")),
        ("forecast_batch_summary", batch_summary.get("record_count")),
    ):
        expected = _to_int(value)
        if expected is not None and expected != record_count:
            blockers.append(f"record_count_mismatch:{label}")
    if blockers:
        return {"ok": False, "blocked_reasons": blockers, "payload": {}}

    generated_at = _clean(manifest_payload.get("generated_at") or summary.get("generated_at") or batch_summary.get("generated_at"))
    payload = {
        "generated_at": generated_at,
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": safety.get("broker_execution_requested") is True,
        "command_ledger_append_requested": safety.get("command_ledger_append_requested") is True,
        "approval_append_requested": safety.get("approval_append_requested") is True,
        "forecast_batch": {
            "generated_at": generated_at,
            "read_only": True,
            "non_executing": True,
            "family_count": batch_summary.get("family_count") or summary.get("family_count"),
            "horizon_count": batch_summary.get("horizon_count") or summary.get("horizon_count"),
            "record_count": record_count,
            "records": records,
        },
    }
    return {
        "ok": True,
        "blocked_reasons": [],
        "payload": payload,
        "record_count": record_count,
        "generated_at": generated_at,
        "sidecar_paths": dict(sidecars),
    }


def _q23d_generated_at_is_older(left: Any, right: Any) -> bool:
    left_dt = _parse_utc(left)
    right_dt = _parse_utc(right)
    if left_dt is None or right_dt is None:
        return False
    return left_dt < right_dt


def load_latest_prediction_payload_status_manifest_first(
    *,
    hot_latest_root_hint: str | Path | None = None,
    max_bytes: int = DEFAULT_MAX_ARTIFACT_BYTES,
    prefer_distributed: bool = True,
) -> dict[str, Any]:
    root = Path(str(hot_latest_root_hint).rstrip("\\/")) if hot_latest_root_hint else core_paths.runtime_root(ensure=False)
    legacy_path = root / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    manifest_path = root / LATEST_MANIFEST_RELATIVE_PATH
    legacy_status = load_latest_prediction_payload_status(path=legacy_path, max_bytes=max_bytes)
    legacy_payload = legacy_status.get("payload") if isinstance(legacy_status.get("payload"), dict) else {}
    legacy_generated_at = _q23d_legacy_generated_at(_as_mapping(legacy_payload))
    manifest_status = _q23d_read_json_object_status(manifest_path, max_bytes=max_bytes) if prefer_distributed else {
        "ok": False,
        "blocked_reason": "distributed_preference_disabled",
        "payload": {},
    }

    distributed_status: dict[str, Any] = {
        "ok": False,
        "blocked_reasons": [],
        "payload": {},
        "generated_at": "",
        "record_count": 0,
    }
    if manifest_status.get("ok") is True:
        manifest_payload = _as_mapping(manifest_status.get("payload"))
        run_dir = _clean(manifest_payload.get("run_dir"))
        if not _q23d_relative_path_safe(run_dir):
            distributed_status = {"ok": False, "blocked_reasons": ["latest_manifest_run_dir_unsafe"], "payload": {}, "generated_at": "", "record_count": 0}
        else:
            distributed_status = _q23d_distributed_payload_from_sidecars(root=root, manifest_payload=manifest_payload, max_bytes=max_bytes)
    elif prefer_distributed:
        distributed_status["blocked_reasons"] = [_clean(manifest_status.get("blocked_reason") or "latest_manifest_unavailable")]

    distributed_ready = distributed_status.get("ok") is True
    legacy_ready = legacy_status.get("ok") is True
    distributed_generated_at = _clean(distributed_status.get("generated_at"))
    stale_vs_legacy = bool(distributed_ready and legacy_ready and _q23d_generated_at_is_older(distributed_generated_at, legacy_generated_at))
    warning_reason_codes: list[str] = []
    if stale_vs_legacy:
        warning_reason_codes.append("distributed_artifact_older_than_legacy_latest")

    if distributed_ready and not stale_vs_legacy:
        selected_payload = _as_mapping(distributed_status.get("payload"))
        source_mode = "distributed"
        source_relative = LATEST_MANIFEST_RELATIVE_PATH
        source_path = manifest_path
        ok = True
        blocked_reason = ""
    elif legacy_ready:
        selected_payload = _as_mapping(legacy_payload)
        source_mode = "legacy_fallback"
        source_relative = LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
        source_path = legacy_path
        ok = True
        blocked_reason = ""
    else:
        selected_payload = {}
        source_mode = "blocked"
        source_relative = LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
        source_path = legacy_path
        ok = False
        blocked_reason = "distributed_and_legacy_unavailable"

    return {
        "ok": ok,
        "source_artifact_mode": source_mode,
        "source_artifact_relative_path": source_relative,
        "source_artifact_path": str(source_path),
        "payload": dict(selected_payload),
        "blocked_reason": blocked_reason,
        "warning_reason_codes": warning_reason_codes,
        "distributed_reader_ready": distributed_ready,
        "legacy_fallback_ready": legacy_ready,
        "distributed_stale_vs_legacy": stale_vs_legacy,
        "distributed_generated_at": distributed_generated_at,
        "legacy_generated_at": legacy_generated_at,
        "distributed_status": distributed_status,
        "legacy_status": legacy_status,
        "manifest_status": manifest_status,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "runtime_artifact_write_enabled": False,
        "would_send_to_broker": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
    }


def load_latest_prediction_warroom_read_model_manifest_first(
    *,
    now_utc: str | None = None,
    hot_latest_root_hint: str | Path | None = None,
    prefer_distributed: bool = True,
) -> dict[str, Any]:
    payload_status = load_latest_prediction_payload_status_manifest_first(
        hot_latest_root_hint=hot_latest_root_hint,
        prefer_distributed=prefer_distributed,
    )
    payload = payload_status.get("payload") if isinstance(payload_status.get("payload"), dict) else {}
    market_state = load_latest_market_state(exchange="bitflyer", symbol_raw="FX_BTC_JPY")
    market_diag = market_state_diagnostics(exchange="bitflyer", symbol_raw="FX_BTC_JPY")
    read_model = build_latest_prediction_warroom_read_model(
        payload=payload,
        market_state=market_state,
        market_diag=market_diag,
        now_utc=now_utc,
        source_path=str(payload_status.get("source_artifact_path") or ""),
    )
    read_model["payload_load_ok"] = payload_status.get("ok") is True
    read_model["payload_load_blocked_reason"] = _clean(payload_status.get("blocked_reason"))
    read_model["source_artifact_mode"] = _clean(payload_status.get("source_artifact_mode"))
    read_model["source_artifact_relative_path"] = _clean(payload_status.get("source_artifact_relative_path"))
    read_model["distributed_reader_ready"] = payload_status.get("distributed_reader_ready") is True
    read_model["legacy_fallback_ready"] = payload_status.get("legacy_fallback_ready") is True
    read_model["distributed_stale_vs_legacy"] = payload_status.get("distributed_stale_vs_legacy") is True
    for reason in _as_list(payload_status.get("warning_reason_codes")):
        if str(reason) not in read_model.setdefault("warning_reason_codes", []):
            read_model["warning_reason_codes"].append(str(reason))
    read_model["latest_manifest_written"] = False
    read_model["run_sidecars_written"] = False
    read_model["latest_prediction_artifact_written"] = False
    read_model["status_artifact_written"] = False
    read_model["runtime_artifact_write_enabled"] = False
    read_model["would_send_to_broker"] = False
    read_model["broker_private_api_allowed"] = False
    read_model["autotrade_trigger_allowed"] = False
    return read_model

