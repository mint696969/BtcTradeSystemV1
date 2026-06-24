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
DEFAULT_MAX_ARTIFACT_BYTES = 5_000_000

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


def latest_prediction_artifact_path() -> Path:
    return core_paths.runtime_root(ensure=False) / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH


def load_latest_prediction_payload(*, path: Path | None = None, max_bytes: int = DEFAULT_MAX_ARTIFACT_BYTES) -> dict[str, Any]:
    target = path or latest_prediction_artifact_path()
    try:
        stat = target.stat()
    except Exception:
        return {}
    if stat.st_size > int(max_bytes):
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def load_latest_prediction_warroom_read_model(
    *,
    now_utc: str | None = None,
    prediction_path: Path | None = None,
) -> dict[str, Any]:
    target = prediction_path or latest_prediction_artifact_path()
    payload = load_latest_prediction_payload(path=target)
    market_state = load_latest_market_state(exchange="bitflyer", symbol_raw="FX_BTC_JPY")
    market_diag = market_state_diagnostics(exchange="bitflyer", symbol_raw="FX_BTC_JPY")
    return build_latest_prediction_warroom_read_model(
        payload=payload,
        market_state=market_state,
        market_diag=market_diag,
        now_utc=now_utc,
        source_path=str(target),
    )
