# path: ./tools/test_prediction_system_ps_q9o_actual_read_review_composition_harness_guard.py
# desc: Focused guard for PS-Q9O non-UI actual-read review composition harness.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_read_review_composition_harness import (
    ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_SEQUENCE,
    ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION,
    build_prediction_warroom_actual_read_review_composition_harness,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_read_only_loader import READ_ONLY_LOADER_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_review_composition_harness.py"
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
    "loader_execution_requested: bool = True",
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
    "consume_supplied_explicit_payload_or_loader_result_mapping_only",
    "build_or_use_supplied_q9b_loader_result_mapping_without_running_loader",
    "build_q9c_validation_panel_from_loader_result_mapping_in_memory",
    "build_q9e_display_packet_lowering_result_in_memory",
    "build_q9f_review_packet_in_memory",
    "build_q9n_handoff_preflight_in_memory",
    "return_composition_harness_packet_only",
    "do_not_run_loader",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_mutate_warroom_page_or_panel",
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


def _loader_result(payload: dict, *, ready: bool = True) -> dict:
    return {
        "loader_version": READ_ONLY_LOADER_VERSION,
        "loader_state": "loaded_read_only_payload_decode_succeeded_schema_validation_deferred" if ready else "blocked_actual_read_not_requested",
        "actual_file_read_attempted": ready,
        "actual_file_read_succeeded": ready,
        "payload_decode_attempted": ready,
        "payload_decode_succeeded": ready,
        "loaded_payload_count": 1 if ready else 0,
        "loaded_payloads": {"prediction_system_result_snapshot": payload} if ready else {},
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
    assert packet["non_executing"] is True
    assert packet["local_dev_harness_only"] is True
    assert packet["in_memory_input_only"] is True
    for key in (
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "loader_execution_requested",
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


def test_ps_q9o_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_read_review_composition_harness.ps_q9o.v1" in text
    assert "build_prediction_warroom_actual_read_review_composition_harness" in text
    assert list(ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_SEQUENCE) == EXPECTED_SEQUENCE
    assert ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION == "prediction_warroom_actual_read_review_composition_harness.ps_q9o.v1"


def test_ps_q9o_does_not_mutate_warroom_page_or_panel() -> None:
    marker = "prediction_warroom_actual_read_review_composition_harness"
    assert marker not in WARROOM_PAGE.read_text(encoding="utf-8")
    assert marker not in PANEL.read_text(encoding="utf-8")


def test_ps_q9o_missing_inputs_fail_closed() -> None:
    packet = build_prediction_warroom_actual_read_review_composition_harness().to_dict()
    assert packet["harness_state"] == "actual_read_review_composition_blocked"
    assert packet["loader_result_source"] == "missing"
    assert "prediction_result_payload_or_loader_result_required" in packet["blocked_reasons"]
    assert packet["ready_for_real_payload_review_handoff"] is False
    assert packet["q9n_handoff_preflight_built"] is True
    _assert_safe(packet)


def test_ps_q9o_explicit_payload_without_q9b_loader_result_builds_chain_but_fails_closed() -> None:
    payload = _real_payload()
    packet = build_prediction_warroom_actual_read_review_composition_harness(
        prediction_result_payload=payload,
    ).to_dict()
    assert packet["harness_state"] == "actual_read_review_composition_blocked"
    assert packet["loader_result_source"] == "explicit_payload_surrogate_loader_result"
    assert packet["q9c_validation_panel_built"] is True
    assert packet["q9e_lowering_result_built"] is True
    assert packet["q9f_review_packet_built"] is True
    assert packet["q9n_handoff_preflight_built"] is True
    assert packet["q9f_review_packet"]["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert "q9b_actual_read_decode_not_ready" in packet["blocked_reasons"]
    assert "q9b_actual_loader_result_not_supplied_handoff_will_fail_closed" in packet["warning_reasons"]
    assert packet["ready_for_real_payload_review_handoff"] is False
    _assert_safe(packet)


def test_ps_q9o_supplied_q9b_loader_result_with_real_payload_passes_handoff() -> None:
    payload = _real_payload()
    packet = build_prediction_warroom_actual_read_review_composition_harness(
        loader_result=_loader_result(payload),
    ).to_dict()
    assert packet["harness_state"] == "actual_read_review_composition_ready"
    assert packet["loader_result_source"] == "supplied_q9b_loader_result_mapping"
    assert packet["payload_source"] == "loader_result_loaded_payloads"
    assert packet["ready_for_real_payload_review_handoff"] is True
    assert packet["ready_for_future_top_default_expanded_ux"] is False
    assert packet["q9n_handoff_preflight"]["preflight_state"] == "actual_read_to_review_handoff_preflight_ready"
    assert packet["blocked_reasons"] == []
    assert "real_payload_review_packet_not_verified_by_ui_observation_yet" in packet["warning_reasons"]
    _assert_safe(packet)


def test_ps_q9o_supplied_loader_result_with_synthetic_payload_is_blocked() -> None:
    synthetic = build_prediction_warroom_sample_display_packet()
    packet = build_prediction_warroom_actual_read_review_composition_harness(
        loader_result=_loader_result(synthetic),
    ).to_dict()
    assert packet["harness_state"] == "actual_read_review_composition_blocked"
    assert "real_payload_required_but_synthetic_review_packet_detected" in packet["blocked_reasons"]
    assert packet["q9n_handoff_preflight"]["synthetic_review_packet_detected"] is True
    assert packet["ready_for_real_payload_review_handoff"] is False
    _assert_safe(packet)


def test_ps_q9o_rejects_unsafe_loader_flags() -> None:
    payload = _real_payload()
    loader = _loader_result(payload)
    loader["would_send_to_broker"] = True
    packet = build_prediction_warroom_actual_read_review_composition_harness(
        loader_result=loader,
    ).to_dict()
    assert packet["harness_state"] == "actual_read_review_composition_blocked"
    assert "q9b_loader_result_unsafe_true_flag:would_send_to_broker" in packet["blocked_reasons"]
    _assert_safe(packet)


def main() -> int:
    test_ps_q9o_static_boundaries_and_markers()
    test_ps_q9o_does_not_mutate_warroom_page_or_panel()
    test_ps_q9o_missing_inputs_fail_closed()
    test_ps_q9o_explicit_payload_without_q9b_loader_result_builds_chain_but_fails_closed()
    test_ps_q9o_supplied_q9b_loader_result_with_real_payload_passes_handoff()
    test_ps_q9o_supplied_loader_result_with_synthetic_payload_is_blocked()
    test_ps_q9o_rejects_unsafe_loader_flags()
    print("[OK] Prediction System PS-Q9O actual-read review composition harness guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
