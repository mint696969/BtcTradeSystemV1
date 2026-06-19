# path: ./btcts_next/src/btcts/prediction/calibration_review.py
# desc: Offline/replay-only Prediction System calibration review contracts and in-memory builder. Advisory-only; no collection, writes, broker, mode, grant, or execution behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .evaluation import PredictionEvaluationReport

LOGIC_VERSION = "prediction_calibration_review.ps_p9.v1"


@dataclass(frozen=True)
class PredictionCalibrationReview:
    review_id: str
    review_version: str
    generated_at: str
    source_evaluation_report_id: str | None
    source_evaluation_version: str | None
    market_uid: str
    source_ref: str | None
    evaluation_window_start: str | None
    evaluation_window_end: str | None
    evaluated_record_count: int
    not_evaluable_count: int
    skipped_record_count: int
    confidence_bucket_review: Mapping[str, Any] = field(default_factory=dict)
    caution_bucket_review: Mapping[str, Any] = field(default_factory=dict)
    family_review: Mapping[str, Any] = field(default_factory=dict)
    horizon_review: Mapping[str, Any] = field(default_factory=dict)
    data_quality_review: Mapping[str, Any] = field(default_factory=dict)
    scenario_switch_review: Mapping[str, Any] = field(default_factory=dict)
    refresh_required_review: Mapping[str, Any] = field(default_factory=dict)
    risk_catalog_hits: Tuple[str, ...] = ()
    calibration_candidate_notes: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_change_score_formula: bool = False
    would_change_confidence_behavior: bool = False
    would_change_caution_behavior: bool = False
    would_change_family_labels: bool = False
    would_enable_trigger_eligibility: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    autotrade_decision_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["confidence_bucket_review"] = dict(self.confidence_bucket_review)
        data["caution_bucket_review"] = dict(self.caution_bucket_review)
        data["family_review"] = dict(self.family_review)
        data["horizon_review"] = dict(self.horizon_review)
        data["data_quality_review"] = dict(self.data_quality_review)
        data["scenario_switch_review"] = dict(self.scenario_switch_review)
        data["refresh_required_review"] = dict(self.refresh_required_review)
        data["risk_catalog_hits"] = list(self.risk_catalog_hits)
        data["calibration_candidate_notes"] = list(self.calibration_candidate_notes)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        data["logic_version"] = LOGIC_VERSION
        return data


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _report_to_dict(evaluation_report: PredictionEvaluationReport | Mapping[str, Any] | None) -> Dict[str, Any] | None:
    if evaluation_report is None:
        return None
    if isinstance(evaluation_report, PredictionEvaluationReport):
        return evaluation_report.to_dict()
    return dict(evaluation_report)


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _records(report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    value = report.get("records")
    if not isinstance(value, (list, tuple)):
        return tuple()
    return tuple(item for item in value if isinstance(item, Mapping))


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator > 0 else None


def _unique(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if item))


def _bucket_values(summary: Mapping[str, Any], key: str) -> Dict[str, float | None]:
    raw = summary.get(key)
    if not isinstance(raw, Mapping):
        return {}
    return {str(k): _float_or_none(v) for k, v in raw.items()}


def _confidence_review(summary: Mapping[str, Any], notes: list[str], risks: list[str], warnings: list[str]) -> Dict[str, Any]:
    if not summary:
        warnings.append("confidence_summary_missing")
        notes.append("schema_drift_suspect")
        risks.append("schema_drift")
        return {
            "bucket_hit_rate": {},
            "bucket_average_return_bps": {},
            "bucket_not_evaluable_count": {},
            "ordering_notes": ("confidence_summary_missing",),
            "confidence_ordering_suspect": None,
        }
    hit_rate = _bucket_values(summary, "confidence_bucket_hit_rate")
    avg_return = _bucket_values(summary, "confidence_bucket_average_return_bps")
    not_eval = _mapping(summary.get("confidence_bucket_not_evaluable_count"))
    high = hit_rate.get("high")
    medium = hit_rate.get("medium")
    low = hit_rate.get("low")
    suspect = False
    ordering_notes: list[str] = []
    if high is not None and medium is not None and high < medium:
        suspect = True
        ordering_notes.append("high_below_medium")
    if high is not None and low is not None and high < low:
        suspect = True
        ordering_notes.append("high_below_low")
    if suspect:
        notes.append("confidence_ordering_suspect")
        notes.append("overconfidence_review_required")
        risks.append("overconfidence")
    return {
        "bucket_hit_rate": hit_rate,
        "bucket_average_return_bps": avg_return,
        "bucket_not_evaluable_count": dict(not_eval),
        "ordering_notes": tuple(ordering_notes),
        "confidence_ordering_suspect": suspect,
    }


