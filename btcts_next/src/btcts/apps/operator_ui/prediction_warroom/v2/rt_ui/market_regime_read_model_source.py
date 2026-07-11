# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_read_model_source.py
# desc: MR-VS6.4 pure MarketRegime source selector. Validates push and artifact common read models, prefers valid push, falls back to valid artifact, and fails closed otherwise. No I/O, rendering, inference, confidence merge, broker, AutoTrade, or order behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.prediction.family_read_model import (
    build_prediction_family_push_message,
    validate_prediction_family_push_message,
    validate_prediction_family_read_model,
)

MARKET_REGIME_TOPIC_KEY = "prediction.family.market_regime"
MARKET_REGIME_FAMILY_ID = "market_regime"
MARKET_REGIME_READ_MODEL_SOURCE_VERSION = "market_regime.read_model_source.mr_vs6_4.v1"

_MAX_TEXT_LENGTH = 512
_MAX_DEPTH = 8
_MAX_MAPPING_ITEMS = 64
_MAX_LIST_ITEMS = 32


def _text(value: object) -> str:
    return str(value or "")[:_MAX_TEXT_LENGTH]


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bounded_copy(value: Any, *, depth: int = 0, reject_deep_containers: bool = False) -> Any:
    if depth >= _MAX_DEPTH and isinstance(value, (Mapping, list, tuple)):
        if reject_deep_containers:
            raise ValueError("payload_depth_over_limit")
        return None
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:_MAX_MAPPING_ITEMS]:
            bounded_key = _text(key)
            if not bounded_key:
                continue
            result[bounded_key] = _bounded_copy(
                item,
                depth=depth + 1,
                reject_deep_containers=reject_deep_containers,
            )
        return result
    if isinstance(value, (list, tuple)):
        return [
            _bounded_copy(
                item,
                depth=depth + 1,
                reject_deep_containers=reject_deep_containers,
            )
            for item in list(value)[:_MAX_LIST_ITEMS]
        ]
    if isinstance(value, str):
        return value[:_MAX_TEXT_LENGTH]
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return _text(value)


def _model_identity(model: Mapping[str, Any]) -> dict[str, str]:
    return {
        "prediction_generated_at": _text(model.get("generated_at")),
        "run_id": _text(model.get("run_id")),
        "prediction_id": _text(model.get("prediction_id")),
        "parameter_set_id": _text(model.get("parameter_set_id")),
    }


def _validate_market_regime_model(value: Any) -> tuple[bool, dict[str, Any]]:
    if not isinstance(value, Mapping):
        return False, {"ok": False, "failures": ["model_not_mapping"]}
    validation = validate_prediction_family_read_model(value)
    failures = list(validation.get("failures") or [])
    if value.get("prediction_family_id") != MARKET_REGIME_FAMILY_ID:
        failures.append("prediction_family_id_mismatch")
    return not failures, {
        **dict(validation),
        "ok": not failures,
        "failure_count": len(failures),
        "failures": failures,
    }


def _message_from_widget_state(push_state: Mapping[str, Any]) -> Mapping[str, Any]:
    widgets = push_state.get("widgets") if isinstance(push_state.get("widgets"), Mapping) else {}
    widget = widgets.get("market_regime_prediction_widget") if isinstance(widgets.get("market_regime_prediction_widget"), Mapping) else {}
    snapshots = widget.get("snapshots") if isinstance(widget.get("snapshots"), Mapping) else {}
    snapshot = snapshots.get(MARKET_REGIME_TOPIC_KEY) if isinstance(snapshots.get(MARKET_REGIME_TOPIC_KEY), Mapping) else {}
    value = snapshot.get("value") if isinstance(snapshot.get("value"), Mapping) else {}
    if not value:
        return {}
    try:
        return build_prediction_family_push_message(
            topic_key=MARKET_REGIME_TOPIC_KEY,
            value=value,
            received_at_ms=max(0, _safe_int(snapshot.get("updated_at_ms"))),
            sequence=snapshot.get("sequence"),
        )
    except ValueError:
        return {
            "topic_key": MARKET_REGIME_TOPIC_KEY,
            "received_at_ms": max(0, _safe_int(snapshot.get("updated_at_ms"))),
            "sequence": snapshot.get("sequence"),
            "value": value,
        }


