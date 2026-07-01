# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/market_regime_card_contract.py
# desc: PS-Q26X pure-data market regime card contract helpers. No Streamlit render, runtime reads/writes, producer/scheduler, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

MARKET_REGIME_CARD_CONTRACT_VERSION = "prediction_warroom.market_regime_card_contract.ps_q26x.v1"
MARKET_REGIME_CARD_CONTRACT_ACK = "PS_Q26X_MARKET_REGIME_CARD_CONTRACT_HELPERS_ONLY"
MAX_CONFIDENCE_PERCENT = 99
DEFAULT_HORIZONS = ("現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後")


class MarketRegimeCode(str, Enum):
    UP_TREND = "UP_TREND"
    DOWN_TREND = "DOWN_TREND"
    RANGE = "RANGE"
    LOW_VOL_COMPRESSION = "LOW_VOL_COMPRESSION"
    HIGH_VOL_CHOP = "HIGH_VOL_CHOP"
    BREAKOUT = "BREAKOUT"
    PANIC_SPIKE = "PANIC_SPIKE"
    REVERSAL_WATCH = "REVERSAL_WATCH"
    UNKNOWN = "UNKNOWN"


MARKET_REGIME_LABELS: dict[MarketRegimeCode, str] = {
    MarketRegimeCode.UP_TREND: "上昇トレンド",
    MarketRegimeCode.DOWN_TREND: "下落トレンド",
    MarketRegimeCode.RANGE: "レンジ",
    MarketRegimeCode.LOW_VOL_COMPRESSION: "低ボラ・膠着",
    MarketRegimeCode.HIGH_VOL_CHOP: "高ボラ・乱高下",
    MarketRegimeCode.BREAKOUT: "ブレイク",
    MarketRegimeCode.PANIC_SPIKE: "急変・パニック",
    MarketRegimeCode.REVERSAL_WATCH: "転換候補",
    MarketRegimeCode.UNKNOWN: "予測不能",
}


class BackgroundTone(str, Enum):
    GOOD = "GOOD"
    CAUTION = "CAUTION"
    DANGER = "DANGER"
    UNKNOWN = "UNKNOWN"


BACKGROUND_TONE_STYLE: dict[BackgroundTone, dict[str, str]] = {
    BackgroundTone.GOOD: {"label": "良好", "background": "#DCFAE6", "text": "#101828"},
    BackgroundTone.CAUTION: {"label": "注意", "background": "#FEF7C3", "text": "#101828"},
    BackgroundTone.DANGER: {"label": "危険", "background": "#FEE4E2", "text": "#101828"},
    BackgroundTone.UNKNOWN: {"label": "予測不能", "background": "#F2F4F7", "text": "#101828"},
}


class FreshnessBadge(str, Enum):
    LIVE = "LIVE"
    WARM = "WARM"
    STALE = "STALE"
    MISSING = "MISSING"


class EvidenceQuality(str, Enum):
    STRONG = "STRONG"
    PARTIAL = "PARTIAL"
    WEAK = "WEAK"
    CONFLICTED = "CONFLICTED"
    MISSING = "MISSING"


EVIDENCE_QUALITY_STYLE: dict[EvidenceQuality, dict[str, str]] = {
    EvidenceQuality.STRONG: {"label": "根拠良好", "border_style": "solid", "border_color": "#155EEF"},
    EvidenceQuality.PARTIAL: {"label": "根拠やや不足", "border_style": "solid", "border_color": "#7A5AF8"},
    EvidenceQuality.WEAK: {"label": "根拠不足", "border_style": "solid", "border_color": "#667085"},
    EvidenceQuality.CONFLICTED: {"label": "根拠衝突", "border_style": "dashed", "border_color": "#7A5AF8"},
    EvidenceQuality.MISSING: {"label": "根拠なし", "border_style": "dotted", "border_color": "#98A2B3"},
}


class ShortTag(str, Enum):
    HIGH_ZONE = "HIGH_ZONE"
    LOW_ZONE = "LOW_ZONE"
    PULLBACK_CANDIDATE = "PULLBACK_CANDIDATE"
    RETURN_SELL_WATCH = "RETURN_SELL_WATCH"
    NO_DIRECTION = "NO_DIRECTION"
    CHOPPY = "CHOPPY"
    OVERHEATED = "OVERHEATED"
    REVERSAL_WATCH = "REVERSAL_WATCH"
    NO_NEW_ENTRY = "NO_NEW_ENTRY"
    DATA_MISSING = "DATA_MISSING"
    STALE_INPUT = "STALE_INPUT"
    SIGNAL_CONFLICT = "SIGNAL_CONFLICT"
    POST_SPIKE = "POST_SPIKE"
    THIN_BOOK = "THIN_BOOK"
    WIDE_SPREAD = "WIDE_SPREAD"


