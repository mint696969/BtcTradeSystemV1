# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py
# desc: PS-Q10D non-UI PredictionSystemResult builder runner. It reads bounded D-hot tails through PS-Q10B, consumes PS-Q10A builder kwargs, builds PredictionSystemResult in memory, and returns stdout summary only. It does not export latest artifacts, write runtime files, mutate UI, approve, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from btcts.prediction.system import LOGIC_VERSION as PREDICTION_SYSTEM_LOGIC_VERSION
from btcts.prediction.system import build_prediction_system_result

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_source_mapping_probe_runner import (
    SOURCE_MAPPING_PROBE_RUNNER_VERSION,
    build_prediction_warroom_source_mapping_probe_runner,
)

PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION = "prediction_warroom_prediction_system_result_builder_runner.ps_q10d.v1"
PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_SEQUENCE = (
    "require_operator_acknowledgement",
    "require_actual_read_request",
    "require_prediction_build_request",
    "invoke_ps_q10b_source_mapping_probe_runner",
    "require_ps_q10b_ready_for_future_prediction_system_result_builder",
    "consume_ps_q10a_builder_kwargs_contract",
    "run_build_prediction_system_result_in_memory",
    "emit_stdout_summary_only",
    "do_not_export_latest_prediction_artifact",
    "do_not_write_runtime_artifacts",
    "do_not_mutate_warroom_ui_or_runtime_state",
    "do_not_approve_append_ledger_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomPredictionSystemResultBuilderRunnerPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    hot_latest_root_hint: str
    runner_sequence: Tuple[str, ...] = PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_SEQUENCE
    source_mapping_runner_version: str = SOURCE_MAPPING_PROBE_RUNNER_VERSION
    prediction_system_logic_version: str = PREDICTION_SYSTEM_LOGIC_VERSION
    operator_acknowledged: bool = False
    actual_read_requested: bool = False
    prediction_build_requested: bool = False
    allow_guard_test_root: bool = False
    source_mapping_runner_packet: Mapping[str, Any] = field(default_factory=dict)
    builder_kwargs_contract: Mapping[str, Any] = field(default_factory=dict)
    prediction_result_payload: Mapping[str, Any] = field(default_factory=dict)
    prediction_result_payload_present: bool = False
    prediction_run_id: str = ""
    generated_at: str = ""
    market_uid: str = ""
    output_count: int = 0
    scenario_core_present: bool = False
    usable: bool = False
    prediction_result_blocker_count: int = 0
    prediction_result_warning_count: int = 0
    ready_for_future_latest_payload_export_preflight: bool = False
    ready_for_latest_payload_export: bool = False
    stdout_summary_lines: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_ui_runner_only: bool = True
    bounded_hot_read_via_source_mapping_runner_only: bool = True
    prediction_system_result_built_by_this_runner: bool = False
    latest_prediction_artifact_exported_by_this_runner: bool = False
    runtime_artifact_write_performed_by_this_runner: bool = False
    collector_state_write_performed_by_this_runner: bool = False
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
            "runner_version": self.runner_version,
            "runner_id": self.runner_id,
            "runner_state": self.runner_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "runner_sequence": list(self.runner_sequence),
            "source_mapping_runner_version": self.source_mapping_runner_version,
            "prediction_system_logic_version": self.prediction_system_logic_version,
            "operator_acknowledged": self.operator_acknowledged,
            "actual_read_requested": self.actual_read_requested,
            "prediction_build_requested": self.prediction_build_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "source_mapping_runner_packet": dict(self.source_mapping_runner_packet),
            "builder_kwargs_contract": dict(self.builder_kwargs_contract),
            "prediction_result_payload": dict(self.prediction_result_payload),
            "prediction_result_payload_present": self.prediction_result_payload_present,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "output_count": self.output_count,
            "scenario_core_present": self.scenario_core_present,
            "usable": self.usable,
            "prediction_result_blocker_count": self.prediction_result_blocker_count,
            "prediction_result_warning_count": self.prediction_result_warning_count,
            "ready_for_future_latest_payload_export_preflight": self.ready_for_future_latest_payload_export_preflight,
            "ready_for_latest_payload_export": self.ready_for_latest_payload_export,
            "stdout_summary_lines": list(self.stdout_summary_lines),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_ui_runner_only": self.non_ui_runner_only,
            "bounded_hot_read_via_source_mapping_runner_only": self.bounded_hot_read_via_source_mapping_runner_only,
            "prediction_system_result_built_by_this_runner": self.prediction_system_result_built_by_this_runner,
            "latest_prediction_artifact_exported_by_this_runner": self.latest_prediction_artifact_exported_by_this_runner,
            "runtime_artifact_write_performed_by_this_runner": self.runtime_artifact_write_performed_by_this_runner,
            "collector_state_write_performed_by_this_runner": self.collector_state_write_performed_by_this_runner,
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


def _stdout_lines(
    *,
    state: str,
    run_id: str,
    market_uid: str,
    output_count: int,
    usable: bool,
    result_blockers: int,
    result_warnings: int,
    ready_for_export_preflight: bool,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> tuple[str, ...]:
    return (
        "prediction_system_result_builder_runner=" + PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION,
        "state=" + state,
        "prediction_system_logic_version=" + PREDICTION_SYSTEM_LOGIC_VERSION,
        "prediction_run_id=" + run_id,
        "market_uid=" + market_uid,
        "output_count=" + str(output_count),
        "usable=" + str(usable),
        "prediction_result_blocker_count=" + str(result_blockers),
        "prediction_result_warning_count=" + str(result_warnings),
        "ready_for_future_latest_payload_export_preflight=" + str(ready_for_export_preflight),
        "ready_for_latest_payload_export=False",
        "blockers=" + ",".join(blockers),
        "warnings=" + ",".join(warnings),
        "ui=false;runtime_write=false;prediction_build=true;export=false;approval=false;ledger=false;autotrade=false;broker=false",
    )


def _build_from_kwargs_contract(builder_kwargs: Mapping[str, Any]) -> Mapping[str, Any]:
    result = build_prediction_system_result(
        rows=builder_kwargs.get("rows") if isinstance(builder_kwargs.get("rows"), list) else None,
        venue_snapshots=builder_kwargs.get("venue_snapshots") if isinstance(builder_kwargs.get("venue_snapshots"), list) else None,
        source_quality_by_id=None,
        requested_horizon_groups=builder_kwargs.get("requested_horizon_groups"),
        requested_horizons_sec=builder_kwargs.get("requested_horizons_sec"),
        previous_prediction_run_id=builder_kwargs.get("previous_prediction_run_id"),
        feature_depth_snapshot=None,
        now=builder_kwargs.get("now"),
    )
    return result.to_dict()


def build_prediction_warroom_prediction_system_result_builder_runner(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    allow_actual_read: bool = False,
    allow_prediction_build: bool = False,
    allow_guard_test_root: bool = False,
    requested_latest_payload_export: bool = False,
    requested_runtime_write: bool = False,
    requested_warroom_ui_trigger: bool = False,
    requested_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomPredictionSystemResultBuilderRunnerPacket:
    """Build PredictionSystemResult in memory from D-hot mapping readiness without exporting/writing."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not allow_actual_read:
        blockers.append("allow_actual_read_false")
    if not allow_prediction_build:
        blockers.append("allow_prediction_build_false")
    if requested_latest_payload_export:
        blockers.append("latest_payload_export_not_allowed_by_builder_runner")
    if requested_runtime_write:
        blockers.append("runtime_write_not_allowed_by_builder_runner")
    if requested_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_by_builder_runner")
    if requested_approval_or_ledger_or_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed_by_builder_runner")

    source_packet: Mapping[str, Any] = {}
    builder_kwargs: Mapping[str, Any] = {}
    payload: Mapping[str, Any] = {}
    prediction_built = False
    if not blockers:
        source_packet = build_prediction_warroom_source_mapping_probe_runner(
            hot_latest_root_hint=str(hot_latest_root_hint),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_guard_test_root=allow_guard_test_root,
        ).to_dict()
        blockers.extend(str(item) for item in source_packet.get("blocked_reasons", []))
        warnings.extend(str(item) for item in source_packet.get("warning_reasons", []))
        if not bool(source_packet.get("ready_for_future_prediction_system_result_builder")):
            blockers.append("source_mapping_runner_not_ready_for_prediction_system_result_builder")
        preflight = source_packet.get("q10a_preflight_packet")
        preflight_map = preflight if isinstance(preflight, Mapping) else {}
        raw_builder_kwargs = preflight_map.get("builder_kwargs_contract")
        builder_kwargs = raw_builder_kwargs if isinstance(raw_builder_kwargs, Mapping) else {}
        if not builder_kwargs:
            blockers.append("builder_kwargs_contract_missing")
        if not blockers:
            try:
                payload = _build_from_kwargs_contract(builder_kwargs)
                prediction_built = True
            except Exception as exc:  # noqa: BLE001 - fail closed with diagnostic only
                blockers.append("prediction_system_result_build_failed:" + exc.__class__.__name__)
                warnings.append(str(exc))
    payload_map = _as_mapping(payload)
    run_identity = _as_mapping(payload_map.get("run_identity"))
    result_blockers = tuple(str(item) for item in payload_map.get("blockers", []) if item) if isinstance(payload_map.get("blockers", []), list) else tuple()
    result_warnings = tuple(str(item) for item in payload_map.get("warnings", []) if item) if isinstance(payload_map.get("warnings", []), list) else tuple()
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    output_count = len(payload_map.get("outputs", [])) if isinstance(payload_map.get("outputs", []), list) else 0
    usable = bool(payload_map.get("usable")) and not result_blockers
    ready_for_export_preflight = bool(prediction_built and payload_map and not unique_blockers and not result_blockers and bool(payload_map.get("usable")) and output_count > 0)
    state = "prediction_system_result_builder_runner_built" if ready_for_export_preflight else "prediction_system_result_builder_runner_blocked"
    stdout = _stdout_lines(
        state=state,
        run_id=str(run_identity.get("prediction_run_id") or ""),
        market_uid=str(run_identity.get("market_uid") or ""),
        output_count=output_count,
        usable=usable,
        result_blockers=len(result_blockers),
        result_warnings=len(result_warnings),
        ready_for_export_preflight=ready_for_export_preflight,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )
    return PredictionWarRoomPredictionSystemResultBuilderRunnerPacket(
        runner_version=PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION,
        runner_id=f"{PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION}:{state}",
        runner_state=state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        operator_acknowledged=operator_acknowledged,
        actual_read_requested=allow_actual_read,
        prediction_build_requested=allow_prediction_build,
        allow_guard_test_root=allow_guard_test_root,
        source_mapping_runner_packet=source_packet,
        builder_kwargs_contract=builder_kwargs,
        prediction_result_payload=payload_map,
        prediction_result_payload_present=bool(payload_map),
        prediction_run_id=str(run_identity.get("prediction_run_id") or ""),
        generated_at=str(run_identity.get("generated_at") or ""),
        market_uid=str(run_identity.get("market_uid") or ""),
        output_count=output_count,
        scenario_core_present=payload_map.get("scenario_core") is not None,
        usable=usable,
        prediction_result_blocker_count=len(result_blockers),
        prediction_result_warning_count=len(result_warnings),
        ready_for_future_latest_payload_export_preflight=ready_for_export_preflight,
        ready_for_latest_payload_export=False,
        stdout_summary_lines=stdout,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        prediction_system_result_built_by_this_runner=prediction_built,
    )


def format_prediction_warroom_prediction_system_result_builder_runner_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    data = packet.to_dict() if hasattr(packet, "to_dict") else packet
    mapping = data if isinstance(data, Mapping) else {}
    lines = [str(item) for item in mapping.get("stdout_summary_lines", []) if str(item)]
    if lines:
        return "\n".join(lines)
    return "prediction_system_result_builder_runner=" + PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION + "\nstate=missing_packet"
