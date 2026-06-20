# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_loaded_payload_schema_validation_result_panel.py
# desc: PS-Q9C validation-result panel data for loaded Prediction WarRoom payloads. Consumes PS-Q9B loader result mappings and Q5C schema validators; no file reads, payload decode, rendering, WarRoom mutation, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_latest_payload_read_only_loader import READ_ONLY_LOADER_VERSION
from .prediction_warroom_payload_schema_validator import (
    DISPLAY_PACKET_VERSION,
    VALIDATOR_VERSION,
    validate_prediction_warroom_display_packet_schema,
    validate_prediction_warroom_widget_group_index_schema,
)

LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION = "prediction_warroom_loaded_payload_schema_validation_result_panel.ps_q9c.v1"

_ROLE_SCHEMA_TARGETS = {
    "prediction_warroom_display_packet": "display_packet",
    "prediction_warroom_widget_group_index": "widget_group_index",
    "prediction_source_quality_snapshot": "source_quality_snapshot_minimal",
    "prediction_system_result_snapshot": "prediction_system_result_snapshot_minimal",
}


@dataclass(frozen=True)
class PredictionWarRoomLoadedPayloadSchemaValidationItem:
    artifact_role: str
    schema_target: str
    validation_state: str
    validator_report_version: str
    valid: bool = False
    issue_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    summary_ja: str = ""
    checked_sections: Tuple[str, ...] = ()
    issue_summaries: Tuple[Mapping[str, Any], ...] = ()
    loaded_payload_present: bool = False
    payload_type: str | None = None
    payload_key_count: int = 0
    payload_preview_keys: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    validation_panel_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_role": self.artifact_role,
            "schema_target": self.schema_target,
            "validation_state": self.validation_state,
            "validator_report_version": self.validator_report_version,
            "valid": self.valid,
            "issue_count": self.issue_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "summary_ja": self.summary_ja,
            "checked_sections": list(self.checked_sections),
            "issue_summaries": [dict(item) for item in self.issue_summaries],
            "loaded_payload_present": self.loaded_payload_present,
            "payload_type": self.payload_type,
            "payload_key_count": self.payload_key_count,
            "payload_preview_keys": list(self.payload_preview_keys),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "validation_panel_only": self.validation_panel_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


@dataclass(frozen=True)
class PredictionWarRoomLoadedPayloadSchemaValidationPanelPacket:
    panel_version: str
    panel_id: str
    panel_state: str
    loader_result_version: str
    schema_validator_contract_version: str
    validation_items: Tuple[PredictionWarRoomLoadedPayloadSchemaValidationItem, ...] = ()
    loaded_payload_count: int = 0
    validated_payload_count: int = 0
    valid_payload_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    panel_summary_ja: str = ""
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    validation_panel_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "panel_version": self.panel_version,
            "panel_id": self.panel_id,
            "panel_state": self.panel_state,
            "loader_result_version": self.loader_result_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "validation_items": [item.to_dict() for item in self.validation_items],
            "loaded_payload_count": self.loaded_payload_count,
            "validated_payload_count": self.validated_payload_count,
            "valid_payload_count": self.valid_payload_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "panel_summary_ja": self.panel_summary_ja,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "validation_panel_only": self.validation_panel_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _payload_preview(payload: Any) -> tuple[str, ...]:
    if isinstance(payload, Mapping):
        return tuple(str(key) for key in list(payload.keys())[:12])
    return ()


