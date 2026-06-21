# path: ./tools/test_prediction_system_ps_q10d_prediction_system_result_builder_runner_guard.py
# desc: Focused guard for PS-Q10D PredictionSystemResult builder runner.

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (
    PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION,
    build_prediction_warroom_prediction_system_result_builder_runner,
    format_prediction_warroom_prediction_system_result_builder_runner_stdout_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py"
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
    "aggregate_ohlcv_from_rows(",
    "build_prediction_warroom_latest_payload_export_runner(",
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


def _assert_safe(packet: dict, *, built_allowed: bool) -> None:
    assert packet["read_only"] is True
    assert packet["non_ui_runner_only"] is True
    assert packet["bounded_hot_read_via_source_mapping_runner_only"] is True
    assert packet["prediction_system_result_built_by_this_runner"] is built_allowed
    for key in (
        "ready_for_latest_payload_export",
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


def test_ps_q10d_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "btcts.prediction.system" in imports
    assert "build_prediction_system_result" in text
    assert PREDICTION_SYSTEM_RESULT_BUILDER_RUNNER_VERSION == "prediction_warroom_prediction_system_result_builder_runner.ps_q10d.v1"
    assert "do_not_export_latest_prediction_artifact" in text


def test_ps_q10d_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_prediction_system_result_builder_runner" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q10d_default_blocks_before_read_or_build() -> None:
    packet = build_prediction_warroom_prediction_system_result_builder_runner().to_dict()
    assert packet["runner_state"] == "prediction_system_result_builder_runner_blocked"
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "allow_actual_read_false" in packet["blocked_reasons"]
    assert "allow_prediction_build_false" in packet["blocked_reasons"]
    assert packet["prediction_result_payload_present"] is False
    _assert_safe(packet, built_allowed=False)


def test_ps_q10d_guard_root_builds_prediction_result_in_memory_only() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10d_ready_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_prediction_system_result_builder_runner(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_guard_test_root=True,
        ).to_dict()
        assert packet["runner_state"] == "prediction_system_result_builder_runner_built"
        assert packet["prediction_result_payload_present"] is True
        assert packet["prediction_run_id"]
        assert packet["market_uid"]
        assert packet["output_count"] > 0
        assert packet["scenario_core_present"] is True
        assert packet["usable"] is True
        assert packet["prediction_result_blocker_count"] == 0
        assert packet["ready_for_future_latest_payload_export_preflight"] is True
        assert packet["ready_for_latest_payload_export"] is False
        payload = packet["prediction_result_payload"]
        for key in ("run_identity", "system_input", "outputs", "scenario_core", "gpt_review_digest"):
            assert key in payload
        assert payload["read_only"] is True
        assert payload["non_executing"] is True
        assert payload["would_send_to_broker"] is False
        stdout = format_prediction_warroom_prediction_system_result_builder_runner_stdout_summary(packet)
        assert "prediction_system_result_builder_runner=prediction_warroom_prediction_system_result_builder_runner.ps_q10d.v1" in stdout
        assert "state=prediction_system_result_builder_runner_built" in stdout
        assert "ready_for_future_latest_payload_export_preflight=True" in stdout
        assert "ready_for_latest_payload_export=False" in stdout
        assert "ui=false;runtime_write=false;prediction_build=true;export=false;approval=false;ledger=false;autotrade=false;broker=false" in stdout
        _assert_safe(packet, built_allowed=True)


def test_ps_q10d_rejects_forbidden_export_and_runtime_requests() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q10d_blocked_") as raw_root:
        root = Path(raw_root)
        _sample_root(root)
        packet = build_prediction_warroom_prediction_system_result_builder_runner(
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_guard_test_root=True,
            requested_latest_payload_export=True,
            requested_runtime_write=True,
            requested_warroom_ui_trigger=True,
            requested_approval_or_ledger_or_autotrade_or_broker=True,
        ).to_dict()
        assert packet["runner_state"] == "prediction_system_result_builder_runner_blocked"
        assert "latest_payload_export_not_allowed_by_builder_runner" in packet["blocked_reasons"]
        assert "runtime_write_not_allowed_by_builder_runner" in packet["blocked_reasons"]
        assert "warroom_ui_trigger_not_allowed_by_builder_runner" in packet["blocked_reasons"]
        assert "approval_ledger_autotrade_broker_not_allowed_by_builder_runner" in packet["blocked_reasons"]
        assert packet["prediction_result_payload_present"] is False
        _assert_safe(packet, built_allowed=False)


def main() -> int:
    test_ps_q10d_static_boundaries_and_markers()
    test_ps_q10d_not_mounted_in_warroom_ui()
    test_ps_q10d_default_blocks_before_read_or_build()
    test_ps_q10d_guard_root_builds_prediction_result_in_memory_only()
    test_ps_q10d_rejects_forbidden_export_and_runtime_requests()
    print("[OK] Prediction System PS-Q10D PredictionSystemResult builder runner guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
