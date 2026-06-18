# path: ./btcts_next/src/btcts/autotrade/prediction_preview_status.py
# desc: Read-only AutoTrade status contract for already-provided prediction preview/readiness objects. No runtime publication, ledger append, mode apply, grant execution, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from btcts.prediction.prearmed_readiness import PredictionPreArmedReadinessSnapshot
from btcts.prediction.shadow_adapter import AutoTradeShadowSignalPreview

LOGIC_VERSION = "autotrade_prediction_preview_status.s138.v1"


@dataclass(frozen=True)
class AutoTradePredictionPreviewStatus:
    status_id: str
    generated_at: str
    status_state: str
    preview_id: str | None = None
    readiness_id: str | None = None
    readiness_state: str | None = None
    intended_mode: str | None = None
    preview_action: str | None = None
    preview_bias: str | None = None
    preview_confidence: str | None = None
    validation_state: str | None = None
    average_score: float | None = None
    label_hit_rate: float | None = None
    weak_families: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_append_shadow_decision: bool = False
    would_apply_mode: bool = False
    would_execute_prearmed_grant: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return self.status_state != "blocked" and not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["weak_families"] = list(self.weak_families)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        data["logic_version"] = LOGIC_VERSION
        return data


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _unique(values: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _metric(readiness: PredictionPreArmedReadinessSnapshot | None, name: str) -> Any:
    if readiness is None:
        return None
    metrics: Mapping[str, Any] = readiness.metrics
    return metrics.get(name)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dangerous_flag_blockers(prefix: str, obj: object) -> list[str]:
    checks = {
        "would_append_shadow_decision": "append_shadow_decision",
        "would_apply_mode": "mode_apply",
        "would_execute_prearmed_grant": "prearmed_grant_execution",
        "would_write_runtime_artifact": "runtime_artifact_write",
        "would_send_to_broker": "broker_send",
        "broker_execution_requested": "broker_execution_request",
        "mode_apply_requested": "mode_apply_request",
        "command_ledger_append_requested": "command_ledger_append_request",
        "approval_append_requested": "approval_append_request",
    }
    blockers: list[str] = []
    for attr, code in checks.items():
        if bool(getattr(obj, attr, False)):
            blockers.append(f"{prefix}_{code}_not_allowed")
    if getattr(obj, "read_only", True) is not True:
        blockers.append(f"{prefix}_not_read_only")
    if getattr(obj, "non_executing", True) is not True:
        blockers.append(f"{prefix}_not_non_executing")
    return blockers


def _status_state(*, readiness_state: str | None, blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blockers or readiness_state == "blocked":
        return "blocked"
    if warnings or readiness_state in {"review", "warn"}:
        return "review"
    return "ok"


def build_autotrade_prediction_preview_status(
    preview: AutoTradeShadowSignalPreview | None,
    readiness: PredictionPreArmedReadinessSnapshot | None,
    *,
    now: datetime | None = None,
) -> AutoTradePredictionPreviewStatus:
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []

    preview_id: str | None = None
    intended_mode: str | None = None
    preview_action: str | None = None
    preview_bias: str | None = None
    preview_confidence: str | None = None

    if preview is None:
        blockers.append("prediction_preview_missing")
    else:
        preview_id = preview.preview_id
        intended_mode = preview.intended_mode
        preview_action = preview.recommended_action
        preview_bias = preview.action_bias
        preview_confidence = preview.confidence
        blockers.extend(preview.blockers)
        warnings.extend(preview.warnings)
        blockers.extend(_dangerous_flag_blockers("prediction_preview", preview))

    readiness_id: str | None = None
    readiness_state: str | None = None
    validation_state: str | None = None
    average_score: float | None = None
    label_hit_rate: float | None = None
    weak_families: Tuple[str, ...] = ()

    if readiness is None:
        blockers.append("prediction_readiness_missing")
    else:
        readiness_id = readiness.readiness_id
        readiness_state = readiness.readiness_state
        validation_state = readiness.validation_state
        intended_mode = readiness.intended_mode or intended_mode
        preview_action = readiness.preview_action or preview_action
        preview_bias = readiness.preview_bias or preview_bias
        average_score = _float_or_none(readiness.calibration_average_score)
        if average_score is None:
            average_score = _float_or_none(_metric(readiness, "average_score"))
        label_hit_rate = _float_or_none(readiness.label_hit_rate)
        if label_hit_rate is None:
            label_hit_rate = _float_or_none(_metric(readiness, "label_hit_rate"))
        weak_families = tuple(readiness.weak_families)
        blockers.extend(readiness.blockers)
        warnings.extend(readiness.warnings)
        if readiness.readiness_state == "blocked":
            blockers.append("prediction_readiness_blocked")
        blockers.extend(_dangerous_flag_blockers("prediction_readiness", readiness))

    blocked_tuple = _unique(blockers)
    warning_tuple = _unique(warnings)
    state = _status_state(readiness_state=readiness_state, blockers=blocked_tuple, warnings=warning_tuple)
    return AutoTradePredictionPreviewStatus(
        status_id=f"{LOGIC_VERSION}:{generated_at}:{preview_id or 'missing_preview'}:{readiness_id or 'missing_readiness'}",
        generated_at=generated_at,
        status_state=state,
        preview_id=preview_id,
        readiness_id=readiness_id,
        readiness_state=readiness_state,
        intended_mode=intended_mode,
        preview_action=preview_action,
        preview_bias=preview_bias,
        preview_confidence=preview_confidence,
        validation_state=validation_state,
        average_score=average_score,
        label_hit_rate=label_hit_rate,
        weak_families=weak_families,
        blockers=blocked_tuple,
        warnings=warning_tuple,
        read_only=True,
        non_executing=True,
        would_append_shadow_decision=False,
        would_apply_mode=False,
        would_execute_prearmed_grant=False,
        would_write_runtime_artifact=False,
        would_send_to_broker=False,
        broker_execution_requested=False,
        mode_apply_requested=False,
        command_ledger_append_requested=False,
        approval_append_requested=False,
    )
