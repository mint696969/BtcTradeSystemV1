# path: ./tools/test_prediction_system_ps_q9a_latest_payload_actual_read_preflight_contract_guard.py
# desc: Focused guard for PS-Q9A latest payload actual-read preflight final contract. Contract/readiness only; no filesystem reads, payload decode, WarRoom mutation, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_actual_read_preflight_contract import (
    ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION,
    build_prediction_warroom_latest_payload_actual_read_preflight_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_actual_read_preflight_contract.py"
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
    "loader_execution_allowed_by_this_contract: bool = True",
    "approval_granted: bool = True",
    "authorization_granted: bool = True",
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
EXPECTED_ROLES = [
    "prediction_system_result_snapshot",
    "prediction_warroom_display_packet",
    "prediction_warroom_widget_group_index",
    "prediction_source_quality_snapshot",
]
EXPECTED_SEQUENCE = [
    "q6b_permission_contract_path_rules_loaded_as_contract_data",
    "allowed_hot_latest_root_check_under_d_btc_ts_hot",
    "expected_artifact_role_and_path_match_check",
    "json_extension_check_before_any_read",
    "file_size_metadata_check_before_any_read",
    "freshness_metadata_check_before_any_read",
    "schema_validation_plan_with_q5c_after_ps_q9b_decode",
    "ps_q9b_guarded_actual_read_requires_separate_guard",
    "ps_q9c_loaded_payload_validation_panel_before_display",
    "fail_closed_keep_runtime_disconnected_on_any_blocker",
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


def _assert_all_runtime_flags_false(packet: dict) -> None:
    false_keys = (
        "actual_file_read_allowed_by_this_contract",
        "actual_payload_decode_allowed_by_this_contract",
        "loader_execution_allowed_by_this_contract",
        "approval_granted",
        "authorization_granted",
        "read_by_this_slice",
        "decoded_in_this_slice",
        "loaded_in_this_slice",
        "would_load_hot_latest_artifacts",
        "would_read_runtime_file",
        "would_collect_public_source",
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
    for item in packet["allowed_candidates"]:
        for key in false_keys:
            if key in item:
                assert item[key] is False, f"{item['artifact_role']}:{key}"


def test_ps_q9a_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_actual_read_preflight_contract.ps_q9a.v1" in text
    assert "PredictionWarRoomLatestPayloadActualReadCandidate" in text
    assert "PredictionWarRoomLatestPayloadActualReadPreflightContractPacket" in text
    assert "build_prediction_warroom_latest_payload_actual_read_preflight_contract" in text
    assert "ps_q9b_guarded_actual_read_requires_separate_guard" in text
    assert "do_not_attempt_file_read" in text


def test_ps_q9a_default_contract_blocks_without_metadata_and_reads_nothing() -> None:
    packet = build_prediction_warroom_latest_payload_actual_read_preflight_contract().to_dict()
    assert packet["contract_version"] == ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION
    assert packet["contract_state"] == "blocked_waiting_for_ps_q9b_actual_read_candidate_metadata"
    assert packet["hot_latest_root_hint"] == "D:\\btc_ts_hot"
    assert packet["q6a_preflight_status_contract_version"] == "prediction_warroom_latest_payload_preflight_status.ps_q6a.v1"
    assert packet["q6b_loader_permission_contract_version"] == "prediction_warroom_latest_payload_loader_permission_contract.ps_q6b.v1"
    assert packet["schema_validator_contract_version"] == "prediction_warroom_payload_schema_validator.ps_q5c.v1"
    assert [item["artifact_role"] for item in packet["allowed_candidates"]] == EXPECTED_ROLES
    assert packet["required_candidate_count"] == 1
    assert packet["optional_candidate_count"] == 3
    assert packet["ready_candidate_count"] == 0
    assert packet["ready_for_ps_q9b_guarded_actual_read"] is False
    assert "required_actual_read_candidate_metadata_not_supplied" in packet["blocked_reasons"]
    assert "optional_actual_read_candidate_metadata_not_supplied" in packet["warning_reasons"]
    assert packet["actual_read_preflight_sequence"] == EXPECTED_SEQUENCE
    _assert_all_runtime_flags_false(packet)


def test_ps_q9a_allowed_candidates_are_scoped_to_hot_prediction_jsons() -> None:
    packet = build_prediction_warroom_latest_payload_actual_read_preflight_contract().to_dict()
    for item in packet["allowed_candidates"]:
        assert item["allowed_root_hint"] == "D:\\btc_ts_hot"
        assert item["allowed_path_hint"].startswith("D:\\btc_ts_hot\\prediction\\")
        assert item["allowed_path_hint"].endswith(".json")
        assert item["allowed_extension"] == ".json"
        assert item["max_file_size_bytes"] > 0
        assert item["freshness_max_age_sec"] > 0
        assert item["actual_file_read_allowed_by_this_contract"] is False
        assert item["actual_payload_decode_allowed_by_this_contract"] is False
        assert item["loader_execution_allowed_by_this_contract"] is False


def test_ps_q9a_valid_required_metadata_becomes_ready_for_q9b_but_still_no_read() -> None:
    packet = build_prediction_warroom_latest_payload_actual_read_preflight_contract(
        candidate_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json",
                "file_size_bytes": 1200,
                "freshness_status": "fresh",
                "observed_age_sec": 12,
                "schema_validation_status": "planned_not_run",
            },
        )
    ).to_dict()
    assert packet["contract_state"] == "ready_for_ps_q9b_guarded_actual_read_contract_handoff"
    assert packet["operator_visible_readiness_state"] == "ready_for_ps_q9b_guarded_actual_read"
    assert packet["ready_for_ps_q9b_guarded_actual_read"] is True
    assert packet["ready_candidate_count"] == 1
    assert "actual_read_still_not_allowed_by_ps_q9a_contract" in packet["warning_reasons"]
    assert "ps_q9b_must_be_separate_read_only_guarded_slice" in packet["warning_reasons"]
    required = [item for item in packet["allowed_candidates"] if item["artifact_role"] == "prediction_system_result_snapshot"][0]
    assert required["candidate_ready_for_ps_q9b_guarded_actual_read"] is True
    assert required["path_scope_status"] == "passed"
    assert required["extension_status"] == "passed"
    assert required["file_size_status"] == "passed"
    assert required["freshness_status"] == "fresh"
    assert required["schema_validation_status"] == "planned_not_run"
    assert "ps_q9b_must_decode_then_ps_q9c_must_validate_with_q5c_before_display" in required["warning_reasons"]
    _assert_all_runtime_flags_false(packet)


