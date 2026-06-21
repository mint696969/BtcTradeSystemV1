# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_preflight_bridge.py
# desc: PS-Q10F non-UI bridge from PS-Q10D built PredictionSystemResult payload to PS-Q9X latest payload export preflight. It does not export/write artifacts, create directories, mutate UI/runtime state, approve, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_latest_payload_export_preflight_contract import (
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION,
    TARGET_ARTIFACT_PATH_HINT,
    build_prediction_warroom_latest_payload_export_preflight_contract,
)
from .prediction_warroom_prediction_system_result_builder_runner import (
    PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION,
    build_prediction_warroom_prediction_system_result_builder_runner,
)

LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION = "prediction_warroom_latest_payload_export_preflight_bridge.ps_q10f.v1"
LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_SEQUENCE = (
    "require_operator_acknowledgement",
    "require_actual_read_request",
    "require_prediction_build_request",
    "require_export_preflight_request",
    "invoke_ps_q10d_prediction_system_result_builder_runner",
    "require_ps_q10d_ready_for_future_latest_payload_export_preflight",
    "pass_built_payload_to_ps_q9x_export_preflight_contract",
    "require_ps_q9x_ready_for_future_non_ui_export_runner",
    "emit_stdout_summary_only",
    "do_not_export_latest_prediction_artifact",
    "do_not_create_prediction_directory",
    "do_not_write_runtime_artifacts",
    "do_not_mutate_warroom_ui_or_runtime_state",
    "do_not_approve_append_ledger_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadExportPreflightBridgePacket:
    bridge_version: str
    bridge_id: str
    bridge_state: str
    hot_latest_root_hint: str
    target_artifact_path_hint: str = TARGET_ARTIFACT_PATH_HINT
    bridge_sequence: Tuple[str, ...] = LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_SEQUENCE
    builder_runner_version: str = PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION
    export_preflight_contract_version: str = LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION
    operator_acknowledged: bool = False
    actual_read_requested: bool = False
    prediction_build_requested: bool = False
    export_preflight_requested: bool = False
    allow_guard_test_root: bool = False
    builder_runner_packet: Mapping[str, Any] = field(default_factory=dict)
    export_preflight_packet: Mapping[str, Any] = field(default_factory=dict)
    prediction_result_payload_present: bool = False
    prediction_run_id: str = ""
    generated_at: str = ""
    market_uid: str = ""
    output_count: int = 0
    prediction_result_blocker_count: int = 0
    prediction_result_warning_count: int = 0
    prediction_result_warning_reasons: Tuple[str, ...] = ()
    ready_for_future_latest_payload_export_preflight: bool = False
    ready_for_future_non_ui_export_runner: bool = False
    ready_for_latest_payload_export: bool = False
    stdout_summary_lines: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_ui_bridge_only: bool = True
    stdout_only: bool = True
    prediction_system_result_built_by_child_runner: bool = False
    latest_prediction_artifact_exported_by_this_bridge: bool = False
    runtime_artifact_write_performed_by_this_bridge: bool = False
    target_directory_created_by_this_bridge: bool = False
    target_file_written_by_this_bridge: bool = False
    collector_state_write_performed_by_this_bridge: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_bridge_execution: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    would_collect_public_source: bool = False
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
            "bridge_version": self.bridge_version,
            "bridge_id": self.bridge_id,
            "bridge_state": self.bridge_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "target_artifact_path_hint": self.target_artifact_path_hint,
            "bridge_sequence": list(self.bridge_sequence),
            "builder_runner_version": self.builder_runner_version,
            "export_preflight_contract_version": self.export_preflight_contract_version,
            "operator_acknowledged": self.operator_acknowledged,
            "actual_read_requested": self.actual_read_requested,
            "prediction_build_requested": self.prediction_build_requested,
            "export_preflight_requested": self.export_preflight_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "builder_runner_packet": dict(self.builder_runner_packet),
            "export_preflight_packet": dict(self.export_preflight_packet),
            "prediction_result_payload_present": self.prediction_result_payload_present,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "output_count": self.output_count,
            "prediction_result_blocker_count": self.prediction_result_blocker_count,
            "prediction_result_warning_count": self.prediction_result_warning_count,
            "prediction_result_warning_reasons": list(self.prediction_result_warning_reasons),
            "ready_for_future_latest_payload_export_preflight": self.ready_for_future_latest_payload_export_preflight,
            "ready_for_future_non_ui_export_runner": self.ready_for_future_non_ui_export_runner,
            "ready_for_latest_payload_export": self.ready_for_latest_payload_export,
            "stdout_summary_lines": list(self.stdout_summary_lines),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_ui_bridge_only": self.non_ui_bridge_only,
            "stdout_only": self.stdout_only,
            "prediction_system_result_built_by_child_runner": self.prediction_system_result_built_by_child_runner,
            "latest_prediction_artifact_exported_by_this_bridge": self.latest_prediction_artifact_exported_by_this_bridge,
            "runtime_artifact_write_performed_by_this_bridge": self.runtime_artifact_write_performed_by_this_bridge,
            "target_directory_created_by_this_bridge": self.target_directory_created_by_this_bridge,
            "target_file_written_by_this_bridge": self.target_file_written_by_this_bridge,
            "collector_state_write_performed_by_this_bridge": self.collector_state_write_performed_by_this_bridge,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_bridge_execution": self.ui_triggered_bridge_execution,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "would_collect_public_source": self.would_collect_public_source,
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


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value if item)
    return tuple()


