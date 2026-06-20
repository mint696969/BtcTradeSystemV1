# path: ./btcts_next/src/btcts/prediction/source_artifact_coverage.py
# desc: PS-Q2 source/artifact input coverage contracts for standalone Prediction System. Contract-only; no collection, runtime writes, broker, AutoTrade, or external API behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

LOGIC_VERSION = "prediction_source_artifact_coverage.ps_q2.v1"
REGISTRY_VERSION = "prediction_source_registry.ps_q2.v1"
EVIDENCE_PROFILE_VERSION = "prediction_evidence_profiles.ps_q2.v1"


class EvidenceTier(str, Enum):
    TIER_0_SOURCE_QUALITY = "tier_0_source_quality_freshness_integrity_gate"
    TIER_1_LOCAL_EXECUTABLE_MARKET = "tier_1_local_executable_market_truth"
    TIER_2_TECHNICAL_STRUCTURE = "tier_2_multitimeframe_price_technical_structure"
    TIER_3_CROSS_VENUE_SPOT = "tier_3_cross_venue_spot_confirmation"
    TIER_4_DERIVATIVES_LEVERAGE = "tier_4_derivatives_leverage_context"
    TIER_5_MACRO_SESSION_EVENT = "tier_5_macro_session_calendar_incident_news_context"
    TIER_6_AI_PRO_BEHAVIOR = "tier_6_ai_pro_participant_behavior_hypothesis"
    TIER_7_REPLAY_CALIBRATION = "tier_7_replay_outcome_calibration_prior"


class DirectionOwnership(str, Enum):
    NONE = "none"
    SUPPORTING = "supporting"
    PRIMARY_CANDIDATE = "primary_candidate"


class SourceEffect(str, Enum):
    CONFIRM = "confirm"
    WARN = "warn"
    CAP = "cap"
    VETO = "veto"
    STRENGTHEN = "strengthen"
    WEAKEN = "weaken"
    CONTEXT_ONLY = "context_only"


class ArtifactOwner(str, Enum):
    COLLECTOR = "collector"
    PREDICTION = "prediction"
    EXTERNAL_CONTRACT = "external_contract"
    REPLAY = "replay"
    HUMAN_GPT_REVIEW = "human_gpt_review"


@dataclass(frozen=True)
class SourceArtifactContract:
    artifact_contract_id: str
    owner_system: ArtifactOwner
    artifact_kind: str
    expected_path_hint: str | None = None
    portable_snapshot_allowed: bool = True
    runtime_collection_allowed: bool = False
    runtime_write_allowed: bool = False
    collector_runtime_import_allowed: bool = False
    external_api_call_allowed: bool = False
    broker_or_autotrade_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["owner_system"] = self.owner_system.value
        return data


@dataclass(frozen=True)
class ReferenceSourceRegistryEntry:
    source_id: str
    provider_id: str
    source_family: str
    evidence_tier: EvidenceTier
    artifact_contract: SourceArtifactContract
    freshness_policy: str
    quality_policy: str
    direction_ownership: DirectionOwnership = DirectionOwnership.SUPPORTING
    allowed_effects: Tuple[SourceEffect, ...] = (SourceEffect.CONTEXT_ONLY,)
    default_weight: float = 0.0
    maximum_weight: float = 1.0
    minimum_required_quality: str = "usable_or_warn_only"
    missing_behavior: str = "warn_and_reduce_coverage"
    stale_behavior: str = "cap_or_warn"
    conflict_behavior: str = "expose_conflict_and_reduce_signal_strength"
    warroom_display_label_ja: str = "参考情報"
    machine_reason_codes: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider_id": self.provider_id,
            "source_family": self.source_family,
            "evidence_tier": self.evidence_tier.value,
            "artifact_contract": self.artifact_contract.to_dict(),
            "freshness_policy": self.freshness_policy,
            "quality_policy": self.quality_policy,
            "direction_ownership": self.direction_ownership.value,
            "allowed_effects": [item.value for item in self.allowed_effects],
            "default_weight": self.default_weight,
            "maximum_weight": self.maximum_weight,
            "minimum_required_quality": self.minimum_required_quality,
            "missing_behavior": self.missing_behavior,
            "stale_behavior": self.stale_behavior,
            "conflict_behavior": self.conflict_behavior,
            "warroom_display_label_ja": self.warroom_display_label_ja,
            "machine_reason_codes": list(self.machine_reason_codes),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "logic_version": LOGIC_VERSION,
        }


