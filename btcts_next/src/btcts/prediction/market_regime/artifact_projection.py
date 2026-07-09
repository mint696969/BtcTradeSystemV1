# path: ./btcts_next/src/btcts/prediction/market_regime/artifact_projection.py
# desc: Pure projection from MarketRegimePredictionPacket to latest_cards/latest_read_model payload parts. No UI imports, filesystem writes, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from typing import Any, Dict, Mapping

from .contracts import EvidenceQuality, FreshnessState, MarketRegimeCode, MarketRegimePrediction, MarketRegimePredictionPacket

MARKET_REGIME_ARTIFACT_PROJECTION_VERSION = "prediction.market_regime.artifact_projection.2026_07_08.v1"

_REGIME_LABELS = {
    MarketRegimeCode.UP_TREND: "上昇地合い",
    MarketRegimeCode.DOWN_TREND: "下落地合い",
    MarketRegimeCode.RANGE: "レンジ",
    MarketRegimeCode.LOW_VOL_COMPRESSION: "低ボラ圧縮",
    MarketRegimeCode.HIGH_VOL_CHOP: "荒れ相場",
    MarketRegimeCode.BREAKOUT: "ブレイク監視",
    MarketRegimeCode.PANIC_SPIKE: "急変動警戒",
    MarketRegimeCode.REVERSAL_WATCH: "反転警戒",
    MarketRegimeCode.UNKNOWN: "不明",
}

_SHORT_TAGS = {
    MarketRegimeCode.UP_TREND: "押し目候補",
    MarketRegimeCode.DOWN_TREND: "戻り売り警戒",
    MarketRegimeCode.RANGE: "方向感なし",
    MarketRegimeCode.LOW_VOL_COMPRESSION: "低ボラ圧縮",
    MarketRegimeCode.HIGH_VOL_CHOP: "荒れ注意",
    MarketRegimeCode.BREAKOUT: "ブレイク監視",
    MarketRegimeCode.PANIC_SPIKE: "新規注意",
    MarketRegimeCode.REVERSAL_WATCH: "反転警戒",
    MarketRegimeCode.UNKNOWN: "データ不足",
}

_BACKGROUND_STYLES = {
    MarketRegimeCode.UP_TREND: {"background": "#ECFDF3", "text": "#064E3B"},
    MarketRegimeCode.DOWN_TREND: {"background": "#FEF3F2", "text": "#7A271A"},
    MarketRegimeCode.RANGE: {"background": "#FFFAEB", "text": "#7A2E0E"},
    MarketRegimeCode.LOW_VOL_COMPRESSION: {"background": "#F9FAFB", "text": "#344054"},
    MarketRegimeCode.HIGH_VOL_CHOP: {"background": "#FEF3F2", "text": "#7A271A"},
    MarketRegimeCode.BREAKOUT: {"background": "#EFF8FF", "text": "#1849A9"},
    MarketRegimeCode.PANIC_SPIKE: {"background": "#FEF3F2", "text": "#7A271A"},
    MarketRegimeCode.REVERSAL_WATCH: {"background": "#F4F3FF", "text": "#5925DC"},
    MarketRegimeCode.UNKNOWN: {"background": "#F2F4F7", "text": "#344054"},
}

_EVIDENCE_STYLES = {
    EvidenceQuality.STRONG: {"border_color": "#12B76A", "border_style": "solid"},
    EvidenceQuality.PARTIAL: {"border_color": "#F79009", "border_style": "solid"},
    EvidenceQuality.WEAK: {"border_color": "#98A2B3", "border_style": "dashed"},
    EvidenceQuality.CONFLICTED: {"border_color": "#D92D20", "border_style": "dashed"},
    EvidenceQuality.MISSING: {"border_color": "#667085", "border_style": "dotted"},
}


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _regime_label(regime: MarketRegimeCode) -> str:
    return _REGIME_LABELS.get(regime, "不明")


def _short_tag(regime: MarketRegimeCode) -> str:
    return _SHORT_TAGS.get(regime, "データ不足")


