# path: ./tools/test_prediction_system_ps_q9j_guarded_local_observation_hook_guard.py
# desc: Focused guard for PS-Q9J guarded local WarRoom observation hook.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_local_observation_hook import (
    LOCAL_OBSERVATION_ALLOWED_MODE,
    LOCAL_OBSERVATION_ENABLE_KEY,
    LOCAL_OBSERVATION_HOOK_VERSION,
    LOCAL_OBSERVATION_MODE_KEY,
    LOCAL_OBSERVATION_SEQUENCE,
    build_prediction_warroom_local_observation_hook,
)
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import SESSION_REVIEW_PACKET_KEYS

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_local_observation_hook.py"
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
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
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
    "default_passive_no_mutation",
    "read_existing_in_memory_review_packet_via_ps_q9h",
    "require_explicit_enable_for_synthetic_injection",
    "require_allowed_local_observation_mode",
    "call_ps_q9i_harness_only_when_enabled",
    "store_only_under_ps_q9h_allowed_candidate_key",
    "verify_with_ps_q9h_source_handoff",
    "return_hook_packet_only",
    "do_not_add_ui_controls",
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
    assert packet["local_observation_hook_only"] is True
    assert packet["in_memory_input_only"] is True
    for key in (
        "streamlit_import_required",
        "ui_controls_added",
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


def test_ps_q9j_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_local_observation_hook.ps_q9j.v1" in text
    assert "build_prediction_warroom_local_observation_hook" in text
    assert list(LOCAL_OBSERVATION_SEQUENCE) == EXPECTED_SEQUENCE
    assert LOCAL_OBSERVATION_ENABLE_KEY == "warroom_prediction_local_synthetic_review_enabled"
    assert LOCAL_OBSERVATION_MODE_KEY == "warroom_prediction_local_observation_mode"
    assert LOCAL_OBSERVATION_ALLOWED_MODE == "synthetic_review_packet_only"


def test_ps_q9j_does_not_mutate_warroom_page() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert "prediction_warroom_local_observation_hook" not in text
    assert "warroom_prediction_local_synthetic_review_enabled" not in text


def test_ps_q9j_default_is_passive_and_does_not_install_packet() -> None:
    state: dict = {}
    packet = build_prediction_warroom_local_observation_hook(session_state=state).to_dict()
    assert packet["hook_state"] == "local_observation_hook_passive_waiting_for_review_packet"
    assert packet["synthetic_injection_requested"] is False
    assert packet["synthetic_injection_enabled"] is False
    assert packet["session_state_updated"] is False
    assert state == {}
    assert "local_observation_hook_passive_no_synthetic_injection_requested" in packet["warning_reasons"]
    _assert_safe(packet)


def test_ps_q9j_explicit_enable_requires_allowed_mode() -> None:
    state: dict = {}
    packet = build_prediction_warroom_local_observation_hook(
        session_state=state,
        enable_synthetic_review_packet=True,
    ).to_dict()
    assert packet["hook_state"] == "local_observation_hook_blocked"
    assert packet["session_state_updated"] is False
    assert "local_observation_mode_not_allowed" in packet["blocked_reasons"]
    assert state == {}
    _assert_safe(packet)


def test_ps_q9j_installs_synthetic_packet_only_when_explicitly_enabled_and_mode_allowed() -> None:
    state: dict = {}
    packet = build_prediction_warroom_local_observation_hook(
        session_state=state,
        enable_synthetic_review_packet=True,
        local_observation_mode=LOCAL_OBSERVATION_ALLOWED_MODE,
    ).to_dict()
    assert packet["hook_state"] == "local_observation_hook_synthetic_ready_packet_installed"
    assert packet["synthetic_injection_requested"] is True
    assert packet["synthetic_injection_enabled"] is True
    assert packet["session_state_updated"] is True
    assert packet["source_handoff_ready"] is True
    assert packet["target_session_key"] == SESSION_REVIEW_PACKET_KEYS[0]
    assert SESSION_REVIEW_PACKET_KEYS[0] in state
    assert state[SESSION_REVIEW_PACKET_KEYS[0]]["ready_for_ps_q9g_guarded_ui_mount"] is True
    _assert_safe(packet)


def test_ps_q9j_can_use_enable_and_mode_from_existing_mapping() -> None:
    state: dict = {
        LOCAL_OBSERVATION_ENABLE_KEY: True,
        LOCAL_OBSERVATION_MODE_KEY: LOCAL_OBSERVATION_ALLOWED_MODE,
    }
    packet = build_prediction_warroom_local_observation_hook(session_state=state).to_dict()
    assert packet["hook_state"] == "local_observation_hook_synthetic_ready_packet_installed"
    assert packet["mode"] == LOCAL_OBSERVATION_ALLOWED_MODE
    assert packet["session_state_updated"] is True
    assert SESSION_REVIEW_PACKET_KEYS[0] in state
    _assert_safe(packet)


def test_ps_q9j_rejects_unknown_target_session_key_without_mutation() -> None:
    state: dict = {}
    packet = build_prediction_warroom_local_observation_hook(
        session_state=state,
        enable_synthetic_review_packet=True,
        local_observation_mode=LOCAL_OBSERVATION_ALLOWED_MODE,
        target_session_key="not_allowed",
    ).to_dict()
    assert packet["hook_state"] == "local_observation_hook_blocked"
    assert packet["session_state_updated"] is False
    assert "target_session_key_not_allowed" in packet["blocked_reasons"]
    assert state == {}
    _assert_safe(packet)


def main() -> int:
    test_ps_q9j_static_boundaries_and_markers()
    test_ps_q9j_does_not_mutate_warroom_page()
    test_ps_q9j_default_is_passive_and_does_not_install_packet()
    test_ps_q9j_explicit_enable_requires_allowed_mode()
    test_ps_q9j_installs_synthetic_packet_only_when_explicitly_enabled_and_mode_allowed()
    test_ps_q9j_can_use_enable_and_mode_from_existing_mapping()
    test_ps_q9j_rejects_unknown_target_session_key_without_mutation()
    print("[OK] Prediction System PS-Q9J guarded local observation hook guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
