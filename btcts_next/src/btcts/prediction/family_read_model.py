# path: ./btcts_next/src/btcts/prediction/family_read_model.py
# desc: Family-neutral prediction read-model and receive-only push contracts. Pure builders and validators; no family inference, UI, persistence, broker, or AutoTrade side effects.

from __future__ import annotations

from typing import Any, Iterable, Mapping

PREDICTION_FAMILY_READ_MODEL_CONTRACT_VERSION = "prediction.family_read_model.2026_07_11.v1"
PREDICTION_FAMILY_PUSH_MESSAGE_CONTRACT_VERSION = "prediction.family_push_message.2026_07_11.v1"

_MAX_HORIZON_ROWS = 16
_MAX_TEXT_ITEMS = 32
_MAX_REF_ITEMS = 32
_MAX_FAMILY_PAYLOAD_KEYS = 16
_MAX_TEXT_LENGTH = 512
_FORBIDDEN_RAW_KEYS = {
    "raw_candles", "raw_orderbook", "raw_trades", "raw_executions",
    "raw_market_payload", "raw_source_payload", "bids", "asks",
    "trades", "executions", "candles", "orderbook",
}
_REQUIRED_FALSE_SAFETY = (
    "raw_market_payload_included",
    "ui_render_invokes_prediction",
    "ui_render_invokes_classifier",
    "ui_confidence_recalculation",
    "broker_private_api_allowed",
    "autotrade_trigger_allowed",
    "order_intent_submitted",
    "parameter_auto_promotion_allowed",
    "live_parameter_apply_allowed",
    "would_send_to_broker",
)


def _text(value: object) -> str:
    return str(value or "")[:_MAX_TEXT_LENGTH]


def _text_list(value: Iterable[object] | None) -> list[str]:
    return [_text(item) for item in list(value or [])[:_MAX_TEXT_ITEMS] if _text(item)]


