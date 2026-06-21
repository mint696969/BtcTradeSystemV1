# path: ./tools/test_prediction_system_ps_q9i_synthetic_review_packet_session_state_harness_guard.py
# desc: Focused guard for PS-Q9I synthetic review-packet session-state harness.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import SESSION_REVIEW_PACKET_KEYS, resolve_prediction_warroom_lowered_display_packet_visibility_review_source
from btcts.apps.operator_ui.components.prediction_warroom_synthetic_review_packet_session_state_harness import (
    DEFAULT_SESSION_REVIEW_PACKET_KEY,
    HARNESS_SEQUENCE,
    SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION,
    build_prediction_warroom_synthetic_lowered_display_packet_review_packet,
    build_prediction_warroom_synthetic_review_packet_session_state_harness,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_synthetic_review_packet_session_state_harness.py"
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
    "streamlit_import_required: bool = True",
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
    "build_synthetic_display_packet_fixture_in_memory",
    "lower_fixture_with_ps_q9e_adapter_in_memory",
    "build_ps_q9f_visibility_review_packet_in_memory",
    "optionally_store_review_packet_in_provided_mapping",
    "verify_with_ps_q9h_source_handoff",
    "return_harness_packet_only",
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


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["synthetic_only"] is True
    assert packet["session_state_harness_only"] is True
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


def test_ps_q9i_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_synthetic_review_packet_session_state_harness.ps_q9i.v1" in text
    assert "build_prediction_warroom_synthetic_review_packet_session_state_harness" in text
    assert "build_prediction_warroom_synthetic_lowered_display_packet_review_packet" in text
    assert list(HARNESS_SEQUENCE) == EXPECTED_SEQUENCE
    assert DEFAULT_SESSION_REVIEW_PACKET_KEY == SESSION_REVIEW_PACKET_KEYS[0]


def test_ps_q9i_builds_ready_synthetic_review_packet() -> None:
    packet = build_prediction_warroom_synthetic_lowered_display_packet_review_packet()
    assert packet["contract_version"] == "prediction_warroom_lowered_display_packet_visibility_review_contract.ps_q9f.v1"
    assert packet["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert packet["widget_group_index_built"] is True
    assert packet["widget_group_count"] == 6
    assert packet["visible_widget_group_count"] == 6


def test_ps_q9i_default_harness_builds_without_session_mutation() -> None:
    packet = build_prediction_warroom_synthetic_review_packet_session_state_harness().to_dict()
    assert packet["harness_version"] == SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION
    assert packet["harness_state"] == "synthetic_review_packet_session_state_ready"
    assert packet["review_packet_built"] is True
    assert packet["review_packet_ready"] is True
    assert packet["session_state_updated"] is False
    assert packet["source_handoff_ready"] is True
    assert packet["warning_reasons"] == []
    _assert_safe(packet)


def test_ps_q9i_can_store_review_packet_in_provided_mapping() -> None:
    state: dict = {}
    packet = build_prediction_warroom_synthetic_review_packet_session_state_harness(
        session_state=state,
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "synthetic_review_packet_session_state_ready"
    assert packet["target_session_key"] == DEFAULT_SESSION_REVIEW_PACKET_KEY
    assert packet["session_state_updated"] is True
    assert DEFAULT_SESSION_REVIEW_PACKET_KEY in state
    assert state[DEFAULT_SESSION_REVIEW_PACKET_KEY]["ready_for_ps_q9g_guarded_ui_mount"] is True
    handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(session_state=state).to_dict()
    assert handoff["handoff_state"] == "review_source_handoff_ready"
    assert handoff["matched_key"] == DEFAULT_SESSION_REVIEW_PACKET_KEY
    _assert_safe(packet)


def test_ps_q9i_rejects_unknown_target_session_key() -> None:
    state: dict = {}
    packet = build_prediction_warroom_synthetic_review_packet_session_state_harness(
        session_state=state,
        target_session_key="not_allowed",
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "synthetic_review_packet_session_state_blocked"
    assert packet["session_state_updated"] is False
    assert "target_session_key_not_allowed" in packet["blocked_reasons"]
    assert state == {}
    _assert_safe(packet)


def test_ps_q9i_store_requires_mapping_when_enabled() -> None:
    packet = build_prediction_warroom_synthetic_review_packet_session_state_harness(
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "synthetic_review_packet_session_state_blocked"
    assert packet["session_state_updated"] is False
    assert "session_state_mapping_not_supplied" in packet["blocked_reasons"]
    _assert_safe(packet)


def main() -> int:
    test_ps_q9i_static_boundaries_and_markers()
    test_ps_q9i_builds_ready_synthetic_review_packet()
    test_ps_q9i_default_harness_builds_without_session_mutation()
    test_ps_q9i_can_store_review_packet_in_provided_mapping()
    test_ps_q9i_rejects_unknown_target_session_key()
    test_ps_q9i_store_requires_mapping_when_enabled()
    print("[OK] Prediction System PS-Q9I synthetic review-packet session-state harness guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