@dataclass(frozen=True)
class ContextEvidenceProfile:
    evidence_profile_id: str
    evidence_profile_version: str
    applies_to_cards: Tuple[str, ...]
    applies_to_families: Tuple[str, ...]
    applies_to_horizon_groups: Tuple[str, ...]
    primary_evidence_tiers: Tuple[EvidenceTier, ...]
    secondary_evidence_tiers: Tuple[EvidenceTier, ...] = ()
    caution_only_tiers: Tuple[EvidenceTier, ...] = ()
    cap_only_tiers: Tuple[EvidenceTier, ...] = ()
    veto_tiers: Tuple[EvidenceTier, ...] = (EvidenceTier.TIER_0_SOURCE_QUALITY,)
    context_weight_overrides: Mapping[str, float] = field(default_factory=dict)
    minimum_required_sources: Tuple[str, ...] = ()
    minimum_required_tiers: Tuple[EvidenceTier, ...] = ()
    missing_source_behavior: str = "warn_and_reduce_signal_strength"
    conflict_resolution_policy: str = "lower_strength_and_expose_conflict"
    signal_strength_floor: int = 0
    signal_strength_ceiling: int = 99
    warroom_explanation_template_id: str = "default_context_profile_explanation"
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_profile_id": self.evidence_profile_id,
            "evidence_profile_version": self.evidence_profile_version,
            "applies_to_cards": list(self.applies_to_cards),
            "applies_to_families": list(self.applies_to_families),
            "applies_to_horizon_groups": list(self.applies_to_horizon_groups),
            "primary_evidence_tiers": [item.value for item in self.primary_evidence_tiers],
            "secondary_evidence_tiers": [item.value for item in self.secondary_evidence_tiers],
            "caution_only_tiers": [item.value for item in self.caution_only_tiers],
            "cap_only_tiers": [item.value for item in self.cap_only_tiers],
            "veto_tiers": [item.value for item in self.veto_tiers],
            "context_weight_overrides": dict(self.context_weight_overrides),
            "minimum_required_sources": list(self.minimum_required_sources),
            "minimum_required_tiers": [item.value for item in self.minimum_required_tiers],
            "missing_source_behavior": self.missing_source_behavior,
            "conflict_resolution_policy": self.conflict_resolution_policy,
            "signal_strength_floor": self.signal_strength_floor,
            "signal_strength_ceiling": self.signal_strength_ceiling,
            "warroom_explanation_template_id": self.warroom_explanation_template_id,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "logic_version": LOGIC_VERSION,
        }


@dataclass(frozen=True)
class SourceArtifactCoverageReport:
    generated_at: str
    registry_version: str = REGISTRY_VERSION
    evidence_profile_version: str = EVIDENCE_PROFILE_VERSION
    required_source_ids: Tuple[str, ...] = ()
    covered_source_ids: Tuple[str, ...] = ()
    missing_required_source_ids: Tuple[str, ...] = ()
    observed_source_ids: Tuple[str, ...] = ()
    observed_required_source_ids: Tuple[str, ...] = ()
    missing_observed_required_source_ids: Tuple[str, ...] = ()
    active_context_profile_ids: Tuple[str, ...] = ()
    input_coverage_state: str = "unknown"
    signal_strength_cap_reason: str | None = None
    registry_entries: Tuple[ReferenceSourceRegistryEntry, ...] = ()
    context_evidence_profiles: Tuple[ContextEvidenceProfile, ...] = ()
    coverage_state: str = "unknown"
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False

    @property
    def coverage_ratio(self) -> float:
        if not self.required_source_ids:
            return 1.0
        return round(len(self.covered_source_ids) / len(self.required_source_ids), 6)

    @property
    def input_coverage_ratio(self) -> float:
        if not self.required_source_ids:
            return 1.0
        return round(len(self.observed_required_source_ids) / len(self.required_source_ids), 6)

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "registry_version": self.registry_version,
            "evidence_profile_version": self.evidence_profile_version,
            "required_source_ids": list(self.required_source_ids),
            "covered_source_ids": list(self.covered_source_ids),
            "missing_required_source_ids": list(self.missing_required_source_ids),
            "observed_source_ids": list(self.observed_source_ids),
            "observed_required_source_ids": list(self.observed_required_source_ids),
            "missing_observed_required_source_ids": list(self.missing_observed_required_source_ids),
            "active_context_profile_ids": list(self.active_context_profile_ids),
            "coverage_ratio": self.coverage_ratio,
            "input_coverage_ratio": self.input_coverage_ratio,
            "coverage_state": self.coverage_state,
            "input_coverage_state": self.input_coverage_state,
            "signal_strength_cap_reason": self.signal_strength_cap_reason,
            "registry_entries": [item.to_dict() for item in self.registry_entries],
            "context_evidence_profiles": [item.to_dict() for item in self.context_evidence_profiles],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "logic_version": LOGIC_VERSION,
        }


