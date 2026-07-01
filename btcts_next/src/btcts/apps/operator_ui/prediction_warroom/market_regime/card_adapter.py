# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/card_adapter.py
# desc: Pure adapter from core MarketRegimePredictionPacket to WarRoom market-regime card specs. No UI mount, Streamlit import, data-root read, or runtime write.

from __future__ import annotations

from typing import Any, Iterable

from btcts.apps.operator_ui.prediction_warroom.contracts.market_regime_card_contract import (
    BackgroundTone,
    EvidenceQuality,
    FreshnessBadge,
    MarketRegimeCode,
    RegimeDiagnosticReason,
    ShortTag,
    build_market_regime_card_spec,
    build_market_regime_detail_payload,
    build_unknown_market_regime_diagnostic_record,
)
from btcts.prediction.market_regime import MarketRegimePrediction, MarketRegimePredictionPacket, TacticalHint

WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION = "prediction_warroom.market_regime_card_adapter.ps_q27k.v1"


def _coerce_card_regime(value: Any) -> MarketRegimeCode:
    try:
        return MarketRegimeCode(str(getattr(value, "value", value)))
    except Exception:
        return MarketRegimeCode.UNKNOWN


def _coerce_evidence(value: Any) -> EvidenceQuality:
    try:
        return EvidenceQuality(str(getattr(value, "value", value)))
    except Exception:
        return EvidenceQuality.MISSING


def _coerce_freshness(value: Any) -> FreshnessBadge:
    try:
        return FreshnessBadge(str(getattr(value, "value", value)))
    except Exception:
        return FreshnessBadge.MISSING


def _background_tone(prediction: MarketRegimePrediction) -> BackgroundTone:
    regime = _coerce_card_regime(prediction.regime_code)
    warnings = set(str(item) for item in prediction.warnings)
    if regime == MarketRegimeCode.UNKNOWN:
        return BackgroundTone.UNKNOWN
    if regime in (MarketRegimeCode.PANIC_SPIKE, MarketRegimeCode.HIGH_VOL_CHOP):
        return BackgroundTone.DANGER
    if "negative_spread_seen" in warnings or "tactical_hint_forced_no_new_entry" in warnings:
        return BackgroundTone.CAUTION
    if regime in (MarketRegimeCode.RANGE, MarketRegimeCode.LOW_VOL_COMPRESSION, MarketRegimeCode.REVERSAL_WATCH):
        return BackgroundTone.CAUTION
    return BackgroundTone.GOOD


def _short_tag(prediction: MarketRegimePrediction) -> ShortTag:
    regime = _coerce_card_regime(prediction.regime_code)
    warnings = set(str(item) for item in prediction.warnings)
    missing = tuple(str(item) for item in prediction.missing_sources)
    tactical_hint = str(getattr(prediction.tactical_hint, "value", prediction.tactical_hint))
    freshness = _coerce_freshness(prediction.freshness_state)

    if missing:
        return ShortTag.DATA_MISSING
    if freshness in (FreshnessBadge.STALE, FreshnessBadge.MISSING):
        return ShortTag.STALE_INPUT
    if tactical_hint == TacticalHint.NO_NEW_ENTRY.value or "tactical_hint_forced_no_new_entry" in warnings:
        return ShortTag.NO_NEW_ENTRY
    if "negative_spread_seen" in warnings or "wide_spread" in warnings:
        return ShortTag.WIDE_SPREAD
    if regime == MarketRegimeCode.RANGE:
        return ShortTag.NO_DIRECTION
    if regime == MarketRegimeCode.UP_TREND:
        return ShortTag.PULLBACK_CANDIDATE
    if regime == MarketRegimeCode.DOWN_TREND:
        return ShortTag.RETURN_SELL_WATCH
    if regime == MarketRegimeCode.HIGH_VOL_CHOP:
        return ShortTag.CHOPPY
    if regime == MarketRegimeCode.PANIC_SPIKE:
        return ShortTag.POST_SPIKE
    if regime == MarketRegimeCode.REVERSAL_WATCH:
        return ShortTag.REVERSAL_WATCH
    if regime == MarketRegimeCode.UNKNOWN:
        return ShortTag.DATA_MISSING
    return ShortTag.NO_DIRECTION


def _diagnostic_reasons(prediction: MarketRegimePrediction) -> tuple[RegimeDiagnosticReason, ...]:
    reasons: list[RegimeDiagnosticReason] = []
    warnings = set(str(item) for item in prediction.warnings)
    if prediction.missing_sources:
        reasons.append(RegimeDiagnosticReason.DATA_MISSING)
    if _coerce_freshness(prediction.freshness_state) in (FreshnessBadge.STALE, FreshnessBadge.MISSING):
        reasons.append(RegimeDiagnosticReason.STALE_INPUT)
    if "negative_spread_seen" in warnings or "wide_spread" in warnings:
        reasons.append(RegimeDiagnosticReason.WIDE_SPREAD)
    if _coerce_card_regime(prediction.regime_code) == MarketRegimeCode.UNKNOWN:
        reasons.append(RegimeDiagnosticReason.NO_CLEAR_REGIME)
    if prediction.confidence_percent < 45:
        reasons.append(RegimeDiagnosticReason.LOW_CONFIDENCE)
    return tuple(dict.fromkeys(reasons)) or (RegimeDiagnosticReason.NO_CLEAR_REGIME,)


