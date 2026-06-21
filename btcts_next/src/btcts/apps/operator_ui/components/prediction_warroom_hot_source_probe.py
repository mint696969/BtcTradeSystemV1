# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_hot_source_probe.py
# desc: PS-Q9Z bounded read-only D-hot source probe for PredictionSystemResult input readiness. It summarizes market.overview / market.trade / market.orderbook.snapshot JSONL tails without building predictions, exporting artifacts, mutating UI, writing runtime files, approving, appending ledgers, triggering AutoTrade, or calling broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT

HOT_SOURCE_PROBE_VERSION = "prediction_warroom_hot_source_probe.ps_q9z.v1"
DEFAULT_EXCHANGE = "bitflyer"
DEFAULT_SYMBOL_RAW = "FX_BTC_JPY"
DEFAULT_MAX_TAIL_LINES = 8
DEFAULT_MAX_TAIL_BYTES = 1024 * 1024

HOT_SOURCE_PROBE_SEQUENCE = (
    "require_explicit_actual_probe_request",
    "verify_hot_root_D_btc_ts_hot_or_guard_test_root",
    "find_latest_market_overview_part_file",
    "find_latest_market_trade_part_file",
    "find_latest_orderbook_snapshot_part_file",
    "read_bounded_tail_bytes_only",
    "decode_jsonl_tail_to_schema_summary_only",
    "evaluate_future_prediction_source_mapping_readiness",
    "do_not_build_prediction_system_result",
    "do_not_export_latest_prediction_artifact",
    "do_not_mutate_warroom_ui_or_runtime_state",
)

SOURCE_ROLES = (
    "market_overview",
    "market_trade",
    "orderbook_snapshot",
)

ROLE_RELATIVE_ROOTS = {
    "market_overview": "data/market_state/exchange={exchange}/symbol={symbol}/type=market.overview",
    "market_trade": "data/market_data/exchange={exchange}/symbol={symbol}/type=market.trade",
    "orderbook_snapshot": "data/market_data/exchange={exchange}/symbol={symbol}/type=market.orderbook.snapshot",
}


@dataclass(frozen=True)
class PredictionWarRoomHotSourceProbeSourceSummary:
    source_role: str
    source_state: str
    relative_root: str
    latest_part_path: str = ""
    latest_date_partition: str = ""
    file_exists: bool = False
    file_size_bytes: int | None = None
    file_mtime_utc: str = ""
    tail_read_attempted: bool = False
    tail_read_succeeded: bool = False
    parsed_row_count: int = 0
    top_level_key_sample: Tuple[str, ...] = ()
    payload_key_sample: Tuple[str, ...] = ()
    record_types: Tuple[str, ...] = ()
    channels: Tuple[str, ...] = ()
    transports: Tuple[str, ...] = ()
    latest_collector_ts: str = ""
    latest_event_ts: str = ""
    latest_market_uid: str = ""
    latest_symbol_raw: str = ""
    latest_trust_state: str = ""
    latest_continuity_state: str = ""
    latest_interpretation_bucket: str = ""
    latest_schema_contract: str = ""
    latest_payload_contract_version: str = ""
    overview_best_bid: float | None = None
    overview_best_ask: float | None = None
    overview_mid_price: float | None = None
    overview_spread: float | None = None
    overview_near_size_imbalance: float | None = None
    trade_price_sample: Tuple[float, ...] = ()
    trade_side_sample: Tuple[str, ...] = ()
    orderbook_bid_level_count: int = 0
    orderbook_ask_level_count: int = 0
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    bounded_tail_only: bool = True
    schema_summary_only: bool = True
    no_runtime_write: bool = True
    no_prediction_build: bool = True
    no_export: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_role": self.source_role,
            "source_state": self.source_state,
            "relative_root": self.relative_root,
            "latest_part_path": self.latest_part_path,
            "latest_date_partition": self.latest_date_partition,
            "file_exists": self.file_exists,
            "file_size_bytes": self.file_size_bytes,
            "file_mtime_utc": self.file_mtime_utc,
            "tail_read_attempted": self.tail_read_attempted,
            "tail_read_succeeded": self.tail_read_succeeded,
            "parsed_row_count": self.parsed_row_count,
            "top_level_key_sample": list(self.top_level_key_sample),
            "payload_key_sample": list(self.payload_key_sample),
            "record_types": list(self.record_types),
            "channels": list(self.channels),
            "transports": list(self.transports),
            "latest_collector_ts": self.latest_collector_ts,
            "latest_event_ts": self.latest_event_ts,
            "latest_market_uid": self.latest_market_uid,
            "latest_symbol_raw": self.latest_symbol_raw,
            "latest_trust_state": self.latest_trust_state,
            "latest_continuity_state": self.latest_continuity_state,
            "latest_interpretation_bucket": self.latest_interpretation_bucket,
            "latest_schema_contract": self.latest_schema_contract,
            "latest_payload_contract_version": self.latest_payload_contract_version,
            "overview_best_bid": self.overview_best_bid,
            "overview_best_ask": self.overview_best_ask,
            "overview_mid_price": self.overview_mid_price,
            "overview_spread": self.overview_spread,
            "overview_near_size_imbalance": self.overview_near_size_imbalance,
            "trade_price_sample": list(self.trade_price_sample),
            "trade_side_sample": list(self.trade_side_sample),
            "orderbook_bid_level_count": self.orderbook_bid_level_count,
            "orderbook_ask_level_count": self.orderbook_ask_level_count,
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "bounded_tail_only": self.bounded_tail_only,
            "schema_summary_only": self.schema_summary_only,
            "no_runtime_write": self.no_runtime_write,
            "no_prediction_build": self.no_prediction_build,
            "no_export": self.no_export,
        }


