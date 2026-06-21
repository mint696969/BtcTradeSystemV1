# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_actual_export_runner.py
# desc: PS-Q10H non-UI actual latest payload export wrapper. It invokes PS-Q10F to build/preflight a PredictionSystemResult payload, then invokes PS-Q9Y to write exactly prediction/latest_prediction_system_result.json only when explicitly acknowledged. No UI, approval, ledger, AutoTrade, or broker/private API behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_latest_payload_export_preflight_bridge import (
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION,
    build_prediction_warroom_latest_payload_export_preflight_bridge,
)
from .prediction_warroom_latest_payload_export_runner import (
    LATEST_PAYLOAD_EXPORT_RUNNER_VERSION,
    build_prediction_warroom_latest_payload_export_runner,
)

LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION = "prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1"
LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_SEQUENCE = (
    "require_operator_acknowledgement",
    "require_actual_read_request",
    "require_prediction_build_request",
    "require_export_preflight_request",
    "require_latest_payload_export_request",
    "require_runtime_artifact_write_request",
    "invoke_ps_q10f_latest_payload_export_preflight_bridge",
    "require_ps_q10f_ready_for_future_non_ui_export_runner",
    "extract_built_prediction_system_result_payload_from_ps_q10d_child_packet",
    "invoke_ps_q9y_latest_payload_export_runner",
    "write_exactly_prediction_latest_prediction_system_result_json_via_ps_q9y",
    "emit_stdout_summary_only",
    "do_not_run_from_warroom_ui",
    "do_not_mutate_warroom_ui_or_runtime_state",
    "do_not_approve_append_ledger_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadActualExportRunnerPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    hot_latest_root_hint: str
    runner_sequence: Tuple[str, ...] = LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_SEQUENCE
    preflight_bridge_version: str = LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION
    export_runner_version: str = LATEST_PAYLOAD_EXPORT_RUNNER_VERSION
    operator_acknowledged: bool = False
    actual_read_requested: bool = False
    prediction_build_requested: bool = False
    export_preflight_requested: bool = False
    latest_payload_export_requested: bool = False
    runtime_artifact_write_requested: bool = False
    allow_guard_test_root: bool = False
    preflight_bridge_packet: Mapping[str, Any] = field(default_factory=dict)
    export_runner_packet: Mapping[str, Any] = field(default_factory=dict)
    prediction_result_payload_present: bool = False
    prediction_run_id: str = ""
    generated_at: str = ""
    market_uid: str = ""
    output_count: int = 0
    prediction_result_blocker_count: int = 0
    prediction_result_warning_count: int = 0
    target_artifact_path: str = ""
    target_file_written: bool = False
    target_file_size_bytes: int | None = None
    exported_at: str = ""
    stdout_summary_lines: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only_input: bool = True
    non_ui_runner_only: bool = True
    stdout_only: bool = True
    prediction_system_result_built_by_child_runner: bool = False
    latest_prediction_artifact_exported_by_child_runner: bool = False
    runtime_artifact_write_performed_by_child_runner: bool = False
    target_directory_created_by_child_runner: bool = False
    target_file_written_by_child_runner: bool = False
    collector_state_write_performed_by_this_runner: bool = False
    hot_file_read_performed_by_export_runner: bool = False
    payload_decode_performed_by_export_runner: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_runner_execution: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    would_collect_public_source: bool = False
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
            "runner_version": self.runner_version,
            "runner_id": self.runner_id,
            "runner_state": self.runner_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "runner_sequence": list(self.runner_sequence),
            "preflight_bridge_version": self.preflight_bridge_version,
            "export_runner_version": self.export_runner_version,
            "operator_acknowledged": self.operator_acknowledged,
            "actual_read_requested": self.actual_read_requested,
            "prediction_build_requested": self.prediction_build_requested,
            "export_preflight_requested": self.export_preflight_requested,
            "latest_payload_export_requested": self.latest_payload_export_requested,
            "runtime_artifact_write_requested": self.runtime_artifact_write_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "preflight_bridge_packet": dict(self.preflight_bridge_packet),
            "export_runner_packet": dict(self.export_runner_packet),
            "prediction_result_payload_present": self.prediction_result_payload_present,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "output_count": self.output_count,
            "prediction_result_blocker_count": self.prediction_result_blocker_count,
            "prediction_result_warning_count": self.prediction_result_warning_count,
            "target_artifact_path": self.target_artifact_path,
            "target_file_written": self.target_file_written,
            "target_file_size_bytes": self.target_file_size_bytes,
            "exported_at": self.exported_at,
            "stdout_summary_lines": list(self.stdout_summary_lines),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only_input": self.read_only_input,
            "non_ui_runner_only": self.non_ui_runner_only,
            "stdout_only": self.stdout_only,
            "prediction_system_result_built_by_child_runner": self.prediction_system_result_built_by_child_runner,
            "latest_prediction_artifact_exported_by_child_runner": self.latest_prediction_artifact_exported_by_child_runner,
            "runtime_artifact_write_performed_by_child_runner": self.runtime_artifact_write_performed_by_child_runner,
            "target_directory_created_by_child_runner": self.target_directory_created_by_child_runner,
            "target_file_written_by_child_runner": self.target_file_written_by_child_runner,
            "collector_state_write_performed_by_this_runner": self.collector_state_write_performed_by_this_runner,
            "hot_file_read_performed_by_export_runner": self.hot_file_read_performed_by_export_runner,
            "payload_decode_performed_by_export_runner": self.payload_decode_performed_by_export_runner,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "would_collect_public_source": self.would_collect_public_source,
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
    bridge_state: str,
    export_state: str,
    run_id: str,
    target_path: str,
    target_file_written: bool,
    target_file_size_bytes: int | None,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> tuple[str, ...]:
    return (
        "latest_payload_actual_export_runner=" + LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION,
        "state=" + state,
        "q10f_state=" + bridge_state,
        "q9y_state=" + export_state,
        "prediction_run_id=" + run_id,
        "target_path=" + target_path,
        "target_file_written=" + str(target_file_written),
        "target_file_size_bytes=" + str(target_file_size_bytes if target_file_size_bytes is not None else 0),
        "blockers=" + ",".join(blockers),
        "warnings=" + ",".join(warnings),
        "ui=false;runtime_write=true;prediction_build=true;export=true;approval=false;ledger=false;autotrade=false;broker=false",
    )


def build_prediction_warroom_latest_payload_actual_export_runner(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    allow_actual_read: bool = False,
    allow_prediction_build: bool = False,
    allow_export_preflight: bool = False,
    allow_latest_payload_export: bool = False,
    allow_runtime_artifact_write: bool = False,
    allow_guard_test_root: bool = False,
    requested_warroom_ui_trigger: bool = False,
    requested_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomLatestPayloadActualExportRunnerPacket:
    """Build/preflight and then export latest PredictionSystemResult JSON through PS-Q9Y only when explicit flags are true."""
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
    if not allow_latest_payload_export:
        blockers.append("allow_latest_payload_export_false")
    if not allow_runtime_artifact_write:
        blockers.append("allow_runtime_artifact_write_false")
    if requested_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_by_actual_export_runner")
    if requested_approval_or_ledger_or_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed_by_actual_export_runner")

    bridge_packet: Mapping[str, Any] = {}
    export_packet: Mapping[str, Any] = {}
    payload: Mapping[str, Any] = {}
    if not blockers:
        bridge_packet = build_prediction_warroom_latest_payload_export_preflight_bridge(
            hot_latest_root_hint=str(hot_latest_root_hint),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_guard_test_root=allow_guard_test_root,
        ).to_dict()
        blockers.extend(str(item) for item in bridge_packet.get("blocked_reasons", []))
        warnings.extend(str(item) for item in bridge_packet.get("warning_reasons", []))
        if not bool(bridge_packet.get("ready_for_future_non_ui_export_runner")):
            blockers.append("latest_payload_export_preflight_bridge_not_ready")
        builder_packet = _as_mapping(bridge_packet.get("builder_runner_packet"))
        payload = _as_mapping(builder_packet.get("prediction_result_payload"))
        if not payload:
            blockers.append("prediction_result_payload_missing_from_preflight_bridge")
        if not blockers:
            export_packet = build_prediction_warroom_latest_payload_export_runner(
                prediction_result_payload=payload,
                hot_latest_root_hint=str(hot_latest_root_hint),
                operator_acknowledged=True,
                execute_export=True,
                allow_guard_test_root=allow_guard_test_root,
            ).to_dict()
            blockers.extend(str(item) for item in export_packet.get("blocked_reasons", []))
            warnings.extend(str(item) for item in export_packet.get("warning_reasons", []))
            if not bool(export_packet.get("target_file_written_by_this_runner")):
                blockers.append("latest_payload_export_runner_did_not_write_target_file")
    payload_map = _as_mapping(payload)
    run_identity = _as_mapping(payload_map.get("run_identity"))
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    target_file_written = bool(export_packet.get("target_file_written_by_this_runner")) and not unique_blockers
    state = "latest_payload_actual_export_runner_exported" if target_file_written else "latest_payload_actual_export_runner_blocked"
    stdout = _stdout_lines(
        state=state,
        bridge_state=str(bridge_packet.get("bridge_state") or ""),
        export_state=str(export_packet.get("runner_state") or ""),
        run_id=str(run_identity.get("prediction_run_id") or ""),
        target_path=str(export_packet.get("target_artifact_path") or ""),
        target_file_written=target_file_written,
        target_file_size_bytes=export_packet.get("target_file_size_bytes") if isinstance(export_packet.get("target_file_size_bytes"), int) else None,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )
    result_warnings = _as_str_tuple(payload_map.get("warnings"))
    return PredictionWarRoomLatestPayloadActualExportRunnerPacket(
        runner_version=LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION,
        runner_id=f"{LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION}:{state}",
        runner_state=state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        operator_acknowledged=operator_acknowledged,
        actual_read_requested=allow_actual_read,
        prediction_build_requested=allow_prediction_build,
        export_preflight_requested=allow_export_preflight,
        latest_payload_export_requested=allow_latest_payload_export,
        runtime_artifact_write_requested=allow_runtime_artifact_write,
        allow_guard_test_root=allow_guard_test_root,
        preflight_bridge_packet=bridge_packet,
        export_runner_packet=export_packet,
        prediction_result_payload_present=bool(payload_map),
        prediction_run_id=str(run_identity.get("prediction_run_id") or ""),
        generated_at=str(run_identity.get("generated_at") or ""),
        market_uid=str(run_identity.get("market_uid") or ""),
        output_count=len(payload_map.get("outputs", [])) if isinstance(payload_map.get("outputs", []), list) else 0,
        prediction_result_blocker_count=len(payload_map.get("blockers", [])) if isinstance(payload_map.get("blockers", []), list) else 0,
        prediction_result_warning_count=len(result_warnings),
        target_artifact_path=str(export_packet.get("target_artifact_path") or ""),
        target_file_written=target_file_written,
        target_file_size_bytes=export_packet.get("target_file_size_bytes") if isinstance(export_packet.get("target_file_size_bytes"), int) else None,
        exported_at=str(export_packet.get("exported_at") or ""),
        stdout_summary_lines=stdout,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        prediction_system_result_built_by_child_runner=bool(bridge_packet.get("prediction_system_result_built_by_child_runner")),
        latest_prediction_artifact_exported_by_child_runner=target_file_written,
        runtime_artifact_write_performed_by_child_runner=target_file_written,
        target_directory_created_by_child_runner=bool(export_packet.get("target_directory_created_by_this_runner")),
        target_file_written_by_child_runner=target_file_written,
        hot_file_read_performed_by_export_runner=bool(export_packet.get("hot_file_read_performed_by_this_runner")),
        payload_decode_performed_by_export_runner=bool(export_packet.get("payload_decode_performed_by_this_runner")),
    )


def format_prediction_warroom_latest_payload_actual_export_runner_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    data = packet.to_dict() if hasattr(packet, "to_dict") else packet
    mapping = data if isinstance(data, Mapping) else {}
    lines = [str(item) for item in mapping.get("stdout_summary_lines", []) if str(item)]
    if lines:
        return "\n".join(lines)
    return "latest_payload_actual_export_runner=" + LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION + "\nstate=missing_packet"
