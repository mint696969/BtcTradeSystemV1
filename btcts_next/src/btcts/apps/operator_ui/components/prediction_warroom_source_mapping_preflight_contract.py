# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_mapping_preflight_contract.py
# desc: PS-Q10A non-UI preflight contract that maps already-supplied PS-Q9Z probe summaries and bounded source rows into PredictionSystemResult builder-input candidates. Does not import/run PredictionSystem, read hot files, export artifacts, mutate UI/runtime state, approve, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_hot_source_probe import HOT_SOURCE_PROBE_VERSION

SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION = "prediction_warroom_source_mapping_preflight_contract.ps_q10a.v1"
MIN_NORMALIZED_TRADE_ROWS_FOR_BUILDER = 2
DEFAULT_TARGET_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"
DEFAULT_TARGET_SYMBOL_RAW = "FX_BTC_JPY"

SOURCE_MAPPING_PREFLIGHT_SEQUENCE = (
    "consume_ps_q9z_probe_packet_or_bounded_supplied_rows_only",
    "verify_probe_ready_for_future_prediction_source_mapping",
    "normalize_market_trade_payload_to_ohlcv_rows",
    "normalize_market_overview_to_venue_snapshot_candidate",
    "summarize_orderbook_snapshot_as_feature_depth_context_only",
    "declare_future_build_prediction_system_result_kwargs",
    "do_not_build_prediction_system_result",
    "do_not_export_latest_prediction_artifact",
    "do_not_read_hot_files",
    "do_not_mutate_warroom_ui_or_runtime_state",
)


@dataclass(frozen=True)
class PredictionWarRoomSourceMappingPreflightPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    mapping_sequence: Tuple[str, ...] = SOURCE_MAPPING_PREFLIGHT_SEQUENCE
    q9z_probe_version_expected: str = HOT_SOURCE_PROBE_VERSION
    q9z_probe_state: str = ""
    q9z_ready_for_future_prediction_source_mapping: bool = False
    target_market_uid: str = DEFAULT_TARGET_MARKET_UID
    target_symbol_raw: str = DEFAULT_TARGET_SYMBOL_RAW
    supplied_market_trade_row_count: int = 0
    supplied_market_overview_present: bool = False
    supplied_orderbook_snapshot_present: bool = False
    normalized_ohlcv_row_count: int = 0
    normalized_ohlcv_rows_preview: Tuple[Mapping[str, Any], ...] = ()
    venue_snapshot_candidate_count: int = 0
    venue_snapshots_preview: Tuple[Mapping[str, Any], ...] = ()
    feature_depth_context_candidate_present: bool = False
    feature_depth_context_summary: Mapping[str, Any] = field(default_factory=dict)
    builder_kwargs_contract: Mapping[str, Any] = field(default_factory=dict)
    ready_for_future_prediction_system_result_builder: bool = False
    ready_for_latest_payload_export: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_ui_contract_only: bool = True
    supplied_rows_only: bool = True
    schema_mapping_only: bool = True
    prediction_system_result_built_by_this_contract: bool = False
    latest_prediction_artifact_exported_by_this_contract: bool = False
    hot_file_read_performed_by_this_contract: bool = False
    payload_decode_performed_by_this_contract: bool = False
    runtime_artifact_write_performed_by_this_contract: bool = False
    collector_state_write_performed_by_this_contract: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_mapping_execution: bool = False
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
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "mapping_sequence": list(self.mapping_sequence),
            "q9z_probe_version_expected": self.q9z_probe_version_expected,
            "q9z_probe_state": self.q9z_probe_state,
            "q9z_ready_for_future_prediction_source_mapping": self.q9z_ready_for_future_prediction_source_mapping,
            "target_market_uid": self.target_market_uid,
            "target_symbol_raw": self.target_symbol_raw,
            "supplied_market_trade_row_count": self.supplied_market_trade_row_count,
            "supplied_market_overview_present": self.supplied_market_overview_present,
            "supplied_orderbook_snapshot_present": self.supplied_orderbook_snapshot_present,
            "normalized_ohlcv_row_count": self.normalized_ohlcv_row_count,
            "normalized_ohlcv_rows_preview": [dict(item) for item in self.normalized_ohlcv_rows_preview],
            "venue_snapshot_candidate_count": self.venue_snapshot_candidate_count,
            "venue_snapshots_preview": [dict(item) for item in self.venue_snapshots_preview],
            "feature_depth_context_candidate_present": self.feature_depth_context_candidate_present,
            "feature_depth_context_summary": dict(self.feature_depth_context_summary),
            "builder_kwargs_contract": dict(self.builder_kwargs_contract),
            "ready_for_future_prediction_system_result_builder": self.ready_for_future_prediction_system_result_builder,
            "ready_for_latest_payload_export": self.ready_for_latest_payload_export,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_ui_contract_only": self.non_ui_contract_only,
            "supplied_rows_only": self.supplied_rows_only,
            "schema_mapping_only": self.schema_mapping_only,
            "prediction_system_result_built_by_this_contract": self.prediction_system_result_built_by_this_contract,
            "latest_prediction_artifact_exported_by_this_contract": self.latest_prediction_artifact_exported_by_this_contract,
            "hot_file_read_performed_by_this_contract": self.hot_file_read_performed_by_this_contract,
            "payload_decode_performed_by_this_contract": self.payload_decode_performed_by_this_contract,
            "runtime_artifact_write_performed_by_this_contract": self.runtime_artifact_write_performed_by_this_contract,
            "collector_state_write_performed_by_this_contract": self.collector_state_write_performed_by_this_contract,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_mapping_execution": self.ui_triggered_mapping_execution,
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