@dataclass(frozen=True)
class PredictionWarRoomHotSourceProbePacket:
    probe_version: str
    probe_id: str
    probe_state: str
    hot_latest_root_hint: str
    exchange: str
    symbol_raw: str
    probe_sequence: Tuple[str, ...] = HOT_SOURCE_PROBE_SEQUENCE
    requested_actual_probe: bool = False
    allow_guard_test_root: bool = False
    target_root_valid: bool = False
    source_summaries: Tuple[PredictionWarRoomHotSourceProbeSourceSummary, ...] = ()
    source_summary_count: int = 0
    ready_for_future_prediction_source_mapping: bool = False
    ready_for_future_prediction_system_result_build: bool = False
    ready_for_latest_payload_export: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    probe_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    bounded_tail_only: bool = True
    schema_summary_only: bool = True
    non_ui_probe_only: bool = True
    prediction_system_result_built_by_this_probe: bool = False
    latest_prediction_artifact_exported_by_this_probe: bool = False
    runtime_artifact_write_performed_by_this_probe: bool = False
    collector_state_write_performed_by_this_probe: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_probe_execution: bool = False
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
            "probe_version": self.probe_version,
            "probe_id": self.probe_id,
            "probe_state": self.probe_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "exchange": self.exchange,
            "symbol_raw": self.symbol_raw,
            "probe_sequence": list(self.probe_sequence),
            "requested_actual_probe": self.requested_actual_probe,
            "allow_guard_test_root": self.allow_guard_test_root,
            "target_root_valid": self.target_root_valid,
            "source_summaries": [item.to_dict() for item in self.source_summaries],
            "source_summary_count": self.source_summary_count,
            "ready_for_future_prediction_source_mapping": self.ready_for_future_prediction_source_mapping,
            "ready_for_future_prediction_system_result_build": self.ready_for_future_prediction_system_result_build,
            "ready_for_latest_payload_export": self.ready_for_latest_payload_export,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "probe_summary": dict(self.probe_summary),
            "read_only": self.read_only,
            "bounded_tail_only": self.bounded_tail_only,
            "schema_summary_only": self.schema_summary_only,
            "non_ui_probe_only": self.non_ui_probe_only,
            "prediction_system_result_built_by_this_probe": self.prediction_system_result_built_by_this_probe,
            "latest_prediction_artifact_exported_by_this_probe": self.latest_prediction_artifact_exported_by_this_probe,
            "runtime_artifact_write_performed_by_this_probe": self.runtime_artifact_write_performed_by_this_probe,
            "collector_state_write_performed_by_this_probe": self.collector_state_write_performed_by_this_probe,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_probe_execution": self.ui_triggered_probe_execution,
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


def _role_root(data_root: Path, role: str, *, exchange: str, symbol_raw: str) -> Path:
    rel = ROLE_RELATIVE_ROOTS[role].format(exchange=exchange, symbol=symbol_raw)
    return data_root / rel


def _latest_part_file(root: Path) -> Path | None:
    if not root.exists() or not root.is_dir():
        return None
    date_dirs = sorted((p for p in root.iterdir() if p.is_dir() and p.name.startswith("date=")), key=lambda item: item.name)
    if not date_dirs:
        return None
    part_files = sorted(date_dirs[-1].glob("part-*.jsonl"))
    return part_files[-1] if part_files else None