SHORT_TAG_LABELS: dict[ShortTag, str] = {
    ShortTag.HIGH_ZONE: "高値圏",
    ShortTag.LOW_ZONE: "安値圏",
    ShortTag.PULLBACK_CANDIDATE: "押し目候補",
    ShortTag.RETURN_SELL_WATCH: "戻り売り警戒",
    ShortTag.NO_DIRECTION: "方向感なし",
    ShortTag.CHOPPY: "乱高下",
    ShortTag.OVERHEATED: "過熱",
    ShortTag.REVERSAL_WATCH: "反転警戒",
    ShortTag.NO_NEW_ENTRY: "新規回避",
    ShortTag.DATA_MISSING: "情報不足",
    ShortTag.STALE_INPUT: "鮮度不足",
    ShortTag.SIGNAL_CONFLICT: "シグナル割れ",
    ShortTag.POST_SPIKE: "急変直後",
    ShortTag.THIN_BOOK: "薄板",
    ShortTag.WIDE_SPREAD: "spread広い",
}


class RegimeDiagnosticReason(str, Enum):
    DATA_MISSING = "DATA_MISSING"
    STALE_INPUT = "STALE_INPUT"
    SIGNAL_CONFLICT = "SIGNAL_CONFLICT"
    LOW_LIQUIDITY = "LOW_LIQUIDITY"
    WIDE_SPREAD = "WIDE_SPREAD"
    POST_SPIKE_UNSTABLE = "POST_SPIKE_UNSTABLE"
    MODEL_DISAGREEMENT = "MODEL_DISAGREEMENT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    NO_CLEAR_REGIME = "NO_CLEAR_REGIME"


@dataclass(frozen=True)
class MarketRegimeDetailPayload:
    horizon: str
    regime_code: MarketRegimeCode
    regime_label: str
    confidence_percent: int
    background_tone: BackgroundTone
    freshness_badge: FreshnessBadge
    evidence_quality: EvidenceQuality
    short_tag: ShortTag
    summary: str = ""
    reading: str = ""
    reason_lines: tuple[str, ...] = ()
    source_lines: tuple[str, ...] = ()
    warning_lines: tuple[str, ...] = ()
    freshness_detail: str = ""
    unknown_or_low_confidence_diagnostic_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "horizon": self.horizon,
            "regime_code": self.regime_code.value,
            "regime_label": self.regime_label,
            "confidence_percent": self.confidence_percent,
            "background_tone": self.background_tone.value,
            "freshness_badge": self.freshness_badge.value,
            "evidence_quality": self.evidence_quality.value,
            "short_tag": self.short_tag.value,
            "summary": self.summary,
            "reading": self.reading,
            "reason_lines": list(self.reason_lines),
            "source_lines": list(self.source_lines),
            "warning_lines": list(self.warning_lines),
            "freshness_detail": self.freshness_detail,
            "unknown_or_low_confidence_diagnostic_id": self.unknown_or_low_confidence_diagnostic_id,
        }


