# path: ./btcts_next/src/btcts/prediction/shadow_adapter.py
# desc: Non-executing AutoTrade Shadow preview contracts from prediction bundles/reports. No publication, write, mode apply, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .calibration import MissedOpportunityReport, PredictionCalibrationReport
from .contracts import InferenceBundle, PredictionOutput

LOGIC_VERSION = "prediction_shadow_adapter.s133.v1"


@dataclass(frozen=True)
class AutoTradeInferenceSnapshot:
    snapshot_id: str
    bundle_id: str
    generated_at: str
    families_present: Tuple[str, ...]
    horizons_present_sec: Tuple[int, ...]
    labels_by_family: Mapping[str, str] = field(default_factory=dict)
    scores_by_family: Mapping[str, float | None] = field(default_factory=dict)
    risk_state: str = "unknown"
    agreement_state: str = "unknown"
    calibration_average_score: float | None = None
    weak_families: Tuple[str, ...] = ()
    near_miss_count: int | None = None
    wait_too_much_count: int | None = None
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_publish_to_autotrade: bool = False
    would_append_shadow_decision: bool = False
    would_apply_mode: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["families_present"] = list(self.families_present)
        data["horizons_present_sec"] = list(self.horizons_present_sec)
        data["labels_by_family"] = dict(self.labels_by_family)
        data["scores_by_family"] = dict(self.scores_by_family)
        data["weak_families"] = list(self.weak_families)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        data["logic_version"] = LOGIC_VERSION
        return data


@dataclass(frozen=True)
class AutoTradeShadowSignalPreview:
    preview_id: str
    generated_at: str
    intended_mode: str = "SHADOW"
    recommended_action: str = "HOLD"
    action_bias: str = "neutral"
    confidence: str = "unknown"
    reason_codes: Tuple[str, ...] = ()
    inference_snapshot: AutoTradeInferenceSnapshot | None = None
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    preview_only: bool = True
    would_publish_to_autotrade: bool = False
    would_append_shadow_decision: bool = False
    would_apply_mode: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preview_id": self.preview_id,
            "generated_at": self.generated_at,
            "intended_mode": self.intended_mode,
            "recommended_action": self.recommended_action,
            "action_bias": self.action_bias,
            "confidence": self.confidence,
            "reason_codes": list(self.reason_codes),
            "inference_snapshot": self.inference_snapshot.to_dict() if self.inference_snapshot else None,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "preview_only": self.preview_only,
            "would_publish_to_autotrade": self.would_publish_to_autotrade,
            "would_append_shadow_decision": self.would_append_shadow_decision,
            "would_apply_mode": self.would_apply_mode,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "logic_version": LOGIC_VERSION,
        }


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _output_by_family(bundle: InferenceBundle) -> Dict[str, PredictionOutput]:
    return {output.family.value: output for output in bundle.outputs}


def _confidence_from_score(score: float | None, blockers: Tuple[str, ...]) -> str:
    if blockers or score is None:
        return "unknown"
    if score >= 0.70:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _bias_and_action(labels: Mapping[str, str], risk_state: str, blockers: Tuple[str, ...]) -> tuple[str, str, Tuple[str, ...]]:
    reasons: list[str] = []
    if blockers:
        return "blocked", "HOLD", ("blocked_preview",)
    if risk_state in ("blocked", "risk_warning"):
        reasons.append(f"risk_state_{risk_state}")
        return "risk_off", "HOLD", tuple(reasons)
    trend = labels.get("trend_bias", "unknown")
    regime = labels.get("market_regime", "unknown")
    cross = labels.get("cross_venue_confirmation", "unknown")
    if trend == "long_bias" and cross in ("confirmed", "divergent_warning"):
        reasons.extend(("trend_long_bias", f"cross_{cross}"))
        return "long", "WATCH_LONG", tuple(reasons)
    if trend == "short_bias" and cross in ("confirmed", "divergent_warning"):
        reasons.extend(("trend_short_bias", f"cross_{cross}"))
        return "short", "WATCH_SHORT", tuple(reasons)
    if regime in ("range_candidate", "volatile_or_divergent"):
        reasons.append(f"regime_{regime}")
    return "neutral", "HOLD", tuple(reasons or ("no_directional_shadow_edge",))


