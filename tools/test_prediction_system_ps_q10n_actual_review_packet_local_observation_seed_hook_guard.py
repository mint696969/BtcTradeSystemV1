# path: ./tools/test_prediction_system_ps_q10n_actual_review_packet_local_observation_seed_hook_guard.py
# desc: Focused guard for PS-Q10N actual review-packet local/session seed hook.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_local_observation_seed_hook import (
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ENABLE_KEY,
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_MODE_KEY,
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION,
    build_prediction_warroom_actual_review_packet_local_observation_seed_hook,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import resolve_prediction_warroom_lowered_display_packet_visibility_review_source
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_local_observation_seed_hook.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SYNTHETIC_HOOK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_local_observation_hook.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "pathlib",
    "json",
    "subprocess",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "btcts.collector_vnext",
    "btcts.autotrade",
)
FORBIDDEN_MODULE_TOKENS = (
    "import streamlit",
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
    "subprocess",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "build_prediction_warroom_actual_read_operator_runner_scaffold(",
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "load_prediction_warroom_latest_payload_read_only(",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_loader_execution: bool = True",
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


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _actual_like_display_packet(*, synthetic: bool = False) -> dict:
    payload = build_prediction_warroom_sample_display_packet()
    run_id = "synthetic_actual_seed_hook_run" if synthetic else "actual_seed_hook_run_20260621T000000Z"
    payload["prediction_run_id"] = run_id
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:" + run_id
    payload["headline_ja"] = "Actual seed hook: 短期は上方向優勢、参考度59%。"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["boundaries"] = dict(payload["boundaries"])
    if synthetic:
        payload["primary_signal_summary"]["synthetic_only"] = True
        payload["boundaries"]["synthetic_only"] = True
        payload["synthetic_only"] = True
    else:
        payload["primary_signal_summary"].pop("synthetic_only", None)
        payload["primary_signal_summary"].pop("fixture_only", None)
        payload["boundaries"].pop("synthetic_only", None)
        payload["boundaries"].pop("fixture_only", None)
        payload.pop("synthetic_only", None)
        payload.pop("fixture_only", None)
    return payload


def _review_packet(*, synthetic: bool = False) -> dict:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=_actual_like_display_packet(synthetic=synthetic),
    ).to_dict()
    review = build_prediction_warroom_lowered_display_packet_visibility_review_contract(
        lowering_result=lowering,
    ).to_dict()
    assert review["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert review["widget_group_count"] == 6
    return review


def _assert_no_side_effect_flags(packet: dict) -> None:
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


def test_ps_q10n_static_boundaries_and_not_mounted() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    assert ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION == "prediction_warroom_actual_review_packet_local_observation_seed_hook.ps_q10n.v1"
    assert "default_passive_no_mutation" in text
    assert "call_ps_q10k_harness_only_when_enabled" in text
    assert "do_not_run_loader_from_ui" in text
    assert "do_not_read_runtime_file" in text
    assert "do_not_decode_payload" in text
    assert "do_not_write_runtime_artifact" in text
    assert "do_not_trigger_autotrade_or_broker" in text
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    synthetic_hook_text = SYNTHETIC_HOOK.read_text(encoding="utf-8")
    assert "prediction_warroom_actual_review_packet_local_observation_seed_hook" not in page_text
    assert "prediction_warroom_actual_review_packet_local_observation_seed_hook" not in synthetic_hook_text


def test_ps_q10n_default_passive_does_not_mutate_empty_session() -> None:
    state: dict[str, object] = {}
    packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(session_state=state).to_dict()
    assert packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_passive_waiting_for_review_packet"
    assert packet["actual_seed_requested"] is False
    assert packet["actual_seed_enabled"] is False
    assert packet["session_state_updated"] is False
    assert packet["source_handoff_ready"] is False
    assert "actual_review_packet_seed_hook_passive_no_seed_requested" in packet["warning_reasons"]
    assert state == {}
    _assert_no_side_effect_flags(packet)


def test_ps_q10n_requires_mode_and_review_packet_for_seed() -> None:
    state: dict[str, object] = {}
    packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        session_state=state,
        enable_actual_review_packet_seed=True,
    ).to_dict()
    assert packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_blocked"
    assert "actual_local_observation_mode_not_allowed" in packet["blocked_reasons"]
    assert "actual_review_packet_mapping_required" in packet["blocked_reasons"]
    assert packet["session_state_updated"] is False
    assert state == {}
    _assert_no_side_effect_flags(packet)


def test_ps_q10n_accepts_explicit_actual_review_packet_and_verifies_q9h() -> None:
    state: dict[str, object] = {}
    packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        review_packet=_review_packet(),
        session_state=state,
        enable_actual_review_packet_seed=True,
        local_observation_mode=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ).to_dict()
    assert packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_actual_packet_installed"
    assert packet["actual_seed_requested"] is True
    assert packet["actual_seed_enabled"] is True
    assert packet["actual_review_packet_present"] is True
    assert packet["actual_review_packet_ready"] is True
    assert packet["synthetic_review_packet_detected"] is False
    assert packet["fixture_review_packet_detected"] is False
    assert packet["session_state_updated"] is True
    assert packet["source_handoff_ready"] is True
    assert packet["blocker_count"] == 0
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in state
    resolved = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(session_state=state).to_dict()
    assert resolved["handoff_state"] == "review_source_handoff_ready"
    assert resolved["source_kind"] == "session_state_in_memory_mapping"
    assert resolved["fallback_used"] is False
    assert resolved["review_packet_ready"] is True
    _assert_no_side_effect_flags(packet)


def test_ps_q10n_accepts_state_flag_enable_but_still_requires_allowed_mode() -> None:
    state: dict[str, object] = {
        ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ENABLE_KEY: True,
        ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_MODE_KEY: ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    }
    packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        review_packet=_review_packet(),
        session_state=state,
    ).to_dict()
    assert packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_actual_packet_installed"
    assert packet["mode"] == ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE
    assert packet["session_state_updated"] is True
    assert packet["source_handoff_ready"] is True
    _assert_no_side_effect_flags(packet)


def test_ps_q10n_rejects_synthetic_review_packet() -> None:
    state: dict[str, object] = {}
    packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        review_packet=_review_packet(synthetic=True),
        session_state=state,
        enable_actual_review_packet_seed=True,
        local_observation_mode=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ).to_dict()
    assert packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_blocked"
    assert packet["session_state_updated"] is False
    assert packet["source_handoff_ready"] is False
    assert "actual_review_packet_required_but_synthetic_detected" in packet["blocked_reasons"]
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY not in state
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q10n_static_boundaries_and_not_mounted()
    test_ps_q10n_default_passive_does_not_mutate_empty_session()
    test_ps_q10n_requires_mode_and_review_packet_for_seed()
    test_ps_q10n_accepts_explicit_actual_review_packet_and_verifies_q9h()
    test_ps_q10n_accepts_state_flag_enable_but_still_requires_allowed_mode()
    test_ps_q10n_rejects_synthetic_review_packet()
    print("[OK] Prediction System PS-Q10N actual review-packet local observation seed hook guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
