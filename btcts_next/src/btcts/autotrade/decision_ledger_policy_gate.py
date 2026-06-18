# path: ./btcts_next/src/btcts/autotrade/decision_ledger_policy_gate.py
# desc: Read-only policy/status gate for future explicit decision ledger integration. No decision append, live_shadow wiring, mode apply, grant execution, runtime write, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from btcts.autotrade.prediction_preview_artifact_preflight import AutoTradePredictionPreviewArtifactPreflight
from btcts.autotrade.shadow_prediction_context import AutoTradeShadowPredictionContext

LOGIC_VERSION = "autotrade_decision_ledger_policy_gate.s143.v1"
POLICY_GATE_SCOPE = "explicit_decision_ledger_integration_policy_gate"

REQUIRED_APPROVALS = (
    "operator_explicit_policy_rescope",
    "operator_acknowledges_decision_ledger_append_risk",
    "operator_confirms_shadow_only_no_broker_execution",
)
REQUIRED_GUARDS = (
    "persist_false_or_append_disabled_guard",
    "no_broker_private_api_external_api_guard",
    "no_mode_apply_guard",
    "no_prearmed_grant_execution_guard",
    "no_ui_command_buttons_guard",
    "explicit_diff_review_guard",
)
NON_PERMISSIONS = (
    "no_decision_append_in_s143",
    "no_live_shadow_behavior_modification_in_s143",
    "no_persist_true_path_in_s143",
    "no_mode_apply_in_s143",
    "no_prearmed_grant_execution_in_s143",
    "no_broker_or_private_api_in_s143",
    "no_external_api_or_collector_import_in_s143",
    "no_ui_command_buttons_in_s143",
)


@dataclass(frozen=True)
class AutoTradeDecisionLedgerIntegrationPolicyGate:
    gate_id: str
    generated_at: str
    gate_state: str
    requested_scope: str = POLICY_GATE_SCOPE
    source_preflight_id: str | None = None
    source_context_id: str | None = None
    preflight_state: str | None = None
    context_state: str | None = None
    operator_policy_acknowledged: bool = False
    explicit_operator_approval: bool = False
    decision_ledger_integration_allowed: bool = False
    decision_append_allowed: bool = False
    live_shadow_behavior_change_allowed: bool = False
    persist_true_allowed: bool = False
    required_approvals: Tuple[str, ...] = REQUIRED_APPROVALS
    required_guards: Tuple[str, ...] = REQUIRED_GUARDS
    non_permissions: Tuple[str, ...] = NON_PERMISSIONS
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    policy_gate_only: bool = True
    would_append_shadow_decision: bool = False
    would_apply_mode: bool = False
    would_execute_prearmed_grant: bool = False
    would_write_runtime_artifact: bool = False
    would_write_preview_status_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def closed(self) -> bool:
        return self.gate_state == "blocked"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["required_approvals"] = list(self.required_approvals)
        data["required_guards"] = list(self.required_guards)
        data["non_permissions"] = list(self.non_permissions)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["closed"] = self.closed
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
        "artifact_write_allowed": "artifact_write_allowance",
        "artifact_write_requested": "artifact_write_request",
        "would_write_preview_status_artifact": "preview_status_artifact_write",
        "would_write_runtime_artifact": "runtime_artifact_write",
        "decision_ledger_integration_allowed": "decision_ledger_integration_allowance",
        "decision_append_allowed": "decision_append_allowance",
        "live_shadow_behavior_change_allowed": "live_shadow_behavior_change_allowance",
        "persist_true_allowed": "persist_true_allowance",
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


def _gate_state(blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blockers:
        return "blocked"
    if warnings:
        return "review"
    return "blocked"


def build_decision_ledger_integration_policy_gate(
    preflight: AutoTradePredictionPreviewArtifactPreflight | Mapping[str, Any] | None,
    context: AutoTradeShadowPredictionContext | Mapping[str, Any] | None = None,
    *,
    operator_policy_acknowledged: bool = False,
    explicit_operator_approval: bool = False,
    now: datetime | None = None,
) -> AutoTradeDecisionLedgerIntegrationPolicyGate:
    generated_at = _generated_at(now)
    preflight_data = _payload(preflight)
    context_data = _payload(context)
    blockers: list[str] = ["s143_policy_gate_does_not_authorize_decision_append"]
    warnings: list[str] = []

    if not preflight_data:
        blockers.append("artifact_preflight_missing")
    else:
        blockers.extend(_tuple_text(preflight_data.get("blockers")))
        warnings.extend(_tuple_text(preflight_data.get("warnings")))
        blockers.extend(_dangerous_payload_blockers("artifact_preflight", preflight_data))
        if preflight_data.get("preflight_state") != "ready":
            blockers.append("artifact_preflight_not_ready")

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

    if not operator_policy_acknowledged:
        blockers.append("operator_policy_acknowledgement_missing")
    if not explicit_operator_approval:
        blockers.append("explicit_operator_approval_missing")

    blocked_tuple = _unique(blockers)
    warning_tuple = _unique(warnings)
    gate_state = _gate_state(blocked_tuple, warning_tuple)
    preflight_id = preflight_data.get("preflight_id")
    context_id = context_data.get("context_id")
    return AutoTradeDecisionLedgerIntegrationPolicyGate(
        gate_id=f"{LOGIC_VERSION}:{generated_at}:{preflight_id or 'missing_preflight'}:{context_id or 'no_context'}",
        generated_at=generated_at,
        gate_state=gate_state,
        source_preflight_id=str(preflight_id) if preflight_id is not None else None,
        source_context_id=str(context_id) if context_id is not None else None,
        preflight_state=str(preflight_data.get("preflight_state")) if preflight_data.get("preflight_state") is not None else None,
        context_state=str(context_data.get("context_state")) if context_data.get("context_state") is not None else None,
        operator_policy_acknowledged=bool(operator_policy_acknowledged),
        explicit_operator_approval=bool(explicit_operator_approval),
        decision_ledger_integration_allowed=False,
        decision_append_allowed=False,
        live_shadow_behavior_change_allowed=False,
        persist_true_allowed=False,
        required_approvals=REQUIRED_APPROVALS,
        required_guards=REQUIRED_GUARDS,
        non_permissions=NON_PERMISSIONS,
        blockers=blocked_tuple,
        warnings=warning_tuple,
        read_only=True,
        non_executing=True,
        policy_gate_only=True,
        would_append_shadow_decision=False,
        would_apply_mode=False,
        would_execute_prearmed_grant=False,
        would_write_runtime_artifact=False,
        would_write_preview_status_artifact=False,
        would_send_to_broker=False,
        broker_execution_requested=False,
        mode_apply_requested=False,
        command_ledger_append_requested=False,
        approval_append_requested=False,
    )
