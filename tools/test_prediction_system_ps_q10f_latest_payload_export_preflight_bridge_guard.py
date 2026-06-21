# path: ./tools/test_prediction_system_ps_q10f_latest_payload_export_preflight_bridge_guard.py
# desc: Focused guard for PS-Q10F latest payload export preflight bridge.

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_export_preflight_bridge import (
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION,
    build_prediction_warroom_latest_payload_export_preflight_bridge,
    format_prediction_warroom_latest_payload_export_preflight_bridge_stdout_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_preflight_bridge.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
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
    "write_text(",
    "write_bytes(",
    "append_jsonl",
    "atomic_write_text",
    "atomic_write_bytes",
    "write_json(",
    "mkdir",
    "open(",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "persist=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "latest_prediction_artifact_exported_by_this_bridge: bool = True",
    "runtime_artifact_write_performed_by_this_bridge: bool = True",
    "target_directory_created_by_this_bridge: bool = True",
    "target_file_written_by_this_bridge: bool = True",
    "collector_state_write_performed_by_this_bridge: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_bridge_execution: bool = True",
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
    trades: list[dict] = []
    for idx in range(90):
        price = 100.0 + (idx * 0.1)
        trades.append(
            {
                "schema_contract": "collector.vnext.canonical.required.v1",
                "payload_contract_version": 1,
                "record_type": "market.trade",
                "exchange": "bitflyer",
                "symbol": "FX_BTC_JPY",
                "instrument_id": "bitflyer.fx.FX_BTC_JPY",
                "channel": "executions",
                "transport": "rest" if idx % 2 == 0 else "websocket",
                "source_event_id": str(idx),
                "event_ts": f"2026-06-21T07:44:{idx % 60:02d}Z",
                "payload": {"side": "BUY" if idx % 2 == 0 else "SELL", "price": price, "size": 0.01, "notional": price * 0.01, "trade_ts": f"2026-06-21T07:44:{idx % 60:02d}Z"},
            }
        )
    book = {
        "record_type": "market.orderbook.snapshot",
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
    assert packet["non_ui_bridge_only"] is True
    assert packet["stdout_only"] is True
    assert packet["prediction_system_result_built_by_child_runner"] in (False, True)
    for key in (
        "ready_for_latest_payload_export",
        "latest_prediction_artifact_exported_by_this_bridge",
        "runtime_artifact_write_performed_by_this_bridge",
        "target_directory_created_by_this_bridge",
        "target_file_written_by_this_bridge",
        "collector_state_write_performed_by_this_bridge",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_bridge_execution",
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


def test_ps_q10f_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_prediction_system_result_builder_runner" in imports
    assert "prediction_warroom_latest_payload_export_preflight_contract" in imports
    assert LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION == "prediction_warroom_latest_payload_export_preflight_bridge.ps_q10f.v1"
    assert "do_not_export_latest_prediction_artifact" in text


def test_ps_q10f_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_latest_payload_export_preflight_bridge" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q10f_default_blocks_before_work() -> None:
    packet = build_prediction_warroom_latest_payload_export_preflight_bridge().to_dict()
    assert packet["bridge_state"] == "latest_payload_export_preflight_bridge_blocked"
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "allow_actual_read_false" in packet["blocked_reasons"]
    assert "allow_prediction_build_false" in packet["blocked_reasons"]
    assert "allow_export_preflight_false" in packet["blocked_reasons"]
    assert packet["builder_runner_packet"] == {}
    assert packet["export_preflight_packet"] == {}
    _assert_safe(packet)


def test_ps_q10f_guard_root_bridges_built_payload_to_export_preflight_only() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10f_ready_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_latest_payload_export_preflight_bridge(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_guard_test_root=True,
        ).to_dict()
        assert packet["bridge_state"] == "latest_payload_export_preflight_bridge_ready_for_future_non_ui_export_runner"
        assert packet["prediction_result_payload_present"] is True
        assert packet["prediction_run_id"]
        assert packet["output_count"] > 0
        assert packet["prediction_result_blocker_count"] == 0
        assert packet["ready_for_future_latest_payload_export_preflight"] is True
        assert packet["ready_for_future_non_ui_export_runner"] is True
        assert packet["ready_for_latest_payload_export"] is False
        assert packet["builder_runner_packet"]["runner_state"] == "prediction_system_result_builder_runner_built"
        assert packet["export_preflight_packet"]["contract_state"] == "latest_payload_export_preflight_ready_for_future_non_ui_export_runner"
        assert packet["export_preflight_packet"]["target_artifact_path_hint"] == "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json"
        stdout = format_prediction_warroom_latest_payload_export_preflight_bridge_stdout_summary(packet)
        assert "latest_payload_export_preflight_bridge=prediction_warroom_latest_payload_export_preflight_bridge.ps_q10f.v1" in stdout
        assert "state=latest_payload_export_preflight_bridge_ready_for_future_non_ui_export_runner" in stdout
        assert "ready_for_future_non_ui_export_runner=True" in stdout
        assert "ready_for_latest_payload_export=False" in stdout
        assert "ui=false;runtime_write=false;prediction_build=true;export=false;approval=false;ledger=false;autotrade=false;broker=false" in stdout
        _assert_safe(packet)


def test_ps_q10f_rejects_forbidden_export_write_ui_or_broker_requests() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10f_blocked_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_latest_payload_export_preflight_bridge(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_guard_test_root=True,
            requested_latest_payload_export=True,
            requested_runtime_write=True,
            requested_warroom_ui_trigger=True,
            requested_approval_or_ledger_or_autotrade_or_broker=True,
        ).to_dict()
        assert packet["bridge_state"] == "latest_payload_export_preflight_bridge_blocked"
        assert "latest_payload_export_not_allowed_by_preflight_bridge" in packet["blocked_reasons"]
        assert "runtime_write_not_allowed_by_preflight_bridge" in packet["blocked_reasons"]
        assert "warroom_ui_trigger_not_allowed_by_preflight_bridge" in packet["blocked_reasons"]
        assert "approval_ledger_autotrade_broker_not_allowed_by_preflight_bridge" in packet["blocked_reasons"]
        assert packet["builder_runner_packet"] == {}
        _assert_safe(packet)


def main() -> int:
    test_ps_q10f_static_boundaries_and_markers()
    test_ps_q10f_not_mounted_in_warroom_ui()
    test_ps_q10f_default_blocks_before_work()
    test_ps_q10f_guard_root_bridges_built_payload_to_export_preflight_only()
    test_ps_q10f_rejects_forbidden_export_write_ui_or_broker_requests()
    print("[OK] Prediction System PS-Q10F latest payload export preflight bridge guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
