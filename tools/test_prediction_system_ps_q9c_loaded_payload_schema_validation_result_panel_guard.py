# path: ./tools/test_prediction_system_ps_q9c_loaded_payload_schema_validation_result_panel_guard.py
# desc: Focused guard for PS-Q9C loaded payload schema validation result panel.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_loaded_payload_schema_validation_result_panel import (
    LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION,
    build_prediction_warroom_loaded_payload_schema_validation_result_panel,
)
from btcts.apps.operator_ui.components.prediction_warroom_payload_schema_validator import DISPLAY_PACKET_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_loaded_payload_schema_validation_result_panel.py"
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
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_decode_payload: bool = True",
    "would_write_runtime_artifact: bool = True",
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


def _assert_no_side_effect_flags(packet: dict) -> None:
    false_keys = (
        "would_load_hot_latest_artifacts",
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
    )
    for key in false_keys:
        assert packet[key] is False, key
    for item in packet["validation_items"]:
        for key in false_keys:
            assert item[key] is False, f"{item['artifact_role']}:{key}"


def _valid_display_packet() -> dict:
    return {
        "packet_version": DISPLAY_PACKET_VERSION,
        "packet_id": "packet-1",
        "generated_at": "2026-06-21T00:00:00Z",
        "market_uid": "btc_jpy.bitflyer",
        "prediction_run_id": "run-1",
        "primary_signal_summary": {
            "estimated_signal_strength_percent": 42,
            "estimated_reference_hit_rate_percent": 55,
            "signal_strength_band": "medium",
        },
        "horizon_cards": [
            {"horizon_group": "short", "estimated_signal_strength_percent": 42, "signal_strength_band": "medium"},
        ],
        "family_cards": [
            {"family": "flow", "horizon_sec": 60, "estimated_signal_strength_percent": 42},
        ],
        "source_quality_panel": {"tier0_source_quality_gate": "passed"},
        "warning_panel": {"blockers": [], "warnings": []},
        "ui_contract": {"trigger_buttons_allowed": False, "broker_controls_allowed": False, "mode_controls_allowed": False},
        "boundaries": {
            "read_only": True,
            "non_executing": True,
            "display_only": True,
            "render_intent_only": True,
            "not_loaded_as_runtime_display_source": True,
            "would_write_runtime_artifact": False,
            "would_send_to_broker": False,
            "broker_execution_requested": False,
            "mode_apply_requested": False,
            "command_ledger_append_requested": False,
            "approval_append_requested": False,
        },
        "read_only": True,
        "non_executing": True,
    }


def test_ps_q9c_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_loaded_payload_schema_validation_result_panel.ps_q9c.v1" in text
    assert "build_prediction_warroom_loaded_payload_schema_validation_result_panel" in text
    assert "validate_prediction_warroom_display_packet_schema" in text
    assert "display_packet_lowering_enabled" in text
    assert "warroom_card_rendering_enabled" in text


