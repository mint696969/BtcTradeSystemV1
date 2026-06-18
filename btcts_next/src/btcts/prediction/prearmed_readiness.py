# path: ./btcts_next/src/btcts/prediction/prearmed_readiness.py
# desc: Non-executing Pre-Armed integration readiness contract over prediction validation objects. No grants, mode apply, writes, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .calibration import PredictionCalibrationReport
from .replay_validation import ReplayValidationResult
from .shadow_adapter import AutoTradeShadowSignalPreview

LOGIC_VERSION = "prediction_prearmed_readiness.s135.v1"


@dataclass(frozen=True)
class PredictionPreArmedReadinessSnapshot:
    readiness_id: str
    generated_at: str
    readiness_state: str
    validation_id: str | None = None
    preview_id: str | None = None
    calibration_report_id: str | None = None
    intended_mode: str = "ARMED_DRY_RUN"
    validation_state: str | None = None
    preview_action: str | None = None
    preview_bias: str | None = None
    calibration_average_score: float | None = None
    label_hit_rate: float | None = None
    weak_families: Tuple[str, ...] = ()
    readiness_checks: Mapping[str, bool] = field(default_factory=dict)
    metrics: Mapping[str, Any] = field(default_factory=dict)
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    preview_only: bool = True
    would_execute_prearmed_grant: bool = False
    would_apply_mode: bool = False
    would_publish_to_autotrade: bool = False
    would_append_ledger: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["weak_families"] = list(self.weak_families)
        data["readiness_checks"] = dict(self.readiness_checks)
        data["metrics"] = dict(self.metrics)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        data["logic_version"] = LOGIC_VERSION
        return data


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state(blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blockers:
        return "blocked"
    if warnings:
        return "review"
    return "ready"


def _checks(
    validation: ReplayValidationResult | None,
    preview: AutoTradeShadowSignalPreview | None,
    calibration: PredictionCalibrationReport | None,
    *,
    min_average_score: float,
    min_label_hit_rate: float,
) -> Dict[str, bool]:
    return {
        "validation_present": validation is not None,
        "validation_not_blocked": bool(validation and validation.usable),
        "validation_has_consistency_checks": bool(validation and validation.consistency_checks and all(validation.consistency_checks.values())),
        "preview_present": preview is not None,
        "preview_usable": bool(preview and preview.usable),
        "preview_is_shadow_preview_only": bool(preview and preview.intended_mode == "SHADOW" and preview.preview_only),
        "calibration_present": calibration is not None,
        "calibration_usable": bool(calibration and calibration.usable),
        "calibration_average_score_min": bool(calibration and calibration.average_score is not None and float(calibration.average_score) >= min_average_score),
        "calibration_label_hit_rate_min": bool(calibration and calibration.label_hit_rate is not None and float(calibration.label_hit_rate) >= min_label_hit_rate),
    }


def _metrics(validation: ReplayValidationResult | None, preview: AutoTradeShadowSignalPreview | None, calibration: PredictionCalibrationReport | None) -> Dict[str, Any]:
    validation_metrics = dict(validation.metrics) if validation else {}
    return {
        "validation_state": validation.validation_state if validation else None,
        "preview_recommended_action": preview.recommended_action if preview else None,
        "preview_action_bias": preview.action_bias if preview else None,
        "preview_confidence": preview.confidence if preview else None,
        "average_score": calibration.average_score if calibration else None,
        "label_hit_rate": calibration.label_hit_rate if calibration else None,
        "direction_hit_rate": calibration.direction_hit_rate if calibration else None,
        "weak_family_count": len(calibration.weak_families) if calibration else 0,
        "scored_record_count": validation_metrics.get("scored_record_count"),
        "near_miss_count": validation_metrics.get("near_miss_count"),
        "wait_too_much_count": validation_metrics.get("wait_too_much_count"),
    }


def build_prediction_prearmed_readiness_snapshot(
    *,
    validation: ReplayValidationResult | None,
    preview: AutoTradeShadowSignalPreview | None,
    calibration_report: PredictionCalibrationReport | None,
    now: datetime | None = None,
    intended_mode: str = "ARMED_DRY_RUN",
    min_average_score: float = 0.75,
    min_label_hit_rate: float = 0.70,
    require_no_weak_families: bool = False,
) -> PredictionPreArmedReadinessSnapshot:
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []
    checks = _checks(validation, preview, calibration_report, min_average_score=min_average_score, min_label_hit_rate=min_label_hit_rate)
    for name, ok in checks.items():
        if not ok:
            blockers.append(f"readiness_check_failed:{name}")
    if validation is not None:
        blockers.extend(validation.blockers)
        warnings.extend(validation.warnings)
        if validation.validation_state == "warn":
            warnings.append("validation_warn_state_requires_review")
    if preview is not None:
        blockers.extend(preview.blockers)
        warnings.extend(preview.warnings)
        if preview.recommended_action == "HOLD" and preview.action_bias == "risk_off":
            warnings.append("risk_off_hold_preview_requires_review")
    if calibration_report is not None:
        blockers.extend(calibration_report.blockers)
        warnings.extend(calibration_report.warnings)
        if calibration_report.weak_families:
            warnings.append("weak_prediction_families_present")
            if require_no_weak_families:
                blockers.append("weak_prediction_families_block_readiness")
    readiness_blockers = tuple(dict.fromkeys(blockers))
    readiness_warnings = tuple(dict.fromkeys(warnings))
    return PredictionPreArmedReadinessSnapshot(
        readiness_id=f"{LOGIC_VERSION}:{generated_at}:{intended_mode}",
        generated_at=generated_at,
        readiness_state=_state(readiness_blockers, readiness_warnings),
        validation_id=validation.validation_id if validation else None,
        preview_id=preview.preview_id if preview else None,
        calibration_report_id=calibration_report.report_id if calibration_report else None,
        intended_mode=intended_mode,
        validation_state=validation.validation_state if validation else None,
        preview_action=preview.recommended_action if preview else None,
        preview_bias=preview.action_bias if preview else None,
        calibration_average_score=calibration_report.average_score if calibration_report else None,
        label_hit_rate=calibration_report.label_hit_rate if calibration_report else None,
        weak_families=tuple(calibration_report.weak_families) if calibration_report else (),
        readiness_checks=checks,
        metrics=_metrics(validation, preview, calibration_report),
        blockers=readiness_blockers,
        warnings=readiness_warnings,
    )
