# path: ./btcts_next/src/btcts/prediction/replay_validation.py
# desc: Non-executing paper/replay validation contracts over already-provided prediction objects. No runner execution, writes, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .calibration import MissedOpportunityReport, PredictionCalibrationReport
from .forecast_ledger import ForecastLedgerBatch
from .outcome_ledger import ForecastOutcomeBatch
from .shadow_adapter import AutoTradeShadowSignalPreview

LOGIC_VERSION = "prediction_replay_validation.s134.v1"


@dataclass(frozen=True)
class ReplayValidationScenario:
    scenario_id: str
    scenario_kind: str = "paper_replay_contract"
    description: str = "already-provided objects only; no replay runner execution"
    expected_mode: str = "SHADOW"
    min_scored_records: int = 1
    min_average_score: float | None = None
    require_preview_usable: bool = True
    require_report_usable: bool = True
    allow_risk_off_hold: bool = True
    read_only: bool = True
    non_executing: bool = True
    would_run_replay: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self) | {"logic_version": LOGIC_VERSION}


@dataclass(frozen=True)
class ReplayValidationResult:
    validation_id: str
    generated_at: str
    scenario: ReplayValidationScenario
    validation_state: str
    preview_id: str | None = None
    forecast_batch_id: str | None = None
    outcome_batch_id: str | None = None
    calibration_report_id: str | None = None
    missed_report_id: str | None = None
    consistency_checks: Mapping[str, bool] = field(default_factory=dict)
    metrics: Mapping[str, Any] = field(default_factory=dict)
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_run_replay: bool = False
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
            "validation_id": self.validation_id,
            "generated_at": self.generated_at,
            "scenario": self.scenario.to_dict(),
            "validation_state": self.validation_state,
            "preview_id": self.preview_id,
            "forecast_batch_id": self.forecast_batch_id,
            "outcome_batch_id": self.outcome_batch_id,
            "calibration_report_id": self.calibration_report_id,
            "missed_report_id": self.missed_report_id,
            "consistency_checks": dict(self.consistency_checks),
            "metrics": dict(self.metrics),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_run_replay": self.would_run_replay,
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


def _default_scenario() -> ReplayValidationScenario:
    return ReplayValidationScenario(scenario_id="paper_replay_validation_contract_v0")


