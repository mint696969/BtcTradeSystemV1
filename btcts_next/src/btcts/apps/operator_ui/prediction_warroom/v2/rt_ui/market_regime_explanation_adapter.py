# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_explanation_adapter.py
# desc: Read-only MarketRegime explanation adapter. Normalizes persisted artifacts for WarRoom without inference, confidence recalculation, writes, or broker/AutoTrade actions.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

MARKET_REGIME_EXPLANATION_ADAPTER_VERSION = "warroom.market_regime.explanation_adapter.2026_07_11.v1"

LATEST_CARDS_RELATIVE_PATH = "prediction/market_regime/latest_cards.json"
LATEST_READ_MODEL_RELATIVE_PATH = "prediction/market_regime/latest_read_model.json"
CALIBRATION_READ_MODEL_RELATIVE_PATH = "prediction/market_regime/calibration/latest_read_model.json"
SOURCE_SCORECARD_RELATIVE_PATH = "prediction/market_regime/source_scorecard/latest_current_primary.json"
PARAMETER_SET_COMPARISON_RELATIVE_PATH = "prediction/market_regime/parameter_set_comparison/latest_read_model.json"

ARTIFACT_MAX_BYTES: dict[str, int] = {
    LATEST_CARDS_RELATIVE_PATH: 2_000_000,
    LATEST_READ_MODEL_RELATIVE_PATH: 2_000_000,
    CALIBRATION_READ_MODEL_RELATIVE_PATH: 1_000_000,
    SOURCE_SCORECARD_RELATIVE_PATH: 1_000_000,
    PARAMETER_SET_COMPARISON_RELATIVE_PATH: 1_000_000,
}