def _issue_summaries(report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    summaries: list[Mapping[str, Any]] = []
    for raw in _list(report.get("issues"))[:12]:
        item = _as_mapping(raw)
        summaries.append(
            {
                "issue_code": str(item.get("issue_code") or "unknown"),
                "severity": str(item.get("severity") or "unknown"),
                "path": str(item.get("path") or ""),
                "message_ja": str(item.get("message_ja") or ""),
            }
        )
    return tuple(summaries)


def _minimal_payload_report(*, artifact_role: str, payload: Any) -> Mapping[str, Any]:
    issues: list[Mapping[str, Any]] = []
    if not isinstance(payload, Mapping):
        issues.append(
            {
                "issue_code": "loaded_payload_not_mapping",
                "severity": "blocker",
                "path": artifact_role,
                "message_ja": "loaded payloadがMappingではありません。",
            }
        )
    elif not payload:
        issues.append(
            {
                "issue_code": "loaded_payload_empty_mapping",
                "severity": "warning",
                "path": artifact_role,
                "message_ja": "loaded payloadが空です。",
            }
        )
    blocker_count = sum(1 for item in issues if item.get("severity") == "blocker")
    warning_count = sum(1 for item in issues if item.get("severity") == "warning")
    return {
        "report_version": VALIDATOR_VERSION,
        "schema_target": _ROLE_SCHEMA_TARGETS.get(artifact_role, "loaded_payload_minimal"),
        "valid": blocker_count == 0,
        "issue_count": len(issues),
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "info_count": 0,
        "issues": issues,
        "summary_ja": "schema valid" if blocker_count == 0 else f"schema blockers: {blocker_count}",
        "checked_sections": ("loaded_payload_mapping", "loaded_payload_non_empty"),
    }


def _validate_loaded_payload(*, artifact_role: str, payload: Any) -> Mapping[str, Any]:
    if artifact_role == "prediction_warroom_display_packet":
        return validate_prediction_warroom_display_packet_schema(payload).to_dict()
    if artifact_role == "prediction_warroom_widget_group_index":
        return validate_prediction_warroom_widget_group_index_schema(payload).to_dict()
    if artifact_role == "prediction_source_quality_snapshot":
        return _minimal_payload_report(artifact_role=artifact_role, payload=payload)
    if artifact_role == "prediction_system_result_snapshot":
        # The actual PredictionSystemResult-to-display lowering belongs to PS-Q9D.
        # PS-Q9C only checks that a decoded mapping is present and reportable.
        return _minimal_payload_report(artifact_role=artifact_role, payload=payload)
    return _minimal_payload_report(artifact_role=artifact_role, payload=payload)


def _item_from_report(*, artifact_role: str, payload: Any, report: Mapping[str, Any]) -> PredictionWarRoomLoadedPayloadSchemaValidationItem:
    valid = bool(report.get("valid"))
    blocker_count = int(report.get("blocker_count") or 0)
    warning_count = int(report.get("warning_count") or 0)
    if blocker_count:
        state = "schema_validation_blocked"
    elif warning_count:
        state = "schema_validation_valid_with_warnings"
    elif valid:
        state = "schema_validation_valid"
    else:
        state = "schema_validation_unknown"
    return PredictionWarRoomLoadedPayloadSchemaValidationItem(
        artifact_role=artifact_role,
        schema_target=str(report.get("schema_target") or _ROLE_SCHEMA_TARGETS.get(artifact_role, "loaded_payload_minimal")),
        validation_state=state,
        validator_report_version=str(report.get("report_version") or VALIDATOR_VERSION),
        valid=valid,
        issue_count=int(report.get("issue_count") or 0),
        blocker_count=blocker_count,
        warning_count=warning_count,
        info_count=int(report.get("info_count") or 0),
        summary_ja=str(report.get("summary_ja") or ""),
        checked_sections=tuple(str(item) for item in _list(report.get("checked_sections"))),
        issue_summaries=_issue_summaries(report),
        loaded_payload_present=True,
        payload_type=type(payload).__name__,
        payload_key_count=len(payload) if isinstance(payload, Mapping) else 0,
        payload_preview_keys=_payload_preview(payload),
    )


def build_prediction_warroom_loaded_payload_schema_validation_result_panel(
    *,
    loader_result: Mapping[str, Any] | Any,
) -> PredictionWarRoomLoadedPayloadSchemaValidationPanelPacket:
    """Build PS-Q9C loaded-payload validation result panel data without reading, decoding, rendering, or mutating runtime state."""
    loader = _as_mapping(loader_result)
    loaded_payloads = _as_mapping(loader.get("loaded_payloads"))
    loader_version = str(loader.get("loader_version") or READ_ONLY_LOADER_VERSION)
    items: list[PredictionWarRoomLoadedPayloadSchemaValidationItem] = []
    blocked_reasons: list[str] = [str(item) for item in _list(loader.get("blocker_reasons"))]
    warning_reasons: list[str] = [str(item) for item in _list(loader.get("warning_reasons"))]
    if not loaded_payloads:
        blocked_reasons.append("no_loaded_payloads_available_for_schema_validation")
    for artifact_role, payload in loaded_payloads.items():
        role = str(artifact_role)
        report = _validate_loaded_payload(artifact_role=role, payload=payload)
        item = _item_from_report(artifact_role=role, payload=payload, report=report)
        items.append(item)
        if item.blocker_count:
            blocked_reasons.append(f"{role}_schema_validation_blocked")
        if item.warning_count:
            warning_reasons.append(f"{role}_schema_validation_warning")
    validated_count = len(items)
    valid_count = sum(1 for item in items if item.valid)
    blocker_count = sum(item.blocker_count for item in items) + (1 if not loaded_payloads else 0)
    warning_count = sum(item.warning_count for item in items)
    if blocker_count:
        panel_state = "schema_validation_panel_blocked"
        summary = f"loaded payload schema blockers: {blocker_count}"
    elif warning_count:
        panel_state = "schema_validation_panel_valid_with_warnings"
        summary = f"loaded payload schema valid with warnings: {warning_count}"
    else:
        panel_state = "schema_validation_panel_valid"
        summary = "loaded payload schema valid"
    return PredictionWarRoomLoadedPayloadSchemaValidationPanelPacket(
        panel_version=LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION,
        panel_id=f"{LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION}:latest:{panel_state}",
        panel_state=panel_state,
        loader_result_version=loader_version,
        schema_validator_contract_version=VALIDATOR_VERSION,
        validation_items=tuple(items),
        loaded_payload_count=len(loaded_payloads),
        validated_payload_count=validated_count,
        valid_payload_count=valid_count,
        blocker_count=blocker_count,
        warning_count=warning_count,
        panel_summary_ja=summary,
        blocked_reasons=tuple(dict.fromkeys(item for item in blocked_reasons if item)),
        warning_reasons=tuple(dict.fromkeys(item for item in warning_reasons if item)),
        handoff_summary={
            "panel_boundary": "ps_q9c_loaded_payload_schema_validation_result_panel_only",
            "responsibility": "validate/report loaded payload schema state before PS-Q9D display-packet lowering",
            "loader_result_version": loader_version,
            "schema_validator_contract_version": VALIDATOR_VERSION,
            "loaded_payload_count": len(loaded_payloads),
            "validated_payload_count": validated_count,
            "valid_payload_count": valid_count,
            "display_packet_lowering_enabled": False,
            "warroom_card_rendering_enabled": False,
            "warroom_page_mutation_enabled": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled_by_this_panel": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