def test_ps_q9a_bad_path_extension_size_or_freshness_blocks_before_read() -> None:
    packet = build_prediction_warroom_latest_payload_actual_read_preflight_contract(
        candidate_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "E:\\btc_ts\\prediction\\latest_prediction_system_result.txt",
                "file_size_bytes": 12_000_000,
                "freshness_status": "stale",
                "schema_validation_status": "planned_not_run",
            },
        )
    ).to_dict()
    assert packet["ready_for_ps_q9b_guarded_actual_read"] is False
    required = [item for item in packet["allowed_candidates"] if item["artifact_role"] == "prediction_system_result_snapshot"][0]
    assert required["candidate_ready_for_ps_q9b_guarded_actual_read"] is False
    assert required["path_scope_status"] == "outside_hot_latest_root"
    assert required["extension_status"] == "not_json"
    assert required["file_size_status"] == "too_large"
    assert "path_scope_not_under_hot_latest_root" in required["blocker_reasons"]
    assert "extension_not_allowed_before_actual_read" in required["blocker_reasons"]
    assert "file_size_exceeds_max_before_actual_read" in required["blocker_reasons"]
    assert "freshness_status_stale_before_actual_read" in required["blocker_reasons"]
    _assert_all_runtime_flags_false(packet)


def test_ps_q9a_handoff_summary_keeps_responsibility_separated() -> None:
    packet = build_prediction_warroom_latest_payload_actual_read_preflight_contract().to_dict()
    summary = packet["handoff_summary"]
    assert summary["contract_boundary"] == "ps_q9a_actual_read_preflight_final_contract_only"
    assert summary["responsibility"] == "declare allowed candidates and exact pre-read readiness conditions for PS-Q9B"
    assert summary["actual_file_read_allowed_by_this_contract"] is False
    assert summary["actual_payload_decode_allowed_by_this_contract"] is False
    assert summary["loader_execution_allowed_by_this_contract"] is False
    assert summary["approval_granted"] is False
    assert summary["authorization_granted"] is False
    assert summary["runtime_file_read_enabled"] is False
    assert summary["runtime_artifact_write_enabled"] is False
    assert summary["autotrade_trigger_enabled"] is False
    assert summary["broker_private_api_enabled"] is False
    assert "human_review_required_before_actual_read_attempt" in packet["ps_q9b_entry_requirements"]
    assert "do_not_attempt_file_read" in packet["fail_closed_behavior"]


def main() -> int:
    test_ps_q9a_static_boundaries_and_markers()
    test_ps_q9a_default_contract_blocks_without_metadata_and_reads_nothing()
    test_ps_q9a_allowed_candidates_are_scoped_to_hot_prediction_jsons()
    test_ps_q9a_valid_required_metadata_becomes_ready_for_q9b_but_still_no_read()
    test_ps_q9a_bad_path_extension_size_or_freshness_blocks_before_read()
    test_ps_q9a_handoff_summary_keeps_responsibility_separated()
    print("[OK] Prediction System PS-Q9A latest payload actual-read preflight contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