def _iso_now(now: datetime | None = None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _artifact(source_id: str, owner: ArtifactOwner, kind: str, hint: str | None = None) -> SourceArtifactContract:
    return SourceArtifactContract(
        artifact_contract_id=f"{REGISTRY_VERSION}:{source_id}:{kind}",
        owner_system=owner,
        artifact_kind=kind,
        expected_path_hint=hint,
    )


def _entry(
    source_id: str,
    provider_id: str,
    source_family: str,
    tier: EvidenceTier,
    owner: ArtifactOwner,
    kind: str,
    label_ja: str,
    effects: Tuple[SourceEffect, ...],
    *,
    direction_ownership: DirectionOwnership = DirectionOwnership.SUPPORTING,
    default_weight: float = 0.25,
    maximum_weight: float = 1.0,
    freshness_policy: str = "requires_current_or_recent_snapshot",
    quality_policy: str = "requires_source_quality_status",
) -> ReferenceSourceRegistryEntry:
    return ReferenceSourceRegistryEntry(
        source_id=source_id,
        provider_id=provider_id,
        source_family=source_family,
        evidence_tier=tier,
        artifact_contract=_artifact(source_id, owner, kind),
        freshness_policy=freshness_policy,
        quality_policy=quality_policy,
        direction_ownership=direction_ownership,
        allowed_effects=effects,
        default_weight=default_weight,
        maximum_weight=maximum_weight,
        warroom_display_label_ja=label_ja,
        machine_reason_codes=(source_id, source_family, tier.value),
    )


REQUIRED_SOURCE_IDS: Tuple[str, ...] = (
    "bitflyer_spot_ticker",
    "bitflyer_fx_ticker",
    "bitflyer_trades",
    "bitflyer_board_summary",
    "ohlcv_1m",
    "ohlcv_5m",
    "ohlcv_10m",
    "ohlcv_15m",
    "ohlcv_30m",
    "ohlcv_1h",
    "ohlcv_4h",
    "ohlcv_1d",
    "global_spot_reference",
    "global_derivatives_context",
    "funding_context",
    "basis_context",
    "liquidation_context",
    "macro_context",
    "session_calendar_context",
    "exchange_status_incident_context",
    "news_event_context",
    "provider_source_reliability_state",
    "internal_replay_outcome_calibration",
)


def build_default_reference_source_registry() -> Tuple[ReferenceSourceRegistryEntry, ...]:
    """Return PS-Q2 required source contracts without collecting or reading runtime data."""
    entries = (
        _entry("provider_source_reliability_state", "prediction", "source_quality", EvidenceTier.TIER_0_SOURCE_QUALITY, ArtifactOwner.PREDICTION, "source_quality_summary", "ソース品質", (SourceEffect.VETO, SourceEffect.CAP, SourceEffect.WARN), direction_ownership=DirectionOwnership.NONE, default_weight=0.0),
        _entry("bitflyer_spot_ticker", "bitflyer", "local_spot_ticker", EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, ArtifactOwner.COLLECTOR, "ticker_snapshot", "bitFlyer Spot ticker", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.50),
        _entry("bitflyer_fx_ticker", "bitflyer", "local_fx_ticker", EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, ArtifactOwner.COLLECTOR, "ticker_snapshot", "bitFlyer FX ticker", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.55),
        _entry("bitflyer_trades", "bitflyer", "local_tradeflow", EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, ArtifactOwner.COLLECTOR, "trades_snapshot", "bitFlyer trades", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WEAKEN, SourceEffect.WARN), default_weight=0.60),
        _entry("bitflyer_board_summary", "bitflyer", "local_orderbook", EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, ArtifactOwner.COLLECTOR, "orderbook_summary", "bitFlyer board", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.CAP, SourceEffect.WARN), default_weight=0.65),
        _entry("ohlcv_1m", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_1m", "OHLCV 1m", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.40),
        _entry("ohlcv_5m", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_5m", "OHLCV 5m", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.45),
        _entry("ohlcv_10m", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_10m", "OHLCV 10m", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.45),
        _entry("ohlcv_15m", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_15m", "OHLCV 15m", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.45),
        _entry("ohlcv_30m", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_30m", "OHLCV 30m", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.40),
        _entry("ohlcv_1h", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_1h", "OHLCV 1h", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.35),
        _entry("ohlcv_4h", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_4h", "OHLCV 4h", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.30),
        _entry("ohlcv_1d", "prediction_or_collector", "ohlcv", EvidenceTier.TIER_2_TECHNICAL_STRUCTURE, ArtifactOwner.COLLECTOR, "ohlcv_1d", "OHLCV 1d", (SourceEffect.CONFIRM, SourceEffect.STRENGTHEN, SourceEffect.WARN), default_weight=0.25),
        _entry("global_spot_reference", "global_spot", "cross_venue_spot", EvidenceTier.TIER_3_CROSS_VENUE_SPOT, ArtifactOwner.EXTERNAL_CONTRACT, "venue_reference_snapshot", "海外現物", (SourceEffect.CONFIRM, SourceEffect.WEAKEN, SourceEffect.WARN), default_weight=0.35),
        _entry("global_derivatives_context", "global_derivatives", "derivatives", EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE, ArtifactOwner.EXTERNAL_CONTRACT, "derivatives_context", "デリバティブ", (SourceEffect.CONFIRM, SourceEffect.CAP, SourceEffect.WARN), default_weight=0.25),
        _entry("funding_context", "global_derivatives", "funding", EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE, ArtifactOwner.EXTERNAL_CONTRACT, "funding_context", "Funding", (SourceEffect.CAP, SourceEffect.WARN, SourceEffect.WEAKEN), default_weight=0.20),
        _entry("basis_context", "global_derivatives", "basis", EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE, ArtifactOwner.EXTERNAL_CONTRACT, "basis_context", "Basis", (SourceEffect.CONFIRM, SourceEffect.CAP, SourceEffect.WARN), default_weight=0.20),
        _entry("liquidation_context", "global_derivatives", "liquidation", EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE, ArtifactOwner.EXTERNAL_CONTRACT, "liquidation_context", "清算", (SourceEffect.CAP, SourceEffect.WARN, SourceEffect.WEAKEN), default_weight=0.25),
        _entry("macro_context", "macro", "macro_risk", EvidenceTier.TIER_5_MACRO_SESSION_EVENT, ArtifactOwner.EXTERNAL_CONTRACT, "macro_context", "マクロ", (SourceEffect.CAP, SourceEffect.WARN, SourceEffect.CONTEXT_ONLY), direction_ownership=DirectionOwnership.NONE, default_weight=0.15),
        _entry("session_calendar_context", "calendar", "session_calendar", EvidenceTier.TIER_5_MACRO_SESSION_EVENT, ArtifactOwner.EXTERNAL_CONTRACT, "session_calendar_context", "時間帯/カレンダー", (SourceEffect.CAP, SourceEffect.WARN, SourceEffect.CONTEXT_ONLY), direction_ownership=DirectionOwnership.NONE, default_weight=0.10),
        _entry("exchange_status_incident_context", "exchange_status", "incident_status", EvidenceTier.TIER_5_MACRO_SESSION_EVENT, ArtifactOwner.EXTERNAL_CONTRACT, "exchange_status_context", "取引所ステータス", (SourceEffect.VETO, SourceEffect.CAP, SourceEffect.WARN), direction_ownership=DirectionOwnership.NONE, default_weight=0.0),
        _entry("news_event_context", "news_event", "news_event", EvidenceTier.TIER_5_MACRO_SESSION_EVENT, ArtifactOwner.EXTERNAL_CONTRACT, "news_event_context", "ニュース/イベント", (SourceEffect.CAP, SourceEffect.WARN, SourceEffect.CONTEXT_ONLY), direction_ownership=DirectionOwnership.NONE, default_weight=0.10),
        _entry("internal_replay_outcome_calibration", "prediction", "replay_outcome_calibration", EvidenceTier.TIER_7_REPLAY_CALIBRATION, ArtifactOwner.REPLAY, "calibration_digest", "replay/calibration", (SourceEffect.CAP, SourceEffect.STRENGTHEN, SourceEffect.WEAKEN, SourceEffect.WARN), direction_ownership=DirectionOwnership.NONE, default_weight=0.15),
    )
    return entries


def build_default_context_evidence_profiles() -> Tuple[ContextEvidenceProfile, ...]:
    return (
        ContextEvidenceProfile(
            evidence_profile_id="trend_short_horizon_v1",
            evidence_profile_version=EVIDENCE_PROFILE_VERSION,
            applies_to_cards=("trend_bias",),
            applies_to_families=("trend_bias", "market_regime", "human_technical_structure", "cross_venue_confirmation"),
            applies_to_horizon_groups=("short_horizon",),
            primary_evidence_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, EvidenceTier.TIER_2_TECHNICAL_STRUCTURE),
            secondary_evidence_tiers=(EvidenceTier.TIER_3_CROSS_VENUE_SPOT,),
            caution_only_tiers=(EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE, EvidenceTier.TIER_5_MACRO_SESSION_EVENT),
            minimum_required_sources=("bitflyer_trades", "bitflyer_board_summary", "ohlcv_5m", "ohlcv_10m"),
            minimum_required_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, EvidenceTier.TIER_2_TECHNICAL_STRUCTURE),
            context_weight_overrides={"bitflyer_trades": 0.70, "bitflyer_board_summary": 0.70, "ohlcv_5m": 0.55, "global_spot_reference": 0.35},
            signal_strength_ceiling=99,
            warroom_explanation_template_id="trend_short_horizon_evidence_profile_ja",
        ),
        ContextEvidenceProfile(
            evidence_profile_id="reversal_now_short_v1",
            evidence_profile_version=EVIDENCE_PROFILE_VERSION,
            applies_to_cards=("reversal_risk",),
            applies_to_families=("reversal_zone", "volatility_risk", "breakout_false_break", "algorithmic_participant_footprint"),
            applies_to_horizon_groups=("nowcast", "short_horizon"),
            primary_evidence_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, EvidenceTier.TIER_2_TECHNICAL_STRUCTURE),
            secondary_evidence_tiers=(EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE,),
            caution_only_tiers=(EvidenceTier.TIER_3_CROSS_VENUE_SPOT, EvidenceTier.TIER_5_MACRO_SESSION_EVENT),
            minimum_required_sources=("bitflyer_board_summary", "bitflyer_trades", "ohlcv_1m", "ohlcv_5m"),
            minimum_required_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET, EvidenceTier.TIER_2_TECHNICAL_STRUCTURE),
            context_weight_overrides={"bitflyer_board_summary": 0.75, "bitflyer_trades": 0.70, "liquidation_context": 0.45, "funding_context": 0.30},
            signal_strength_ceiling=99,
            warroom_explanation_template_id="reversal_now_short_evidence_profile_ja",
        ),
        ContextEvidenceProfile(
            evidence_profile_id="macro_long_horizon_v1",
            evidence_profile_version=EVIDENCE_PROFILE_VERSION,
            applies_to_cards=("macro_context", "market_regime"),
            applies_to_families=("macro_risk_context", "market_regime", "human_technical_structure"),
            applies_to_horizon_groups=("long_horizon",),
            primary_evidence_tiers=(EvidenceTier.TIER_5_MACRO_SESSION_EVENT, EvidenceTier.TIER_2_TECHNICAL_STRUCTURE),
            secondary_evidence_tiers=(EvidenceTier.TIER_3_CROSS_VENUE_SPOT, EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE),
            caution_only_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET,),
            minimum_required_sources=("macro_context", "session_calendar_context", "ohlcv_4h", "ohlcv_1d"),
            minimum_required_tiers=(EvidenceTier.TIER_5_MACRO_SESSION_EVENT, EvidenceTier.TIER_2_TECHNICAL_STRUCTURE),
            context_weight_overrides={"macro_context": 0.60, "session_calendar_context": 0.40, "ohlcv_4h": 0.45, "ohlcv_1d": 0.45},
            signal_strength_ceiling=90,
            warroom_explanation_template_id="macro_long_horizon_evidence_profile_ja",
        ),
        ContextEvidenceProfile(
            evidence_profile_id="liquidity_nowcast_v1",
            evidence_profile_version=EVIDENCE_PROFILE_VERSION,
            applies_to_cards=("liquidity_execution_quality",),
            applies_to_families=("liquidity_execution_quality", "opportunity_participation"),
            applies_to_horizon_groups=("nowcast",),
            primary_evidence_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET,),
            secondary_evidence_tiers=(EvidenceTier.TIER_3_CROSS_VENUE_SPOT, EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE),
            caution_only_tiers=(EvidenceTier.TIER_5_MACRO_SESSION_EVENT,),
            minimum_required_sources=("bitflyer_board_summary", "bitflyer_trades"),
            minimum_required_tiers=(EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET,),
            context_weight_overrides={"bitflyer_board_summary": 0.85, "bitflyer_trades": 0.70},
            signal_strength_ceiling=99,
            warroom_explanation_template_id="liquidity_nowcast_evidence_profile_ja",
        ),
    )


