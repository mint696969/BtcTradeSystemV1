# path: ./btcts_next/src/btcts/prediction/system_contract.py
# desc: Standalone Prediction System top-level contracts. Contract-only; no Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

from .contracts import InferenceBundle, PredictionOutput
from .forecast_ledger import ForecastLedgerBatch

LOGIC_VERSION = "prediction_system_contract.ps_c.v1"


class HorizonGroup(str, Enum):
    NOWCAST = "nowcast"
    SHORT_HORIZON = "short_horizon"
    MID_HORIZON = "mid_horizon"
    LONG_HORIZON = "long_horizon"


DEFAULT_HORIZON_GROUPS: Tuple[HorizonGroup, ...] = (
    HorizonGroup.NOWCAST,
    HorizonGroup.SHORT_HORIZON,
    HorizonGroup.MID_HORIZON,
    HorizonGroup.LONG_HORIZON,
)

DEFAULT_HORIZONS_BY_GROUP: Mapping[HorizonGroup, Tuple[int, ...]] = {
    HorizonGroup.NOWCAST: (15, 30, 60),
    HorizonGroup.SHORT_HORIZON: (300, 600, 900),
    HorizonGroup.MID_HORIZON: (1800, 3600),
    HorizonGroup.LONG_HORIZON: (14400, 21600, 43200, 86400),
}

DISPLAY_LABEL_JA_BY_GROUP: Mapping[HorizonGroup, str] = {
    HorizonGroup.NOWCAST: "現在",
    HorizonGroup.SHORT_HORIZON: "短期",
    HorizonGroup.MID_HORIZON: "中期",
    HorizonGroup.LONG_HORIZON: "長期",
}


@dataclass(frozen=True)
class PredictionRunIdentity:
    prediction_run_id: str
    generated_at: str
    market_uid: str = "BTC_JPY:bitFlyer"
    system_version: str = LOGIC_VERSION
    previous_prediction_run_id: str | None = None
    run_reason: str = "manual_or_scheduled_prediction"
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionLifetime:
    valid_from: str
    valid_until: str | None = None
    stale_after_sec: int | None = None
    refresh_required: bool = False
    refresh_reason: str | None = None
    refresh_trigger: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionRevisionSummary:
    previous_prediction_run_id: str | None = None
    revision_reason: str | None = None
    revision_trigger: str | None = None
    changed_families: Tuple[str, ...] = ()
    changed_horizons_sec: Tuple[int, ...] = ()
    previous_primary_label: str | None = None
    new_primary_label: str | None = None
    previous_confidence: str | None = None
    new_confidence: str | None = None
    previous_invalidation_state: str | None = None
    new_invalidation_state: str | None = None
    change_summary_for_human: str | None = None
    change_summary_for_gpt: Mapping[str, Any] = field(default_factory=dict)

    @property
    def has_revision(self) -> bool:
        return bool(self.previous_prediction_run_id or self.revision_reason or self.changed_families or self.changed_horizons_sec)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "previous_prediction_run_id": self.previous_prediction_run_id,
            "revision_reason": self.revision_reason,
            "revision_trigger": self.revision_trigger,
            "changed_families": list(self.changed_families),
            "changed_horizons_sec": list(self.changed_horizons_sec),
            "previous_primary_label": self.previous_primary_label,
            "new_primary_label": self.new_primary_label,
            "previous_confidence": self.previous_confidence,
            "new_confidence": self.new_confidence,
            "previous_invalidation_state": self.previous_invalidation_state,
            "new_invalidation_state": self.new_invalidation_state,
            "change_summary_for_human": self.change_summary_for_human,
            "change_summary_for_gpt": dict(self.change_summary_for_gpt),
            "has_revision": self.has_revision,
        }


@dataclass(frozen=True)
class PredictionEvidenceRef:
    evidence_ref_id: str
    evidence_kind: str
    source_id: str | None = None
    family: str | None = None
    horizon_sec: int | None = None
    summary: str | None = None
    weight: float | None = None
    usable: bool = True
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        return data