def test_ps_q9c_blocks_without_loaded_payloads() -> None:
    packet = build_prediction_warroom_loaded_payload_schema_validation_result_panel(loader_result={"loaded_payloads": {}}).to_dict()
    assert packet["panel_version"] == LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION
    assert packet["panel_state"] == "schema_validation_panel_blocked"
    assert packet["loaded_payload_count"] == 0
    assert packet["validated_payload_count"] == 0
    assert packet["valid_payload_count"] == 0
    assert "no_loaded_payloads_available_for_schema_validation" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9c_validates_prediction_system_result_snapshot_minimally() -> None:
    packet = build_prediction_warroom_loaded_payload_schema_validation_result_panel(
        loader_result={
            "loader_version": "prediction_warroom_latest_payload_read_only_loader.ps_q9b.v1",
            "loaded_payloads": {"prediction_system_result_snapshot": {"prediction_run_id": "run-1", "value": 42}},
        }
    ).to_dict()
    assert packet["panel_state"] == "schema_validation_panel_valid"
    assert packet["loaded_payload_count"] == 1
    assert packet["validated_payload_count"] == 1
    assert packet["valid_payload_count"] == 1
    item = packet["validation_items"][0]
    assert item["artifact_role"] == "prediction_system_result_snapshot"
    assert item["schema_target"] == "prediction_system_result_snapshot_minimal"
    assert item["validation_state"] == "schema_validation_valid"
    assert item["payload_type"] == "dict"
    assert "prediction_run_id" in item["payload_preview_keys"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9c_empty_prediction_system_result_snapshot_warns_but_does_not_block() -> None:
    packet = build_prediction_warroom_loaded_payload_schema_validation_result_panel(
        loader_result={"loaded_payloads": {"prediction_system_result_snapshot": {}}}
    ).to_dict()
    assert packet["panel_state"] == "schema_validation_panel_valid_with_warnings"
    assert packet["blocker_count"] == 0
    assert packet["warning_count"] == 1
    item = packet["validation_items"][0]
    assert item["valid"] is True
    assert item["warning_count"] == 1
    assert item["issue_summaries"][0]["issue_code"] == "loaded_payload_empty_mapping"
    _assert_no_side_effect_flags(packet)


def test_ps_q9c_validates_warroom_display_packet_with_q5c() -> None:
    packet = build_prediction_warroom_loaded_payload_schema_validation_result_panel(
        loader_result={"loaded_payloads": {"prediction_warroom_display_packet": _valid_display_packet()}}
    ).to_dict()
    assert packet["panel_state"] == "schema_validation_panel_valid"
    item = packet["validation_items"][0]
    assert item["artifact_role"] == "prediction_warroom_display_packet"
    assert item["schema_target"] == "display_packet"
    assert item["valid"] is True
    assert item["blocker_count"] == 0
    assert "display_packet" in item["checked_sections"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9c_invalid_warroom_display_packet_blocks() -> None:
    packet = build_prediction_warroom_loaded_payload_schema_validation_result_panel(
        loader_result={"loaded_payloads": {"prediction_warroom_display_packet": {"packet_version": "bad"}}}
    ).to_dict()
    assert packet["panel_state"] == "schema_validation_panel_blocked"
    assert packet["blocker_count"] > 0
    assert "prediction_warroom_display_packet_schema_validation_blocked" in packet["blocked_reasons"]
    item = packet["validation_items"][0]
    assert item["valid"] is False
    assert item["blocker_count"] > 0
    assert item["issue_summaries"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9c_handoff_summary_keeps_next_boundary() -> None:
    packet = build_prediction_warroom_loaded_payload_schema_validation_result_panel(
        loader_result={"loaded_payloads": {"prediction_system_result_snapshot": {"prediction_run_id": "run-1"}}}
    ).to_dict()
    summary = packet["handoff_summary"]
    assert summary["panel_boundary"] == "ps_q9c_loaded_payload_schema_validation_result_panel_only"
    assert summary["responsibility"] == "validate/report loaded payload schema state before PS-Q9D display-packet lowering"
    assert summary["display_packet_lowering_enabled"] is False
    assert summary["warroom_card_rendering_enabled"] is False
    assert summary["warroom_page_mutation_enabled"] is False
    assert summary["runtime_file_read_enabled"] is False
    assert summary["payload_decode_enabled_by_this_panel"] is False
    assert summary["runtime_artifact_write_enabled"] is False
    assert summary["autotrade_trigger_enabled"] is False
    assert summary["broker_private_api_enabled"] is False
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q9c_static_boundaries_and_markers()
    test_ps_q9c_blocks_without_loaded_payloads()
    test_ps_q9c_validates_prediction_system_result_snapshot_minimally()
    test_ps_q9c_empty_prediction_system_result_snapshot_warns_but_does_not_block()
    test_ps_q9c_validates_warroom_display_packet_with_q5c()
    test_ps_q9c_invalid_warroom_display_packet_blocks()
    test_ps_q9c_handoff_summary_keeps_next_boundary()
    print("[OK] Prediction System PS-Q9C loaded payload schema validation result panel guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
