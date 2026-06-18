# path: ./btcts_next/src/btcts/autotrade/prediction_preview_artifact_preflight.py
# desc: Controlled preflight packet for a future prediction preview/status artifact. No artifact write, runtime path creation, decision append, mode apply, grant execution, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus
from btcts.autotrade.shadow_prediction_context import AutoTradeShadowPredictionContext

LOGIC_VERSION = "autotrade_prediction_preview_artifact_preflight.s142.v1"
ARTIFACT_KIND = "prediction_preview_status_artifact"
ARTIFACT_FORMAT = "json"


@dataclass(frozen=True)
class AutoTradePredictionPreviewArtifactPreflight:
    preflight_id: str
    generated_at: str
    preflight_state: str
    artifact_kind: str = ARTIFACT_KIND
    artifact_format: str = ARTIFACT_FORMAT
    artifact_path: str | None = None
    source_status_id: str | None = None
    source_context_id: str | None = None
    status_state: str | None = None
    context_state: str | None = None
    preview_id: str | None = None
    readiness_id: str | None = None
    readiness_state: str | None = None
    preview_action: str | None = None
    preview_bias: str | None = None
    preview_confidence: str | None = None
    weak_families: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    planned_payload_keys: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    preflight_only: bool = True
    artifact_write_preflight_only: bool = True
    artifact_write_allowed: bool = False
    artifact_write_requested: bool = False
    would_write_preview_status_artifact: bool = False
    would_write_runtime_artifact: bool = False
    would_append_shadow_decision: bool = False
    would_apply_mode: bool = False
    would_execute_prearmed_grant: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def ready_for_future_write(self) -> bool:
        return self.preflight_state == "ready" and not self.blockers and self.artifact_path is not None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["weak_families"] = list(self.weak_families)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["planned_payload_keys"] = list(self.planned_payload_keys)
        data["ready_for_future_write"] = self.ready_for_future_write
        data["logic_version"] = LOGIC_VERSION
        return data


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _payload(obj: object | Mapping[str, Any] | None) -> dict[str, Any]:
    if obj is None:
        return {}
    if isinstance(obj, Mapping):
        return dict(obj)
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        data = to_dict()
        return dict(data) if isinstance(data, Mapping) else {}
    return {}