def build_source_artifact_coverage_report(
    *,
    registry_entries: Tuple[ReferenceSourceRegistryEntry, ...] | None = None,
    context_evidence_profiles: Tuple[ContextEvidenceProfile, ...] | None = None,
    required_source_ids: Tuple[str, ...] = REQUIRED_SOURCE_IDS,
    observed_source_ids: Tuple[str, ...] = (),
    active_context_profile_ids: Tuple[str, ...] = (),
    now: datetime | None = None,
) -> SourceArtifactCoverageReport:
    entries = tuple(registry_entries or build_default_reference_source_registry())
    profiles = tuple(context_evidence_profiles or build_default_context_evidence_profiles())
    covered = tuple(dict.fromkeys(entry.source_id for entry in entries))
    missing = tuple(source_id for source_id in required_source_ids if source_id not in set(covered))
    observed = tuple(dict.fromkeys(str(source_id) for source_id in observed_source_ids if str(source_id).strip()))
    observed_required = tuple(source_id for source_id in required_source_ids if source_id in set(observed))
    missing_observed = tuple(source_id for source_id in required_source_ids if source_id not in set(observed_required))
    active_profiles = tuple(dict.fromkeys(active_context_profile_ids or tuple(profile.evidence_profile_id for profile in profiles)))
    blockers: list[str] = []
    warnings: list[str] = []
    if missing:
        blockers.append("required_source_artifact_contract_missing")
    if not profiles:
        blockers.append("context_evidence_profiles_missing")
    if any(entry.artifact_contract.runtime_collection_allowed for entry in entries):
        blockers.append("runtime_collection_allowed_in_prediction_contract")
    if any(entry.artifact_contract.collector_runtime_import_allowed for entry in entries):
        blockers.append("collector_runtime_import_allowed_in_prediction_contract")
    if any(entry.artifact_contract.broker_or_autotrade_allowed for entry in entries):
        blockers.append("broker_or_autotrade_allowed_in_prediction_contract")
    if any(entry.direction_ownership == DirectionOwnership.PRIMARY_CANDIDATE for entry in entries):
        warnings.append("primary_candidate_source_requires_future_human_review")
    if missing_observed:
        warnings.append("runtime_source_input_coverage_incomplete")
    input_coverage_state = "complete_inputs" if not missing_observed else "incomplete_inputs"
    signal_strength_cap_reason = "required_runtime_source_inputs_missing" if missing_observed else None
    coverage_state = "complete_contract" if not blockers else "incomplete_contract"
    return SourceArtifactCoverageReport(
        generated_at=_iso_now(now),
        required_source_ids=tuple(required_source_ids),
        covered_source_ids=covered,
        missing_required_source_ids=missing,
        observed_source_ids=observed,
        observed_required_source_ids=observed_required,
        missing_observed_required_source_ids=missing_observed,
        active_context_profile_ids=active_profiles,
        input_coverage_state=input_coverage_state,
        signal_strength_cap_reason=signal_strength_cap_reason,
        registry_entries=entries,
        context_evidence_profiles=profiles,
        coverage_state=coverage_state,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