def _refs(value: Iterable[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    return [dict(item) for item in list(value or [])[:_MAX_REF_ITEMS] if isinstance(item, Mapping)]


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bounded_percent(value: object) -> int:
    return max(0, min(99, _safe_int(value)))


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key) in _FORBIDDEN_RAW_KEYS or _has_forbidden_raw_keys(nested)
            for key, nested in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def _safety() -> dict[str, bool]:
    safety = {key: False for key in _REQUIRED_FALSE_SAFETY}
    safety.update({"read_only": True, "non_executing": True})
    return safety


def _build_horizon_row(row: Mapping[str, Any]) -> dict[str, Any]:
    payload = row.get("family_payload") if isinstance(row.get("family_payload"), Mapping) else {}
    bounded_payload = {
        _text(key): value
        for key, value in list(payload.items())[:_MAX_FAMILY_PAYLOAD_KEYS]
        if _text(key)
    }
    return {
        "horizon_key": _text(row.get("horizon_key")),
        "horizon_sec": max(0, _safe_int(row.get("horizon_sec"))),
        "horizon_group": _text(row.get("horizon_group")),
        "primary_label": _text(row.get("primary_label") or "unknown"),
        "primary_label_display": _text(row.get("primary_label_display") or row.get("primary_label") or "unknown"),
        "confidence_percent": _bounded_percent(row.get("confidence_percent")),
        "confidence_kind": _text(row.get("confidence_kind") or "heuristic_support"),
        "freshness_state": _text(row.get("freshness_state") or "unknown"),
        "evidence_quality": _text(row.get("evidence_quality") or "unknown"),
        "drivers": _text_list(row.get("drivers") if isinstance(row.get("drivers"), (list, tuple)) else []),
        "blockers": _text_list(row.get("blockers") if isinstance(row.get("blockers"), (list, tuple)) else []),
        "warnings": _text_list(row.get("warnings") if isinstance(row.get("warnings"), (list, tuple)) else []),
        "invalidation_hints": _text_list(row.get("invalidation_hints") if isinstance(row.get("invalidation_hints"), (list, tuple)) else []),
        "source_refs": _refs(row.get("source_refs") if isinstance(row.get("source_refs"), (list, tuple)) else []),
        "trace_refs": _refs(row.get("trace_refs") if isinstance(row.get("trace_refs"), (list, tuple)) else []),
        "outcome_refs": _refs(row.get("outcome_refs") if isinstance(row.get("outcome_refs"), (list, tuple)) else []),
        "calibration_refs": _refs(row.get("calibration_refs") if isinstance(row.get("calibration_refs"), (list, tuple)) else []),
        "scenario_part_ref": dict(row.get("scenario_part_ref")) if isinstance(row.get("scenario_part_ref"), Mapping) else {},
        "family_payload": bounded_payload,
    }


def build_prediction_family_read_model(
    *,
    prediction_family_id: str,
    generated_at: str,
    run_id: str,
    prediction_id: str,
    logic_version: str,
    parameter_set_id: str,
    horizon_rows: Iterable[Mapping[str, Any]],
    model_id: str = "",
    feature_set_version: str = "",
    target_definition_version: str = "",
    training_window_ref: str = "",
    evaluation_window_ref: str = "",
) -> dict[str, Any]:
    rows = [_build_horizon_row(row) for row in list(horizon_rows)[:_MAX_HORIZON_ROWS] if isinstance(row, Mapping)]
    model = {
        "schema_version": "prediction_family_read_model.2026_07_11.v1",
        "contract_version": PREDICTION_FAMILY_READ_MODEL_CONTRACT_VERSION,
        "artifact_family": "prediction/family_read_models",
        "artifact_kind": "prediction_family_read_model",
        "prediction_family_id": _text(prediction_family_id),
        "generated_at": _text(generated_at),
        "run_id": _text(run_id),
        "prediction_id": _text(prediction_id),
        "model_id": _text(model_id),
        "logic_version": _text(logic_version),
        "parameter_set_id": _text(parameter_set_id),
        "feature_set_version": _text(feature_set_version),
        "target_definition_version": _text(target_definition_version),
        "training_window_ref": _text(training_window_ref),
        "evaluation_window_ref": _text(evaluation_window_ref),
        "horizon_rows": rows,
        "horizon_count": len(rows),
        "safety": _safety(),
    }
    validation = validate_prediction_family_read_model(model)
    if not validation["ok"]:
        raise ValueError(f"prediction family read-model validation failed: {validation}")
    return model


def validate_prediction_family_read_model(model: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if model.get("artifact_kind") != "prediction_family_read_model":
        failures.append("artifact_kind_mismatch")
    for key in ("prediction_family_id", "generated_at", "run_id", "prediction_id", "logic_version", "parameter_set_id"):
        if not _text(model.get(key)):
            failures.append(f"{key}_missing")
    rows = model.get("horizon_rows") if isinstance(model.get("horizon_rows"), list) else []
    if not rows:
        failures.append("horizon_rows_missing")
    if len(rows) > _MAX_HORIZON_ROWS:
        failures.append("horizon_rows_over_limit")
    if _safe_int(model.get("horizon_count"), -1) != len(rows):
        failures.append("horizon_count_mismatch")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            failures.append(f"horizon_row_{index}_not_mapping")
            continue
        key = _text(row.get("horizon_key"))
        if not key:
            failures.append(f"horizon_row_{index}_key_missing")
        elif key in seen:
            failures.append(f"horizon_row_{index}_duplicate_key")
        seen.add(key)
        if _safe_int(row.get("horizon_sec")) < 0:
            failures.append(f"horizon_row_{index}_negative_sec")
        percent = _safe_int(row.get("confidence_percent"), -1)
        if not 0 <= percent <= 99:
            failures.append(f"horizon_row_{index}_confidence_out_of_range")
        payload = row.get("family_payload") if isinstance(row.get("family_payload"), Mapping) else {}
        if len(payload) > _MAX_FAMILY_PAYLOAD_KEYS:
            failures.append(f"horizon_row_{index}_family_payload_over_limit")
    if _has_forbidden_raw_keys(model):
        failures.append("forbidden_raw_payload_key_present")
    safety = model.get("safety") if isinstance(model.get("safety"), Mapping) else {}
    if safety.get("read_only") is not True:
        failures.append("safety_read_only_not_true")
    if safety.get("non_executing") is not True:
        failures.append("safety_non_executing_not_true")
    for key in _REQUIRED_FALSE_SAFETY:
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    return {
        "ok": not failures,
        "contract_version": PREDICTION_FAMILY_READ_MODEL_CONTRACT_VERSION,
        "failure_count": len(failures),
        "failures": failures,
    }


def build_prediction_family_push_message(
    *,
    topic_key: str,
    value: Mapping[str, Any],
    received_at_ms: int,
    sequence: int | None = None,
) -> dict[str, Any]:
    validation = validate_prediction_family_read_model(value)
    if not validation["ok"]:
        raise ValueError(f"invalid prediction family read model: {validation}")
    message = {
        "schema_version": "prediction_family_push_message.2026_07_11.v1",
        "contract_version": PREDICTION_FAMILY_PUSH_MESSAGE_CONTRACT_VERSION,
        "message_kind": "prediction_family_read_model",
        "topic_key": _text(topic_key),
        "receive_only": True,
        "received_at_ms": max(0, _safe_int(received_at_ms)),
        "sequence": None if sequence is None else max(0, _safe_int(sequence)),
        "value": dict(value),
        "safety": _safety(),
    }
    push_validation = validate_prediction_family_push_message(message)
    if not push_validation["ok"]:
        raise ValueError(f"prediction family push validation failed: {push_validation}")
    return message


def validate_prediction_family_push_message(message: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if message.get("message_kind") != "prediction_family_read_model":
        failures.append("message_kind_mismatch")
    if not _text(message.get("topic_key")).startswith("prediction.family."):
        failures.append("topic_key_not_prediction_family")
    if message.get("receive_only") is not True:
        failures.append("receive_only_not_true")
    if _safe_int(message.get("received_at_ms"), -1) < 0:
        failures.append("received_at_ms_invalid")
    value = message.get("value") if isinstance(message.get("value"), Mapping) else {}
    model_validation = validate_prediction_family_read_model(value)
    if not model_validation["ok"]:
        failures.extend(f"value_{item}" for item in model_validation["failures"])
    if _has_forbidden_raw_keys(message):
        failures.append("forbidden_raw_payload_key_present")
    safety = message.get("safety") if isinstance(message.get("safety"), Mapping) else {}
    if safety.get("read_only") is not True:
        failures.append("safety_read_only_not_true")
    if safety.get("non_executing") is not True:
        failures.append("safety_non_executing_not_true")
    for key in _REQUIRED_FALSE_SAFETY:
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    return {
        "ok": not failures,
        "contract_version": PREDICTION_FAMILY_PUSH_MESSAGE_CONTRACT_VERSION,
        "failure_count": len(failures),
        "failures": failures,
    }