def _stdout_lines(
    *,
    state: str,
    q10d_state: str,
    q9x_state: str,
    run_id: str,
    output_count: int,
    result_warning_count: int,
    ready_for_export_runner: bool,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> tuple[str, ...]:
    return (
        "latest_payload_export_preflight_bridge=" + LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION,
        "state=" + state,
        "q10d_state=" + q10d_state,
        "q9x_state=" + q9x_state,
        "prediction_run_id=" + run_id,
        "output_count=" + str(output_count),
        "prediction_result_warning_count=" + str(result_warning_count),
        "ready_for_future_non_ui_export_runner=" + str(ready_for_export_runner),
        "ready_for_latest_payload_export=False",
        "blockers=" + ",".join(blockers),
        "warnings=" + ",".join(warnings),
        "ui=false;runtime_write=false;prediction_build=true;export=false;approval=false;ledger=false;autotrade=false;broker=false",
    )


def build_prediction_warroom_latest_payload_export_preflight_bridge(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    allow_actual_read: bool = False,
    allow_prediction_build: bool = False,
    allow_export_preflight: bool = False,
    allow_guard_test_root: bool = False,
    requested_latest_payload_export: bool = False,
    requested_runtime_write: bool = False,
    requested_warroom_ui_trigger: bool = False,
    requested_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomLatestPayloadExportPreflightBridgePacket:
    """Bridge PS-Q10D built payload to PS-Q9X export preflight without writing/exporting."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not allow_actual_read:
        blockers.append("allow_actual_read_false")
    if not allow_prediction_build:
        blockers.append("allow_prediction_build_false")
    if not allow_export_preflight:
        blockers.append("allow_export_preflight_false")
    if requested_latest_payload_export:
        blockers.append("latest_payload_export_not_allowed_by_preflight_bridge")
    if requested_runtime_write:
        blockers.append("runtime_write_not_allowed_by_preflight_bridge")
    if requested_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_by_preflight_bridge")
    if requested_approval_or_ledger_or_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed_by_preflight_bridge")

    builder_packet: Mapping[str, Any] = {}
    preflight_packet: Mapping[str, Any] = {}
    payload: Mapping[str, Any] = {}
    if not blockers:
        builder_packet = build_prediction_warroom_prediction_system_result_builder_runner(
            hot_latest_root_hint=str(hot_latest_root_hint),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_guard_test_root=allow_guard_test_root,
        ).to_dict()
        blockers.extend(str(item) for item in builder_packet.get("blocked_reasons", []))
        warnings.extend(str(item) for item in builder_packet.get("warning_reasons", []))
        if not bool(builder_packet.get("ready_for_future_latest_payload_export_preflight")):
            blockers.append("prediction_system_result_builder_runner_not_ready_for_export_preflight")
        payload = _as_mapping(builder_packet.get("prediction_result_payload"))
        if not payload:
            blockers.append("prediction_result_payload_missing_from_builder_runner")
        if not blockers:
            export_preflight_root = DEFAULT_HOT_LATEST_ROOT_HINT if allow_guard_test_root else str(hot_latest_root_hint)
            preflight_packet = build_prediction_warroom_latest_payload_export_preflight_contract(
                prediction_result_payload=payload,
                hot_latest_root_hint=export_preflight_root,
                operator_acknowledged=True,
            ).to_dict()
            blockers.extend(str(item) for item in preflight_packet.get("blocked_reasons", []))
            warnings.extend(str(item) for item in preflight_packet.get("warning_reasons", []))
            if not bool(preflight_packet.get("ready_for_future_non_ui_export_runner")):
                blockers.append("latest_payload_export_preflight_contract_not_ready")
    payload_map = _as_mapping(payload)
    run_identity = _as_mapping(payload_map.get("run_identity"))
    result_warnings = _as_str_tuple(payload_map.get("warnings"))
    if result_warnings:
        warnings.append("prediction_result_warnings_present:" + str(len(result_warnings)))
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready_for_export_runner = bool(preflight_packet.get("ready_for_future_non_ui_export_runner")) and not unique_blockers
    state = "latest_payload_export_preflight_bridge_ready_for_future_non_ui_export_runner" if ready_for_export_runner else "latest_payload_export_preflight_bridge_blocked"
    stdout = _stdout_lines(
        state=state,
        q10d_state=str(builder_packet.get("runner_state") or ""),
        q9x_state=str(preflight_packet.get("contract_state") or ""),
        run_id=str(run_identity.get("prediction_run_id") or ""),
        output_count=len(payload_map.get("outputs", [])) if isinstance(payload_map.get("outputs", []), list) else 0,
        result_warning_count=len(result_warnings),
        ready_for_export_runner=ready_for_export_runner,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )
    return PredictionWarRoomLatestPayloadExportPreflightBridgePacket(
        bridge_version=LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION,
        bridge_id=f"{LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION}:{state}",
        bridge_state=state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        operator_acknowledged=operator_acknowledged,
        actual_read_requested=allow_actual_read,
        prediction_build_requested=allow_prediction_build,
        export_preflight_requested=allow_export_preflight,
        allow_guard_test_root=allow_guard_test_root,
        builder_runner_packet=builder_packet,
        export_preflight_packet=preflight_packet,
        prediction_result_payload_present=bool(payload_map),
        prediction_run_id=str(run_identity.get("prediction_run_id") or ""),
        generated_at=str(run_identity.get("generated_at") or ""),
        market_uid=str(run_identity.get("market_uid") or ""),
        output_count=len(payload_map.get("outputs", [])) if isinstance(payload_map.get("outputs", []), list) else 0,
        prediction_result_blocker_count=int(builder_packet.get("prediction_result_blocker_count") or 0),
        prediction_result_warning_count=len(result_warnings),
        prediction_result_warning_reasons=result_warnings,
        ready_for_future_latest_payload_export_preflight=bool(builder_packet.get("ready_for_future_latest_payload_export_preflight")),
        ready_for_future_non_ui_export_runner=ready_for_export_runner,
        ready_for_latest_payload_export=False,
        stdout_summary_lines=stdout,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        prediction_system_result_built_by_child_runner=bool(builder_packet.get("prediction_system_result_built_by_this_runner")),
    )


def format_prediction_warroom_latest_payload_export_preflight_bridge_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    data = packet.to_dict() if hasattr(packet, "to_dict") else packet
    mapping = data if isinstance(data, Mapping) else {}
    lines = [str(item) for item in mapping.get("stdout_summary_lines", []) if str(item)]
    if lines:
        return "\n".join(lines)
    return "latest_payload_export_preflight_bridge=" + LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION + "\nstate=missing_packet"