def _caution_review(summary: Mapping[str, Any], notes: list[str], risks: list[str], warnings: list[str]) -> Dict[str, Any]:
    if not summary:
        warnings.append("caution_summary_missing")
        notes.append("schema_drift_suspect")
        risks.append("schema_drift")
        return {
            "bucket_adverse_excursion": {},
            "bucket_wrong_direction_rate": {},
            "bucket_not_evaluable_count": {},
            "discrimination_notes": ("caution_summary_missing",),
            "caution_bucket_not_discriminative": None,
        }
    adverse = _bucket_values(summary, "caution_bucket_adverse_excursion")
    wrong_rate = _bucket_values(summary, "caution_bucket_wrong_direction_rate")
    not_eval = _mapping(summary.get("caution_bucket_not_evaluable_count"))
    low = wrong_rate.get("low")
    high = wrong_rate.get("high")
    medium = wrong_rate.get("medium")
    not_discriminative = False
    discrimination_notes: list[str] = []
    if high is not None and low is not None and high <= low:
        not_discriminative = True
        discrimination_notes.append("high_not_above_low_wrong_direction_rate")
    if medium is not None and low is not None and medium <= low:
        discrimination_notes.append("medium_not_above_low_wrong_direction_rate")
    if not_discriminative:
        notes.append("caution_bucket_not_discriminative")
        risks.append("metric_mismatch")
    return {
        "bucket_adverse_excursion": adverse,
        "bucket_wrong_direction_rate": wrong_rate,
        "bucket_not_evaluable_count": dict(not_eval),
        "discrimination_notes": tuple(discrimination_notes),
        "caution_bucket_not_discriminative": not_discriminative,
    }


def _family_review(summary: Mapping[str, Any], warnings: list[str]) -> Dict[str, Any]:
    if not summary:
        warnings.append("family_summary_missing")
    hit_rate = _mapping(summary.get("directional_hit_rate_by_family"))
    candidates = tuple(str(key) for key, value in hit_rate.items() if _float_or_none(value) is not None and float(value) < 0.5)
    return {
        "directional_hit_rate_by_family": dict(hit_rate),
        "average_return_bps_by_family": _mapping(summary.get("average_return_bps_by_family")),
        "adverse_excursion_bps_by_family": _mapping(summary.get("adverse_excursion_bps_by_family")),
        "not_evaluable_count_by_family": _mapping(summary.get("not_evaluable_count_by_family")),
        "family_underperformance_candidates": candidates,
    }


def _horizon_review(summary: Mapping[str, Any], warnings: list[str]) -> Dict[str, Any]:
    if not summary:
        warnings.append("horizon_summary_missing")
    hit_rate = _mapping(summary.get("directional_hit_rate_by_horizon"))
    candidates = tuple(str(key) for key, value in hit_rate.items() if _float_or_none(value) is not None and float(value) < 0.5)
    return {
        "directional_hit_rate_by_horizon": dict(hit_rate),
        "average_return_bps_by_horizon": _mapping(summary.get("average_return_bps_by_horizon")),
        "adverse_excursion_bps_by_horizon": _mapping(summary.get("adverse_excursion_bps_by_horizon")),
        "not_evaluable_count_by_horizon": _mapping(summary.get("not_evaluable_count_by_horizon")),
        "horizon_underperformance_candidates": candidates,
    }


def _data_quality_review(report: Mapping[str, Any], records: tuple[Mapping[str, Any], ...], notes: list[str], risks: list[str]) -> Dict[str, Any]:
    evaluated = int(report.get("evaluated_record_count") or 0)
    not_eval = int(report.get("not_evaluable_count") or 0)
    total = evaluated + not_eval
    ratio = _ratio(not_eval, total)
    data_notes = tuple(str(item) for item in report.get("data_quality_notes") or ())
    skew = ratio is not None and ratio > 0.5
    missing_outcome = "outcome_window_missing" in data_notes
    if skew:
        notes.append("not_evaluable_skew")
        risks.append("not_evaluable_skew")
    if missing_outcome and not_eval > 0:
        notes.append("missing_outcome_skew")
        risks.append("missing_data_optimism")
    return {
        "not_evaluable_count": not_eval,
        "not_evaluable_ratio": ratio,
        "data_quality_notes": data_notes,
        "not_evaluable_skew": skew,
        "missing_outcome_skew": missing_outcome and not_eval > 0,
        "record_count": len(records),
    }


def _scenario_switch_review(summary: Mapping[str, Any], notes: list[str]) -> Dict[str, Any]:
    follow = summary.get("scenario_switch_watch_follow_through_rate")
    wrong = summary.get("scenario_switch_watch_wrong_direction_rate")
    not_ready = follow is None and wrong is None
    if not_ready:
        notes.append("scenario_switch_review_not_ready")
    return {
        "scenario_switch_watch_follow_through_rate": follow,
        "scenario_switch_watch_wrong_direction_rate": wrong,
        "scenario_switch_review_not_ready": not_ready,
    }