def _mtime_utc(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except Exception:
        return ""


def _tail_lines(path: Path, *, max_lines: int, max_bytes: int) -> tuple[str, ...]:
    try:
        size = int(path.stat().st_size)
    except Exception:
        return ()
    if size <= 0:
        return ()
    read_size = min(size, max(1024, int(max_bytes)))
    try:
        with path.open("rb") as handle:
            handle.seek(max(0, size - read_size))
            data = handle.read(read_size)
    except Exception:
        return ()
    if read_size < size:
        first_newline = data.find(bytes((10,)))
        if first_newline >= 0:
            data = data[first_newline + 1 :]
    try:
        lines = data.decode("utf-8", errors="replace").splitlines()
    except Exception:
        return ()
    return tuple(line for line in lines[-max(1, int(max_lines)) :] if line.strip())


def _parse_rows(lines: tuple[str, ...]) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line in lines:
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, Mapping):
            rows.append(value)
    return tuple(rows)


def _unique_strings(rows: tuple[Mapping[str, Any], ...], key: str, *, limit: int = 8) -> tuple[str, ...]:
    out: list[str] = []
    for row in rows:
        value = row.get(key)
        if value is None or value == "":
            continue
        text = str(value)
        if text not in out:
            out.append(text)
    return tuple(out[:limit])


def _float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _path_display(path: Path, data_root: Path) -> str:
    try:
        return str(path.relative_to(data_root)).replace("/", "\\")
    except Exception:
        return str(path)