def _extract_push_candidate(push_state: Any) -> tuple[bool, bool, Mapping[str, Any], dict[str, Any]]:
    if not isinstance(push_state, Mapping) or not push_state:
        return False, False, {}, {"ok": False, "failures": ["push_missing"]}

    if isinstance(push_state.get("message"), Mapping):
        message = push_state.get("message")
    elif isinstance(push_state.get("widgets"), Mapping):
        message = _message_from_widget_state(push_state)
    else:
        message = push_state
    if not isinstance(message, Mapping) or not message:
        return False, False, {}, {"ok": False, "failures": ["push_missing"]}
    push_validation = validate_prediction_family_push_message(message)
    failures = list(push_validation.get("failures") or [])
    if message.get("topic_key") != MARKET_REGIME_TOPIC_KEY:
        failures.append("topic_key_mismatch")
    model = message.get("value") if isinstance(message.get("value"), Mapping) else {}
    model_valid, model_validation = _validate_market_regime_model(model)
    if not model_valid:
        failures.extend(f"model_{item}" for item in model_validation.get("failures", []))
    valid = not failures
    return True, valid, model if valid else {}, {
        **dict(push_validation),
        "ok": valid,
        "failure_count": len(failures),
        "failures": failures,
        "transport_received_at_ms": max(0, _safe_int(message.get("received_at_ms"))),
    }


def _extract_artifact_candidate(artifact_read_model: Any) -> tuple[bool, bool, Mapping[str, Any], dict[str, Any]]:
    if not isinstance(artifact_read_model, Mapping) or not artifact_read_model:
        return False, False, {}, {"ok": False, "failures": ["artifact_missing"]}
    valid, validation = _validate_market_regime_model(artifact_read_model)
    return True, valid, artifact_read_model if valid else {}, validation


def select_market_regime_read_model_source(
    *,
    push_state: Mapping[str, Any] | None = None,
    artifact_read_model: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Select one validated MarketRegime common read model without merging source values."""
    push_present, push_valid, push_model, push_validation = _extract_push_candidate(push_state)
    artifact_present, artifact_valid, artifact_model, artifact_validation = _extract_artifact_candidate(artifact_read_model)

    selected_source = "unavailable"
    selected_model: Mapping[str, Any] = {}
    fallback_used = False
    fallback_reason = ""

    if push_valid:
        selected_source = "push"
        selected_model = push_model
    elif artifact_valid:
        selected_source = "artifact"
        selected_model = artifact_model
        fallback_used = True
        fallback_reason = "push_invalid" if push_present else "push_missing"
    else:
        if push_present and artifact_present:
            fallback_reason = "push_and_artifact_invalid"
        elif push_present:
            fallback_reason = "push_invalid_artifact_missing"
        elif artifact_present:
            fallback_reason = "push_missing_artifact_invalid"
        else:
            fallback_reason = "push_and_artifact_missing"

    bounding_failure = ""
    try:
        bounded_model = (
            _bounded_copy(selected_model, reject_deep_containers=True)
            if selected_model
            else {}
        )
    except ValueError as exc:
        bounding_failure = _text(exc) or "payload_bounding_failed"
        bounded_model = {}

    bounded_validation: dict[str, Any] = {"ok": True, "failure_count": 0, "failures": []}
    if bounding_failure:
        bounded_valid = False
        bounded_validation = {
            "ok": False,
            "failure_count": 1,
            "failures": [bounding_failure],
        }
    elif bounded_model:
        bounded_valid, bounded_validation = _validate_market_regime_model(bounded_model)
    else:
        bounded_valid = True

    if selected_model and not bounded_valid:
        selected_source = "unavailable"
        fallback_used = False
        fallback_reason = "selected_model_bounding_invalid"
        selected_model = {}
        bounded_model = {}
        if push_valid:
            push_valid = False
            push_validation = {
                **push_validation,
                "ok": False,
                "failures": list(push_validation.get("failures") or [])
                + ["bounded_model_invalid"]
                + list(bounded_validation.get("failures") or []),
            }
        elif artifact_valid:
            artifact_valid = False
            artifact_validation = bounded_validation
    identity = _model_identity(selected_model) if selected_model else {
        "prediction_generated_at": "",
        "run_id": "",
        "prediction_id": "",
        "parameter_set_id": "",
    }

    return {
        "source_adapter_version": MARKET_REGIME_READ_MODEL_SOURCE_VERSION,
        "selected_source": selected_source,
        "push_present": push_present,
        "push_valid": push_valid,
        "artifact_present": artifact_present,
        "artifact_valid": artifact_valid,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "transport_received_at_ms": int(push_validation.get("transport_received_at_ms") or 0),
        **identity,
        "read_model": bounded_model,
        "push_validation": _bounded_copy(push_validation),
        "artifact_validation": _bounded_copy(artifact_validation),
        "confidence_merge_performed": False,
        "confidence_recalculation_performed": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
        "artifact_read_performed": False,
        "render_invoked": False,
        "mount_enabled": False,
        "read_only": True,
        "non_executing": True,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