def _refresh_required_review(summary: Mapping[str, Any], notes: list[str]) -> Dict[str, Any]:
    follow = summary.get("refresh_required_follow_through_rate")
    not_eval = summary.get("refresh_required_not_evaluable_count")
    not_ready = follow is None
    if not_ready:
        notes.append("refresh_required_review_not_ready")
    return {
        "refresh_required_follow_through_rate": follow,
        "refresh_required_not_evaluable_count": not_eval,
        "refresh_required_review_not_ready": not_ready,
    }


def build_prediction_calibration_review(
    *,
    evaluation_report: PredictionEvaluationReport | Mapping[str, Any] | None,
    now: datetime | None = None,
) -> PredictionCalibrationReview:
    generated_at = _generated_at(now)
    report = _report_to_dict(evaluation_report)
    blockers: list[str] = []
    warnings: list[str] = []
    notes: list[str] = ["calibration_review_in_memory_only"]
    risks: list[str] = []

    if report is None:
        blockers.append("evaluation_report_missing")
        notes.append("evaluation_report_missing")
        return PredictionCalibrationReview(
            review_id=f"{LOGIC_VERSION}:{generated_at}:missing_evaluation_report",
            review_version=LOGIC_VERSION,
            generated_at=generated_at,
            source_evaluation_report_id=None,
            source_evaluation_version=None,
            market_uid="unknown",
            source_ref=None,
            evaluation_window_start=None,
            evaluation_window_end=None,
            evaluated_record_count=0,
            not_evaluable_count=0,
            skipped_record_count=0,
            confidence_bucket_review={},
            caution_bucket_review={},
            family_review={},
            horizon_review={},
            data_quality_review={"not_evaluable_count": 0, "not_evaluable_ratio": None, "data_quality_notes": (), "not_evaluable_skew": False, "missing_outcome_skew": False, "record_count": 0},
            scenario_switch_review={"scenario_switch_review_not_ready": True},
            refresh_required_review={"refresh_required_review_not_ready": True},
            risk_catalog_hits=(),
            calibration_candidate_notes=_unique(notes),
            blockers=_unique(blockers),
            warnings=_unique(warnings),
        )

    records = _records(report)
    if not records:
        warnings.append("evaluation_records_missing")
        notes.append("evaluation_records_missing")
    confidence = _confidence_review(_mapping(report.get("confidence_summary")), notes, risks, warnings)
    caution = _caution_review(_mapping(report.get("caution_summary")), notes, risks, warnings)
    family = _family_review(_mapping(report.get("family_summary")), warnings)
    horizon = _horizon_review(_mapping(report.get("horizon_summary")), warnings)
    data_quality = _data_quality_review(report, records, notes, risks)
    scenario = _scenario_switch_review(_mapping(report.get("scenario_switch_summary")), notes)
    refresh = _refresh_required_review(_mapping(report.get("refresh_required_summary")), notes)

    if family.get("family_underperformance_candidates"):
        notes.append("family_underperformance_candidate")
        risks.append("aggregation_hiding")
    if horizon.get("horizon_underperformance_candidates"):
        notes.append("horizon_underperformance_candidate")
        risks.append("aggregation_hiding")

    source_report_id = str(report.get("evaluation_report_id") or "") or None
    return PredictionCalibrationReview(
        review_id=f"{LOGIC_VERSION}:{generated_at}:{source_report_id or 'unknown_evaluation_report'}",
        review_version=LOGIC_VERSION,
        generated_at=generated_at,
        source_evaluation_report_id=source_report_id,
        source_evaluation_version=str(report.get("evaluation_version") or "") or None,
        market_uid=str(report.get("market_uid") or "unknown"),
        source_ref=str(report.get("source_ref") or "") or None,
        evaluation_window_start=str(report.get("evaluation_window_start") or "") or None,
        evaluation_window_end=str(report.get("evaluation_window_end") or "") or None,
        evaluated_record_count=int(report.get("evaluated_record_count") or 0),
        not_evaluable_count=int(report.get("not_evaluable_count") or 0),
        skipped_record_count=int(report.get("skipped_record_count") or 0),
        confidence_bucket_review=confidence,
        caution_bucket_review=caution,
        family_review=family,
        horizon_review=horizon,
        data_quality_review=data_quality,
        scenario_switch_review=scenario,
        refresh_required_review=refresh,
        risk_catalog_hits=_unique(risks),
        calibration_candidate_notes=_unique(notes),
        blockers=_unique(blockers),
        warnings=_unique(warnings),
    )
