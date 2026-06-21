# path: ./tools/test_prediction_system_ps_q10b_source_mapping_probe_runner_guard.py
# desc: Focused guard for PS-Q10B source mapping probe runner.

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_source_mapping_probe_runner import (
    SOURCE_MAPPING_PROBE_RUNNER_VERSION,
    build_prediction_warroom_source_mapping_probe_runner,
    format_prediction_warroom_source_mapping_probe_runner_stdout_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_mapping_probe_runner.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "build_prediction_system_result(",
    "aggregate_ohlcv_from_rows(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "build_prediction_warroom_display_packet(",
    "load_prediction_warroom_latest_payload_read_only(",
    "write_text(",
    "write_bytes(",
    "append_jsonl",
    "atomic_write_text",
    "atomic_write_bytes",
    "write_json(",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "persist=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "prediction_system_result_built_by_this_runner: bool = True",
    "latest_prediction_artifact_exported_by_this_runner: bool = True",
    "runtime_artifact_write_performed_by_this_runner: bool = True",
    "collector_state_write_performed_by_this_runner: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_runner_execution: bool = True",
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


def _append_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _sample_root(root: Path) -> None:
    overview = {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-21T07:44:33Z",
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "top_book_summary": {"best_bid": 100.0, "best_ask": 102.0, "mid_price": 101.0, "spread": 2.0},
    }
    trades = [
        {
            "schema_contract": "collector.vnext.canonical.required.v1",
            "payload_contract_version": 1,
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
            "schema_contract": "collector.vnext.canonical.required.v1",
            "payload_contract_version": 1,
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
    book = {
        "schema_contract": "collector.vnext.canonical.required.v1",
        "payload_contract_version": 1,
        "record_type": "market.orderbook.snapshot",
        "channel": "board_snapshot",
        "transport": "rest",
        "symbol": "FX_BTC_JPY",
        "instrument_id": "bitflyer.fx.FX_BTC_JPY",
        "collector_ts": "2026-06-21T07:44:31Z",
        "event_ts": "2026-06-21T07:44:31Z",
        "quality_flags": ["missing_exchange_ts"],
        "payload": {"bids": [{"price": 100.0, "size": 1.0}], "asks": [{"price": 102.0, "size": 1.0}]},
    }
    _append_jsonl(root / "data/market_state/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.overview/date=2026-06-21/part-00001.jsonl", [overview])
    _append_jsonl(root / "data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.trade/date=2026-06-21/part-00001.jsonl", trades)
    _append_jsonl(root / "data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.orderbook.snapshot/date=2026-06-21/part-00001.jsonl", [book])


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["bounded_tail_only"] is True
    assert packet["stdout_only"] is True
    assert packet["non_ui_runner_only"] is True
    for key in (
        "ready_for_latest_payload_export",
        "prediction_system_result_built_by_this_runner",
        "latest_prediction_artifact_exported_by_this_runner",
        "runtime_artifact_write_performed_by_this_runner",
        "collector_state_write_performed_by_this_runner",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_runner_execution",
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


def test_ps_q10b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert SOURCE_MAPPING_PROBE_RUNNER_VERSION == "prediction_warroom_source_mapping_probe_runner.ps_q10b.v1"
    assert "read_bounded_market_trade_tail" in text
    assert "invoke_ps_q9z_hot_source_probe" in text
    assert "invoke_ps_q10a_source_mapping_preflight" in text
    assert "do_not_build_prediction_system_result" in text


def test_ps_q10b_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_source_mapping_probe_runner" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q10b_default_blocks_before_read() -> None:
    packet = build_prediction_warroom_source_mapping_probe_runner().to_dict()
    assert packet["runner_state"] == "source_mapping_probe_runner_blocked"
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "allow_actual_read_false" in packet["blocked_reasons"]
    assert packet["market_trade_tail_row_count"] == 0
    assert packet["q9z_probe_packet"] == {}
    assert packet["q10a_preflight_packet"] == {}
    _assert_safe(packet)


def test_ps_q10b_rejects_wrong_root_without_guard_mode() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10b_wrong_root_") as raw_root:
        packet = build_prediction_warroom_source_mapping_probe_runner(
            hot_latest_root_hint=raw_root,
            operator_acknowledged=True,
            allow_actual_read=True,
        ).to_dict()
        assert packet["runner_state"] == "source_mapping_probe_runner_blocked"
        assert "source_mapping_probe_runner_root_must_be_D_btc_ts_hot" in packet["blocked_reasons"]
        assert packet["market_trade_tail_row_count"] == 0
        _assert_safe(packet)


def test_ps_q10b_guard_test_root_ready_for_future_builder_only() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10b_ready_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_source_mapping_probe_runner(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_guard_test_root=True,
            market_trade_tail_lines=8,
            market_overview_tail_lines=2,
            orderbook_snapshot_tail_lines=1,
            max_tail_bytes=64 * 1024,
        ).to_dict()
        assert packet["runner_state"] == "source_mapping_probe_runner_ready_for_future_prediction_system_result_builder"
        assert packet["ready_for_future_prediction_system_result_builder"] is True
        assert packet["ready_for_latest_payload_export"] is False
        assert packet["market_overview_tail_row_count"] == 1
        assert packet["market_trade_tail_row_count"] == 2
        assert packet["orderbook_snapshot_tail_row_count"] == 1
        assert packet["normalized_ohlcv_row_count"] == 2
        assert packet["venue_snapshot_candidate_count"] == 1
        assert packet["feature_depth_context_candidate_present"] is True
        assert packet["q9z_probe_packet"]["ready_for_future_prediction_source_mapping"] is True
        assert packet["q10a_preflight_packet"]["ready_for_future_prediction_system_result_builder"] is True
        stdout = format_prediction_warroom_source_mapping_probe_runner_stdout_summary(packet)
        assert "prediction_source_mapping_probe_runner=prediction_warroom_source_mapping_probe_runner.ps_q10b.v1" in stdout
        assert "state=source_mapping_probe_runner_ready_for_future_prediction_system_result_builder" in stdout
        assert "ready_for_latest_payload_export=False" in stdout
        assert "ui=false;runtime_write=false;prediction_build=false;export=false;approval=false;ledger=false;autotrade=false;broker=false" in stdout
        _assert_safe(packet)


def test_ps_q10b_blocks_when_trade_file_missing() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10b_missing_trade_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        trade = root / "data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.trade/date=2026-06-21/part-00001.jsonl"
        trade.unlink()
        packet = build_prediction_warroom_source_mapping_probe_runner(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_guard_test_root=True,
        ).to_dict()
        assert packet["runner_state"] == "source_mapping_probe_runner_blocked"
        assert "market_trade_latest_part_missing" in packet["blocked_reasons"]
        assert packet["ready_for_future_prediction_system_result_builder"] is False
        _assert_safe(packet)


def main() -> int:
    test_ps_q10b_static_boundaries_and_markers()
    test_ps_q10b_not_mounted_in_warroom_ui()
    test_ps_q10b_default_blocks_before_read()
    test_ps_q10b_rejects_wrong_root_without_guard_mode()
    test_ps_q10b_guard_test_root_ready_for_future_builder_only()
    test_ps_q10b_blocks_when_trade_file_missing()
    print("[OK] Prediction System PS-Q10B source mapping probe runner guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
