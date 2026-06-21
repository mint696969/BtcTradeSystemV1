# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_mapping_probe_runner.py
# desc: PS-Q10B non-UI bounded source mapping probe runner. It reads small D-hot JSONL tails, invokes PS-Q9Z probe and PS-Q10A preflight, and returns stdout summary only. No prediction build, latest artifact export, UI mutation, runtime write, approval, ledger, AutoTrade, or broker/private API behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from btcts.core.io import read_jsonl_tail

from .prediction_warroom_hot_source_probe import (
    DEFAULT_EXCHANGE,
    DEFAULT_MAX_TAIL_BYTES,
    DEFAULT_SYMBOL_RAW,
    HOT_SOURCE_PROBE_VERSION,
    ROLE_RELATIVE_ROOTS,
    build_prediction_warroom_hot_source_probe,
)
from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_source_mapping_preflight_contract import (
    SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION,
    build_prediction_warroom_source_mapping_preflight_contract,
)

SOURCE_MAPPING_PROBE_RUNNER_VERSION = "prediction_warroom_source_mapping_probe_runner.ps_q10b.v1"
DEFAULT_MARKET_TRADE_TAIL_LINES = 64
DEFAULT_MARKET_OVERVIEW_TAIL_LINES = 4
DEFAULT_ORDERBOOK_SNAPSHOT_TAIL_LINES = 2

SOURCE_MAPPING_PROBE_RUNNER_SEQUENCE = (
    "require_operator_acknowledgement",
    "require_actual_read_request",
    "verify_hot_root_D_btc_ts_hot_or_guard_test_root",
    "read_bounded_market_overview_tail",
    "read_bounded_market_trade_tail",
    "read_bounded_orderbook_snapshot_tail",
    "invoke_ps_q9z_hot_source_probe",
    "invoke_ps_q10a_source_mapping_preflight",
    "emit_stdout_summary_only",
    "do_not_build_prediction_system_result",
    "do_not_export_latest_prediction_artifact",
    "do_not_write_runtime_artifacts",
    "do_not_mutate_warroom_ui_or_runtime_state",
)


@dataclass(frozen=True)
class PredictionWarRoomSourceMappingProbeRunnerPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    hot_latest_root_hint: str
    exchange: str
    symbol_raw: str
    runner_sequence: Tuple[str, ...] = SOURCE_MAPPING_PROBE_RUNNER_SEQUENCE
    operator_acknowledged: bool = False
    actual_read_requested: bool = False
    allow_guard_test_root: bool = False
    target_root_valid: bool = False
    market_overview_latest_part_path: str = ""
    market_trade_latest_part_path: str = ""
    orderbook_snapshot_latest_part_path: str = ""
    market_overview_tail_row_count: int = 0
    market_trade_tail_row_count: int = 0
    orderbook_snapshot_tail_row_count: int = 0
    q9z_probe_version: str = HOT_SOURCE_PROBE_VERSION
    q9z_probe_packet: Mapping[str, Any] = field(default_factory=dict)
    q10a_preflight_version: str = SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION
    q10a_preflight_packet: Mapping[str, Any] = field(default_factory=dict)
    normalized_ohlcv_row_count: int = 0
    venue_snapshot_candidate_count: int = 0
    feature_depth_context_candidate_present: bool = False
    ready_for_future_prediction_system_result_builder: bool = False
    ready_for_latest_payload_export: bool = False
    stdout_summary_lines: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    bounded_tail_only: bool = True
    stdout_only: bool = True
    non_ui_runner_only: bool = True
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
            "exchange": self.exchange,
            "symbol_raw": self.symbol_raw,
            "runner_sequence": list(self.runner_sequence),
            "operator_acknowledged": self.operator_acknowledged,
            "actual_read_requested": self.actual_read_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "target_root_valid": self.target_root_valid,
            "market_overview_latest_part_path": self.market_overview_latest_part_path,
            "market_trade_latest_part_path": self.market_trade_latest_part_path,
            "orderbook_snapshot_latest_part_path": self.orderbook_snapshot_latest_part_path,
            "market_overview_tail_row_count": self.market_overview_tail_row_count,
            "market_trade_tail_row_count": self.market_trade_tail_row_count,
            "orderbook_snapshot_tail_row_count": self.orderbook_snapshot_tail_row_count,
            "q9z_probe_version": self.q9z_probe_version,
            "q9z_probe_packet": dict(self.q9z_probe_packet),
            "q10a_preflight_version": self.q10a_preflight_version,
            "q10a_preflight_packet": dict(self.q10a_preflight_packet),
            "normalized_ohlcv_row_count": self.normalized_ohlcv_row_count,
            "venue_snapshot_candidate_count": self.venue_snapshot_candidate_count,
            "feature_depth_context_candidate_present": self.feature_depth_context_candidate_present,
            "ready_for_future_prediction_system_result_builder": self.ready_for_future_prediction_system_result_builder,
            "ready_for_latest_payload_export": self.ready_for_latest_payload_export,
            "stdout_summary_lines": list(self.stdout_summary_lines),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "bounded_tail_only": self.bounded_tail_only,
            "stdout_only": self.stdout_only,
            "non_ui_runner_only": self.non_ui_runner_only,
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