def _prediction_card(prediction: MarketRegimePrediction) -> Dict[str, Any]:
    regime = prediction.regime_code
    evidence = prediction.evidence_quality
    line1 = _regime_label(regime)
    line2 = f"{int(prediction.confidence_percent)}%"
    line3 = _short_tag(regime)
    return {
        "horizon": prediction.horizon_label,
        "horizon_sec": int(prediction.horizon_sec),
        "horizon_key": prediction.horizon_key,
        "regime_code": _enum_value(regime),
        "regime_label": line1,
        "confidence_percent": int(prediction.confidence_percent),
        "freshness_badge": _enum_value(prediction.freshness_state),
        "evidence_quality": _enum_value(evidence),
        "short_tag_label": line3,
        "card_lines": [line1, line2, line3],
        "background_style": dict(_BACKGROUND_STYLES.get(regime, _BACKGROUND_STYLES[MarketRegimeCode.UNKNOWN])),
        "evidence_quality_style": dict(_EVIDENCE_STYLES.get(evidence, _EVIDENCE_STYLES[EvidenceQuality.MISSING])),
        "detail": {
            "summary": f"{prediction.horizon_label}: {line1} / {line2}",
            "reason_lines": list(prediction.drivers),
            "warning_lines": list(prediction.warnings),
            "source_lines": ["market_regime_inference_artifact"],
            "invalidation_lines": list(prediction.invalidation_hints),
            "percent_meaning": "地合い見立ての信頼性であり、勝率ではありません。",
            "parameter_set_id": prediction.parameter_set_id,
            "source_priority_policy_id": prediction.source_priority_policy_id,
        },
        "extra": {
            "artifact_projection_version": MARKET_REGIME_ARTIFACT_PROJECTION_VERSION,
            "read_model_only": True,
            "prediction_invoked_by_ui": False,
            "classifier_invoked_by_ui": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    }


def build_market_regime_cards_from_packet(packet: MarketRegimePredictionPacket) -> list[Dict[str, Any]]:
    return [_prediction_card(prediction) for prediction in packet.predictions]


def build_market_regime_read_model_horizons(packet: MarketRegimePredictionPacket) -> list[Dict[str, Any]]:
    horizons: list[Dict[str, Any]] = []
    for prediction in packet.predictions:
        horizons.append({
            "horizon": prediction.horizon_label,
            "horizon_sec": int(prediction.horizon_sec),
            "horizon_key": prediction.horizon_key,
            "primary_regime": _enum_value(prediction.regime_code),
            "primary_regime_label": _regime_label(prediction.regime_code),
            "confidence_percent": int(prediction.confidence_percent),
            "freshness_state": _enum_value(prediction.freshness_state),
            "evidence_quality": _enum_value(prediction.evidence_quality),
            "drivers": list(prediction.drivers),
            "conflicts": list(prediction.warnings),
            "invalidation": list(prediction.invalidation_hints),
            "parameter_set_id": prediction.parameter_set_id,
            "diagnostic_record": dict(prediction.diagnostic_record),
        })
    return horizons


def build_market_regime_read_model_summaries(packet: MarketRegimePredictionPacket) -> dict[str, Mapping[str, Any]]:
    warnings = tuple(dict.fromkeys(warn for prediction in packet.predictions for warn in prediction.warnings))
    invalidations = tuple(dict.fromkeys(item for prediction in packet.predictions for item in prediction.invalidation_hints))
    drivers = tuple(dict.fromkeys(driver for prediction in packet.predictions for driver in prediction.drivers))
    return {
        "source_contribution_summary": {
            "driver_count": len(drivers),
            "top_drivers": list(drivers[:8]),
            "source_coverage": [coverage.to_dict() for coverage in packet.source_coverage],
        },
        "conflict_summary": {
            "warning_count": len(warnings),
            "warnings": list(warnings[:12]),
        },
        "invalidation_summary": {
            "invalidation_count": len(invalidations),
            "invalidation_conditions": list(invalidations[:12]),
        },
    }


def build_market_regime_source_refs_from_snapshot(snapshot: object) -> Dict[str, Any]:
    latest_manifest = getattr(snapshot, "latest_manifest", None)
    latest_prediction = getattr(snapshot, "latest_prediction", None)
    forecast_records = getattr(snapshot, "forecast_records", None)
    nowcast = getattr(snapshot, "nowcast", None)
    market_state = getattr(nowcast, "market_state", None)
    health = getattr(nowcast, "health", None)
    executions = getattr(nowcast, "executions", None)
    # MR_A2_SOURCE_REFS_WARROOM_CANDLES_2026_07_09
    warroom_candles = getattr(snapshot, "warroom_candles", None)
    return {
        "latest_manifest": {"relpath": str(getattr(latest_manifest, "relative_path", "")), "ok": bool(getattr(latest_manifest, "ok", False))},
        "latest_prediction": {"relpath": str(getattr(latest_prediction, "relative_path", "")), "ok": bool(getattr(latest_prediction, "ok", False))},
        "forecast_records": {
            "relpath": str(getattr(forecast_records, "relative_path", "")),
            "ok": bool(getattr(forecast_records, "ok", False)),
            "record_count": int(getattr(forecast_records, "record_count", 0) or 0),
            "market_regime_record_count": int(getattr(forecast_records, "market_regime_record_count", 0) or 0),
        },
        "collector_market_state": {"relpath": str(getattr(market_state, "relative_path", "")), "ok": bool(getattr(market_state, "ok", False))},
        "collector_health": {"relpath": str(getattr(health, "relative_path", "")), "ok": bool(getattr(health, "ok", False))},
        "collector_executions": {"relpath": str(getattr(executions, "relative_path", "")), "ok": bool(getattr(executions, "ok", False))},
        "warroom_candles": {
            "relpath": str(getattr(warroom_candles, "relative_path", "")),
            "ok": bool(getattr(warroom_candles, "ok", False)),
            "timeframe_sec": int(getattr(warroom_candles, "timeframe_sec", 0) or 0),
            "closed_candle_count": int(getattr(warroom_candles, "closed_candle_count", 0) or 0),
            "latest_closed_time_utc": str(getattr(warroom_candles, "latest_closed_time_utc", "") or ""),
            "latest_forming_time_utc": str(getattr(warroom_candles, "latest_forming_time_utc", "") or ""),
            "latest_time_utc": str(getattr(warroom_candles, "latest_time_utc", "") or ""),
        },
    }