def _state(blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blockers:
        return "blocked"
    if warnings:
        return "warn"
    return "passed"


def _ids_match(preview: AutoTradeShadowSignalPreview | None, forecast_batch: ForecastLedgerBatch | None, outcome_batch: ForecastOutcomeBatch | None, calibration_report: PredictionCalibrationReport | None) -> dict[str, bool]:
    snapshot = preview.inference_snapshot if preview else None
    return {
        "preview_has_snapshot": snapshot is not None,
        "forecast_batch_has_records": bool(forecast_batch and forecast_batch.records),
        "outcome_batch_has_records": bool(outcome_batch and outcome_batch.records),
        "outcome_matches_forecast_batch": bool(forecast_batch and outcome_batch and outcome_batch.forecast_batch_id == forecast_batch.batch_id),
        "calibration_matches_outcome_batch": bool(outcome_batch and calibration_report and calibration_report.outcome_batch_id == outcome_batch.batch_id),
        "preview_forecast_count_matches_snapshot_family_count": bool(snapshot and forecast_batch and len(snapshot.families_present) == forecast_batch.family_count),
        "preview_horizon_count_matches_forecast_batch": bool(snapshot and forecast_batch and len(snapshot.horizons_present_sec) == forecast_batch.horizon_count),
    }


def _metrics(preview: AutoTradeShadowSignalPreview | None, forecast_batch: ForecastLedgerBatch | None, outcome_batch: ForecastOutcomeBatch | None, calibration_report: PredictionCalibrationReport | None, missed_report: MissedOpportunityReport | None) -> Dict[str, Any]:
    return {
        "recommended_action": preview.recommended_action if preview else None,
        "action_bias": preview.action_bias if preview else None,
        "preview_confidence": preview.confidence if preview else None,
        "forecast_record_count": forecast_batch.record_count if forecast_batch else 0,
        "outcome_record_count": outcome_batch.record_count if outcome_batch else 0,
        "scored_record_count": outcome_batch.scored_record_count if outcome_batch else 0,
        "average_score": calibration_report.average_score if calibration_report else None,
        "label_hit_rate": calibration_report.label_hit_rate if calibration_report else None,
        "direction_hit_rate": calibration_report.direction_hit_rate if calibration_report else None,
        "weak_families": list(calibration_report.weak_families) if calibration_report else [],
        "near_miss_count": missed_report.near_miss_count if missed_report else None,
        "wait_too_much_count": missed_report.wait_too_much_count if missed_report else None,
    }


def build_replay_validation_result(
    *,
    preview: AutoTradeShadowSignalPreview | None,
    forecast_batch: ForecastLedgerBatch | None,
    outcome_batch: ForecastOutcomeBatch | None,
    calibration_report: PredictionCalibrationReport | None = None,
    missed_opportunity_report: MissedOpportunityReport | None = None,
    scenario: ReplayValidationScenario | None = None,
    now: datetime | None = None,
) -> ReplayValidationResult:
    generated_at = _generated_at(now)
    active = scenario or _default_scenario()
    blockers: list[str] = []
    warnings: list[str] = []
    if preview is None:
        blockers.append("shadow_preview_missing")
    elif active.require_preview_usable and not preview.usable:
        blockers.extend(preview.blockers or ("shadow_preview_blocked",))
    if forecast_batch is None:
        blockers.append("forecast_batch_missing")
    elif not forecast_batch.records:
        blockers.append("forecast_records_missing")
    if outcome_batch is None:
        blockers.append("outcome_batch_missing")
    elif outcome_batch.scored_record_count < active.min_scored_records:
        blockers.append("insufficient_scored_outcome_records")
    if active.require_report_usable and calibration_report is not None and not calibration_report.usable:
        blockers.extend(calibration_report.blockers or ("calibration_report_blocked",))
    if calibration_report is None:
        warnings.append("calibration_report_missing")
    if missed_opportunity_report is None:
        warnings.append("missed_opportunity_report_missing")
    checks = _ids_match(preview, forecast_batch, outcome_batch, calibration_report)
    for name, ok in checks.items():
        if not ok:
            blockers.append(f"consistency_check_failed:{name}")
    metrics = _metrics(preview, forecast_batch, outcome_batch, calibration_report, missed_opportunity_report)
    avg_score = metrics.get("average_score")
    if active.min_average_score is not None and (avg_score is None or float(avg_score) < float(active.min_average_score)):
        blockers.append("average_score_below_scenario_minimum")
    if preview is not None and preview.intended_mode != active.expected_mode:
        blockers.append("preview_intended_mode_mismatch")
    if preview is not None and preview.recommended_action == "HOLD" and preview.action_bias == "risk_off" and active.allow_risk_off_hold:
        warnings.append("risk_off_hold_preview")
    if calibration_report is not None and calibration_report.weak_families:
        warnings.append("weak_prediction_families_present")
    if missed_opportunity_report is not None and missed_opportunity_report.near_miss_count > 0:
        warnings.append("near_miss_candidates_present")
    return ReplayValidationResult(
        validation_id=f"{LOGIC_VERSION}:{generated_at}:{active.scenario_id}",
        generated_at=generated_at,
        scenario=active,
        validation_state=_state(tuple(dict.fromkeys(blockers)), tuple(dict.fromkeys(warnings))),
        preview_id=preview.preview_id if preview else None,
        forecast_batch_id=forecast_batch.batch_id if forecast_batch else None,
        outcome_batch_id=outcome_batch.batch_id if outcome_batch else None,
        calibration_report_id=calibration_report.report_id if calibration_report else None,
        missed_report_id=missed_opportunity_report.report_id if missed_opportunity_report else None,
        consistency_checks=checks,
        metrics=metrics,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