@dataclass(frozen=True)
class MarketRegimeDiagnosticRecord:
    record_id: str
    created_at_utc: str
    horizon: str
    regime_code: MarketRegimeCode
    confidence_percent: int
    is_unknown: bool
    is_low_confidence: bool
    unknown_reason_codes: tuple[RegimeDiagnosticReason, ...] = ()
    low_confidence_reason_codes: tuple[RegimeDiagnosticReason, ...] = ()
    used_sources: tuple[str, ...] = ()
    missing_sources: tuple[str, ...] = ()
    conflicting_sources: tuple[str, ...] = ()
    freshness_state: str = ""
    spread_state: str = ""
    liquidity_state: str = ""
    board_state: str = ""
    executions_state: str = ""
    rule_version: str = MARKET_REGIME_CARD_CONTRACT_VERSION
    model_version: str = ""
    feature_bundle_hash: str = ""
    input_snapshot_ref: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "created_at_utc": self.created_at_utc,
            "horizon": self.horizon,
            "regime_code": self.regime_code.value,
            "confidence_percent": self.confidence_percent,
            "is_unknown": self.is_unknown,
            "is_low_confidence": self.is_low_confidence,
            "unknown_reason_codes": [item.value for item in self.unknown_reason_codes],
            "low_confidence_reason_codes": [item.value for item in self.low_confidence_reason_codes],
            "used_sources": list(self.used_sources),
            "missing_sources": list(self.missing_sources),
            "conflicting_sources": list(self.conflicting_sources),
            "freshness_state": self.freshness_state,
            "spread_state": self.spread_state,
            "liquidity_state": self.liquidity_state,
            "board_state": self.board_state,
            "executions_state": self.executions_state,
            "rule_version": self.rule_version,
            "model_version": self.model_version,
            "feature_bundle_hash": self.feature_bundle_hash,
            "input_snapshot_ref": self.input_snapshot_ref,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class MarketRegimeCardSpec:
    horizon: str
    regime_code: MarketRegimeCode
    confidence_percent: int
    background_tone: BackgroundTone
    freshness_badge: FreshnessBadge
    evidence_quality: EvidenceQuality
    short_tag: ShortTag
    detail: MarketRegimeDetailPayload
    diagnostic_record: MarketRegimeDiagnosticRecord | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "horizon": self.horizon,
            "regime_code": self.regime_code.value,
            "regime_label": MARKET_REGIME_LABELS[self.regime_code],
            "confidence_percent": self.confidence_percent,
            "background_tone": self.background_tone.value,
            "background_style": dict(BACKGROUND_TONE_STYLE[self.background_tone]),
            "freshness_badge": self.freshness_badge.value,
            "evidence_quality": self.evidence_quality.value,
            "evidence_quality_style": dict(EVIDENCE_QUALITY_STYLE[self.evidence_quality]),
            "short_tag": self.short_tag.value,
            "short_tag_label": SHORT_TAG_LABELS[self.short_tag],
            "card_lines": [MARKET_REGIME_LABELS[self.regime_code], f"{self.confidence_percent}%", SHORT_TAG_LABELS[self.short_tag]],
            "confidence_meaning": "market_regime_classification_certainty_not_win_rate",
            "freshness_encoded_by_badge_only": True,
            "border_meaning": "evidence_quality",
            "detail": self.detail.to_dict(),
            "diagnostic_record": self.diagnostic_record.to_dict() if self.diagnostic_record else None,
            "extra": dict(self.extra),
        }


def clamp_confidence_percent(value: int | float | str | None) -> int:
    try:
        numeric = int(float(value))
    except (TypeError, ValueError):
        numeric = 0
    if numeric < 0:
        return 0
    return min(numeric, MAX_CONFIDENCE_PERCENT)


def coerce_enum(enum_type: type[Enum], value: Any, default: Enum) -> Enum:
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(str(value))
    except Exception:
        return default


def build_market_regime_detail_payload(
    *,
    horizon: str,
    regime_code: MarketRegimeCode,
    confidence_percent: int,
    background_tone: BackgroundTone,
    freshness_badge: FreshnessBadge,
    evidence_quality: EvidenceQuality,
    short_tag: ShortTag,
    summary: str = "",
    reading: str = "",
    reason_lines: tuple[str, ...] | list[str] = (),
    source_lines: tuple[str, ...] | list[str] = (),
    warning_lines: tuple[str, ...] | list[str] = (),
    freshness_detail: str = "",
    unknown_or_low_confidence_diagnostic_id: str = "",
) -> MarketRegimeDetailPayload:
    return MarketRegimeDetailPayload(
        horizon=str(horizon),
        regime_code=regime_code,
        regime_label=MARKET_REGIME_LABELS[regime_code],
        confidence_percent=clamp_confidence_percent(confidence_percent),
        background_tone=background_tone,
        freshness_badge=freshness_badge,
        evidence_quality=evidence_quality,
        short_tag=short_tag,
        summary=str(summary),
        reading=str(reading),
        reason_lines=tuple(str(item) for item in reason_lines),
        source_lines=tuple(str(item) for item in source_lines),
        warning_lines=tuple(str(item) for item in warning_lines),
        freshness_detail=str(freshness_detail),
        unknown_or_low_confidence_diagnostic_id=str(unknown_or_low_confidence_diagnostic_id),
    )


