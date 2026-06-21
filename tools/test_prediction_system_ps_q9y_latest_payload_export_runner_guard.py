# path: ./tools/test_prediction_system_ps_q9y_latest_payload_export_runner_guard.py
# desc: Focused guard for PS-Q9Y non-UI latest payload export runner.

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_export_runner import (
    LATEST_PAYLOAD_EXPORT_RUNNER_VERSION,
    build_prediction_warroom_latest_payload_export_runner,
    format_prediction_warroom_latest_payload_export_runner_stdout_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_runner.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
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
    "build_prediction_warroom_display_packet(",
    "load_prediction_warroom_latest_payload_read_only(",
    "read_text(",
    "read_bytes(",
    "json.load",
    "json.loads",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "persist=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "prediction_system_result_built_by_this_runner: bool = True",
    "hot_file_read_performed_by_this_runner: bool = True",
    "payload_decode_performed_by_this_runner: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_export_execution: bool = True",
    "approval_or_authorization_allowed: bool = True",
    "ledger_append_allowed: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "would_collect_public_source: bool = True",
    "would_write_collector_state: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
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


def _sample_result() -> dict:
    return {
        "run_identity": {
            "prediction_run_id": "real_candidate_run_1",
            "generated_at": "2026-06-21T00:00:00Z",
            "market_uid": "BTC_JPY:bitFlyer",
        },
        "system_input": {"market_uid": "BTC_JPY:bitFlyer"},
        "outputs": [],
        "scenario_core": {"scenario_id": "scenario-1"},
        "gpt_review_digest": {"signal_strength_summary": {"estimated_signal_strength_percent": 0}},
        "read_only": True,
        "non_executing": True,
    }


def _assert_no_trade_or_ui_side_effects(packet: dict) -> None:
    for key in (
        "prediction_system_result_built_by_this_runner",
        "hot_file_read_performed_by_this_runner",
        "payload_decode_performed_by_this_runner",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_export_execution",
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


def test_ps_q9y_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_export_runner.ps_q9y.v1" in text
    assert "write_exactly_latest_prediction_system_result_json" in text
    assert "do_not_build_prediction_system_result" in text
    assert "do_not_read_hot_files" in text


def test_ps_q9y_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_latest_payload_export_runner" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q9y_default_blocks_and_writes_nothing() -> None:
    packet = build_prediction_warroom_latest_payload_export_runner().to_dict()
    assert packet["runner_version"] == LATEST_PAYLOAD_EXPORT_RUNNER_VERSION
    assert packet["runner_state"] == "latest_payload_export_runner_blocked"
    assert "execute_export_false" in packet["blocked_reasons"]
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert packet["target_file_written_by_this_runner"] is False
    assert packet["target_directory_created_by_this_runner"] is False
    _assert_no_trade_or_ui_side_effects(packet)


def test_ps_q9y_rejects_wrong_root_without_guard_test_mode() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9y_wrong_root_") as raw_root:
        packet = build_prediction_warroom_latest_payload_export_runner(
            prediction_result_payload=_sample_result(),
            hot_latest_root_hint=raw_root,
            operator_acknowledged=True,
            execute_export=True,
        ).to_dict()
        assert packet["runner_state"] == "latest_payload_export_runner_blocked"
        assert "target_root_invalid_for_latest_payload_export_runner" in packet["blocked_reasons"]
        assert packet["target_file_written_by_this_runner"] is False
        assert not (Path(raw_root) / "prediction" / "latest_prediction_system_result.json").exists()
        _assert_no_trade_or_ui_side_effects(packet)


def test_ps_q9y_writes_exactly_one_latest_json_in_guard_test_mode() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9y_export_") as raw_root:
        root = Path(raw_root)
        packet = build_prediction_warroom_latest_payload_export_runner(
            prediction_result_payload=_sample_result(),
            hot_latest_root_hint=str(root),
            operator_acknowledged=True,
            execute_export=True,
            allow_guard_test_root=True,
        ).to_dict()
        target = root / "prediction" / "latest_prediction_system_result.json"
        assert packet["runner_state"] == "latest_payload_export_runner_exported"
        assert packet["target_file_written_by_this_runner"] is True
        assert packet["target_artifact_path"] == str(target)
        assert packet["target_file_size_bytes"] and packet["target_file_size_bytes"] > 0
        assert target.exists()
        assert sorted(str(item.relative_to(root)).replace("\\", "/") for item in root.rglob("*") if item.is_file()) == [
            "prediction/latest_prediction_system_result.json"
        ]
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded["run_identity"]["prediction_run_id"] == "real_candidate_run_1"
        assert loaded["read_only"] is True
        assert loaded["non_executing"] is True
        stdout = format_prediction_warroom_latest_payload_export_runner_stdout_summary(packet)
        assert "prediction_latest_payload_export_runner=prediction_warroom_latest_payload_export_runner.ps_q9y.v1" in stdout
        assert "state=latest_payload_export_runner_exported" in stdout
        assert "ui=false;hot_file_read=false;prediction_build=false;approval=false;ledger=false;autotrade=false;broker=false" in stdout
        _assert_no_trade_or_ui_side_effects(packet)


def test_ps_q9y_rejects_incomplete_payload_before_write() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9y_incomplete_") as raw_root:
        packet = build_prediction_warroom_latest_payload_export_runner(
            prediction_result_payload={"run_identity": {"prediction_run_id": "run-only"}},
            hot_latest_root_hint=raw_root,
            operator_acknowledged=True,
            execute_export=True,
            allow_guard_test_root=True,
        ).to_dict()
        assert packet["runner_state"] == "latest_payload_export_runner_blocked"
        assert any(str(item).startswith("prediction_system_result_required_fields_missing:") for item in packet["blocked_reasons"])
        assert packet["target_file_written_by_this_runner"] is False
        assert not (Path(raw_root) / "prediction" / "latest_prediction_system_result.json").exists()
        _assert_no_trade_or_ui_side_effects(packet)


def main() -> int:
    test_ps_q9y_static_boundaries_and_markers()
    test_ps_q9y_not_mounted_in_warroom_ui()
    test_ps_q9y_default_blocks_and_writes_nothing()
    test_ps_q9y_rejects_wrong_root_without_guard_test_mode()
    test_ps_q9y_writes_exactly_one_latest_json_in_guard_test_mode()
    test_ps_q9y_rejects_incomplete_payload_before_write()
    print("[OK] Prediction System PS-Q9Y latest payload export runner guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
