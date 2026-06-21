# path: ./tools/test_prediction_system_ps_q9h_lowered_display_packet_review_source_handoff_guard.py
# desc: Focused guard for PS-Q9H lowered display-packet review source handoff.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
    SESSION_REVIEW_PACKET_KEYS,
    SOURCE_HANDOFF_SEQUENCE,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_source_handoff.py"
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
    "load_prediction",
    "latest_payload",
    "hot_latest",
    "build_prediction_system_result",
    "assess_source_quality",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "st.button",
    "st.form",
    "persist=True",
    "ui_triggered_loader_execution: bool = True",
    "would_load_source_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_decode_payload: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
EXPECTED_SEQUENCE = [
    "prefer_explicit_in_memory_review_packet",
    "scan_session_state_candidate_keys_read_only",
    "validate_review_packet_contract_shape",
    "fallback_to_blocked_review_contract_when_missing_or_invalid",
    "return_source_handoff_packet_only",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
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


def _review_packet() -> dict:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=build_prediction_warroom_sample_display_packet()
    ).to_dict()
    return build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=lowering).to_dict()


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["source_handoff_only"] is True
    assert packet["in_memory_input_only"] is True
    for key in (
        "streamlit_import_required",
        "ui_triggered_loader_execution",
        "would_load_source_artifacts",
        "would_read_runtime_file",
        "would_decode_payload",
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


def test_ps_q9h_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_lowered_display_packet_review_source_handoff.ps_q9h.v1" in text
    assert "resolve_prediction_warroom_lowered_display_packet_visibility_review_source" in text
    assert list(SOURCE_HANDOFF_SEQUENCE) == EXPECTED_SEQUENCE
    assert SESSION_REVIEW_PACKET_KEYS == (
        "warroom_prediction_lowered_display_packet_visibility_review_packet",
        "prediction_warroom_lowered_display_packet_visibility_review_packet",
        "warroom_prediction_ps_q9f_review_packet",
    )


def test_ps_q9h_missing_source_falls_back_to_blocked_contract() -> None:
    packet = resolve_prediction_warroom_lowered_display_packet_visibility_review_source().to_dict()
    assert packet["handoff_version"] == LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION
    assert packet["handoff_state"] == "review_source_handoff_fallback_blocked"
    assert packet["source_kind"] == "blocked_fallback_contract"
    assert packet["fallback_used"] is True
    assert packet["review_packet"]["contract_state"] == "blocked_visibility_review_contract"
    assert "review_packet_not_supplied_using_blocked_fallback" in packet["warning_reasons"]
    _assert_safe(packet)


def test_ps_q9h_accepts_explicit_in_memory_review_packet() -> None:
    source = _review_packet()
    packet = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(explicit_review_packet=source).to_dict()
    assert packet["handoff_state"] == "review_source_handoff_ready"
    assert packet["source_kind"] == "explicit_in_memory_argument"
    assert packet["fallback_used"] is False
    assert packet["review_packet_contract_version_valid"] is True
    assert packet["review_packet_ready"] is True
    assert packet["review_packet"]["contract_version"] == source["contract_version"]
    _assert_safe(packet)


def test_ps_q9h_accepts_session_state_review_packet_candidate() -> None:
    source = _review_packet()
    packet = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        session_state={"warroom_prediction_ps_q9f_review_packet": source}
    ).to_dict()
    assert packet["handoff_state"] == "review_source_handoff_ready"
    assert packet["source_kind"] == "session_state_in_memory_mapping"
    assert packet["matched_key"] == "warroom_prediction_ps_q9f_review_packet"
    assert packet["review_packet_ready"] is True
    _assert_safe(packet)


def test_ps_q9h_invalid_review_packet_falls_back_without_runtime_access() -> None:
    packet = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        explicit_review_packet={"contract_version": "wrong"}
    ).to_dict()
    assert packet["handoff_state"] == "review_source_handoff_fallback_blocked"
    assert packet["fallback_used"] is True
    assert "invalid_review_packet_using_blocked_fallback" in packet["warning_reasons"]
    assert "review_packet_contract_version_invalid" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9h_panel_uses_source_handoff_bridge() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "resolve_prediction_warroom_lowered_display_packet_visibility_review_source" in text
    assert "session_state=st.session_state" in text
    assert "source_handoff=" in text
    assert "source_kind=" in text
    assert "fallback=" in text
    assert "review_packet_not_supplied_using_blocked_fallback" not in text


def main() -> int:
    test_ps_q9h_static_boundaries_and_markers()
    test_ps_q9h_missing_source_falls_back_to_blocked_contract()
    test_ps_q9h_accepts_explicit_in_memory_review_packet()
    test_ps_q9h_accepts_session_state_review_packet_candidate()
    test_ps_q9h_invalid_review_packet_falls_back_without_runtime_access()
    test_ps_q9h_panel_uses_source_handoff_bridge()
    print("[OK] Prediction System PS-Q9H lowered display-packet review source handoff guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