def build_market_regime_card_spec(
    *,
    horizon: str,
    regime_code: MarketRegimeCode | str,
    confidence_percent: int | float | str | None,
    background_tone: BackgroundTone | str,
    freshness_badge: FreshnessBadge | str,
    evidence_quality: EvidenceQuality | str,
    short_tag: ShortTag | str,
    detail: MarketRegimeDetailPayload | None = None,
    diagnostic_record: MarketRegimeDiagnosticRecord | None = None,
    extra: dict[str, Any] | None = None,
) -> MarketRegimeCardSpec:
    regime = coerce_enum(MarketRegimeCode, regime_code, MarketRegimeCode.UNKNOWN)  # type: ignore[assignment]
    tone = coerce_enum(BackgroundTone, background_tone, BackgroundTone.UNKNOWN)  # type: ignore[assignment]
    fresh = coerce_enum(FreshnessBadge, freshness_badge, FreshnessBadge.MISSING)  # type: ignore[assignment]
    evidence = coerce_enum(EvidenceQuality, evidence_quality, EvidenceQuality.MISSING)  # type: ignore[assignment]
    tag = coerce_enum(ShortTag, short_tag, ShortTag.DATA_MISSING)  # type: ignore[assignment]
    confidence = clamp_confidence_percent(confidence_percent)
    payload = detail or build_market_regime_detail_payload(
        horizon=str(horizon),
        regime_code=regime,
        confidence_percent=confidence,
        background_tone=tone,
        freshness_badge=fresh,
        evidence_quality=evidence,
        short_tag=tag,
    )
    return MarketRegimeCardSpec(
        horizon=str(horizon),
        regime_code=regime,
        confidence_percent=confidence,
        background_tone=tone,
        freshness_badge=fresh,
        evidence_quality=evidence,
        short_tag=tag,
        detail=payload,
        diagnostic_record=diagnostic_record,
        extra=dict(extra or {}),
    )


def build_unknown_market_regime_diagnostic_record(
    *,
    record_id: str,
    created_at_utc: str,
    horizon: str,
    confidence_percent: int | float | str | None,
    unknown_reason_codes: tuple[RegimeDiagnosticReason, ...] | list[RegimeDiagnosticReason],
    used_sources: tuple[str, ...] | list[str] = (),
    missing_sources: tuple[str, ...] | list[str] = (),
    conflicting_sources: tuple[str, ...] | list[str] = (),
    freshness_state: str = "",
    spread_state: str = "",
    liquidity_state: str = "",
    board_state: str = "",
    executions_state: str = "",
    model_version: str = "",
    feature_bundle_hash: str = "",
    input_snapshot_ref: str = "",
    notes: str = "",
) -> MarketRegimeDiagnosticRecord:
    return MarketRegimeDiagnosticRecord(
        record_id=str(record_id),
        created_at_utc=str(created_at_utc),
        horizon=str(horizon),
        regime_code=MarketRegimeCode.UNKNOWN,
        confidence_percent=clamp_confidence_percent(confidence_percent),
        is_unknown=True,
        is_low_confidence=True,
        unknown_reason_codes=tuple(unknown_reason_codes),
        low_confidence_reason_codes=(RegimeDiagnosticReason.LOW_CONFIDENCE,),
        used_sources=tuple(str(item) for item in used_sources),
        missing_sources=tuple(str(item) for item in missing_sources),
        conflicting_sources=tuple(str(item) for item in conflicting_sources),
        freshness_state=str(freshness_state),
        spread_state=str(spread_state),
        liquidity_state=str(liquidity_state),
        board_state=str(board_state),
        executions_state=str(executions_state),
        model_version=str(model_version),
        feature_bundle_hash=str(feature_bundle_hash),
        input_snapshot_ref=str(input_snapshot_ref),
        notes=str(notes),
    )


def build_market_regime_card_contract_report() -> dict[str, Any]:
    return {
        "ok": True,
        "contract_version": MARKET_REGIME_CARD_CONTRACT_VERSION,
        "contract_ack": MARKET_REGIME_CARD_CONTRACT_ACK,
        "default_horizons": list(DEFAULT_HORIZONS),
        "regime_codes": [item.value for item in MarketRegimeCode],
        "regime_labels": {item.value: MARKET_REGIME_LABELS[item] for item in MarketRegimeCode},
        "background_tones": [item.value for item in BackgroundTone],
        "freshness_badges": [item.value for item in FreshnessBadge],
        "evidence_quality_values": [item.value for item in EvidenceQuality],
        "short_tags": [item.value for item in ShortTag],
        "diagnostic_reason_codes": [item.value for item in RegimeDiagnosticReason],
        "confidence_max_percent": MAX_CONFIDENCE_PERCENT,
        "confidence_meaning": "market_regime_classification_certainty_not_win_rate",
        "freshness_encoded_by_badge_only": True,
        "border_meaning": "evidence_quality",
        "background_tone_is_readability_first": True,
        "unknown_regime_available": True,
        "diagnostic_record_required_for_unknown_and_low_confidence": True,
        "pure_data_contract_only": True,
        "production_ui_code_changed": False,
        "warroom_page_changed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
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
