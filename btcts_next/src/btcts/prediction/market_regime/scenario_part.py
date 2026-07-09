# path: ./btcts_next/src/btcts/prediction/market_regime/scenario_part.py
# desc: MarketRegime family scenario-part builders. Pure adapters from read models/cards to parent scenario-part contract; no D-hot writes, UI inference, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

from typing import Any, Mapping

from btcts.prediction.scenario_parts import build_prediction_family_scenario_part, validate_prediction_family_scenario_part

MARKET_REGIME_SCENARIO_PART_VERSION = "prediction.market_regime.scenario_part.2026_07_10.v1"

_REGIME_TO_SCENARIO_STATE = {
    "UP_TREND": "bullish",
    "BREAKOUT": "bullish",
    "DOWN_TREND": "bearish",
    "RANGE": "range",
    "LOW_VOL_COMPRESSION": "range",
    "HIGH_VOL_CHOP": "risk_off",
    "PANIC_SPIKE": "risk_off",
    "REVERSAL_WATCH": "conflicting",
    "UNKNOWN": "unknown",
}


def _as_text_list(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _horizon_key_from_item(item: Mapping[str, Any]) -> str:
    if item.get("horizon_key"):
        return str(item.get("horizon_key") or "")
    horizon_sec = _safe_int(item.get("horizon_sec"))
    return "current" if horizon_sec == 0 else f"{horizon_sec}s"


def _horizon_sec_from_key(horizon_key: str) -> int:
    key = str(horizon_key or "")
    if key == "current":
        return 0
    if key.endswith("s"):
        return _safe_int(key[:-1])
    return 0


def _horizon_group(horizon_key: str, horizon_sec: int) -> str:
    key = str(horizon_key or "")
    sec = int(horizon_sec or 0)
    if sec <= 0 and key:
        sec = _horizon_sec_from_key(key)
    if key == "current" or sec == 0:
        return "nowcast"
    if sec <= 900:
        return "short_horizon"
    if sec <= 3600:
        return "mid_horizon"
    return "long_horizon"


def _regime_to_state(regime_code: object) -> str:
    return _REGIME_TO_SCENARIO_STATE.get(str(regime_code or "UNKNOWN").upper(), "unknown")


def _select_item(items: object, *, horizon_key: str = "") -> Mapping[str, Any]:
    if not isinstance(items, list) or not items:
        return {}
    mappings = [item for item in items if isinstance(item, Mapping)]
    if not mappings:
        return {}
    key = str(horizon_key or "")
    if key:
        for item in mappings:
            if _horizon_key_from_item(item) == key:
                return item
        return {}
    return mappings[0]


def _scenario_blockers(item: Mapping[str, Any], *, selected: bool) -> list[str]:
    blockers: list[str] = []
    if not selected:
        blockers.append("market_regime_horizon_not_found")
    if str(item.get("primary_regime") or item.get("regime_code") or "UNKNOWN").upper() == "UNKNOWN":
        blockers.append("market_regime_unknown")
    if _safe_int(item.get("confidence_percent")) <= 0:
        blockers.append("market_regime_confidence_unavailable")
    return blockers


def build_market_regime_scenario_part_from_latest_read_model(
    latest_read_model: Mapping[str, Any],
    *,
    horizon_key: str = "",
) -> dict[str, Any]:
    horizons = latest_read_model.get("horizons") if isinstance(latest_read_model, Mapping) else []
    item = _select_item(horizons, horizon_key=horizon_key)
    selected = bool(item)
    regime_code = str(item.get("primary_regime") or "UNKNOWN") if selected else "UNKNOWN"
    label = str(item.get("primary_regime_label") or item.get("horizon") or "地合い不明") if selected else "地合い不明"
    key = _horizon_key_from_item(item) if selected else str(horizon_key or "unknown_horizon")
    sec = _safe_int(item.get("horizon_sec")) if selected else _horizon_sec_from_key(key)
    drivers = _as_text_list(item.get("drivers"))
    conflicts = _as_text_list(item.get("conflicts"))
    invalidation = _as_text_list(item.get("invalidation"))
    blockers = _scenario_blockers(item, selected=selected)
    part = build_prediction_family_scenario_part(
        prediction_family_id="market_regime",
        horizon_key=key,
        horizon_group=_horizon_group(key, sec),
        scenario_state=_regime_to_state(regime_code),
        scenario_label=label,
        scenario_summary=(
            f"market_regime={regime_code} / label={label} / "
            f"confidence={_safe_int(item.get('confidence_percent'))} / source=latest_read_model / read_only=true"
        ),
        confidence_percent=_safe_int(item.get("confidence_percent")),
        estimated_signal_strength_percent=_safe_int(item.get("confidence_percent")),
        part_role="primary_context",
        drivers=drivers,
        blockers=blockers,
        warnings=conflicts + invalidation,
        evidence_refs=[{
            "artifact_ref": "prediction/market_regime/latest_read_model.json",
            "artifact_kind": str(latest_read_model.get("artifact_kind") or "latest_read_model"),
            "run_id": str(latest_read_model.get("run_id") or ""),
            "scenario_part_builder_version": MARKET_REGIME_SCENARIO_PART_VERSION,
        }],
        source_quality_notes=_as_text_list(latest_read_model.get("conflict_summary")),
        trace_refs=[],
        parameter_set_id=str(item.get("parameter_set_id") or latest_read_model.get("parameter_set_id") or ""),
        generated_at=str(latest_read_model.get("generated_at") or ""),
    )
    validation = validate_market_regime_scenario_part(part)
    if not validation["ok"]:
        raise ValueError(f"market-regime scenario part validation failed: {validation}")
    return part


def build_market_regime_scenario_part_from_latest_cards(
    latest_cards: Mapping[str, Any],
    *,
    horizon_key: str = "",
) -> dict[str, Any]:
    cards = latest_cards.get("cards") if isinstance(latest_cards, Mapping) else []
    item = _select_item(cards, horizon_key=horizon_key)
    selected = bool(item)
    detail = item.get("detail") if isinstance(item.get("detail"), Mapping) else {}
    regime_code = str(item.get("regime_code") or "UNKNOWN") if selected else "UNKNOWN"
    label = str(item.get("regime_label") or item.get("horizon") or "地合い不明") if selected else "地合い不明"
    key = _horizon_key_from_item(item) if selected else str(horizon_key or "unknown_horizon")
    sec = _safe_int(item.get("horizon_sec")) if selected else _horizon_sec_from_key(key)
    drivers = _as_text_list(detail.get("reason_lines"))
    warnings = _as_text_list(detail.get("warning_lines")) + _as_text_list(detail.get("invalidation_lines"))
    blockers = _scenario_blockers(item, selected=selected)
    part = build_prediction_family_scenario_part(
        prediction_family_id="market_regime",
        horizon_key=key,
        horizon_group=_horizon_group(key, sec),
        scenario_state=_regime_to_state(regime_code),
        scenario_label=label,
        scenario_summary=(
            f"market_regime={regime_code} / label={label} / "
            f"confidence={_safe_int(item.get('confidence_percent'))} / source=latest_cards / read_only=true"
        ),
        confidence_percent=_safe_int(item.get("confidence_percent")),
        estimated_signal_strength_percent=_safe_int(item.get("confidence_percent")),
        part_role="primary_context",
        drivers=drivers,
        blockers=blockers,
        warnings=warnings,
        evidence_refs=[{
            "artifact_ref": "prediction/market_regime/latest_cards.json",
            "artifact_kind": str(latest_cards.get("artifact_kind") or "latest_cards"),
            "run_id": str(latest_cards.get("run_id") or ""),
            "scenario_part_builder_version": MARKET_REGIME_SCENARIO_PART_VERSION,
        }],
        source_quality_notes=_as_text_list(detail.get("source_lines")),
        trace_refs=[],
        parameter_set_id=str(detail.get("parameter_set_id") or latest_cards.get("parameter_set_id") or ""),
        generated_at=str(latest_cards.get("generated_at") or ""),
    )
    validation = validate_market_regime_scenario_part(part)
    if not validation["ok"]:
        raise ValueError(f"market-regime scenario part validation failed: {validation}")
    return part


def validate_market_regime_scenario_part(part: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_prediction_family_scenario_part(part)
    failures = list(validation.get("failures") or [])
    if part.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_not_market_regime")
    if part.get("part_role") != "primary_context":
        failures.append("part_role_not_primary_context")
    merge = part.get("parent_merge") if isinstance(part.get("parent_merge"), Mapping) else {}
    if merge.get("family_decides_overall_scenario") is not False:
        failures.append("family_decides_overall_scenario_not_false")
    if merge.get("same_run_recursive_dependency_allowed") is not False:
        failures.append("same_run_recursive_dependency_allowed_not_false")
    return {
        "ok": not failures,
        "market_regime_scenario_part_version": MARKET_REGIME_SCENARIO_PART_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "scenario_state": str(part.get("scenario_state") or ""),
    }