def _as_mapping_tuple(rows: Iterable[Mapping[str, Any]] | None) -> tuple[Mapping[str, Any], ...]:
    if rows is None:
        return tuple()
    out: list[Mapping[str, Any]] = []
    for row in rows:
        if isinstance(row, Mapping):
            out.append(row)
    return tuple(out)


def _float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _normalize_trade_row(row: Mapping[str, Any], *, target_market_uid: str, target_symbol_raw: str) -> Mapping[str, Any] | None:
    payload = row.get("payload") if isinstance(row.get("payload"), Mapping) else {}
    payload_map = payload if isinstance(payload, Mapping) else {}
    price = _float(payload_map.get("price") or row.get("price"))
    size = _float(payload_map.get("size") or row.get("size") or row.get("volume"))
    event_ts = str(row.get("event_ts") or row.get("exchange_ts") or row.get("collector_ts") or payload_map.get("trade_ts") or "").strip()
    if price is None or size is None or not event_ts:
        return None
    return {
        "event_ts": event_ts,
        "price": price,
        "size": size,
        "side": str(payload_map.get("side") or row.get("side") or ""),
        "notional": _float(payload_map.get("notional") or row.get("notional")),
        "exchange": str(row.get("exchange") or "bitflyer"),
        "symbol": str(row.get("symbol") or row.get("symbol_raw") or target_symbol_raw),
        "market_uid": str(row.get("market_uid") or row.get("instrument_id") or target_market_uid),
        "source_family": "d_hot_market_trade_jsonl",
        "source_record_type": str(row.get("record_type") or "market.trade"),
        "source_channel": str(row.get("channel") or ""),
        "source_transport": str(row.get("transport") or ""),
        "source_event_id": str(row.get("source_event_id") or payload_map.get("trade_id") or ""),
        "read_only": True,
        "non_executing": True,
    }


def _normalize_trades(rows: tuple[Mapping[str, Any], ...], *, target_market_uid: str, target_symbol_raw: str) -> tuple[Mapping[str, Any], ...]:
    out: list[Mapping[str, Any]] = []
    for row in rows:
        normalized = _normalize_trade_row(row, target_market_uid=target_market_uid, target_symbol_raw=target_symbol_raw)
        if normalized is not None:
            out.append(normalized)
    return tuple(out)