_FORBIDDEN_TRUE_SAFETY_KEYS = {
    "broker_private_api_allowed",
    "autotrade_trigger_allowed",
    "order_intent_submitted",
    "parameter_auto_promotion_allowed",
    "live_parameter_apply_allowed",
    "would_send_to_broker",
    "classifier_invoked",
    "prediction_invoked",
    "raw_market_data_read",
    "raw_market_source_read_performed",
    "runtime_artifact_write_allowed",
    "writes_dhot",
}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _texts(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value is None or value == "":
        return []
    return [str(value)]


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        text = str(value).strip()
        if not text:
            return None
        number = float(text)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return None


def _int(value: Any, default: int = 0) -> int:
    number = _number(value)
    return int(number) if number is not None else default


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _read_json_artifact(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    packet: dict[str, Any] = {
        "relative_path": relative_path,
        "path": str(path),
        "present": False,
        "used": False,
        "size_bytes": 0,
        "error": "",
        "payload": {},
    }
    try:
        if not path.exists():
            packet["error"] = "artifact_missing"
            return packet
        size = path.stat().st_size
        packet["present"] = True
        packet["size_bytes"] = size
        max_bytes = ARTIFACT_MAX_BYTES[relative_path]
        if size > max_bytes:
            packet["error"] = f"artifact_too_large:{size}>{max_bytes}"
            return packet
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            packet["error"] = "artifact_not_object"
            return packet
        packet["payload"] = dict(payload)
        packet["used"] = True
        return packet
    except json.JSONDecodeError as exc:
        packet["error"] = f"artifact_json_invalid:{exc.__class__.__name__}"
        return packet
    except OSError as exc:
        packet["error"] = f"artifact_read_failed:{exc.__class__.__name__}"
        return packet


def _collect_safety_violations(value: Any, *, prefix: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in _FORBIDDEN_TRUE_SAFETY_KEYS and child is True:
                violations.append(child_prefix)
            violations.extend(_collect_safety_violations(child, prefix=child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(_collect_safety_violations(child, prefix=f"{prefix}[{index}]"))
    return violations


def _card_horizon_key(card: Mapping[str, Any]) -> str:
    for key in ("horizon_key", "horizon", "horizon_sec"):
        value = card.get(key)
        if value is not None and str(value):
            return str(value)
    return ""


def _read_model_horizon_key(row: Mapping[str, Any]) -> str:
    for key in ("horizon_key", "horizon", "horizon_sec"):
        value = row.get(key)
        if value is not None and str(value):
            return str(value)
    diagnostic = _mapping(row.get("diagnostic_record"))
    shadow = _mapping(diagnostic.get("shadow_confidence"))
    value = shadow.get("horizon_key")
    return str(value) if value is not None else ""


def _scorecard_maps(payload: Mapping[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    progress = {
        str(row.get("source_id") or ""): row
        for row in _rows(payload.get("source_progress"))
        if str(row.get("source_id") or "")
    }
    scorecards = {
        str(row.get("source_id") or row.get("key") or ""): row
        for row in _rows(payload.get("source_scorecards"))
        if str(row.get("source_id") or row.get("key") or "")
    }
    return progress, scorecards


def _source_direction(source_row: Mapping[str, Any], progress: Mapping[str, Any]) -> str:
    if progress and not bool(progress.get("ready", False)):
        return "not_ready"
    direction = str(source_row.get("direction") or "").strip().lower()
    if not direction or direction in {"unknown", "unavailable", "none"}:
        return "unavailable"
    if bool(source_row.get("aligned_with_prediction")):
        return "supporting"
    if _int(source_row.get("signal_strength_percent")) <= 0:
        return "neutral"
    return "contradicting"


def _normalize_sources(horizon: Mapping[str, Any], scorecard_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    diagnostic = _mapping(horizon.get("diagnostic_record"))
    shadow = _mapping(diagnostic.get("shadow_confidence"))
    estimator = _mapping(shadow.get("estimator"))
    current_rows = _rows(estimator.get("source_rows"))
    progress_map, scorecard_map = _scorecard_maps(scorecard_payload)

    source_ids = _dedupe(
        [str(row.get("source_id") or "") for row in current_rows]
        + list(progress_map)
        + list(scorecard_map)
    )
    current_map = {
        str(row.get("source_id") or ""): row
        for row in current_rows
        if str(row.get("source_id") or "")
    }

    normalized: list[dict[str, Any]] = []
    for source_id in source_ids:
        current = current_map.get(source_id, {})
        progress = progress_map.get(source_id, {})
        scorecard = scorecard_map.get(source_id, {})
        minimum = _int(
            progress.get("minimum_trusted_sample_count"),
            _int(scorecard.get("minimum_trusted_sample_count"), _int(scorecard_payload.get("minimum_trusted_sample_count"), 0)),
        )
        trusted = _int(progress.get("trusted_sample_count"), _int(scorecard.get("trusted_sample_count"), 0))
        ready = bool(progress.get("ready", trusted >= minimum if minimum else False))
        remaining = _int(progress.get("remaining_trusted_samples"), max(minimum - trusted, 0))
        normalized.append(
            {
                "source_id": source_id,
                "direction": _source_direction(current, progress),
                "configured_weight_percent": _number(current.get("weight_percent")),
                "current_signal_strength_percent": _number(current.get("signal_strength_percent")),
                "current_quality_score_percent": _number(current.get("quality_score_percent")),
                "current_weighted_numerator": _number(current.get("weighted_contribution")),
                "current_quality_percent": _number(current.get("quality_percent")),
                "current_freshness_percent": _number(current.get("freshness_percent")),
                "included_in_confidence": bool(current.get("included_in_confidence", False)),
                "historical_reliability_percent": _number(scorecard.get("reliability_percent")),
                "historical_calibration_score": _number(scorecard.get("calibration_score")),
                "historical_supporting_count": _int(scorecard.get("supporting_count")),
                "historical_contradicting_count": _int(scorecard.get("contradicting_count")),
                "trusted_sample_count": trusted,
                "minimum_trusted_sample_count": minimum,
                "remaining_trusted_samples": remaining,
                "ready": ready,
                "not_ready_reason": "minimum_trusted_samples_not_met" if not ready else "",
            }
        )
    return normalized


def _calibration_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    trust = _mapping(payload.get("calibration_trust"))
    current = _mapping(payload.get("primary_current"))
    current_counts = _mapping(current.get("counts"))
    compatibility = _mapping(payload.get("primary"))
    compatibility_counts = _mapping(compatibility.get("counts"))
    legacy = _mapping(payload.get("trusted_legacy_reference"))
    legacy_counts = _mapping(legacy.get("counts"))

    return {
        "available": bool(current),
        "cohort": "primary_current",
        "cohort_started_at": str(trust.get("current_primary_cohort_started_at") or ""),
        "observation_source": str(payload.get("primary_observation_source") or trust.get("primary_observation_source") or ""),
        "score": _number(current.get("calibration_score")),
        "sample_count": _int(current.get("known_total")),
        "counts": {
            "hit": _int(current_counts.get("hit")),
            "partial": _int(current_counts.get("partial")),
            "miss": _int(current_counts.get("miss")),
            "unknown": _int(current_counts.get("unknown")),
            "invalidated": _int(current_counts.get("invalidated")),
        },
        "interpretation": "not_win_rate",
        "selection_reason": "primary_current_is_canonical_for_current_logic",
        "fallback_used": False,
        "unavailable_reason": "" if current else "primary_current_missing",
        "compatibility_reference": {
            "available": bool(compatibility),
            "cohort": str(compatibility.get("key") or "primary"),
            "score": _number(compatibility.get("calibration_score")),
            "sample_count": _int(compatibility.get("known_total")),
            "counts": {
                "hit": _int(compatibility_counts.get("hit")),
                "partial": _int(compatibility_counts.get("partial")),
                "miss": _int(compatibility_counts.get("miss")),
                "unknown": _int(compatibility_counts.get("unknown")),
                "invalidated": _int(compatibility_counts.get("invalidated")),
            },
        },
        "trusted_legacy_reference": {
            "available": bool(legacy),
            "cohort": str(legacy.get("key") or "trusted_legacy_reference"),
            "score": _number(legacy.get("calibration_score")),
            "sample_count": _int(legacy.get("known_total")),
            "counts": {
                "hit": _int(legacy_counts.get("hit")),
                "partial": _int(legacy_counts.get("partial")),
                "miss": _int(legacy_counts.get("miss")),
                "unknown": _int(legacy_counts.get("unknown")),
                "invalidated": _int(legacy_counts.get("invalidated")),
            },
        },
    }


def _parameter_set_summary(payload: Mapping[str, Any], horizon: Mapping[str, Any]) -> dict[str, Any]:
    trust = _mapping(payload.get("calibration_trust"))
    active = str(payload.get("active_parameter_set_id") or horizon.get("active_parameter_set_id") or "")
    trusted_count = _int(trust.get("trusted_parameter_set_count"))
    comparison_ready = bool(payload.get("comparison_ready", False)) and trusted_count >= 2
    blockers = _texts(payload.get("comparison_blockers"))
    if trusted_count < 2 and "insufficient_parameter_sets" not in blockers:
        blockers.append("insufficient_parameter_sets")
    return {
        "active_parameter_set_id": active,
        "trusted_parameter_set_count": trusted_count,
        "comparable_parameter_set_count": _int(trust.get("comparable_parameter_set_count")),
        "comparison_ready": comparison_ready,
        "comparison_blockers": _dedupe(blockers),
        "best_parameter_set_claim_allowed": False,
        "promotion_recommendation_allowed": False,
        "auto_promotion_allowed": False,
    }


def _horizon_packet(
    card: Mapping[str, Any],
    horizon: Mapping[str, Any],
    calibration_payload: Mapping[str, Any],
    scorecard_payload: Mapping[str, Any],
    parameter_payload: Mapping[str, Any],
) -> dict[str, Any]:
    diagnostic = _mapping(horizon.get("diagnostic_record"))
    shadow = _mapping(diagnostic.get("shadow_confidence"))
    estimator = _mapping(shadow.get("estimator"))
    detail = _mapping(card.get("detail"))

    blockers = _dedupe(
        _texts(horizon.get("blockers"))
        + _texts(detail.get("blocker_lines"))
        + _texts(estimator.get("blockers"))
        + _texts(shadow.get("currentness_gate_blockers"))
    )
    warnings = _dedupe(
        _texts(horizon.get("conflicts"))
        + _texts(horizon.get("warnings"))
        + _texts(detail.get("warning_lines"))
    )
    sources = _normalize_sources(horizon, scorecard_payload)

    display_confidence = _number(card.get("confidence_percent"))
    if display_confidence is None:
        display_confidence = _number(horizon.get("confidence_percent"))
    shadow_confidence = _number(shadow.get("shadow_display_confidence_percent"))

    return {
        "horizon_key": _card_horizon_key(card) or _read_model_horizon_key(horizon),
        "card": {
            "label": str(card.get("regime_code") or horizon.get("regime_code") or horizon.get("label") or ""),
            "label_ja": str(card.get("regime_label") or horizon.get("regime_label") or ""),
            "display_confidence_percent": display_confidence,
            "short_tag": str(card.get("short_tag_label") or ""),
            "freshness_badge": str(card.get("freshness_badge") or ""),
        },
        "confidence": {
            "display_confidence_percent": display_confidence,
            "legacy_confidence_percent": _number(shadow.get("legacy_confidence_percent")),
            "shadow_confidence_percent": shadow_confidence,
            "shadow_only": bool(_mapping(shadow.get("safety")).get("shadow_only", True)),
            "display_replaced": bool(diagnostic.get("display_confidence_replaced", False)),
            "cap_percent": _number(estimator.get("applied_confidence_cap_percent")),
            "cap_reasons": _texts(estimator.get("blockers")),
            "estimated_signal_strength_percent": _number(diagnostic.get("selected_signal_strength_percent")),
            "explanation": "card confidence is market-regime reading confidence, not win rate",
        },
        "evidence": {
            "quality_reason": str(diagnostic.get("selected_evidence_quality_reason") or ""),
            "label_selection_reason": str(diagnostic.get("label_selection_reason") or ""),
            "selected_label_source": str(diagnostic.get("selected_label_source") or ""),
            "available_signal_count": _int(diagnostic.get("available_signal_count")),
            "supporting_source_count": sum(1 for row in sources if row["direction"] == "supporting"),
            "contradicting_source_count": sum(1 for row in sources if row["direction"] == "contradicting"),
        },
        "sources": sources,
        "blockers": blockers,
        "warnings": warnings,
        "fallbacks": [reason for reason in [str(diagnostic.get("label_selection_reason") or "")] if "fallback" in reason],
        "calibration": _calibration_summary(calibration_payload),
        "parameter_set": _parameter_set_summary(parameter_payload, horizon),
        "trace": {
            "run_id": str(card.get("run_id") or horizon.get("run_id") or ""),
            "prediction_id": str(card.get("prediction_id") or horizon.get("prediction_id") or ""),
            "trace_refs": _dedupe(_texts(card.get("trace_refs")) + _texts(horizon.get("trace_refs"))),
        },
        "safety": {
            "read_only": True,
            "prediction_invoked": False,
            "classifier_invoked": False,
            "raw_market_read": False,
            "confidence_recalculated": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def build_market_regime_explanation_packet(root: Path) -> dict[str, Any]:
    """Read persisted artifacts and return one normalized, immutable-display packet.

    This function performs file reads and normalization only. It does not invoke prediction,
    classification, confidence estimation, calibration, persistence, subprocesses, broker APIs,
    AutoTrade, or parameter mutation.
    """

    root = Path(root)
    artifacts = {
        "latest_cards": _read_json_artifact(root, LATEST_CARDS_RELATIVE_PATH),
        "latest_read_model": _read_json_artifact(root, LATEST_READ_MODEL_RELATIVE_PATH),
        "calibration": _read_json_artifact(root, CALIBRATION_READ_MODEL_RELATIVE_PATH),
        "source_scorecard": _read_json_artifact(root, SOURCE_SCORECARD_RELATIVE_PATH),
        "parameter_set_comparison": _read_json_artifact(root, PARAMETER_SET_COMPARISON_RELATIVE_PATH),
    }

    latest_cards_payload = _mapping(artifacts["latest_cards"].get("payload"))
    read_model_payload = _mapping(artifacts["latest_read_model"].get("payload"))
    calibration_payload = _mapping(artifacts["calibration"].get("payload"))
    scorecard_payload = _mapping(artifacts["source_scorecard"].get("payload"))
    parameter_payload = _mapping(artifacts["parameter_set_comparison"].get("payload"))

    cards = _rows(latest_cards_payload.get("cards"))
    horizons = _rows(read_model_payload.get("horizons"))
    card_map = {_card_horizon_key(card): card for card in cards if _card_horizon_key(card)}
    horizon_map = {_read_model_horizon_key(row): row for row in horizons if _read_model_horizon_key(row)}
    horizon_keys = _dedupe(list(card_map) + list(horizon_map))

    safety_violations: list[str] = []
    for artifact_name, artifact in artifacts.items():
        payload = artifact.get("payload")
        safety_violations.extend(
            f"{artifact_name}:{path}" for path in _collect_safety_violations(payload)
        )

    normalized_horizons = [
        _horizon_packet(
            card_map.get(horizon_key, {}),
            horizon_map.get(horizon_key, {}),
            calibration_payload,
            scorecard_payload,
            parameter_payload,
        )
        for horizon_key in horizon_keys
    ]

    required_ok = artifacts["latest_cards"]["used"] and artifacts["latest_read_model"]["used"]
    return {
        "ok": bool(required_ok and normalized_horizons and not safety_violations),
        "adapter_version": MARKET_REGIME_EXPLANATION_ADAPTER_VERSION,
        "artifact_root": str(root),
        "generated_at": str(read_model_payload.get("generated_at") or latest_cards_payload.get("generated_at") or ""),
        "horizon_count": len(normalized_horizons),
        "horizons": normalized_horizons,
        "artifact_status": {
            name: {
                "relative_path": artifact["relative_path"],
                "present": artifact["present"],
                "used": artifact["used"],
                "size_bytes": artifact["size_bytes"],
                "error": artifact["error"],
            }
            for name, artifact in artifacts.items()
        },
        "safety_violations": _dedupe(safety_violations),
        "safety": {
            "read_only": True,
            "writes_dhot": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
            "raw_market_read": False,
            "confidence_recalculated": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }
