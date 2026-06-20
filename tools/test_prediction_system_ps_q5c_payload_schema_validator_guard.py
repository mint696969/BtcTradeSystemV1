# path: ./tools/test_prediction_system_ps_q5c_payload_schema_validator_guard.py
# desc: Guard for PS-Q5C Prediction WarRoom payload schema validator. Pure validation; no runtime reads, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_explanation_widget_groups import build_prediction_warroom_explanation_widget_group_index
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet
from btcts.apps.operator_ui.components.prediction_warroom_source_quality_explanations import build_prediction_warroom_source_quality_explanation_panel
from btcts.apps.operator_ui.components.prediction_warroom_widget_groups import build_prediction_warroom_widget_group_packet_index
from btcts.apps.operator_ui.components.prediction_warroom_payload_schema_validator import (
    validate_prediction_warroom_display_packet_schema,
    validate_prediction_warroom_explanation_panel_schema,
    validate_prediction_warroom_payload_contract_bundle,
    validate_prediction_warroom_widget_group_index_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_payload_schema_validator.py"
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
    "Path.read_text",
    "json.load",
    "json.loads",
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
    "would_load_hot_latest_artifacts=True",
    "would_read_runtime_file=True",
    "would_write_runtime_artifact=True",
    "would_send_to_broker=True",
    "broker_execution_requested=True",
    "mode_apply_requested=True",
    "command_ledger_append_requested=True",
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


def _sample_payloads():
    display_packet = build_prediction_warroom_sample_display_packet()
    widget_index = build_prediction_warroom_widget_group_packet_index(display_packet)
    explanation_panel = build_prediction_warroom_source_quality_explanation_panel(display_packet).to_dict()
    explanation_widget_index = build_prediction_warroom_explanation_widget_group_index(display_packet).to_dict()
    return display_packet, widget_index, explanation_panel, explanation_widget_index


def test_ps_q5c_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_payload_schema_validator.ps_q5c.v1" in text
    assert "PredictionWarRoomPayloadSchemaIssue" in text
    assert "PredictionWarRoomPayloadSchemaValidationReport" in text
    assert "validate_prediction_warroom_display_packet_schema" in text
    assert "validate_prediction_warroom_widget_group_index_schema" in text
    assert "validate_prediction_warroom_explanation_panel_schema" in text
    assert "validate_prediction_warroom_payload_contract_bundle" in text


def test_ps_q5c_validates_current_sample_display_widget_explanation_payloads() -> None:
    display_packet, widget_index, explanation_panel, explanation_widget_index = _sample_payloads()
    display_report = validate_prediction_warroom_display_packet_schema(display_packet).to_dict()
    widget_report = validate_prediction_warroom_widget_group_index_schema(widget_index).to_dict()
    explanation_report = validate_prediction_warroom_explanation_panel_schema(explanation_panel).to_dict()
    explanation_widget_report = validate_prediction_warroom_widget_group_index_schema(explanation_widget_index).to_dict()
    assert display_report["valid"] is True, display_report
    assert widget_report["valid"] is True, widget_report
    assert explanation_report["valid"] is True, explanation_report
    assert explanation_widget_report["valid"] is True, explanation_widget_report
    assert display_report["report_version"] == "prediction_warroom_payload_schema_validator.ps_q5c.v1"
    assert widget_report["would_read_runtime_file"] is False
    assert explanation_report["would_load_hot_latest_artifacts"] is False


def test_ps_q5c_bundle_report_combines_all_payload_sections() -> None:
    display_packet, widget_index, explanation_panel, explanation_widget_index = _sample_payloads()
    report = validate_prediction_warroom_payload_contract_bundle(
        display_packet=display_packet,
        widget_group_index=widget_index,
        explanation_panel=explanation_panel,
        explanation_widget_group_index=explanation_widget_index,
    ).to_dict()
    assert report["valid"] is True, report
    assert report["schema_target"] == "payload_contract_bundle"
    assert report["checked_sections"] == ["display_packet", "widget_group_index", "explanation_panel", "explanation_widget_group_index"]
    assert report["issue_count"] == 0
    assert report["read_only"] is True
    assert report["non_executing"] is True
    assert report["validator_only"] is True


def test_ps_q5c_blocks_bad_versions_and_invalid_signal_percent() -> None:
    bad = dict(build_prediction_warroom_sample_display_packet())
    bad["packet_version"] = "bad.version"
    bad["primary_signal_summary"] = dict(bad["primary_signal_summary"])
    bad["primary_signal_summary"]["estimated_signal_strength_percent"] = 100
    report = validate_prediction_warroom_display_packet_schema(bad).to_dict()
    assert report["valid"] is False
    issue_codes = {item["issue_code"] for item in report["issues"]}
    assert "unexpected_contract_version" in issue_codes
    assert "invalid_signal_percent_range" in issue_codes
    assert report["blocker_count"] >= 2


def test_ps_q5c_blocks_dangerous_flags_and_interactive_controls() -> None:
    bad = dict(build_prediction_warroom_sample_display_packet())
    bad["would_send_to_broker"] = True
    bad["ui_contract"] = dict(bad["ui_contract"])
    bad["ui_contract"]["broker_controls_allowed"] = True
    report = validate_prediction_warroom_display_packet_schema(bad).to_dict()
    assert report["valid"] is False
    issue_codes = {item["issue_code"] for item in report["issues"]}
    assert "dangerous_flag_enabled" in issue_codes
    assert "interactive_controls_enabled" in issue_codes


def test_ps_q5c_empty_bundle_is_blocked_and_safe_flags_remain_false() -> None:
    report = validate_prediction_warroom_payload_contract_bundle().to_dict()
    assert report["valid"] is False
    assert report["schema_target"] == "payload_contract_bundle"
    assert report["blocker_count"] == 1
    assert report["issues"][0]["issue_code"] == "empty_payload_bundle"
    assert report["would_load_hot_latest_artifacts"] is False
    assert report["would_read_runtime_file"] is False
    assert report["would_write_runtime_artifact"] is False
    assert report["would_send_to_broker"] is False
    assert report["broker_execution_requested"] is False
    assert report["mode_apply_requested"] is False
    assert report["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_q5c_static_boundaries_and_markers()
    test_ps_q5c_validates_current_sample_display_widget_explanation_payloads()
    test_ps_q5c_bundle_report_combines_all_payload_sections()
    test_ps_q5c_blocks_bad_versions_and_invalid_signal_percent()
    test_ps_q5c_blocks_dangerous_flags_and_interactive_controls()
    test_ps_q5c_empty_bundle_is_blocked_and_safe_flags_remain_false()
    print("[OK] Prediction System PS-Q5C payload schema validator guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