@dataclass(frozen=True)
class PredictionTriggerEligibility:
    trigger_eligibility_state: str = "not_applicable"
    reason: str | None = "standalone_prediction_not_autotrade_trigger"
    confidence: str = "unknown"
    caution_level: str = "unknown"
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    confirmation_count: int = 0
    minimum_persistence_sec: int | None = None
    horizon_alignment_required: bool = False
    cooldown_after_switch: bool = False
    do_not_trigger_during_conflict: bool = True
    machine_fields: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_eligibility_state": self.trigger_eligibility_state,
            "reason": self.reason,
            "confidence": self.confidence,
            "caution_level": self.caution_level,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "confirmation_count": self.confirmation_count,
            "minimum_persistence_sec": self.minimum_persistence_sec,
            "horizon_alignment_required": self.horizon_alignment_required,
            "cooldown_after_switch": self.cooldown_after_switch,
            "do_not_trigger_during_conflict": self.do_not_trigger_during_conflict,
            "machine_fields": dict(self.machine_fields),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


@dataclass(frozen=True)
class HorizonGroupSummary:
    horizon_group: HorizonGroup
    display_label_ja: str
    horizons_sec: Tuple[int, ...]
    primary_label: str = "unknown"
    regime_state: str = "unknown"
    trend_bias: str = "unknown"
    reversal_risk: str = "unknown"
    breakout_false_break_risk: str = "unknown"
    volatility_risk: str = "unknown"
    liquidity_execution_quality: str = "unknown"
    confidence: str = "unknown"
    caution_level: str = "unknown"
    score: float | None = None
    invalidation_state: str = "unknown"
    scenario_switch_hint: str = "none"
    lifetime: PredictionLifetime | None = None
    trigger_eligibility: PredictionTriggerEligibility = PredictionTriggerEligibility()
    evidence_refs: Tuple[PredictionEvidenceRef, ...] = ()
    human_narrative_ja: str = ""
    gpt_review_digest: Mapping[str, Any] = field(default_factory=dict)
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_group": self.horizon_group.value,
            "display_label_ja": self.display_label_ja,
            "horizons_sec": list(self.horizons_sec),
            "primary_label": self.primary_label,
            "regime_state": self.regime_state,
            "trend_bias": self.trend_bias,
            "reversal_risk": self.reversal_risk,
            "breakout_false_break_risk": self.breakout_false_break_risk,
            "volatility_risk": self.volatility_risk,
            "liquidity_execution_quality": self.liquidity_execution_quality,
            "confidence": self.confidence,
            "caution_level": self.caution_level,
            "score": self.score,
            "invalidation_state": self.invalidation_state,
            "scenario_switch_hint": self.scenario_switch_hint,
            "lifetime": self.lifetime.to_dict() if self.lifetime else None,
            "trigger_eligibility": self.trigger_eligibility.to_dict(),
            "evidence_refs": [item.to_dict() for item in self.evidence_refs],
            "human_narrative_ja": self.human_narrative_ja,
            "gpt_review_digest": dict(self.gpt_review_digest),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
        }


@dataclass(frozen=True)
class ScenarioCoreOutput:
    scenario_id: str
    generated_at: str
    current_regime_state: str = "unknown"
    current_hypothesis_health: str = "unknown"
    outlooks: Tuple[HorizonGroupSummary, ...] = ()
    continuation_vs_reversal_balance: Mapping[str, Any] = field(default_factory=dict)
    turning_point_risk: str = "unknown"
    invalidation_state: str = "unknown"
    rewrite_state: str = "unknown"
    scenario_switch_hint: str = "none"
    evidence_weighting_summary: Mapping[str, Any] = field(default_factory=dict)
    evidence_conflict_state: str = "unknown"
    scenario_trace: Mapping[str, Any] = field(default_factory=dict)
    trigger_eligibility_state: str = "not_applicable"
    human_narrative_ja: str = ""
    gpt_review_digest: Mapping[str, Any] = field(default_factory=dict)
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "generated_at": self.generated_at,
            "current_regime_state": self.current_regime_state,
            "current_hypothesis_health": self.current_hypothesis_health,
            "outlooks": [item.to_dict() for item in self.outlooks],
            "continuation_vs_reversal_balance": dict(self.continuation_vs_reversal_balance),
            "turning_point_risk": self.turning_point_risk,
            "invalidation_state": self.invalidation_state,
            "rewrite_state": self.rewrite_state,
            "scenario_switch_hint": self.scenario_switch_hint,
            "evidence_weighting_summary": dict(self.evidence_weighting_summary),
            "evidence_conflict_state": self.evidence_conflict_state,
            "scenario_trace": dict(self.scenario_trace),
            "trigger_eligibility_state": self.trigger_eligibility_state,
            "human_narrative_ja": self.human_narrative_ja,
            "gpt_review_digest": dict(self.gpt_review_digest),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "logic_version": LOGIC_VERSION,
        }


