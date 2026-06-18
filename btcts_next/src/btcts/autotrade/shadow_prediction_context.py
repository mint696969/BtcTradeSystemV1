# path: ./btcts_next/src/btcts/autotrade/shadow_prediction_context.py
# desc: Read-only optional Shadow prediction context contract built from AutoTradePredictionPreviewStatus. No Shadow runner wiring, decision append, mode apply, grant execution, runtime write, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

LOGIC_VERSION = "autotrade_shadow_prediction_context.s141.v1"


@dataclass(frozen=True)
class AutoTradeShadowPredictionContext:
    context_id: str
    generated_at: str
    context_state: str
    source_status_id: str | None = None
    status_state: str | None = None
    preview_id: str | None = None
    readiness_id: str | None = None
    readiness_state: str | None = None
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
    optional_context_only: bool = True
    persist_false_only: bool = True
    would_change_shadow_candidate: bool = False
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
    def usable_as_context(self) -> bool:
        return self.context_state != "blocked" and not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["weak_families"] = list(self.weak_families)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable_as_context"] = self.usable_as_context
        data["logic_version"] = LOGIC_VERSION
        return data


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _payload(status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    if status is None:
        return {}
    if isinstance(status, Mapping):
        return dict(status)
    return status.to_dict()


def _unique(values: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _tuple_text(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    try:
        return tuple(str(item) for item in value if str(item))
    except TypeError:
        return (str(value),) if str(value) else ()


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dangerous_payload_blockers(data: Mapping[str, Any]) -> list[str]:
    checks = {
        "would_append_shadow_decision": "shadow_decision_append",
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
        if bool(data.get(attr, False)):
            blockers.append(f"prediction_status_{code}_not_allowed")
    if data.get("read_only", True) is not True:
        blockers.append("prediction_status_not_read_only")
    if data.get("non_executing", True) is not True:
        blockers.append("prediction_status_not_non_executing")
    return blockers


def _context_state(status_state: str | None, blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blockers or status_state == "blocked":
        return "blocked"
    if warnings or status_state == "review":
        return "review"
    if status_state == "ok":
        return "ok"
    return "unavailable"


def build_autotrade_shadow_prediction_context(
    status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    *,
    now: datetime | None = None,
) -> AutoTradeShadowPredictionContext:
    generated_at = _generated_at(now)
    data = _payload(status)
    if not data:
        blockers = ("prediction_status_missing",)
        return AutoTradeShadowPredictionContext(
            context_id=f"{LOGIC_VERSION}:{generated_at}:missing_status",
            generated_at=generated_at,
            context_state="blocked",
            blockers=blockers,
        )

    source_status_id = data.get("status_id")
    status_state = data.get("status_state")
    blockers = list(_tuple_text(data.get("blockers")))
    warnings = list(_tuple_text(data.get("warnings")))
    blockers.extend(_dangerous_payload_blockers(data))
    blocked_tuple = _unique(blockers)
    warning_tuple = _unique(warnings)
    context_state = _context_state(str(status_state) if status_state is not None else None, blocked_tuple, warning_tuple)
    return AutoTradeShadowPredictionContext(
        context_id=f"{LOGIC_VERSION}:{generated_at}:{source_status_id or 'unknown_status'}",
        generated_at=generated_at,
        context_state=context_state,
        source_status_id=str(source_status_id) if source_status_id is not None else None,
        status_state=str(status_state) if status_state is not None else None,
        preview_id=str(data.get("preview_id")) if data.get("preview_id") is not None else None,
        readiness_id=str(data.get("readiness_id")) if data.get("readiness_id") is not None else None,
        readiness_state=str(data.get("readiness_state")) if data.get("readiness_state") is not None else None,
        preview_action=str(data.get("preview_action")) if data.get("preview_action") is not None else None,
        preview_bias=str(data.get("preview_bias")) if data.get("preview_bias") is not None else None,
        preview_confidence=str(data.get("preview_confidence")) if data.get("preview_confidence") is not None else None,
        validation_state=str(data.get("validation_state")) if data.get("validation_state") is not None else None,
        average_score=_float_or_none(data.get("average_score")),
        label_hit_rate=_float_or_none(data.get("label_hit_rate")),
        weak_families=_tuple_text(data.get("weak_families")),
        blockers=blocked_tuple,
        warnings=warning_tuple,
        read_only=True,
        non_executing=True,
        optional_context_only=True,
        persist_false_only=True,
        would_change_shadow_candidate=False,
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