def _venue_snapshot_from_overview(row: Mapping[str, Any], *, target_market_uid: str, target_symbol_raw: str) -> Mapping[str, Any] | None:
    top = row.get("top_book_summary") if isinstance(row.get("top_book_summary"), Mapping) else {}
    top_map = top if isinstance(top, Mapping) else {}
    mid_price = _float(row.get("mid_price") or top_map.get("mid_price"))
    best_bid = _float(row.get("best_bid") or top_map.get("best_bid"))
    best_ask = _float(row.get("best_ask") or top_map.get("best_ask"))
    if mid_price is None and (best_bid is None or best_ask is None):
        return None
    if mid_price is None and best_bid is not None and best_ask is not None:
        mid_price = round((best_bid + best_ask) / 2.0, 8)
    return {
        "source_id": "bitflyer_fx_ticker",
        "venue": "bitflyer",
        "symbol": str(row.get("symbol_raw") or target_symbol_raw),
        "market_role": "bitflyer_fx",
        "market_uid": str(row.get("market_uid") or target_market_uid),
        "collector_ts": str(row.get("collector_ts") or ""),
        "price": mid_price,
        "mid_price": mid_price,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": _float(row.get("spread") or top_map.get("spread")),
        "trust_state": str(row.get("trust_state") or ""),
        "continuity_state": str(row.get("continuity_state") or ""),
        "interpretation_bucket": str(row.get("interpretation_bucket") or ""),
        "read_only": True,
        "non_executing": True,
    }


