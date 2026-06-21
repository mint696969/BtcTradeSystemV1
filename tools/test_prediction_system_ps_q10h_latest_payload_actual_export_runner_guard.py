# path: ./tools/test_prediction_system_ps_q10h_latest_payload_actual_export_runner_guard.py
# desc: Focused guard for PS-Q10H latest payload actual export runner wrapper.

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_actual_export_runner import (
    LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION,
    build_prediction_warroom_latest_payload_actual_export_runner,
    format_prediction_warroom_latest_payload_actual_export_runner_stdout_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_actual_export_runner.py"
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
    "pathlib",
    "json",
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
    "Path(",
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
    "would_write_collector_state: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
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


def _assert_no_trade_or_ui_side_effects(packet: dict) -> None:
    for key in (
        "collector_state_write_performed_by_this_runner",
        "hot_file_read_performed_by_export_runner",
        "payload_decode_performed_by_export_runner",
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


def test_ps_q10h_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_export_preflight_bridge" in imports
    assert "prediction_warroom_latest_payload_export_runner" in imports
    assert LATEST_PAYLOAD_ACTUAL_EXPORT_RUNNER_VERSION == "prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1"
    assert "write_exactly_prediction_latest_prediction_system_result_json_via_ps_q9y" in text
    assert "do_not_run_from_warroom_ui" in text


def test_ps_q10h_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_latest_payload_actual_export_runner" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q10h_default_blocks_before_work() -> None:
    packet = build_prediction_warroom_latest_payload_actual_export_runner().to_dict()
    assert packet["runner_state"] == "latest_payload_actual_export_runner_blocked"
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "allow_actual_read_false" in packet["blocked_reasons"]
    assert "allow_prediction_build_false" in packet["blocked_reasons"]
    assert "allow_export_preflight_false" in packet["blocked_reasons"]
    assert "allow_latest_payload_export_false" in packet["blocked_reasons"]
    assert "allow_runtime_artifact_write_false" in packet["blocked_reasons"]
    assert packet["preflight_bridge_packet"] == {}
    assert packet["export_runner_packet"] == {}
    assert packet["target_file_written"] is False
    _assert_no_trade_or_ui_side_effects(packet)


def test_ps_q10h_guard_root_exports_exactly_latest_payload_json_via_ps_q9y() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10h_export_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_latest_payload_actual_export_runner(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_latest_payload_export=True,
            allow_runtime_artifact_write=True,
            allow_guard_test_root=True,
        ).to_dict()
        target = root / "prediction" / "latest_prediction_system_result.json"
        assert packet["runner_state"] == "latest_payload_actual_export_runner_exported"
        assert packet["target_file_written"] is True
        assert packet["latest_prediction_artifact_exported_by_child_runner"] is True
        assert packet["runtime_artifact_write_performed_by_child_runner"] is True
        assert packet["target_file_written_by_child_runner"] is True
        assert packet["target_artifact_path"] == str(target)
        assert packet["target_file_size_bytes"] and packet["target_file_size_bytes"] > 0
        assert target.exists()
        assert not list(target.parent.glob("*.tmp"))
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded["run_identity"]["prediction_run_id"] == packet["prediction_run_id"]
        assert loaded["read_only"] is True
        assert loaded["non_executing"] is True
        assert isinstance(loaded.get("warnings"), list)
        assert packet["preflight_bridge_packet"]["bridge_state"] == "latest_payload_export_preflight_bridge_ready_for_future_non_ui_export_runner"
        assert packet["export_runner_packet"]["runner_state"] == "latest_payload_export_runner_exported"
        stdout = format_prediction_warroom_latest_payload_actual_export_runner_stdout_summary(packet)
        assert "latest_payload_actual_export_runner=prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1" in stdout
        assert "state=latest_payload_actual_export_runner_exported" in stdout
        assert "target_file_written=True" in stdout
        assert "ui=false;runtime_write=true;prediction_build=true;export=true;approval=false;ledger=false;autotrade=false;broker=false" in stdout
        _assert_no_trade_or_ui_side_effects(packet)


def test_ps_q10h_rejects_ui_or_approval_broker_requests_before_work() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10h_blocked_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_latest_payload_actual_export_runner(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_latest_payload_export=True,
            allow_runtime_artifact_write=True,
            allow_guard_test_root=True,
            requested_warroom_ui_trigger=True,
            requested_approval_or_ledger_or_autotrade_or_broker=True,
        ).to_dict()
        assert packet["runner_state"] == "latest_payload_actual_export_runner_blocked"
        assert "warroom_ui_trigger_not_allowed_by_actual_export_runner" in packet["blocked_reasons"]
        assert "approval_ledger_autotrade_broker_not_allowed_by_actual_export_runner" in packet["blocked_reasons"]
        assert packet["preflight_bridge_packet"] == {}
        assert packet["export_runner_packet"] == {}
        assert not (root / "prediction" / "latest_prediction_system_result.json").exists()
        _assert_no_trade_or_ui_side_effects(packet)


def main() -> int:
    test_ps_q10h_static_boundaries_and_markers()
    test_ps_q10h_not_mounted_in_warroom_ui()
    test_ps_q10h_default_blocks_before_work()
    test_ps_q10h_guard_root_exports_exactly_latest_payload_json_via_ps_q9y()
    test_ps_q10h_rejects_ui_or_approval_broker_requests_before_work()
    print("[OK] Prediction System PS-Q10H latest payload actual export runner guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