def _root_ok(root: str, *, allow_guard_test_root: bool = False) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    if normalized == "d:\\btc_ts_hot":
        return True
    return bool(allow_guard_test_root and normalized)


def _latest_part_file(root: Path) -> Path | None:
    if not root.exists() or not root.is_dir():
        return None
    date_dirs = sorted((item for item in root.iterdir() if item.is_dir() and item.name.startswith("date=")), key=lambda item: item.name)
    if not date_dirs:
        return None
    part_files = sorted(date_dirs[-1].glob("part-*.jsonl"))
    return part_files[-1] if part_files else None


def _role_root(data_root: Path, role: str, *, exchange: str, symbol_raw: str) -> Path:
    rel = ROLE_RELATIVE_ROOTS[role].format(exchange=exchange, symbol=symbol_raw)
    return data_root / rel


def _path_display(path: Path | None, data_root: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(data_root)).replace("/", "\\")
    except Exception:
        return str(path)


def _read_tail(path: Path | None, *, max_lines: int, max_bytes: int) -> tuple[Mapping[str, Any], ...]:
    if path is None:
        return tuple()
    return tuple(row for row in read_jsonl_tail(path, max_lines=max_lines, max_bytes=max_bytes) if isinstance(row, Mapping))


def _stdout_lines(
    *,
    state: str,
    root: str,
    symbol_raw: str,
    overview_rows: int,
    trade_rows: int,
    orderbook_rows: int,
    normalized_rows: int,
    ready_for_builder: bool,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> tuple[str, ...]:
    return (
        "prediction_source_mapping_probe_runner=" + SOURCE_MAPPING_PROBE_RUNNER_VERSION,
        "state=" + state,
        "root=" + root,
        "symbol=" + symbol_raw,
        "market_overview_tail_rows=" + str(overview_rows),
        "market_trade_tail_rows=" + str(trade_rows),
        "orderbook_snapshot_tail_rows=" + str(orderbook_rows),
        "normalized_ohlcv_rows=" + str(normalized_rows),
        "ready_for_future_prediction_system_result_builder=" + str(ready_for_builder),
        "ready_for_latest_payload_export=False",
        "blockers=" + ",".join(blockers),
        "warnings=" + ",".join(warnings),
        "ui=false;runtime_write=false;prediction_build=false;export=false;approval=false;ledger=false;autotrade=false;broker=false",
    )


def build_prediction_warroom_source_mapping_probe_runner(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    exchange: str = DEFAULT_EXCHANGE,
    symbol_raw: str = DEFAULT_SYMBOL_RAW,
    operator_acknowledged: bool = False,
    allow_actual_read: bool = False,
    allow_guard_test_root: bool = False,
    market_trade_tail_lines: int = DEFAULT_MARKET_TRADE_TAIL_LINES,
    market_overview_tail_lines: int = DEFAULT_MARKET_OVERVIEW_TAIL_LINES,
    orderbook_snapshot_tail_lines: int = DEFAULT_ORDERBOOK_SNAPSHOT_TAIL_LINES,
    max_tail_bytes: int = DEFAULT_MAX_TAIL_BYTES,
) -> PredictionWarRoomSourceMappingProbeRunnerPacket:
    """Read bounded hot source tails and run Q9Z/Q10A readiness checks without building/exporting."""
    root_text = str(hot_latest_root_hint)
    data_root = Path(root_text)
    root_valid = _root_ok(root_text, allow_guard_test_root=allow_guard_test_root)
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not allow_actual_read:
        blockers.append("allow_actual_read_false")
    if not root_valid:
        blockers.append("source_mapping_probe_runner_root_must_be_D_btc_ts_hot")

    overview_part: Path | None = None
    trade_part: Path | None = None
    orderbook_part: Path | None = None
    overview_rows: tuple[Mapping[str, Any], ...] = tuple()
    trade_rows: tuple[Mapping[str, Any], ...] = tuple()
    orderbook_rows: tuple[Mapping[str, Any], ...] = tuple()
    q9z_packet: Mapping[str, Any] = {}
    q10a_packet: Mapping[str, Any] = {}

    can_read = bool(operator_acknowledged and allow_actual_read and root_valid)
    if can_read:
        overview_part = _latest_part_file(_role_root(data_root, "market_overview", exchange=str(exchange), symbol_raw=str(symbol_raw)))
        trade_part = _latest_part_file(_role_root(data_root, "market_trade", exchange=str(exchange), symbol_raw=str(symbol_raw)))
        orderbook_part = _latest_part_file(_role_root(data_root, "orderbook_snapshot", exchange=str(exchange), symbol_raw=str(symbol_raw)))
        if overview_part is None:
            blockers.append("market_overview_latest_part_missing")
        if trade_part is None:
            blockers.append("market_trade_latest_part_missing")
        if orderbook_part is None:
            warnings.append("orderbook_snapshot_latest_part_missing_context_only")
        overview_rows = _read_tail(overview_part, max_lines=market_overview_tail_lines, max_bytes=max_tail_bytes)
        trade_rows = _read_tail(trade_part, max_lines=market_trade_tail_lines, max_bytes=max_tail_bytes)
        orderbook_rows = _read_tail(orderbook_part, max_lines=orderbook_snapshot_tail_lines, max_bytes=max_tail_bytes)
        if overview_part is not None and not overview_rows:
            blockers.append("market_overview_tail_rows_missing")
        if trade_part is not None and not trade_rows:
            blockers.append("market_trade_tail_rows_missing")
        q9z_packet = build_prediction_warroom_hot_source_probe(
            hot_latest_root_hint=root_text,
            exchange=str(exchange),
            symbol_raw=str(symbol_raw),
            allow_actual_probe=True,
            allow_guard_test_root=allow_guard_test_root,
            max_tail_lines=max(market_overview_tail_lines, orderbook_snapshot_tail_lines, 2),
            max_tail_bytes=max_tail_bytes,
        ).to_dict()
        q10a_packet = build_prediction_warroom_source_mapping_preflight_contract(
            source_probe_packet=q9z_packet,
            supplied_market_trade_rows=trade_rows,
            supplied_market_overview_row=overview_rows[-1] if overview_rows else None,
            supplied_orderbook_snapshot_row=orderbook_rows[-1] if orderbook_rows else None,
        ).to_dict()
        blockers.extend(str(item) for item in q9z_packet.get("blocked_reasons", []))
        warnings.extend(str(item) for item in q9z_packet.get("warning_reasons", []))
        blockers.extend(str(item) for item in q10a_packet.get("blocked_reasons", []))
        warnings.extend(str(item) for item in q10a_packet.get("warning_reasons", []))

    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready_for_builder = bool(q10a_packet.get("ready_for_future_prediction_system_result_builder")) and not unique_blockers
    state = "source_mapping_probe_runner_ready_for_future_prediction_system_result_builder" if ready_for_builder else "source_mapping_probe_runner_blocked"
    stdout = _stdout_lines(
        state=state,
        root=root_text,
        symbol_raw=str(symbol_raw),
        overview_rows=len(overview_rows),
        trade_rows=len(trade_rows),
        orderbook_rows=len(orderbook_rows),
        normalized_rows=int(q10a_packet.get("normalized_ohlcv_row_count") or 0),
        ready_for_builder=ready_for_builder,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )
    return PredictionWarRoomSourceMappingProbeRunnerPacket(
        runner_version=SOURCE_MAPPING_PROBE_RUNNER_VERSION,
        runner_id=f"{SOURCE_MAPPING_PROBE_RUNNER_VERSION}:{str(exchange)}:{str(symbol_raw)}:{state}",
        runner_state=state,
        hot_latest_root_hint=root_text,
        exchange=str(exchange),
        symbol_raw=str(symbol_raw),
        operator_acknowledged=operator_acknowledged,
        actual_read_requested=allow_actual_read,
        allow_guard_test_root=allow_guard_test_root,
        target_root_valid=root_valid,
        market_overview_latest_part_path=_path_display(overview_part, data_root),
        market_trade_latest_part_path=_path_display(trade_part, data_root),
        orderbook_snapshot_latest_part_path=_path_display(orderbook_part, data_root),
        market_overview_tail_row_count=len(overview_rows),
        market_trade_tail_row_count=len(trade_rows),
        orderbook_snapshot_tail_row_count=len(orderbook_rows),
        q9z_probe_packet=q9z_packet,
        q10a_preflight_packet=q10a_packet,
        normalized_ohlcv_row_count=int(q10a_packet.get("normalized_ohlcv_row_count") or 0),
        venue_snapshot_candidate_count=int(q10a_packet.get("venue_snapshot_candidate_count") or 0),
        feature_depth_context_candidate_present=bool(q10a_packet.get("feature_depth_context_candidate_present")),
        ready_for_future_prediction_system_result_builder=ready_for_builder,
        ready_for_latest_payload_export=False,
        stdout_summary_lines=stdout,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
    )


def format_prediction_warroom_source_mapping_probe_runner_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    data = packet.to_dict() if hasattr(packet, "to_dict") else packet
    mapping = data if isinstance(data, Mapping) else {}
    lines = [str(item) for item in mapping.get("stdout_summary_lines", []) if str(item)]
    if lines:
        return "\n".join(lines)
    return "prediction_source_mapping_probe_runner=" + SOURCE_MAPPING_PROBE_RUNNER_VERSION + "\nstate=missing_packet"
