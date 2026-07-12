# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_selected_read_model_bridge.py
# desc: MR-VS6.5 pure bridge from one prevalidated selected MarketRegime common read model into existing WarRoom card and explanation packets.

from __future__ import annotations

from typing import Any, Mapping

MARKET_REGIME_SELECTED_BRIDGE_VERSION = "market_regime.selected_read_model_bridge.mr_vs6_5.v1"

_REGIME_LABELS = {
    "UNKNOWN": "不明",
    "RANGE": "レンジ",
    "LOW_VOL_COMPRESSION": "低ボラ圧縮",
    "UP_TREND": "上昇トレンド",
    "DOWN_TREND": "下降トレンド",
    "HIGH_VOL_CHOP": "高ボラ乱高下",
    "BREAKOUT": "ブレイクアウト",
    "REVERSAL_WATCH": "反転警戒",
    "PANIC_SPIKE": "パニック急変",
}


def _texts(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value is None or value == "":
        return []
    return [str(value)]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _card_from_row(row: Mapping[str, Any], *, run_id: str, prediction_id: str, parameter_set_id: str, selected_source: str) -> dict[str, Any]:
    family_payload = _mapping(row.get("family_payload"))
    label = str(row.get("primary_label") or family_payload.get("regime_code") or "UNKNOWN")
    label_ja = str(row.get("primary_label_display") or family_payload.get("regime_label") or _REGIME_LABELS.get(label, label))
    confidence = int(row.get("confidence_percent") or 0)
    freshness = str(row.get("freshness_state") or "MISSING")
    evidence = str(row.get("evidence_quality") or "MISSING")
    drivers = _texts(row.get("drivers"))
    blockers = _texts(row.get("blockers"))
    warnings = _texts(row.get("warnings"))
    invalidation = _texts(row.get("invalidation_hints"))
    horizon = str(row.get("horizon_key") or row.get("horizon_sec") or "")
    return {
        "horizon": horizon,
        "horizon_key": horizon,
        "regime_code": label,
        "regime_label": label_ja,
        "confidence_percent": confidence,
        "freshness_badge": freshness,
        "evidence_quality": evidence,
        "short_tag_label": str(family_payload.get("tactical_hint") or ""),
        "card_lines": [label_ja, f"{confidence}%", str(family_payload.get("tactical_hint") or "")],
        "background_style": {"background": "#F2F4F7", "text": "#101828"},
        "evidence_quality_style": {"border_style": "solid", "border_color": "#98A2B3"},
        "run_id": run_id,
        "prediction_id": prediction_id,
        "trace_refs": [dict(item) for item in row.get("trace_refs", []) if isinstance(item, Mapping)],
        "detail": {
            "percent_meaning": str(row.get("confidence_kind") or "market_regime_reading_confidence_not_win_rate"),
            "reason_lines": drivers,
            "source_lines": [f"selected_source={selected_source}"],
            "blocker_lines": blockers,
            "warning_lines": warnings,
            "invalidation_lines": invalidation,
            "active_parameter_set_id": parameter_set_id,
            "run_id": run_id,
            "prediction_id": prediction_id,
            "selected_source": selected_source,
        },
    }


def _explanation_horizon(row: Mapping[str, Any], card: Mapping[str, Any], *, run_id: str, prediction_id: str, parameter_set_id: str, selected_source: str) -> dict[str, Any]:
    blockers = _texts(row.get("blockers"))
    warnings = _texts(row.get("warnings"))
    drivers = _texts(row.get("drivers"))
    return {
        "horizon_key": str(row.get("horizon_key") or ""),
        "card": {
            "label": str(card.get("regime_code") or ""),
            "label_ja": str(card.get("regime_label") or ""),
            "display_confidence_percent": card.get("confidence_percent"),
            "short_tag": str(card.get("short_tag_label") or ""),
            "freshness_badge": str(card.get("freshness_badge") or ""),
        },
        "confidence": {
            "display_confidence_percent": card.get("confidence_percent"),
            "legacy_confidence_percent": None,
            "shadow_confidence_percent": None,
            "shadow_only": True,
            "display_replaced": False,
            "cap_percent": None,
            "cap_reasons": [],
            "estimated_signal_strength_percent": None,
            "explanation": "card confidence is market-regime reading confidence, not win rate",
        },
        "evidence": {
            "quality_reason": str(row.get("evidence_quality") or ""),
            "label_selection_reason": "selected_common_read_model",
            "selected_label_source": selected_source,
            "available_signal_count": len(drivers),
            "supporting_source_count": len(drivers),
            "contradicting_source_count": len(blockers),
        },
        "sources": [],
        "blockers": blockers,
        "warnings": warnings,
        "fallbacks": [],
        "calibration": {
            "available": False,
            "cohort": "",
            "sample_count": 0,
            "score": None,
            "interpretation": "not_win_rate",
            "unavailable_reason": "not_part_of_selected_read_model_contract",
        },
        "parameter_set": {
            "active_parameter_set_id": parameter_set_id,
            "trusted_parameter_set_count": 0,
            "comparable_parameter_set_count": 0,
            "comparison_ready": False,
            "comparison_blockers": ["not_part_of_selected_read_model_contract"],
            "best_parameter_set_claim_allowed": False,
            "promotion_recommendation_allowed": False,
            "auto_promotion_allowed": False,
        },
        "trace": {
            "run_id": run_id,
            "prediction_id": prediction_id,
            "trace_refs": [dict(item) for item in row.get("trace_refs", []) if isinstance(item, Mapping)],
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


def build_market_regime_selected_read_model_bridge(source_packet: Mapping[str, Any] | None) -> dict[str, Any]:
    source = source_packet if isinstance(source_packet, Mapping) else {}
    selected_source = str(source.get("selected_source") or "unavailable")
    read_model = _mapping(source.get("read_model"))
    rows = [dict(item) for item in read_model.get("horizon_rows", []) if isinstance(item, Mapping)]
    usable = selected_source in {"push", "artifact"} and bool(rows)
    run_id = str(read_model.get("run_id") or source.get("run_id") or "")
    prediction_id = str(read_model.get("prediction_id") or source.get("prediction_id") or "")
    parameter_set_id = str(read_model.get("parameter_set_id") or source.get("parameter_set_id") or "")
    cards = [
        _card_from_row(
            row,
            run_id=run_id,
            prediction_id=prediction_id,
            parameter_set_id=parameter_set_id,
            selected_source=selected_source,
        )
        for row in rows
    ] if usable else []
    horizons = [
        _explanation_horizon(
            row,
            card,
            run_id=run_id,
            prediction_id=prediction_id,
            parameter_set_id=parameter_set_id,
            selected_source=selected_source,
        )
        for row, card in zip(rows, cards)
    ]
    return {
        "ok": usable,
        "bridge_version": MARKET_REGIME_SELECTED_BRIDGE_VERSION,
        "selected_source": selected_source,
        "prediction_generated_at": str(source.get("prediction_generated_at") or read_model.get("generated_at") or ""),
        "transport_received_at_ms": int(source.get("transport_received_at_ms") or 0),
        "run_id": run_id,
        "prediction_id": prediction_id,
        "parameter_set_id": parameter_set_id,
        "card_count": len(cards),
        "cards": cards,
        "explanation_packet": {
            "ok": usable,
            "adapter_version": MARKET_REGIME_SELECTED_BRIDGE_VERSION,
            "artifact_root": "",
            "generated_at": str(read_model.get("generated_at") or ""),
            "horizon_count": len(horizons),
            "horizons": horizons,
            "artifact_status": {},
            "safety_violations": [],
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
        },
        "confidence_recalculated": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
        "raw_market_read": False,
        "artifact_read_performed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