def _snapshot(
    bundle: InferenceBundle,
    generated_at: str,
    calibration_report: PredictionCalibrationReport | None,
    missed_opportunity_report: MissedOpportunityReport | None,
) -> AutoTradeInferenceSnapshot:
    by_family = _output_by_family(bundle)
    labels = {family: output.primary_label for family, output in by_family.items()}
    scores = {family: output.score for family, output in by_family.items()}
    blockers = list(bundle.blockers)
    warnings = list(bundle.warnings)
    if not bundle.outputs:
        blockers.append("inference_bundle_outputs_missing")
    if calibration_report is not None:
        blockers.extend(calibration_report.blockers)
        warnings.extend(calibration_report.warnings)
    if missed_opportunity_report is not None:
        blockers.extend(missed_opportunity_report.blockers)
        warnings.extend(missed_opportunity_report.warnings)
    return AutoTradeInferenceSnapshot(
        snapshot_id=f"{LOGIC_VERSION}:snapshot:{bundle.bundle_id}",
        bundle_id=bundle.bundle_id,
        generated_at=generated_at,
        families_present=tuple(bundle.families_present()),
        horizons_present_sec=tuple(bundle.horizons_present_sec()),
        labels_by_family=labels,
        scores_by_family=scores,
        risk_state=str(bundle.risk_context.get("risk_state", "unknown")),
        agreement_state=str(bundle.cross_family_agreement.get("agreement_state", "unknown")),
        calibration_average_score=calibration_report.average_score if calibration_report else None,
        weak_families=tuple(calibration_report.weak_families) if calibration_report else (),
        near_miss_count=missed_opportunity_report.near_miss_count if missed_opportunity_report else None,
        wait_too_much_count=missed_opportunity_report.wait_too_much_count if missed_opportunity_report else None,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def build_autotrade_shadow_signal_preview(
    inference_bundle: InferenceBundle | None,
    *,
    calibration_report: PredictionCalibrationReport | None = None,
    missed_opportunity_report: MissedOpportunityReport | None = None,
    now: datetime | None = None,
) -> AutoTradeShadowSignalPreview:
    generated_at = _generated_at(now)
    if inference_bundle is None:
        return AutoTradeShadowSignalPreview(
            preview_id=f"{LOGIC_VERSION}:preview:{generated_at}:missing_bundle",
            generated_at=generated_at,
            recommended_action="HOLD",
            action_bias="blocked",
            confidence="unknown",
            reason_codes=("inference_bundle_missing",),
            inference_snapshot=None,
            blockers=("inference_bundle_missing",),
        )
    snapshot = _snapshot(inference_bundle, generated_at, calibration_report, missed_opportunity_report)
    bias, action, reasons = _bias_and_action(snapshot.labels_by_family, snapshot.risk_state, snapshot.blockers)
    scores = [float(score) for score in snapshot.scores_by_family.values() if score is not None]
    avg_score = sum(scores) / len(scores) if scores else None
    confidence = _confidence_from_score(avg_score, snapshot.blockers)
    warnings = list(snapshot.warnings)
    if snapshot.weak_families:
        warnings.append("weak_prediction_families_present")
    if snapshot.near_miss_count and snapshot.near_miss_count > 0:
        warnings.append("near_miss_candidates_present")
    return AutoTradeShadowSignalPreview(
        preview_id=f"{LOGIC_VERSION}:preview:{inference_bundle.bundle_id}",
        generated_at=generated_at,
        intended_mode="SHADOW",
        recommended_action=action,
        action_bias=bias,
        confidence=confidence,
        reason_codes=tuple(dict.fromkeys(reasons)),
        inference_snapshot=snapshot,
        blockers=tuple(dict.fromkeys(snapshot.blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
