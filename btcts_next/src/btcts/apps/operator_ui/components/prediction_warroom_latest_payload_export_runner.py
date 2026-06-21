# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_runner.py
# desc: PS-Q9Y non-UI latest payload export runner for an already-supplied PredictionSystemResult mapping. Writes exactly one latest JSON artifact only when explicitly acknowledged and executed; no prediction build, hot-file read, Streamlit UI, WarRoom mutation, approval, ledger append, AutoTrade, or broker/private API behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_latest_payload_export_preflight_contract import (
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION,
    TARGET_ARTIFACT_RELATIVE_PATH,
    TARGET_ARTIFACT_ROLE,
    build_prediction_warroom_latest_payload_export_preflight_contract,
)

LATEST_PAYLOAD_EXPORT_RUNNER_VERSION = "prediction_warroom_latest_payload_export_runner.ps_q9y.v1"
LATEST_PAYLOAD_EXPORT_RUNNER_SEQUENCE = (
    "consume_supplied_prediction_system_result_mapping_only",
    "run_ps_q9x_export_preflight_contract",
    "require_operator_acknowledgement",
    "require_execute_export_true",
    "require_target_root_D_btc_ts_hot_or_guard_test_root",
    "create_prediction_directory_if_needed",
    "write_exactly_latest_prediction_system_result_json",
    "emit_stdout_summary_only",
    "do_not_build_prediction_system_result",
    "do_not_read_hot_files",
    "do_not_run_from_warroom_ui",
    "do_not_append_ledger_or_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadExportRunnerPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    runner_sequence: Tuple[str, ...] = LATEST_PAYLOAD_EXPORT_RUNNER_SEQUENCE
    preflight_contract: Mapping[str, Any] = field(default_factory=dict)
    target_artifact_role: str = TARGET_ARTIFACT_ROLE
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT
    target_artifact_relative_path: str = TARGET_ARTIFACT_RELATIVE_PATH
    target_artifact_path: str = ""
    prediction_result_payload_present: bool = False
    prediction_result_payload_key_count: int = 0
    prediction_run_id: str = ""
    generated_at: str = ""
    market_uid: str = ""
    operator_acknowledged: bool = False
    execute_export_requested: bool = False
    allow_guard_test_root: bool = False
    q9x_preflight_version: str = LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION
    preflight_ready: bool = False
    target_root_valid: bool = False
    target_directory_created_by_this_runner: bool = False
    target_file_written_by_this_runner: bool = False
    target_file_size_bytes: int | None = None
    exported_at: str = ""
    stdout_summary_lines: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    runner_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only_input: bool = True
    non_executing_trade: bool = True
    non_ui_runner_only: bool = True
    supplied_payload_only: bool = True
    prediction_system_result_built_by_this_runner: bool = False
    hot_file_read_performed_by_this_runner: bool = False
    payload_decode_performed_by_this_runner: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_export_execution: bool = False
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
            "runner_sequence": list(self.runner_sequence),
            "preflight_contract": dict(self.preflight_contract),
            "target_artifact_role": self.target_artifact_role,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "target_artifact_relative_path": self.target_artifact_relative_path,
            "target_artifact_path": self.target_artifact_path,
            "prediction_result_payload_present": self.prediction_result_payload_present,
            "prediction_result_payload_key_count": self.prediction_result_payload_key_count,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "operator_acknowledged": self.operator_acknowledged,
            "execute_export_requested": self.execute_export_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "q9x_preflight_version": self.q9x_preflight_version,
            "preflight_ready": self.preflight_ready,
            "target_root_valid": self.target_root_valid,
            "target_directory_created_by_this_runner": self.target_directory_created_by_this_runner,
            "target_file_written_by_this_runner": self.target_file_written_by_this_runner,
            "target_file_size_bytes": self.target_file_size_bytes,
            "exported_at": self.exported_at,
            "stdout_summary_lines": list(self.stdout_summary_lines),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "runner_summary": dict(self.runner_summary),
            "read_only_input": self.read_only_input,
            "non_executing_trade": self.non_executing_trade,
            "non_ui_runner_only": self.non_ui_runner_only,
            "supplied_payload_only": self.supplied_payload_only,
            "prediction_system_result_built_by_this_runner": self.prediction_system_result_built_by_this_runner,
            "hot_file_read_performed_by_this_runner": self.hot_file_read_performed_by_this_runner,
            "payload_decode_performed_by_this_runner": self.payload_decode_performed_by_this_runner,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_export_execution": self.ui_triggered_export_execution,
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


def _hot_root_ok(root: str, *, allow_guard_test_root: bool = False) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    if normalized == "d:\\btc_ts_hot":
        return True
    return bool(allow_guard_test_root and normalized)


def _target_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / "prediction" / "latest_prediction_system_result.json"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stdout_lines(*, state: str, target_path: str, written: bool, size: int | None, blockers: tuple[str, ...], warnings: tuple[str, ...]) -> tuple[str, ...]:
    return (
        "prediction_latest_payload_export_runner=" + LATEST_PAYLOAD_EXPORT_RUNNER_VERSION,
        "state=" + state,
        "target_artifact_role=" + TARGET_ARTIFACT_ROLE,
        "target_path=" + target_path,
        "target_file_written=" + str(written),
        "target_file_size_bytes=" + str(size if size is not None else 0),
        "blockers=" + ",".join(blockers),
        "warnings=" + ",".join(warnings),
        "ui=false;hot_file_read=false;prediction_build=false;approval=false;ledger=false;autotrade=false;broker=false",
    )


def _write_json_atomic(target: Path, payload: Mapping[str, Any]) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    body = json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(target)
    return int(target.stat().st_size)


def build_prediction_warroom_latest_payload_export_runner(
    *,
    prediction_result_payload: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    execute_export: bool = False,
    allow_guard_test_root: bool = False,
) -> PredictionWarRoomLatestPayloadExportRunnerPacket:
    """Export a supplied PredictionSystemResult mapping to the latest artifact path when explicitly executed."""
    payload = _as_mapping(prediction_result_payload)
    target = _target_path(str(hot_latest_root_hint))
    target_root_valid = _hot_root_ok(str(hot_latest_root_hint), allow_guard_test_root=allow_guard_test_root)
    preflight_root = str(hot_latest_root_hint) if not allow_guard_test_root else DEFAULT_HOT_LATEST_ROOT_HINT
    preflight = build_prediction_warroom_latest_payload_export_preflight_contract(
        prediction_result_payload=payload,
        hot_latest_root_hint=preflight_root,
        operator_acknowledged=operator_acknowledged,
    ).to_dict()
    blockers: list[str] = [str(item) for item in preflight.get("blocked_reasons", [])]
    warnings: list[str] = [str(item) for item in preflight.get("warning_reasons", [])]
    if not target_root_valid:
        blockers.append("target_root_invalid_for_latest_payload_export_runner")
    if target.name != "latest_prediction_system_result.json" or target.parent.name != "prediction":
        blockers.append("target_path_must_be_prediction_latest_prediction_system_result_json")
    if not execute_export:
        blockers.append("execute_export_false")
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    written = False
    created_dir = False
    size: int | None = None
    exported_at = ""
    if not unique_blockers:
        existed = target.parent.exists()
        try:
            size = _write_json_atomic(target, payload)
            written = True
            created_dir = not existed and target.parent.exists()
            exported_at = _iso_now()
        except Exception as exc:  # noqa: BLE001 - fail closed and report stdout-only
            unique_blockers = tuple(dict.fromkeys(unique_blockers + ("latest_payload_export_write_failed:" + exc.__class__.__name__,)))
            unique_warnings = tuple(dict.fromkeys(unique_warnings + (str(exc),)))
    state = "latest_payload_export_runner_exported" if written and not unique_blockers else "latest_payload_export_runner_blocked"
    stdout = _stdout_lines(
        state=state,
        target_path=str(target),
        written=written,
        size=size,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )
    run_identity = _as_mapping(payload.get("run_identity"))
    return PredictionWarRoomLatestPayloadExportRunnerPacket(
        runner_version=LATEST_PAYLOAD_EXPORT_RUNNER_VERSION,
        runner_id=f"{LATEST_PAYLOAD_EXPORT_RUNNER_VERSION}:latest:{state}",
        runner_state=state,
        preflight_contract=preflight,
        hot_latest_root_hint=str(hot_latest_root_hint),
        target_artifact_path=str(target),
        prediction_result_payload_present=bool(payload),
        prediction_result_payload_key_count=len(payload),
        prediction_run_id=str(run_identity.get("prediction_run_id") or ""),
        generated_at=str(run_identity.get("generated_at") or ""),
        market_uid=str(run_identity.get("market_uid") or ""),
        operator_acknowledged=operator_acknowledged,
        execute_export_requested=execute_export,
        allow_guard_test_root=allow_guard_test_root,
        preflight_ready=bool(preflight.get("ready_for_future_non_ui_export_runner")),
        target_root_valid=target_root_valid,
        target_directory_created_by_this_runner=created_dir,
        target_file_written_by_this_runner=written,
        target_file_size_bytes=size,
        exported_at=exported_at,
        stdout_summary_lines=stdout,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        runner_summary={
            "boundary": "ps_q9y_non_ui_latest_payload_export_runner",
            "target_artifact_role": TARGET_ARTIFACT_ROLE,
            "target_artifact_path": str(target),
            "writes_exactly_latest_prediction_system_result_json": written,
            "prediction_system_result_built_by_this_runner": False,
            "hot_file_read_performed_by_this_runner": False,
            "payload_decode_performed_by_this_runner": False,
            "warroom_ui_trigger_allowed": False,
            "ui_controls_added": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )


def format_prediction_warroom_latest_payload_export_runner_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    """Return the PS-Q9Y stdout-only summary string."""
    data = _as_mapping(packet)
    lines = [str(item) for item in data.get("stdout_summary_lines", []) if str(item)]
    if lines:
        return "\n".join(lines)
    return "prediction_latest_payload_export_runner=" + LATEST_PAYLOAD_EXPORT_RUNNER_VERSION + "\nstate=missing_packet"
