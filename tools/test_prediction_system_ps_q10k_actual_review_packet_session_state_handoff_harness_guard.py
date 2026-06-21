# path: ./tools/test_prediction_system_ps_q10k_actual_review_packet_session_state_handoff_harness_guard.py
# desc: Focused guard for PS-Q10K supplied-actual review-packet session-state handoff harness.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import (
    ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
    ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_SEQUENCE,
    DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
    build_prediction_warroom_actual_review_packet_session_state_handoff_harness,
)
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import SESSION_REVIEW_PACKET_KEYS, resolve_prediction_warroom_lowered_display_packet_visibility_review_source
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_session_state_handoff_harness.py"
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
    "load_prediction",
    "latest_payload",
    "hot_latest",
    "allow_actual_read=True",
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
    "consume_supplied_actual_q9f_review_packet_mapping_only",
    "validate_review_packet_contract_shape_with_q9h",
    "reject_missing_invalid_or_not_ready_review_packet",
    "reject_synthetic_or_fixture_review_packet",
    "optionally_store_review_packet_in_provided_mapping",
    "verify_stored_packet_with_q9h_source_handoff",
    "return_handoff_harness_packet_only",
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


def _real_like_display_packet() -> dict:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "actual_prediction_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:actual_prediction_run_20260621T000000Z"
    payload["headline_ja"] = "Actual-like: 短期は上方向優勢、参考度59%。"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["primary_signal_summary"].pop("fixture_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    payload.pop("synthetic_only", None)
    payload.pop("fixture_only", None)
    return payload


def _review_packet(payload: dict | None = None) -> dict:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=payload or _real_like_display_packet(),
    ).to_dict()
    return build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=lowering).to_dict()


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["actual_review_packet_handoff_only"] is True
    assert packet["session_state_handoff_only"] is True
    assert packet["in_memory_input_only"] is True
    assert packet["display_only"] is True
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


def test_ps_q10k_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_review_packet_session_state_handoff_harness.ps_q10k.v1" in text
    assert "build_prediction_warroom_actual_review_packet_session_state_handoff_harness" in text
    assert list(ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION == "prediction_warroom_actual_review_packet_session_state_handoff_harness.ps_q10k.v1"
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY == SESSION_REVIEW_PACKET_KEYS[0]


def test_ps_q10k_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_review_packet_session_state_handoff_harness"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q10k_missing_review_packet_fails_closed() -> None:
    packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness().to_dict()
    assert packet["harness_state"] == "actual_review_packet_session_state_handoff_blocked"
    assert "actual_review_packet_mapping_required" in packet["blocked_reasons"]
    assert packet["session_state_updated"] is False
    _assert_safe(packet)


def test_ps_q10k_accepts_ready_actual_review_packet_without_mutating_mapping() -> None:
    state: dict = {}
    packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_review_packet(),
        session_state=state,
    ).to_dict()
    assert packet["harness_state"] == "actual_review_packet_session_state_handoff_ready"
    assert packet["review_packet_contract_version_valid"] is True
    assert packet["review_packet_ready"] is True
    assert packet["synthetic_review_packet_detected"] is False
    assert packet["fixture_review_packet_detected"] is False
    assert packet["session_state_updated"] is False
    assert "session_state_mapping_supplied_but_store_disabled" in packet["warning_reasons"]
    assert state == {}
    _assert_safe(packet)


def test_ps_q10k_can_store_ready_actual_review_packet_in_allowed_session_key() -> None:
    state: dict = {}
    packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_review_packet(),
        session_state=state,
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "actual_review_packet_session_state_handoff_ready"
    assert packet["target_session_key"] == DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
    assert packet["session_state_updated"] is True
    assert packet["source_handoff_ready"] is True
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in state
    handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(session_state=state).to_dict()
    assert handoff["handoff_state"] == "review_source_handoff_ready"
    assert handoff["matched_key"] == DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
    assert handoff["review_packet_ready"] is True
    _assert_safe(packet)


def test_ps_q10k_rejects_synthetic_or_fixture_review_packet() -> None:
    packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_review_packet(build_prediction_warroom_sample_display_packet()),
        session_state={},
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "actual_review_packet_session_state_handoff_blocked"
    assert packet["session_state_updated"] is False
    assert "actual_review_packet_required_but_synthetic_detected" in packet["blocked_reasons"]
    assert packet["synthetic_review_packet_detected"] is True
    _assert_safe(packet)


def test_ps_q10k_rejects_invalid_target_session_key_without_mutation() -> None:
    state: dict = {}
    packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_review_packet(),
        session_state=state,
        target_session_key="not_allowed",
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "actual_review_packet_session_state_handoff_blocked"
    assert packet["session_state_updated"] is False
    assert "target_session_key_not_allowed" in packet["blocked_reasons"]
    assert state == {}
    _assert_safe(packet)


def test_ps_q10k_store_requires_session_mapping() -> None:
    packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_review_packet(),
        store_in_session_state=True,
    ).to_dict()
    assert packet["harness_state"] == "actual_review_packet_session_state_handoff_blocked"
    assert packet["session_state_updated"] is False
    assert "session_state_mapping_not_supplied" in packet["blocked_reasons"]
    _assert_safe(packet)


def main() -> int:
    test_ps_q10k_static_boundaries_and_markers()
    test_ps_q10k_does_not_mutate_warroom_page_or_panel()
    test_ps_q10k_missing_review_packet_fails_closed()
    test_ps_q10k_accepts_ready_actual_review_packet_without_mutating_mapping()
    test_ps_q10k_can_store_ready_actual_review_packet_in_allowed_session_key()
    test_ps_q10k_rejects_synthetic_or_fixture_review_packet()
    test_ps_q10k_rejects_invalid_target_session_key_without_mutation()
    test_ps_q10k_store_requires_session_mapping()
    print("[OK] Prediction System PS-Q10K actual review-packet session-state handoff harness guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