def _feature_depth_context_from_orderbook(row: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = row.get("payload") if isinstance(row.get("payload"), Mapping) else {}
    payload_map = payload if isinstance(payload, Mapping) else {}
    bids = payload_map.get("bids") if isinstance(payload_map.get("bids"), list) else []
    asks = payload_map.get("asks") if isinstance(payload_map.get("asks"), list) else []
    quality_flags = tuple(str(item) for item in row.get("quality_flags", []) if item) if isinstance(row.get("quality_flags", []), list) else tuple()
    return {
        "source_id": "bitflyer_board_summary",
        "source_family": "d_hot_orderbook_snapshot_jsonl_context_only",
        "record_type": str(row.get("record_type") or "market.orderbook.snapshot"),
        "collector_ts": str(row.get("collector_ts") or ""),
        "event_ts": str(row.get("event_ts") or row.get("exchange_ts") or ""),
        "bid_level_count": len(bids),
        "ask_level_count": len(asks),
        "quality_flags": list(quality_flags),
        "context_only": True,
        "feature_depth_snapshot_object_created": False,
        "read_only": True,
        "non_executing": True,
    }


def _probe_ready(source_probe_packet: Mapping[str, Any]) -> bool:
    if not source_probe_packet:
        return False
    return bool(source_probe_packet.get("ready_for_future_prediction_source_mapping"))


def build_prediction_warroom_source_mapping_preflight_contract(
    *,
    source_probe_packet: Mapping[str, Any] | Any | None = None,
    supplied_market_trade_rows: Iterable[Mapping[str, Any]] | None = None,
    supplied_market_overview_row: Mapping[str, Any] | None = None,
    supplied_orderbook_snapshot_row: Mapping[str, Any] | None = None,
    target_market_uid: str = DEFAULT_TARGET_MARKET_UID,
    target_symbol_raw: str = DEFAULT_TARGET_SYMBOL_RAW,
    require_probe_ready: bool = True,
    min_normalized_trade_rows: int = MIN_NORMALIZED_TRADE_ROWS_FOR_BUILDER,
    requested_runtime_write: bool = False,
    requested_prediction_build: bool = False,
    requested_latest_payload_export: bool = False,
    requested_warroom_ui_trigger: bool = False,
    requested_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomSourceMappingPreflightPacket:
    """Map already-supplied hot source rows into future builder kwargs without building/exporting."""
    probe = _as_mapping(source_probe_packet)
    trade_rows = _as_mapping_tuple(supplied_market_trade_rows)
    overview_row = _as_mapping(supplied_market_overview_row)
    orderbook_row = _as_mapping(supplied_orderbook_snapshot_row)
    normalized_rows = _normalize_trades(trade_rows, target_market_uid=str(target_market_uid), target_symbol_raw=str(target_symbol_raw))
    venue = _venue_snapshot_from_overview(overview_row, target_market_uid=str(target_market_uid), target_symbol_raw=str(target_symbol_raw)) if overview_row else None
    venues = (venue,) if venue is not None else tuple()
    feature_context = _feature_depth_context_from_orderbook(orderbook_row) if orderbook_row else {}
    blockers: list[str] = []
    warnings: list[str] = []
    probe_state = str(probe.get("probe_state") or "")
    probe_ready = _probe_ready(probe)
    if require_probe_ready and not probe_ready:
        blockers.append("ps_q9z_probe_not_ready_for_future_prediction_source_mapping")
    if not trade_rows:
        blockers.append("supplied_market_trade_rows_missing")
    if len(normalized_rows) < int(min_normalized_trade_rows):
        blockers.append("normalized_ohlcv_rows_below_minimum")
    if not overview_row:
        blockers.append("supplied_market_overview_row_missing")
    if overview_row and venue is None:
        blockers.append("market_overview_could_not_map_to_venue_snapshot")
    if not orderbook_row:
        warnings.append("supplied_orderbook_snapshot_row_missing_feature_depth_context_deferred")
    if feature_context and (int(feature_context.get("bid_level_count") or 0) <= 0 or int(feature_context.get("ask_level_count") or 0) <= 0):
        warnings.append("orderbook_snapshot_feature_depth_context_levels_missing")
    if requested_runtime_write:
        blockers.append("runtime_write_not_allowed_by_source_mapping_preflight")
    if requested_prediction_build:
        blockers.append("prediction_build_not_allowed_by_source_mapping_preflight")
    if requested_latest_payload_export:
        blockers.append("latest_payload_export_not_allowed_by_source_mapping_preflight")
    if requested_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_by_source_mapping_preflight")
    if requested_approval_or_ledger_or_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed_by_source_mapping_preflight")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready_for_builder = not unique_blockers
    state = "source_mapping_preflight_ready_for_future_prediction_system_result_builder" if ready_for_builder else "source_mapping_preflight_blocked"
    builder_kwargs_contract = {
        "future_callable": "btcts.prediction.system.build_prediction_system_result",
        "rows": [dict(item) for item in normalized_rows],
        "venue_snapshots": [dict(item) for item in venues],
        "feature_depth_snapshot": None,
        "feature_depth_context_summary": dict(feature_context),
        "source_artifact_coverage_summary": {
            "mapping_contract_version": SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION,
            "observed_required_source_ids": [
                "bitflyer_trades",
                "bitflyer_fx_ticker",
            ] + (["bitflyer_board_summary"] if feature_context else []),
            "source_mapping_context_only": True,
            "source_probe_version": probe.get("probe_version") or HOT_SOURCE_PROBE_VERSION,
        },
        "source_quality_by_id": None,
        "requested_horizon_groups": None,
        "requested_horizons_sec": None,
        "previous_prediction_run_id": None,
        "now": None,
        "read_only": True,
        "non_executing": True,
    }
    return PredictionWarRoomSourceMappingPreflightPacket(
        contract_version=SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION,
        contract_id=f"{SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION}:{state}",
        contract_state=state,
        q9z_probe_state=probe_state,
        q9z_ready_for_future_prediction_source_mapping=probe_ready,
        target_market_uid=str(target_market_uid),
        target_symbol_raw=str(target_symbol_raw),
        supplied_market_trade_row_count=len(trade_rows),
        supplied_market_overview_present=bool(overview_row),
        supplied_orderbook_snapshot_present=bool(orderbook_row),
        normalized_ohlcv_row_count=len(normalized_rows),
        normalized_ohlcv_rows_preview=tuple(dict(item) for item in normalized_rows[:8]),
        venue_snapshot_candidate_count=len(venues),
        venue_snapshots_preview=tuple(dict(item) for item in venues[:4]),
        feature_depth_context_candidate_present=bool(feature_context),
        feature_depth_context_summary=feature_context,
        builder_kwargs_contract=builder_kwargs_contract,
        ready_for_future_prediction_system_result_builder=ready_for_builder,
        ready_for_latest_payload_export=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
    )