def _source_lines(prediction: MarketRegimePrediction) -> tuple[str, ...]:
    lines: list[str] = []
    for driver in prediction.drivers:
        text = str(driver)
        if text.startswith("forecast_") or text.startswith("cross_venue") or text.startswith("volatility"):
            lines.append(text)
    if not lines:
        lines.append("market_regime_prediction_packet")
    return tuple(dict.fromkeys(lines))


def _reason_lines(prediction: MarketRegimePrediction) -> tuple[str, ...]:
    lines = [str(item) for item in prediction.drivers]
    if prediction.invalidation_hints:
        lines.append("invalidation:" + ",".join(str(item) for item in prediction.invalidation_hints))
    return tuple(dict.fromkeys(lines))


def _summary(prediction: MarketRegimePrediction) -> str:
    regime = _coerce_card_regime(prediction.regime_code).value
    tactical = str(getattr(prediction.tactical_hint, "value", prediction.tactical_hint))
    return f"{prediction.horizon_label}: {regime} / confidence={prediction.confidence_percent}% / tactical={tactical}"


def _diagnostic_record(prediction: MarketRegimePrediction):
    regime = _coerce_card_regime(prediction.regime_code)
    low_confidence = int(prediction.confidence_percent) < 45
    if regime != MarketRegimeCode.UNKNOWN and not low_confidence and not prediction.missing_sources:
        return None
    return build_unknown_market_regime_diagnostic_record(
        record_id=f"q27k-{prediction.horizon_sec}",
        created_at_utc=str(prediction.diagnostic_record.get("created_at_utc") or ""),
        horizon=prediction.horizon_label,
        confidence_percent=prediction.confidence_percent,
        unknown_reason_codes=list(_diagnostic_reasons(prediction)),
        used_sources=list(_source_lines(prediction)),
        missing_sources=list(prediction.missing_sources),
        conflicting_sources=(),
        freshness_state=str(getattr(prediction.freshness_state, "value", prediction.freshness_state)),
        spread_state="negative_or_wide" if "negative_spread_seen" in set(str(item) for item in prediction.warnings) else "",
        liquidity_state="warning" if prediction.warnings else "",
        board_state="",
        executions_state="",
        model_version=str(prediction.diagnostic_record.get("classifier_version") or ""),
        feature_bundle_hash=str(prediction.feature_bundle_hash or ""),
        input_snapshot_ref="market_regime_prediction_packet",
        notes="adapter_generated_diagnostic_record",
    )


def adapt_market_regime_prediction_packet_to_cards(packet: MarketRegimePredictionPacket) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for prediction in packet.predictions:
        regime = _coerce_card_regime(prediction.regime_code)
        freshness = _coerce_freshness(prediction.freshness_state)
        evidence = _coerce_evidence(prediction.evidence_quality)
        tone = _background_tone(prediction)
        tag = _short_tag(prediction)
        detail = build_market_regime_detail_payload(
            horizon=prediction.horizon_label,
            regime_code=regime,
            confidence_percent=prediction.confidence_percent,
            background_tone=tone,
            freshness_badge=freshness,
            evidence_quality=evidence,
            short_tag=tag,
            summary=_summary(prediction),
            reading="地合い分類の確信度であり勝率ではありません。",
            reason_lines=_reason_lines(prediction),
            source_lines=_source_lines(prediction),
            warning_lines=tuple(str(item) for item in prediction.warnings),
            freshness_detail=str(getattr(prediction.freshness_state, "value", prediction.freshness_state)),
            unknown_or_low_confidence_diagnostic_id=f"q27k-{prediction.horizon_sec}" if regime == MarketRegimeCode.UNKNOWN or prediction.confidence_percent < 45 else "",
        )
        cards.append(
            build_market_regime_card_spec(
                horizon=prediction.horizon_label,
                regime_code=regime,
                confidence_percent=prediction.confidence_percent,
                background_tone=tone,
                freshness_badge=freshness,
                evidence_quality=evidence,
                short_tag=tag,
                detail=detail,
                diagnostic_record=_diagnostic_record(prediction),
                extra={
                    "adapter_version": WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION,
                    "source_packet_logic_version": packet.logic_version,
                    "live_data_connected": False,
                    "warroom_page_mounted": False,
                    "display_adapter_only": True,
                    "runtime_read_allowed": False,
                    "runtime_artifact_write_allowed": False,
                    "scheduler_enabled": False,
                    "producer_enabled": False,
                    "autotrade_trigger_allowed": False,
                    "broker_private_api_allowed": False,
                    "ledger_append_allowed": False,
                    "mode_apply_allowed": False,
                    "parameter_apply_allowed": False,
                    "would_send_to_broker": False,
                },
            ).to_dict()
        )
    return cards


def build_warroom_market_regime_card_adapter_packet(packet: MarketRegimePredictionPacket) -> dict[str, Any]:
    cards = adapt_market_regime_prediction_packet_to_cards(packet)
    return {
        "ok": True,
        "adapter_version": WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION,
        "source_packet_logic_version": packet.logic_version,
        "card_count": len(cards),
        "horizons": [str(card.get("horizon", "")) for card in cards],
        "cards": cards,
        "market_regime_only": True,
        "adapter_prep_only": True,
        "display_adapter_only": True,
        "live_data_connected": False,
        "warroom_page_changed": False,
        "warroom_page_mounted": False,
        "renderer_changed": False,
        "streamlit_render_invoked_by_page": False,
        "runtime_read_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
