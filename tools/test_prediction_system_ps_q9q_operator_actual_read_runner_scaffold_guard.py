# path: ./tools/test_prediction_system_ps_q9q_operator_actual_read_runner_scaffold_guard.py
# desc: Focused guard for PS-Q9Q non-UI operator actual-read runner scaffold.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_read_operator_runner_scaffold import (
    ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_SEQUENCE,
    ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION,
    build_prediction_warroom_actual_read_operator_runner_scaffold,
    format_prediction_warroom_actual_read_operator_runner_stdout_summary,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_read_only_loader import READ_ONLY_LOADER_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_operator_runner_scaffold.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
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
    "json",
    "pathlib",
)
FORBIDDEN_TOKENS = (
    "open(",
    "Path(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    ".exists(",
    ".stat(",
    "allow_actual_read=True",
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
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_loader_execution: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "runtime_artifact_write_allowed: bool = True",
    "approval_or_authorization_allowed: bool = True",
    "ledger_append_allowed: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
EXPECTED_SEQUENCE = [
    "build_ps_q9p_operator_script_boundary_contract",
    "require_operator_acknowledged_before_actual_read_request",
    "block_when_execute_actual_read_false",
    "use_supplied_loader_result_or_call_q9b_read_only_loader_non_ui",
    "compose_q9o_review_harness_in_memory",
    "format_stdout_only_summary",
    "return_runner_scaffold_packet_only",
    "do_not_render_streamlit",
    "do_not_mutate_warroom_page_or_panel",
    "do_not_write_runtime_artifact",
    "do_not_append_ledger_or_grant_approval",
    "do_not_trigger_autotrade_or_broker",
]


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _real_payload() -> dict:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "real_prediction_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:real_prediction_run_20260621T000000Z"
    payload["headline_ja"] = "Real-like: 短期は上方向優勢、参考度59%。"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    payload.pop("synthetic_only", None)
    payload.pop("fixture_only", None)
    return payload


def _loader_result(payload: dict) -> dict:
    return {
        "loader_version": READ_ONLY_LOADER_VERSION,
        "loader_state": "loaded_read_only_payload_decode_succeeded_schema_validation_deferred",
        "actual_file_read_attempted": True,
        "actual_file_read_succeeded": True,
        "payload_decode_attempted": True,
        "payload_decode_succeeded": True,
        "loaded_payload_count": 1,
        "loaded_payloads": {"prediction_system_result_snapshot": payload},
        "read_only": True,
        "non_executing": True,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing_trade"] is True
    assert packet["non_ui_operator_runner_scaffold_only"] is True
    assert packet["stdout_only"] is True
    assert packet["in_memory_result_only"] is True
    for key in (
        "ready_for_future_top_default_expanded_ux",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "runtime_artifact_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
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


def test_ps_q9q_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_read_operator_runner_scaffold.ps_q9q.v1" in text
    assert "build_prediction_warroom_actual_read_operator_runner_scaffold" in text
    assert "format_prediction_warroom_actual_read_operator_runner_stdout_summary" in text
    assert list(ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION == "prediction_warroom_actual_read_operator_runner_scaffold.ps_q9q.v1"


def test_ps_q9q_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_read_operator_runner_scaffold"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9q_default_is_blocked_without_loader_call() -> None:
    packet = build_prediction_warroom_actual_read_operator_runner_scaffold().to_dict()
    assert packet["runner_state"] == "actual_read_operator_runner_scaffold_blocked"
    assert packet["operator_acknowledged"] is False
    assert packet["execute_actual_read_requested"] is False
    assert packet["q9b_loader_called_by_this_scaffold"] is False
    assert "operator_acknowledgement_required_before_non_ui_runner_scaffold" in packet["blocked_reasons"]
    assert "ps_q9p_boundary_not_ready_no_loader_call" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9q_acknowledged_dry_run_blocks_before_loader_call() -> None:
    packet = build_prediction_warroom_actual_read_operator_runner_scaffold(
        operator_acknowledged=True,
    ).to_dict()
    assert packet["runner_state"] == "actual_read_operator_runner_scaffold_blocked"
    assert packet["q9b_loader_called_by_this_scaffold"] is False
    assert "execute_actual_read_false" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9q_supplied_real_loader_result_composes_ready_without_calling_loader() -> None:
    packet = build_prediction_warroom_actual_read_operator_runner_scaffold(
        operator_acknowledged=True,
        supplied_loader_result=_loader_result(_real_payload()),
    ).to_dict()
    assert packet["runner_state"] == "actual_read_operator_runner_scaffold_ready"
    assert packet["q9b_loader_called_by_this_scaffold"] is False
    assert packet["supplied_loader_result_used"] is True
    assert packet["ready_for_real_payload_review_handoff"] is True
    assert packet["ready_for_future_top_default_expanded_ux"] is False
    assert packet["actual_file_read_attempted"] is True
    assert packet["payload_decode_succeeded"] is True
    assert packet["blocked_reasons"] == []
    summary = format_prediction_warroom_actual_read_operator_runner_stdout_summary(packet)
    assert "state=actual_read_operator_runner_scaffold_ready" in summary
    assert "ui=false" in summary
    _assert_safe(packet)


def test_ps_q9q_supplied_synthetic_loader_result_is_blocked() -> None:
    packet = build_prediction_warroom_actual_read_operator_runner_scaffold(
        operator_acknowledged=True,
        supplied_loader_result=_loader_result(build_prediction_warroom_sample_display_packet()),
    ).to_dict()
    assert packet["runner_state"] == "actual_read_operator_runner_scaffold_blocked"
    assert "real_payload_required_but_synthetic_review_packet_detected" in packet["blocked_reasons"]
    assert packet["ready_for_real_payload_review_handoff"] is False
    _assert_safe(packet)


def test_ps_q9q_wrong_root_blocks_without_loader_call() -> None:
    packet = build_prediction_warroom_actual_read_operator_runner_scaffold(
        operator_acknowledged=True,
        execute_actual_read=True,
        hot_latest_root_hint="E:\\btc_ts",
    ).to_dict()
    assert packet["runner_state"] == "actual_read_operator_runner_scaffold_blocked"
    assert packet["q9b_loader_called_by_this_scaffold"] is False
    assert "hot_latest_root_must_stay_under_D_btc_ts_hot" in packet["blocked_reasons"]
    assert "ps_q9p_boundary_not_ready_no_loader_call" in packet["blocked_reasons"]
    _assert_safe(packet)


def main() -> int:
    test_ps_q9q_static_boundaries_and_markers()
    test_ps_q9q_does_not_mutate_warroom_page_or_panel()
    test_ps_q9q_default_is_blocked_without_loader_call()
    test_ps_q9q_acknowledged_dry_run_blocks_before_loader_call()
    test_ps_q9q_supplied_real_loader_result_composes_ready_without_calling_loader()
    test_ps_q9q_supplied_synthetic_loader_result_is_blocked()
    test_ps_q9q_wrong_root_blocks_without_loader_call()
    print("[OK] Prediction System PS-Q9Q operator actual-read runner scaffold guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