def _summarize_role(
    *,
    data_root: Path,
    role: str,
    exchange: str,
    symbol_raw: str,
    actual_probe: bool,
    max_tail_lines: int,
    max_tail_bytes: int,
) -> PredictionWarRoomHotSourceProbeSourceSummary:
    rel_root = ROLE_RELATIVE_ROOTS[role].format(exchange=exchange, symbol=symbol_raw)
    root = _role_root(data_root, role, exchange=exchange, symbol_raw=symbol_raw)
    latest = _latest_part_file(root)
    blockers: list[str] = []
    warnings: list[str] = []
    if latest is None:
        return PredictionWarRoomHotSourceProbeSourceSummary(
            source_role=role,
            source_state="source_latest_part_missing",
            relative_root=rel_root,
            blocker_reasons=(role + "_latest_part_missing",),
        )
    if not actual_probe:
        return PredictionWarRoomHotSourceProbeSourceSummary(
            source_role=role,
            source_state="source_probe_blocked_actual_probe_not_requested",
            relative_root=rel_root,
            latest_part_path=_path_display(latest, data_root),
            latest_date_partition=latest.parent.name,
            file_exists=True,
            file_size_bytes=int(latest.stat().st_size),
            file_mtime_utc=_mtime_utc(latest),
            blocker_reasons=("actual_probe_not_requested",),
        )
    lines = _tail_lines(latest, max_lines=max_tail_lines, max_bytes=max_tail_bytes)
    rows = _parse_rows(lines)
    if not rows:
        blockers.append(role + "_tail_json_rows_missing")
    latest_row = rows[-1] if rows else {}
    payload = latest_row.get("payload") if isinstance(latest_row.get("payload"), Mapping) else {}
    payload_map = payload if isinstance(payload, Mapping) else {}
    top_keys = tuple(str(key) for key in list(latest_row.keys())[:20])
    payload_keys = tuple(str(key) for key in list(payload_map.keys())[:20])
    overview_summary = latest_row.get("top_book_summary") if isinstance(latest_row.get("top_book_summary"), Mapping) else {}
    imbalance_summary = latest_row.get("imbalance_summary") if isinstance(latest_row.get("imbalance_summary"), Mapping) else {}
    bid_levels = payload_map.get("bids") if isinstance(payload_map.get("bids"), list) else []
    ask_levels = payload_map.get("asks") if isinstance(payload_map.get("asks"), list) else []
    if role == "market_overview":
        if str(latest_row.get("trust_state") or "") != "trusted":
            blockers.append("market_overview_trust_state_not_trusted")
        if str(latest_row.get("continuity_state") or "") != "continuous":
            blockers.append("market_overview_continuity_state_not_continuous")
        if str(latest_row.get("interpretation_bucket") or "") != "allow_structural_use":
            blockers.append("market_overview_interpretation_bucket_not_allow_structural_use")
        if _float(latest_row.get("mid_price") or overview_summary.get("mid_price")) is None:
            blockers.append("market_overview_mid_price_missing")
    if role == "market_trade":
        if not payload_map.get("price") or not payload_map.get("size") or not payload_map.get("side"):
            blockers.append("market_trade_payload_price_size_side_missing")
    if role == "orderbook_snapshot":
        if len(bid_levels) <= 0 or len(ask_levels) <= 0:
            warnings.append("orderbook_snapshot_bid_or_ask_levels_missing")
        if "missing_exchange_ts" in [str(item) for item in latest_row.get("quality_flags", []) if item]:
            warnings.append("orderbook_snapshot_missing_exchange_ts_context_only")
    state = "source_probe_ready" if not blockers else "source_probe_blocked"
    trade_prices: list[float] = []
    trade_sides: list[str] = []
    for row in rows:
        item_payload = row.get("payload") if isinstance(row.get("payload"), Mapping) else {}
        item_payload_map = item_payload if isinstance(item_payload, Mapping) else {}
        price = _float(item_payload_map.get("price"))
        if price is not None:
            trade_prices.append(price)
        side = str(item_payload_map.get("side") or "")
        if side and side not in trade_sides:
            trade_sides.append(side)
    return PredictionWarRoomHotSourceProbeSourceSummary(
        source_role=role,
        source_state=state,
        relative_root=rel_root,
        latest_part_path=_path_display(latest, data_root),
        latest_date_partition=latest.parent.name,
        file_exists=True,
        file_size_bytes=int(latest.stat().st_size),
        file_mtime_utc=_mtime_utc(latest),
        tail_read_attempted=True,
        tail_read_succeeded=bool(rows),
        parsed_row_count=len(rows),
        top_level_key_sample=top_keys,
        payload_key_sample=payload_keys,
        record_types=_unique_strings(rows, "record_type"),
        channels=_unique_strings(rows, "channel"),
        transports=_unique_strings(rows, "transport"),
        latest_collector_ts=str(latest_row.get("collector_ts") or ""),
        latest_event_ts=str(latest_row.get("event_ts") or latest_row.get("exchange_ts") or ""),
        latest_market_uid=str(latest_row.get("market_uid") or latest_row.get("instrument_id") or ""),
        latest_symbol_raw=str(latest_row.get("symbol_raw") or latest_row.get("symbol") or ""),
        latest_trust_state=str(latest_row.get("trust_state") or ""),
        latest_continuity_state=str(latest_row.get("continuity_state") or ""),
        latest_interpretation_bucket=str(latest_row.get("interpretation_bucket") or ""),
        latest_schema_contract=str(latest_row.get("schema_contract") or ""),
        latest_payload_contract_version=str(latest_row.get("payload_contract_version") or ""),
        overview_best_bid=_float(latest_row.get("best_bid") or overview_summary.get("best_bid")),
        overview_best_ask=_float(latest_row.get("best_ask") or overview_summary.get("best_ask")),
        overview_mid_price=_float(latest_row.get("mid_price") or overview_summary.get("mid_price")),
        overview_spread=_float(latest_row.get("spread") or overview_summary.get("spread")),
        overview_near_size_imbalance=_float(latest_row.get("imbalance") or imbalance_summary.get("near_size_imbalance")),
        trade_price_sample=tuple(trade_prices[-5:]),
        trade_side_sample=tuple(trade_sides[:4]),
        orderbook_bid_level_count=len(bid_levels),
        orderbook_ask_level_count=len(ask_levels),
        blocker_reasons=tuple(dict.fromkeys(blockers)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )


def build_prediction_warroom_hot_source_probe(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    exchange: str = DEFAULT_EXCHANGE,
    symbol_raw: str = DEFAULT_SYMBOL_RAW,
    allow_actual_probe: bool = False,
    allow_guard_test_root: bool = False,
    max_tail_lines: int = DEFAULT_MAX_TAIL_LINES,
    max_tail_bytes: int = DEFAULT_MAX_TAIL_BYTES,
) -> PredictionWarRoomHotSourceProbePacket:
    """Return a bounded read-only D-hot source probe summary for future prediction input mapping."""
    root_text = str(hot_latest_root_hint)
    data_root = Path(root_text)
    target_root_valid = _root_ok(root_text, allow_guard_test_root=allow_guard_test_root)
    blockers: list[str] = []
    warnings: list[str] = []
    summaries: tuple[PredictionWarRoomHotSourceProbeSourceSummary, ...] = ()
    if not allow_actual_probe:
        blockers.append("allow_actual_probe_false")
    if not target_root_valid:
        blockers.append("hot_source_probe_root_must_be_D_btc_ts_hot")
    if target_root_valid:
        summaries = tuple(
            _summarize_role(
                data_root=data_root,
                role=role,
                exchange=str(exchange),
                symbol_raw=str(symbol_raw),
                actual_probe=allow_actual_probe,
                max_tail_lines=max_tail_lines,
                max_tail_bytes=max_tail_bytes,
            )
            for role in SOURCE_ROLES
        )
        for summary in summaries:
            blockers.extend(summary.blocker_reasons)
            warnings.extend(summary.warning_reasons)
    summary_by_role = {item.source_role: item for item in summaries}
    overview = summary_by_role.get("market_overview")
    trade = summary_by_role.get("market_trade")
    orderbook = summary_by_role.get("orderbook_snapshot")
    overview_ready = bool(overview and overview.source_state == "source_probe_ready")
    trade_ready = bool(trade and trade.source_state == "source_probe_ready")
    orderbook_observed = bool(orderbook and orderbook.parsed_row_count > 0)
    ready_for_mapping = bool(allow_actual_probe and target_root_valid and overview_ready and trade_ready)
    if not orderbook_observed:
        warnings.append("orderbook_snapshot_not_observed_for_future_feature_depth_context")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    state = "hot_source_probe_ready_for_future_prediction_source_mapping" if ready_for_mapping and not unique_blockers else "hot_source_probe_blocked"
    return PredictionWarRoomHotSourceProbePacket(
        probe_version=HOT_SOURCE_PROBE_VERSION,
        probe_id=f"{HOT_SOURCE_PROBE_VERSION}:{str(exchange)}:{str(symbol_raw)}:{state}",
        probe_state=state,
        hot_latest_root_hint=root_text,
        exchange=str(exchange),
        symbol_raw=str(symbol_raw),
        requested_actual_probe=allow_actual_probe,
        allow_guard_test_root=allow_guard_test_root,
        target_root_valid=target_root_valid,
        source_summaries=summaries,
        source_summary_count=len(summaries),
        ready_for_future_prediction_source_mapping=ready_for_mapping and not unique_blockers,
        ready_for_future_prediction_system_result_build=False,
        ready_for_latest_payload_export=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        probe_summary={
            "boundary": "ps_q9z_hot_source_probe_bounded_read_only_schema_summary",
            "overview_ready": overview_ready,
            "trade_ready": trade_ready,
            "orderbook_observed": orderbook_observed,
            "future_mapping_requires_next_slice": True,
            "prediction_system_result_built_by_this_probe": False,
            "latest_prediction_artifact_exported_by_this_probe": False,
            "runtime_artifact_write_performed_by_this_probe": False,
            "warroom_ui_trigger_allowed": False,
            "ui_controls_added": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )


def format_prediction_warroom_hot_source_probe_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    data = packet.to_dict() if hasattr(packet, "to_dict") else packet
    mapping = data if isinstance(data, Mapping) else {}
    source_summaries = mapping.get("source_summaries", []) if isinstance(mapping.get("source_summaries", []), list) else []
    lines = [
        "prediction_hot_source_probe=" + HOT_SOURCE_PROBE_VERSION,
        "state=" + str(mapping.get("probe_state") or "missing"),
        "root=" + str(mapping.get("hot_latest_root_hint") or ""),
        "symbol=" + str(mapping.get("symbol_raw") or ""),
        "source_summary_count=" + str(mapping.get("source_summary_count") or 0),
        "ready_for_future_prediction_source_mapping=" + str(bool(mapping.get("ready_for_future_prediction_source_mapping"))),
        "ready_for_future_prediction_system_result_build=" + str(bool(mapping.get("ready_for_future_prediction_system_result_build"))),
        "ready_for_latest_payload_export=" + str(bool(mapping.get("ready_for_latest_payload_export"))),
        "blockers=" + ",".join(str(item) for item in mapping.get("blocked_reasons", [])),
        "warnings=" + ",".join(str(item) for item in mapping.get("warning_reasons", [])),
    ]
    for item in source_summaries:
        if isinstance(item, Mapping):
            lines.append(
                "source=" + str(item.get("source_role"))
                + ";state=" + str(item.get("source_state"))
                + ";rows=" + str(item.get("parsed_row_count"))
                + ";path=" + str(item.get("latest_part_path"))
            )
    lines.append("ui=false;runtime_write=false;prediction_build=false;export=false;approval=false;ledger=false;autotrade=false;broker=false")
    return "\n".join(lines)