def _tuple_text(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    try:
        return tuple(str(item) for item in value if str(item))
    except TypeError:
        return (str(value),) if str(value) else ()


def _unique(values: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _dangerous_payload_blockers(prefix: str, data: Mapping[str, Any]) -> list[str]:
    checks = {
        "would_write_preview_status_artifact": "preview_status_artifact_write",
        "would_write_runtime_artifact": "runtime_artifact_write",
        "would_append_shadow_decision": "shadow_decision_append",
        "would_change_shadow_candidate": "shadow_candidate_change",
        "would_apply_mode": "mode_apply",
        "would_execute_prearmed_grant": "prearmed_grant_execution",
        "would_send_to_broker": "broker_send",
        "broker_execution_requested": "broker_execution_request",
        "mode_apply_requested": "mode_apply_request",
        "command_ledger_append_requested": "command_ledger_append_request",
        "approval_append_requested": "approval_append_request",
    }
    blockers: list[str] = []
    for attr, code in checks.items():
        if bool(data.get(attr, False)):
            blockers.append(f"{prefix}_{code}_not_allowed")
    if data.get("read_only", True) is not True:
        blockers.append(f"{prefix}_not_read_only")
    if data.get("non_executing", True) is not True:
        blockers.append(f"{prefix}_not_non_executing")
    return blockers


def _preflight_state(status_state: str | None, context_state: str | None, blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blockers or status_state == "blocked" or context_state == "blocked":
        return "blocked"
    if warnings or status_state == "review" or context_state == "review":
        return "review"
    if status_state == "ok" and context_state in {"ok", None}:
        return "ready"
    return "blocked"


def build_prediction_preview_artifact_preflight(
    status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
    context: AutoTradeShadowPredictionContext | Mapping[str, Any] | None = None,
    *,
    artifact_path: str | None = None,
    now: datetime | None = None,
) -> AutoTradePredictionPreviewArtifactPreflight:
    generated_at = _generated_at(now)
    status_data = _payload(status)
    context_data = _payload(context)
    blockers: list[str] = []
    warnings: list[str] = []

    if not status_data:
        blockers.append("prediction_status_missing")
    else:
        blockers.extend(_tuple_text(status_data.get("blockers")))
        warnings.extend(_tuple_text(status_data.get("warnings")))
        blockers.extend(_dangerous_payload_blockers("prediction_status", status_data))
        if status_data.get("status_state") == "blocked":
            blockers.append("prediction_status_blocked")

    if context is not None:
        if not context_data:
            blockers.append("prediction_context_unreadable")
        else:
            blockers.extend(_tuple_text(context_data.get("blockers")))
            warnings.extend(_tuple_text(context_data.get("warnings")))
            blockers.extend(_dangerous_payload_blockers("prediction_context", context_data))
            if context_data.get("context_state") == "blocked":
                blockers.append("prediction_context_blocked")
    else:
        warnings.append("prediction_context_not_provided")

    if artifact_path is None or str(artifact_path).strip() == "":
        blockers.append("artifact_path_missing")

    status_state = str(status_data.get("status_state")) if status_data.get("status_state") is not None else None
    context_state = str(context_data.get("context_state")) if context_data.get("context_state") is not None else None
    blocked_tuple = _unique(blockers)
    warning_tuple = _unique(warnings)
    state = _preflight_state(status_state, context_state, blocked_tuple, warning_tuple)
    source_status_id = status_data.get("status_id")
    source_context_id = context_data.get("context_id")
    return AutoTradePredictionPreviewArtifactPreflight(
        preflight_id=f"{LOGIC_VERSION}:{generated_at}:{source_status_id or 'missing_status'}:{source_context_id or 'no_context'}",
        generated_at=generated_at,
        preflight_state=state,
        artifact_path=str(artifact_path).strip() if artifact_path is not None and str(artifact_path).strip() else None,
        source_status_id=str(source_status_id) if source_status_id is not None else None,
        source_context_id=str(source_context_id) if source_context_id is not None else None,
        status_state=status_state,
        context_state=context_state,
        preview_id=str(status_data.get("preview_id")) if status_data.get("preview_id") is not None else None,
        readiness_id=str(status_data.get("readiness_id")) if status_data.get("readiness_id") is not None else None,
        readiness_state=str(status_data.get("readiness_state")) if status_data.get("readiness_state") is not None else None,
        preview_action=str(status_data.get("preview_action")) if status_data.get("preview_action") is not None else None,
        preview_bias=str(status_data.get("preview_bias")) if status_data.get("preview_bias") is not None else None,
        preview_confidence=str(status_data.get("preview_confidence")) if status_data.get("preview_confidence") is not None else None,
        weak_families=_tuple_text(status_data.get("weak_families") or context_data.get("weak_families")),
        blockers=blocked_tuple,
        warnings=warning_tuple,
        planned_payload_keys=(
            "artifact_kind",
            "generated_at",
            "prediction_preview_status",
            "shadow_prediction_context",
            "read_only",
            "non_executing",
            "no_decision_append",
        ),
        read_only=True,
        non_executing=True,
        preflight_only=True,
        artifact_write_preflight_only=True,
        artifact_write_allowed=False,
        artifact_write_requested=False,
        would_write_preview_status_artifact=False,
        would_write_runtime_artifact=False,
        would_append_shadow_decision=False,
        would_apply_mode=False,
        would_execute_prearmed_grant=False,
        would_send_to_broker=False,
        broker_execution_requested=False,
        mode_apply_requested=False,
        command_ledger_append_requested=False,
        approval_append_requested=False,
    )
