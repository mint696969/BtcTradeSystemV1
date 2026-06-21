# path: ./tools/test_prediction_system_ps_q9z_hot_source_probe_guard.py
# desc: Focused guard for PS-Q9Z hot source probe.

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_hot_source_probe import (
    HOT_SOURCE_PROBE_VERSION,
    build_prediction_warroom_hot_source_probe,
    format_prediction_warroom_hot_source_probe_stdout_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_hot_source_probe.py"
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
)
FORBIDDEN_TOKENS = (
    "build_prediction_system_result(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "build_prediction_warroom_display_packet(",
    "load_prediction_warroom_latest_payload_read_only(",
    "write_text(",
    "write_bytes(",
    "append_jsonl",
    "atomic_write_text",
    "atomic_write_bytes",
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
    "prediction_system_result_built_by_this_probe: bool = True",
    "latest_prediction_artifact_exported_by_this_probe: bool = True",
    "runtime_artifact_write_performed_by_this_probe: bool = True",
    "collector_state_write_performed_by_this_probe: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_probe_execution: bool = True",
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
        "best_bid": 100.0,
        "best_ask": 102.0,
        "mid_price": 101.0,
        "spread": 2.0,
        "imbalance_summary": {"near_size_imbalance": -0.1},
        "top_book_summary": {"best_bid": 100.0, "best_ask": 102.0, "mid_price": 101.0, "spread": 2.0},
    }
    trade_a = {
        "schema_contract": "collector.vnext.canonical.required.v1",
        "payload_contract_version": 1,
        "record_type": "market.trade",
        "channel": "executions",
        "transport": "rest",
        "symbol": "FX_BTC_JPY",
        "instrument_id": "bitflyer.fx.FX_BTC_JPY",
        "collector_ts": "2026-06-21T07:44:30Z",
        "event_ts": "2026-06-21T07:44:29Z",
        "payload": {"side": "BUY", "price": 101.0, "size": 0.01, "notional": 1.01, "trade_ts": "2026-06-21T07:44:29Z"},
    }
    trade_b = dict(trade_a)
    trade_b["transport"] = "websocket"
    trade_b["payload"] = {"side": "SELL", "price": 100.5, "size": 0.02, "notional": 2.01, "trade_ts": "2026-06-21T07:44:31Z"}
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
    _append_jsonl(root / "data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.trade/date=2026-06-21/part-00001.jsonl", [trade_a, trade_b])
    _append_jsonl(root / "data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.orderbook.snapshot/date=2026-06-21/part-00001.jsonl", [book])


def _assert_no_side_effect_flags(packet: dict) -> None:
    for key in (
        "ready_for_future_prediction_system_result_build",
        "ready_for_latest_payload_export",
        "prediction_system_result_built_by_this_probe",
        "latest_prediction_artifact_exported_by_this_probe",
        "runtime_artifact_write_performed_by_this_probe",
        "collector_state_write_performed_by_this_probe",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_probe_execution",
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


def test_ps_q9z_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert HOT_SOURCE_PROBE_VERSION == "prediction_warroom_hot_source_probe.ps_q9z.v1"
    assert "read_bounded_tail_bytes_only" in text
    assert "decode_jsonl_tail_to_schema_summary_only" in text
    assert "do_not_build_prediction_system_result" in text


def test_ps_q9z_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_hot_source_probe" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q9z_default_blocks_without_actual_probe() -> None:
    packet = build_prediction_warroom_hot_source_probe().to_dict()
    assert packet["probe_state"] == "hot_source_probe_blocked"
    assert "allow_actual_probe_false" in packet["blocked_reasons"]
    assert packet["ready_for_future_prediction_source_mapping"] is False
    _assert_no_side_effect_flags(packet)


def test_ps_q9z_rejects_wrong_root_without_guard_mode() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9z_wrong_root_") as raw_root:
        packet = build_prediction_warroom_hot_source_probe(
            hot_latest_root_hint=raw_root,
            allow_actual_probe=True,
        ).to_dict()
        assert packet["probe_state"] == "hot_source_probe_blocked"
        assert "hot_source_probe_root_must_be_D_btc_ts_hot" in packet["blocked_reasons"]
        assert packet["source_summary_count"] == 0
        _assert_no_side_effect_flags(packet)


def test_ps_q9z_guard_test_root_probe_ready_for_future_mapping_only() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9z_probe_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_hot_source_probe(
            hot_latest_root_hint=str(root),
            allow_actual_probe=True,
            allow_guard_test_root=True,
            max_tail_lines=4,
            max_tail_bytes=64 * 1024,
        ).to_dict()
        assert packet["probe_state"] == "hot_source_probe_ready_for_future_prediction_source_mapping"
        assert packet["ready_for_future_prediction_source_mapping"] is True
        assert packet["ready_for_future_prediction_system_result_build"] is False
        assert packet["ready_for_latest_payload_export"] is False
        assert packet["source_summary_count"] == 3
        by_role = {item["source_role"]: item for item in packet["source_summaries"]}
        assert by_role["market_overview"]["source_state"] == "source_probe_ready"
        assert by_role["market_overview"]["latest_trust_state"] == "trusted"
        assert by_role["market_overview"]["overview_mid_price"] == 101.0
        assert by_role["market_trade"]["source_state"] == "source_probe_ready"
        assert by_role["market_trade"]["record_types"] == ["market.trade"]
        assert by_role["market_trade"]["transports"] == ["rest", "websocket"]
        assert by_role["orderbook_snapshot"]["orderbook_bid_level_count"] == 1
        stdout = format_prediction_warroom_hot_source_probe_stdout_summary(packet)
        assert "prediction_hot_source_probe=prediction_warroom_hot_source_probe.ps_q9z.v1" in stdout
        assert "state=hot_source_probe_ready_for_future_prediction_source_mapping" in stdout
        assert "ui=false;runtime_write=false;prediction_build=false;export=false;approval=false;ledger=false;autotrade=false;broker=false" in stdout
        _assert_no_side_effect_flags(packet)


def test_ps_q9z_blocks_when_trade_payload_cannot_map() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9z_bad_trade_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        bad_trade = {
            "record_type": "market.trade",
            "payload": {"side": "BUY"},
        }
        _append_jsonl(root / "data/market_data/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.trade/date=2026-06-22/part-00001.jsonl", [bad_trade])
        packet = build_prediction_warroom_hot_source_probe(
            hot_latest_root_hint=str(root),
            allow_actual_probe=True,
            allow_guard_test_root=True,
        ).to_dict()
        assert packet["probe_state"] == "hot_source_probe_blocked"
        assert "market_trade_payload_price_size_side_missing" in packet["blocked_reasons"]
        assert packet["ready_for_future_prediction_source_mapping"] is False
        _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q9z_static_boundaries_and_markers()
    test_ps_q9z_not_mounted_in_warroom_ui()
    test_ps_q9z_default_blocks_without_actual_probe()
    test_ps_q9z_rejects_wrong_root_without_guard_mode()
    test_ps_q9z_guard_test_root_probe_ready_for_future_mapping_only()
    test_ps_q9z_blocks_when_trade_payload_cannot_map()
    print("[OK] Prediction System PS-Q9Z hot source probe guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
