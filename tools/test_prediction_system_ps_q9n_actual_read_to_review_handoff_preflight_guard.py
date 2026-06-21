# path: ./tools/test_prediction_system_ps_q9n_actual_read_to_review_handoff_preflight_guard.py
# desc: Focused guard for PS-Q9N actual-read-to-review handoff preflight contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_read_to_review_packet_handoff_preflight_contract import (
    ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION,
    ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_SEQUENCE,
    build_prediction_warroom_actual_read_to_review_packet_handoff_preflight,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import (
    ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION,
    build_prediction_warroom_actual_display_packet_lowering_result,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_read_only_loader import READ_ONLY_LOADER_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_loaded_payload_schema_validation_result_panel import LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_synthetic_review_packet_session_state_harness import build_prediction_warroom_synthetic_lowered_display_packet_review_packet
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_to_review_packet_handoff_preflight_contract.py"
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
    "load_prediction_warroom_latest_payload_read_only(",
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
    "consume_supplied_q9b_loader_result_mapping_only",
    "consume_supplied_q9c_validation_panel_mapping_only",
    "consume_supplied_q9e_lowering_result_mapping_only",
    "consume_supplied_q9f_review_packet_mapping_only",
    "verify_q9h_source_handoff_from_explicit_review_packet",
    "require_real_non_synthetic_payload_before_future_top_default_expanded_ux",
    "return_handoff_preflight_packet_only",
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
    assert packet["preflight_contract_only"] is True
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
        "ready_for_future_top_default_expanded_ux",
    ):
        assert packet[key] is False, key


def _loader_result(*, ready: bool = True) -> dict:
    return {
        "loader_version": READ_ONLY_LOADER_VERSION,
        "actual_file_read_succeeded": ready,
        "payload_decode_succeeded": ready,
        "loaded_payload_count": 1 if ready else 0,
        "loaded_payloads": {"prediction_system_result_snapshot": {"prediction_run_id": "real_run_20260621T000000Z"}} if ready else {},
        "read_only": True,
        "non_executing": True,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
        "autotrade_trigger_enabled": False,
    }


def _validation_panel(*, ready: bool = True) -> dict:
    return {
        "panel_version": LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION,
        "panel_state": "schema_validation_panel_valid" if ready else "schema_validation_panel_blocked",
        "blocker_count": 0 if ready else 1,
        "valid_payload_count": 1 if ready else 0,
        "read_only": True,
        "non_executing": True,
        "would_read_runtime_file": False,
        "would_decode_payload": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
        "autotrade_trigger_enabled": False,
    }


def _real_review_packet_bundle() -> tuple[dict, dict]:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "real_prediction_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:real_prediction_run_20260621T000000Z"
    payload["headline_ja"] = "Real-like: 短期は上方向優勢、参考度59%。"
    payload["synthetic_only"] = False
    payload["fixture_only"] = False
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=payload,
        validation_panel=_validation_panel(),
    ).to_dict()
    assert lowering["display_packet_valid"] is True
    review = build_prediction_warroom_lowered_display_packet_visibility_review_contract(
        lowering_result=lowering,
    ).to_dict()
    assert review["ready_for_ps_q9g_guarded_ui_mount"] is True
    return lowering, review


