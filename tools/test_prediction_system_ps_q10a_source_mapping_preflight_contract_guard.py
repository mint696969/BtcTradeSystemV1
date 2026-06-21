# path: ./tools/test_prediction_system_ps_q10a_source_mapping_preflight_contract_guard.py
# desc: Focused guard for PS-Q10A source mapping preflight contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_source_mapping_preflight_contract import (
    SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION,
    build_prediction_warroom_source_mapping_preflight_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_hot_source_probe import HOT_SOURCE_PROBE_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_mapping_preflight_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade",
    "btcts.processing.l4_consumer_models.shared",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "json",
    "pathlib",
)
FORBIDDEN_TOKENS = (
    "build_prediction_system_result(",
    "aggregate_ohlcv_from_rows(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "build_prediction_warroom_display_packet(",
    "load_prediction_warroom_latest_payload_read_only(",
    "open(",
    "Path(",
    "read_text(",
    "read_bytes(",
    "write_text(",
    "write_bytes(",
    "append_jsonl",
    "atomic_write_text",
    "atomic_write_bytes",
    "json.load",
    "json.loads",
    "json.dump",
    "json.dumps",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "persist=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "prediction_system_result_built_by_this_contract: bool = True",
    "latest_prediction_artifact_exported_by_this_contract: bool = True",
    "hot_file_read_performed_by_this_contract: bool = True",
    "payload_decode_performed_by_this_contract: bool = True",
    "runtime_artifact_write_performed_by_this_contract: bool = True",
    "collector_state_write_performed_by_this_contract: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_mapping_execution: bool = True",
    "approval_or_authorization_allowed: bool = True",
    "ledger_append_allowed: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "would_collect_public_source: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_write_collector_state: bool = True",
    "would_send_to_broker: bool = True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _probe() -> dict:
    return {
        "probe_version": HOT_SOURCE_PROBE_VERSION,
        "probe_state": "hot_source_probe_ready_for_future_prediction_source_mapping",
        "ready_for_future_prediction_source_mapping": True,
    }


def _trades() -> list[dict]:
    return [
        {
            "record_type": "market.trade",
            "exchange": "bitflyer",
            "symbol": "FX_BTC_JPY",
            "instrument_id": "bitflyer.fx.FX_BTC_JPY",
            "channel": "executions",
            "transport": "rest",
            "source_event_id": "1",
            "event_ts": "2026-06-21T07:44:29Z",
            "payload": {"side": "BUY", "price": 101.0, "size": 0.01, "notional": 1.01, "trade_ts": "2026-06-21T07:44:29Z"},
        },
        {
            "record_type": "market.trade",
            "exchange": "bitflyer",
            "symbol": "FX_BTC_JPY",
            "instrument_id": "bitflyer.fx.FX_BTC_JPY",
            "channel": "executions_ws",
            "transport": "websocket",
            "source_event_id": "2",
            "event_ts": "2026-06-21T07:44:31Z",
            "payload": {"side": "SELL", "price": 100.5, "size": 0.02, "notional": 2.01, "trade_ts": "2026-06-21T07:44:31Z"},
        },
    ]


def _overview() -> dict:
    return {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-21T07:44:33Z",
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "top_book_summary": {"best_bid": 100.0, "best_ask": 102.0, "mid_price": 101.0, "spread": 2.0},
    }


def _book() -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "collector_ts": "2026-06-21T07:44:31Z",
        "quality_flags": ["missing_exchange_ts"],
        "payload": {"bids": [{"price": 100.0, "size": 1.0}], "asks": [{"price": 102.0, "size": 1.0}]},
    }


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_ui_contract_only"] is True
    assert packet["supplied_rows_only"] is True
    assert packet["schema_mapping_only"] is True
    for key in (
        "ready_for_latest_payload_export",
        "prediction_system_result_built_by_this_contract",
        "latest_prediction_artifact_exported_by_this_contract",
        "hot_file_read_performed_by_this_contract",
        "payload_decode_performed_by_this_contract",
        "runtime_artifact_write_performed_by_this_contract",
        "collector_state_write_performed_by_this_contract",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_mapping_execution",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_collect_public_source",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10a_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert SOURCE_MAPPING_PREFLIGHT_CONTRACT_VERSION == "prediction_warroom_source_mapping_preflight_contract.ps_q10a.v1"
    assert "normalize_market_trade_payload_to_ohlcv_rows" in text
    assert "declare_future_build_prediction_system_result_kwargs" in text
    assert "do_not_build_prediction_system_result" in text


def test_ps_q10a_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_source_mapping_preflight_contract" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q10a_blocks_without_probe_or_rows() -> None:
    packet = build_prediction_warroom_source_mapping_preflight_contract().to_dict()
    assert packet["contract_state"] == "source_mapping_preflight_blocked"
    assert "ps_q9z_probe_not_ready_for_future_prediction_source_mapping" in packet["blocked_reasons"]
    assert "supplied_market_trade_rows_missing" in packet["blocked_reasons"]
    assert "normalized_ohlcv_rows_below_minimum" in packet["blocked_reasons"]
    assert "supplied_market_overview_row_missing" in packet["blocked_reasons"]
    assert packet["ready_for_future_prediction_system_result_builder"] is False
    _assert_safe(packet)


def test_ps_q10a_maps_supplied_rows_to_future_builder_kwargs_contract() -> None:
    packet = build_prediction_warroom_source_mapping_preflight_contract(
        source_probe_packet=_probe(),
        supplied_market_trade_rows=_trades(),
        supplied_market_overview_row=_overview(),
        supplied_orderbook_snapshot_row=_book(),
    ).to_dict()
    assert packet["contract_state"] == "source_mapping_preflight_ready_for_future_prediction_system_result_builder"
    assert packet["ready_for_future_prediction_system_result_builder"] is True
    assert packet["ready_for_latest_payload_export"] is False
    assert packet["normalized_ohlcv_row_count"] == 2
    rows = packet["builder_kwargs_contract"]["rows"]
    assert rows[0]["event_ts"] == "2026-06-21T07:44:29Z"
    assert rows[0]["price"] == 101.0
    assert rows[0]["size"] == 0.01
    assert rows[1]["source_transport"] == "websocket"
    venues = packet["builder_kwargs_contract"]["venue_snapshots"]
    assert venues[0]["source_id"] == "bitflyer_fx_ticker"
    assert venues[0]["market_role"] == "bitflyer_fx"
    assert venues[0]["mid_price"] == 101.0
    coverage = packet["builder_kwargs_contract"]["source_artifact_coverage_summary"]
    assert "bitflyer_trades" in coverage["observed_required_source_ids"]
    assert "bitflyer_fx_ticker" in coverage["observed_required_source_ids"]
    assert "bitflyer_board_summary" in coverage["observed_required_source_ids"]
    assert packet["feature_depth_context_candidate_present"] is True
    assert packet["feature_depth_context_summary"]["feature_depth_snapshot_object_created"] is False
    _assert_safe(packet)


def test_ps_q10a_blocks_incomplete_trade_mapping() -> None:
    packet = build_prediction_warroom_source_mapping_preflight_contract(
        source_probe_packet=_probe(),
        supplied_market_trade_rows=[{"payload": {"side": "BUY"}}],
        supplied_market_overview_row=_overview(),
    ).to_dict()
    assert packet["contract_state"] == "source_mapping_preflight_blocked"
    assert "normalized_ohlcv_rows_below_minimum" in packet["blocked_reasons"]
    assert packet["normalized_ohlcv_row_count"] == 0
    _assert_safe(packet)


def test_ps_q10a_rejects_forbidden_execution_requests() -> None:
    packet = build_prediction_warroom_source_mapping_preflight_contract(
        source_probe_packet=_probe(),
        supplied_market_trade_rows=_trades(),
        supplied_market_overview_row=_overview(),
        requested_runtime_write=True,
        requested_prediction_build=True,
        requested_latest_payload_export=True,
        requested_warroom_ui_trigger=True,
        requested_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "source_mapping_preflight_blocked"
    assert "runtime_write_not_allowed_by_source_mapping_preflight" in packet["blocked_reasons"]
    assert "prediction_build_not_allowed_by_source_mapping_preflight" in packet["blocked_reasons"]
    assert "latest_payload_export_not_allowed_by_source_mapping_preflight" in packet["blocked_reasons"]
    assert "warroom_ui_trigger_not_allowed_by_source_mapping_preflight" in packet["blocked_reasons"]
    assert "approval_ledger_autotrade_broker_not_allowed_by_source_mapping_preflight" in packet["blocked_reasons"]
    _assert_safe(packet)


def main() -> int:
    test_ps_q10a_static_boundaries_and_markers()
    test_ps_q10a_not_mounted_in_warroom_ui()
    test_ps_q10a_blocks_without_probe_or_rows()
    test_ps_q10a_maps_supplied_rows_to_future_builder_kwargs_contract()
    test_ps_q10a_blocks_incomplete_trade_mapping()
    test_ps_q10a_rejects_forbidden_execution_requests()
    print("[OK] Prediction System PS-Q10A source mapping preflight contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
