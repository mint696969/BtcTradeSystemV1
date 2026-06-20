# path: ./tools/test_prediction_system_ps_q6b_loader_permission_contract_guard.py
# desc: Guard for PS-Q6B latest payload loader dry-run permission contract. Contract-only; no runtime reads, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_permission_contract import (
    build_prediction_warroom_latest_payload_loader_permission_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_permission_contract.py"
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
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
)
EXPECTED_ROLES = [
    "prediction_system_result_snapshot",
    "prediction_warroom_display_packet",
    "prediction_warroom_widget_group_index",
    "prediction_source_quality_snapshot",
]
EXPECTED_SEQUENCE = [
    "path_scope_check_under_hot_latest_root",
    "expected_artifact_role_check",
    "extension_json_check",
    "file_size_check_before_payload_parse",
    "freshness_check_before_display",
    "payload_decode_after_explicit_loader_authorization",
    "schema_validation_with_q5c",
    "q6a_preflight_status_update",
    "handoff_only_when_preflight_ready",
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


def test_ps_q6b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_loader_permission_contract.ps_q6b.v1" in text
    assert "PredictionWarRoomLatestPayloadLoaderPathRule" in text
    assert "PredictionWarRoomLatestPayloadLoaderPermissionContractPacket" in text
    assert "build_prediction_warroom_latest_payload_loader_permission_contract" in text
    assert "future_loader_requires_separate_guard" in text
    assert "actual_file_read_allowed_by_this_contract" in text


def test_ps_q6b_default_contract_is_dry_run_only_and_not_read_allowed() -> None:
    packet = build_prediction_warroom_latest_payload_loader_permission_contract().to_dict()
    assert packet["contract_version"] == "prediction_warroom_latest_payload_loader_permission_contract.ps_q6b.v1"
    assert packet["loader_permission_state"] == "contract_only_actual_read_not_allowed"
    assert packet["hot_latest_root_hint"] == "D:\\btc_ts_hot"
    assert packet["preflight_status_contract_version"] == "prediction_warroom_latest_payload_preflight_status.ps_q6a.v1"
    assert packet["schema_validator_contract_version"] == "prediction_warroom_payload_schema_validator.ps_q5c.v1"
    assert packet["actual_file_read_allowed_by_this_contract"] is False
    assert packet["actual_payload_decode_allowed_by_this_contract"] is False
    assert packet["future_loader_implementation_required"] is True
    assert packet["future_loader_requires_separate_guard"] is True
    assert packet["future_loader_requires_human_approval_before_actual_read"] is True
    assert packet["would_load_hot_latest_artifacts"] is False
    assert packet["would_read_runtime_file"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["broker_execution_requested"] is False
    assert packet["mode_apply_requested"] is False
    assert packet["command_ledger_append_requested"] is False


def test_ps_q6b_path_rules_are_scoped_to_hot_latest_prediction_jsons() -> None:
    packet = build_prediction_warroom_latest_payload_loader_permission_contract().to_dict()
    rules = packet["path_rules"]
    assert [item["artifact_role"] for item in rules] == EXPECTED_ROLES
    assert packet["required_artifact_count"] == 1
    assert packet["optional_artifact_count"] == 3
    for item in rules:
        assert item["allowed_root_hint"] == "D:\\btc_ts_hot"
        assert item["allowed_path_hint"].startswith("D:\\btc_ts_hot\\prediction\\")
        assert item["allowed_path_hint"].endswith(".json")
        assert item["allowed_extension"] == ".json"
        assert item["must_be_under_hot_latest_root"] is True
        assert item["must_match_expected_artifact_ref"] is True
        assert item["max_file_size_bytes"] > 0
        assert item["freshness_max_age_sec"] > 0
        assert item["actual_file_read_allowed_by_this_contract"] is False
        assert item["read_by_this_slice"] is False
        assert item["loaded_in_this_slice"] is False
        assert item["would_load_hot_latest_artifacts"] is False
        assert item["would_read_runtime_file"] is False
        assert item["would_write_runtime_artifact"] is False
        assert item["would_send_to_broker"] is False


def test_ps_q6b_validation_and_failure_sequences_are_explicit() -> None:
    packet = build_prediction_warroom_latest_payload_loader_permission_contract().to_dict()
    assert packet["validation_sequence"] == EXPECTED_SEQUENCE
    assert "return_blocked_preflight_status" in packet["failure_behavior_sequence"]
    assert "do_not_render_unvalidated_payload" in packet["failure_behavior_sequence"]
    assert "do_not_write_runtime_artifact" in packet["failure_behavior_sequence"]
    assert "do_not_trigger_autotrade" in packet["failure_behavior_sequence"]
    assert "do_not_send_to_broker" in packet["failure_behavior_sequence"]
    assert "actual_latest_payload_loader_not_implemented" in packet["blocked_reasons_when_contract_only"]
    assert "actual_file_read_not_allowed_by_ps_q6b_contract" in packet["blocked_reasons_when_contract_only"]
    summary = packet["handoff_summary"]
    assert summary["actual_file_read_allowed_by_this_contract"] is False
    assert summary["actual_payload_decode_allowed_by_this_contract"] is False
    assert summary["future_loader_requires_separate_guard"] is True
    assert summary["runtime_file_read_enabled"] is False
    assert summary["runtime_artifact_write_enabled"] is False
    assert summary["autotrade_trigger_enabled"] is False


def test_ps_q6b_custom_thresholds_apply_without_enabling_reads() -> None:
    packet = build_prediction_warroom_latest_payload_loader_permission_contract(
        required_artifact_max_bytes=1234,
        optional_artifact_max_bytes=5678,
        required_artifact_freshness_max_age_sec=11,
        optional_artifact_freshness_max_age_sec=22,
    ).to_dict()
    required = [item for item in packet["path_rules"] if item["required"]]
    optional = [item for item in packet["path_rules"] if not item["required"]]
    assert required[0]["max_file_size_bytes"] == 1234
    assert required[0]["freshness_max_age_sec"] == 11
    assert all(item["max_file_size_bytes"] == 5678 for item in optional)
    assert all(item["freshness_max_age_sec"] == 22 for item in optional)
    assert packet["actual_file_read_allowed_by_this_contract"] is False
    assert all(item["actual_file_read_allowed_by_this_contract"] is False for item in packet["path_rules"])


def main() -> int:
    test_ps_q6b_static_boundaries_and_markers()
    test_ps_q6b_default_contract_is_dry_run_only_and_not_read_allowed()
    test_ps_q6b_path_rules_are_scoped_to_hot_latest_prediction_jsons()
    test_ps_q6b_validation_and_failure_sequences_are_explicit()
    test_ps_q6b_custom_thresholds_apply_without_enabling_reads()
    print("[OK] Prediction System PS-Q6B loader permission contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