def test_ps_q9n_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_read_to_review_packet_handoff_preflight.ps_q9n.v1" in text
    assert "build_prediction_warroom_actual_read_to_review_packet_handoff_preflight" in text
    assert list(ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION == "prediction_warroom_actual_read_to_review_packet_handoff_preflight.ps_q9n.v1"


def test_ps_q9n_does_not_mutate_warroom_page_or_panel() -> None:
    assert "prediction_warroom_actual_read_to_review_packet_handoff_preflight" not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert "prediction_warroom_actual_read_to_review_packet_handoff_preflight" not in PANEL.read_text(encoding="utf-8")


def test_ps_q9n_missing_inputs_fail_closed() -> None:
    packet = build_prediction_warroom_actual_read_to_review_packet_handoff_preflight().to_dict()
    assert packet["preflight_state"] == "actual_read_to_review_handoff_preflight_blocked"
    assert packet["ready_for_real_payload_review_handoff"] is False
    assert "q9b_loader_result_not_supplied" in packet["blocked_reasons"]
    assert "q9c_validation_panel_not_supplied" in packet["blocked_reasons"]
    assert "q9e_lowering_result_not_supplied" in packet["blocked_reasons"]
    assert "q9f_review_packet_not_supplied" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9n_synthetic_ready_review_packet_is_blocked_for_real_handoff() -> None:
    review = build_prediction_warroom_synthetic_lowered_display_packet_review_packet()
    packet = build_prediction_warroom_actual_read_to_review_packet_handoff_preflight(
        loader_result=_loader_result(),
        validation_panel=_validation_panel(),
        lowering_result={
            "adapter_version": ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION,
            "adapter_state": "display_packet_lowered_and_validated_in_memory",
            "display_packet_valid": True,
            "read_only": True,
            "non_executing": True,
        },
        review_packet=review,
    ).to_dict()
    assert packet["preflight_state"] == "actual_read_to_review_handoff_preflight_blocked"
    assert packet["synthetic_review_packet_detected"] is True
    assert "real_payload_required_but_synthetic_review_packet_detected" in packet["blocked_reasons"]
    assert packet["q9h_source_handoff_ready"] is True
    _assert_safe(packet)


def test_ps_q9n_ready_real_like_supplied_chain_passes_handoff_preflight() -> None:
    lowering, review = _real_review_packet_bundle()
    packet = build_prediction_warroom_actual_read_to_review_packet_handoff_preflight(
        loader_result=_loader_result(),
        validation_panel=_validation_panel(),
        lowering_result=lowering,
        review_packet=review,
    ).to_dict()
    assert packet["preflight_state"] == "actual_read_to_review_handoff_preflight_ready"
    assert packet["ready_for_real_payload_review_handoff"] is True
    assert packet["ready_for_future_top_default_expanded_ux"] is False
    assert packet["synthetic_review_packet_detected"] is False
    assert packet["q9b_actual_file_read_succeeded"] is True
    assert packet["q9c_validation_panel_valid"] is True
    assert packet["q9e_display_packet_valid"] is True
    assert packet["q9f_review_packet_ready"] is True
    assert packet["q9h_source_handoff_ready"] is True
    assert packet["blocked_reasons"] == []
    assert "real_payload_review_packet_not_verified_by_ui_observation_yet" in packet["warning_reasons"]
    _assert_safe(packet)


def test_ps_q9n_rejects_unsafe_true_flags() -> None:
    lowering, review = _real_review_packet_bundle()
    unsafe_loader = _loader_result()
    unsafe_loader["would_send_to_broker"] = True
    packet = build_prediction_warroom_actual_read_to_review_packet_handoff_preflight(
        loader_result=unsafe_loader,
        validation_panel=_validation_panel(),
        lowering_result=lowering,
        review_packet=review,
    ).to_dict()
    assert packet["preflight_state"] == "actual_read_to_review_handoff_preflight_blocked"
    assert "q9b_loader_result_unsafe_true_flag:would_send_to_broker" in packet["blocked_reasons"]
    _assert_safe(packet)


def main() -> int:
    test_ps_q9n_static_boundaries_and_markers()
    test_ps_q9n_does_not_mutate_warroom_page_or_panel()
    test_ps_q9n_missing_inputs_fail_closed()
    test_ps_q9n_synthetic_ready_review_packet_is_blocked_for_real_handoff()
    test_ps_q9n_ready_real_like_supplied_chain_passes_handoff_preflight()
    test_ps_q9n_rejects_unsafe_true_flags()
    print("[OK] Prediction System PS-Q9N actual-read-to-review handoff preflight guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
