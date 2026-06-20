# path: ./tools/test_prediction_system_ps_q6g_supplemental_registry_preflight_guard.py
# desc: Guard for PS-Q6G Prediction WarRoom supplemental registry preflight validator. Validation only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry import build_prediction_warroom_supplemental_widget_registry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry_preflight import (
    build_prediction_warroom_supplemental_widget_registry_preflight_report,
    validate_prediction_warroom_supplemental_widget_registry_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry_preflight.py"
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
    "actual_file_read_allowed_by_this_contract: bool = True",
    "actual_payload_decode_allowed_by_this_contract: bool = True",
    "actual_loader_execution_allowed: bool = True",
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
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


def _sample_display_packet() -> dict:
    return build_prediction_warroom_sample_display_packet()


def test_ps_q6g_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_supplemental_widget_registry_preflight.ps_q6g.v1" in text
    assert "PredictionWarRoomSupplementalWidgetRegistryPreflightReport" in text
    assert "validate_prediction_warroom_supplemental_widget_registry_schema" in text
    assert "build_prediction_warroom_supplemental_widget_registry_preflight_report" in text
    assert "ready_for_warroom_supplemental_handoff" in text


def test_ps_q6g_default_sample_preflight_is_valid_and_safe() -> None:
    report = build_prediction_warroom_supplemental_widget_registry_preflight_report(display_packet=_sample_display_packet()).to_dict()
    assert report["report_version"] == "prediction_warroom_supplemental_widget_registry_preflight.ps_q6g.v1"
    assert report["preflight_state"] == "ready_for_warroom_supplemental_handoff"
    assert report["valid"] is True
    assert report["blocker_count"] == 0
    assert report["supplemental_index_count"] == 3
    assert report["supplemental_widget_group_count"] == 3
    assert report["auto_refresh_group_count"] == 3
    assert "prediction_warroom_supplemental_widget_registry.ps_q6f.v1" in report["checked_contracts"]
    assert "prediction_warroom_widget_groups.ps_q4b.v1" in report["checked_contracts"]
    assert report["actual_loader_execution_allowed"] is False
    assert report["actual_file_read_allowed_by_this_contract"] is False
    assert report["actual_payload_decode_allowed_by_this_contract"] is False
    assert report["would_load_hot_latest_artifacts"] is False
    assert report["would_read_runtime_file"] is False
    assert report["would_write_runtime_artifact"] is False
    assert report["would_send_to_broker"] is False
    assert report["boundaries"]["would_read_runtime_file"] is False


def test_ps_q6g_schema_validator_accepts_valid_registry() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    report = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    assert report["valid"] is True
    assert report["preflight_state"] == "ready_for_warroom_supplemental_handoff"
    assert report["supplemental_widget_group_count"] == 3
    assert report["blocker_count"] == 0


def test_ps_q6g_schema_validator_blocks_wrong_counts_and_order() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    registry["supplemental_widget_group_count"] = 99
    registry["supplemental_widget_group_order"] = ["prediction_latest_payload_loader_authorization_widget", "prediction_latest_payload_dry_run_status_widget", "source_quality_explanation_widgets"]
    report = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    codes = {item["issue_code"] for item in report["issues"]}
    assert report["valid"] is False
    assert report["preflight_state"] == "blocked_before_warroom_supplemental_handoff"
    assert "supplemental_widget_group_count_mismatch" in codes
    assert "supplemental_widget_group_order_mismatch" in codes


def test_ps_q6g_schema_validator_blocks_unsafe_flags() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    registry["widget_groups"][0]["would_read_runtime_file"] = True
    registry["integration_contract"]["requires_hot_file_read"] = True
    registry["boundaries"]["actual_loader_execution_allowed"] = True
    report = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    codes = {item["issue_code"] for item in report["issues"]}
    assert report["valid"] is False
    assert "dangerous_flag_enabled" in codes
    assert "unsafe_integration_contract_flag" in codes


def test_ps_q6g_schema_validator_blocks_bad_attach_points() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    registry["widget_groups"][0]["attach_after_widget_group_id"] = "wrong_widget"
    registry["auto_refresh_groups"][1]["attach_after_widget_group_id"] = "source_quality_widget"
    report = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    codes = {item["issue_code"] for item in report["issues"]}
    assert report["valid"] is False
    assert "unexpected_attach_after_widget_group_id" in codes


def test_ps_q6g_candidate_metadata_keeps_preflight_safe() -> None:
    report = build_prediction_warroom_supplemental_widget_registry_preflight_report(
        display_packet=_sample_display_packet(),
        artifact_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json",
                "file_size_bytes": 1200,
                "freshness_status": "fresh",
                "observed_age_sec": 12,
                "schema_validation_status": "valid",
                "schema_validation_valid": True,
            },
        ),
    ).to_dict()
    assert report["valid"] is True
    assert report["preflight_state"] == "ready_for_warroom_supplemental_handoff"
    assert report["actual_loader_execution_allowed"] is False
    assert report["would_read_runtime_file"] is False


def main() -> int:
    test_ps_q6g_static_boundaries_and_markers()
    test_ps_q6g_default_sample_preflight_is_valid_and_safe()
    test_ps_q6g_schema_validator_accepts_valid_registry()
    test_ps_q6g_schema_validator_blocks_wrong_counts_and_order()
    test_ps_q6g_schema_validator_blocks_unsafe_flags()
    test_ps_q6g_schema_validator_blocks_bad_attach_points()
    test_ps_q6g_candidate_metadata_keeps_preflight_safe()
    print("[OK] Prediction System PS-Q6G supplemental registry preflight guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