@dataclass(frozen=True)
class PredictionSystemInput:
    input_id: str
    generated_at: str
    market_uid: str = "BTC_JPY:bitFlyer"
    requested_horizon_groups: Tuple[HorizonGroup, ...] = DEFAULT_HORIZON_GROUPS
    requested_horizons_sec: Tuple[int, ...] = ()
    provider_quality_summary: Mapping[str, Any] = field(default_factory=dict)
    feature_snapshot: Mapping[str, Any] = field(default_factory=dict)
    source_artifact_refs: Tuple[str, ...] = ()
    previous_prediction_run_id: str | None = None
    calibration_context_refs: Tuple[str, ...] = ()
    raw_input_refs: Tuple[str, ...] = ()
    source_registry_version: str | None = None
    reference_source_registry_ids: Tuple[str, ...] = ()
    evidence_profile_ids: Tuple[str, ...] = ()
    source_artifact_coverage_summary: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_id": self.input_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "requested_horizon_groups": [item.value for item in self.requested_horizon_groups],
            "requested_horizons_sec": list(self.requested_horizons_sec),
            "provider_quality_summary": dict(self.provider_quality_summary),
            "feature_snapshot": dict(self.feature_snapshot),
            "source_artifact_refs": list(self.source_artifact_refs),
            "previous_prediction_run_id": self.previous_prediction_run_id,
            "calibration_context_refs": list(self.calibration_context_refs),
            "raw_input_refs": list(self.raw_input_refs),
            "source_registry_version": self.source_registry_version,
            "reference_source_registry_ids": list(self.reference_source_registry_ids),
            "evidence_profile_ids": list(self.evidence_profile_ids),
            "source_artifact_coverage_summary": dict(self.source_artifact_coverage_summary),
            "diagnostics": dict(self.diagnostics),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
        }


@dataclass(frozen=True)
class PredictionSystemResult:
    run_identity: PredictionRunIdentity
    system_input: PredictionSystemInput
    outputs: Tuple[PredictionOutput, ...] = ()
    scenario_core: ScenarioCoreOutput | None = None
    inference_bundle: InferenceBundle | None = None
    forecast_batch: ForecastLedgerBatch | None = None
    revision_summary: PredictionRevisionSummary = PredictionRevisionSummary()
    calibration_refs: Tuple[str, ...] = ()
    human_narrative_ja: str = ""
    gpt_review_digest: Mapping[str, Any] = field(default_factory=dict)
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_identity": self.run_identity.to_dict(),
            "system_input": self.system_input.to_dict(),
            "outputs": [output.to_dict() for output in self.outputs],
            "scenario_core": self.scenario_core.to_dict() if self.scenario_core else None,
            "inference_bundle": self.inference_bundle.to_dict() if self.inference_bundle else None,
            "forecast_batch": self.forecast_batch.to_dict() if self.forecast_batch else None,
            "revision_summary": self.revision_summary.to_dict(),
            "calibration_refs": list(self.calibration_refs),
            "human_narrative_ja": self.human_narrative_ja,
            "gpt_review_digest": dict(self.gpt_review_digest),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "logic_version": LOGIC_VERSION,
        }


def default_horizon_group_summary(group: HorizonGroup) -> HorizonGroupSummary:
    return HorizonGroupSummary(
        horizon_group=group,
        display_label_ja=DISPLAY_LABEL_JA_BY_GROUP[group],
        horizons_sec=DEFAULT_HORIZONS_BY_GROUP[group],
    )


def build_default_horizon_group_summaries() -> Tuple[HorizonGroupSummary, ...]:
    return tuple(default_horizon_group_summary(group) for group in DEFAULT_HORIZON_GROUPS)
