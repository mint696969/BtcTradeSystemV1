# path: ./tools/test_prediction_system_ps_q9x_latest_payload_export_preflight_contract_guard.py
# desc: Focused guard for PS-Q9X latest payload export preflight contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_export_preflight_contract import (
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION,
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_SEQUENCE,
    TARGET_ARTIFACT_PATH_HINT,
    build_prediction_warroom_latest_payload_export_preflight_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_preflight_contract.py"
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
    "write_text",
    "write_bytes",
    "mkdir",
    "json.load",
    "json.loads",
    "json.dump",
    "json.dumps",
    ".exists(",
    ".stat(",
    "build_prediction_system_result(",
    "build_prediction_warroom_display_packet(",
    "load_prediction_warroom_latest_payload_read_only(",
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
    "runtime_artifact_write_allowed_by_this_contract: bool = True",
    "runtime_artifact_write_performed_by_this_contract: bool = True",
    "target_directory_created_by_this_contract: bool = True",
    "target_file_written_by_this_contract: bool = True",
    "hot_file_read_performed_by_this_contract: bool = True",
    "payload_decode_performed_by_this_contract: bool = True",
    "prediction_system_result_built_by_this_contract: bool = True",
    "ready_for_warroom_ui_mount: bool = True",
    "warroom_page_mutation_allowed: bool = True",
    "warroom_panel_mutation_allowed: bool = True",
    "approval_or_authorization_allowed: bool = True",
    "ledger_append_allowed: bool = True",
    "autotrade_trigger_allowed: bool = True",
    "broker_private_api_allowed: bool = True",
    "streamlit_import_required: bool = True",
    "ui_controls_added: bool = True",
    "ui_triggered_export_execution: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
EXPECTED_SEQUENCE = [
    "consume_supplied_prediction_system_result_mapping_only",
    "verify_target_hot_root_under_d_btc_ts_hot",
    "verify_target_role_prediction_system_result_snapshot",
    "verify_required_result_identity_fields",
    "record_observed_missing_hot_prediction_directory_context",
    "declare_future_non_ui_export_runner_requirements",
    "keep_runtime_artifact_write_false_in_this_contract",
    "keep_warroom_ui_trigger_false",
    "keep_approval_ledger_autotrade_broker_false",
    "return_export_preflight_contract_only",
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


def _sample_result() -> dict:
    return {
        "run_identity": {
            "prediction_run_id": "real_candidate_run_1",
            "generated_at": "2026-06-21T00:00:00Z",
            "market_uid": "BTC_JPY:bitFlyer",
        },
        "system_input": {"market_uid": "BTC_JPY:bitFlyer"},
        "outputs": [],
        "scenario_core": {"scenario_id": "scenario-1"},
        "gpt_review_digest": {},
        "read_only": True,
        "non_executing": True,
    }


def _assert_safe(packet: dict) -> None:
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["contract_only"] is True
    assert packet["supplied_payload_only"] is True
    assert packet["export_preflight_only"] is True
    for key in (
        "ready_for_warroom_ui_mount",
        "actual_export_runner_included",
        "runtime_artifact_write_allowed_by_this_contract",
        "runtime_artifact_write_performed_by_this_contract",
        "target_directory_created_by_this_contract",
        "target_file_written_by_this_contract",
        "hot_file_read_performed_by_this_contract",
        "payload_decode_performed_by_this_contract",
        "prediction_system_result_built_by_this_contract",
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "ui_triggered_export_execution",
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
    ):
        assert packet[key] is False, key


def test_ps_q9x_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION == "prediction_warroom_latest_payload_export_preflight_contract.ps_q9x.v1"
    assert TARGET_ARTIFACT_PATH_HINT == "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json"
    assert list(LATEST_PAYLOAD_EXPORT_PREFLIGHT_SEQUENCE) == EXPECTED_SEQUENCE


def test_ps_q9x_not_mounted_in_warroom_ui() -> None:
    assert "prediction_warroom_latest_payload_export_preflight_contract" not in WARROOM_PAGE.read_text(encoding="utf-8")


def test_ps_q9x_default_blocks_without_payload_or_ack() -> None:
    packet = build_prediction_warroom_latest_payload_export_preflight_contract().to_dict()
    assert packet["contract_state"] == "latest_payload_export_preflight_blocked"
    assert "operator_acknowledgement_required_before_future_non_ui_export_runner" in packet["blocked_reasons"]
    assert "prediction_system_result_payload_required_for_future_export" in packet["blocked_reasons"]
    assert packet["ready_for_future_non_ui_export_runner"] is False
    _assert_safe(packet)


def test_ps_q9x_ready_for_future_export_runner_with_supplied_payload_only() -> None:
    packet = build_prediction_warroom_latest_payload_export_preflight_contract(
        prediction_result_payload=_sample_result(),
        operator_acknowledged=True,
        observed_hot_prediction_dir_exists=False,
        observed_expected_artifact_exists=False,
        observed_candidate_json_count=0,
    ).to_dict()
    assert packet["contract_state"] == "latest_payload_export_preflight_ready_for_future_non_ui_export_runner"
    assert packet["ready_for_future_non_ui_export_runner"] is True
    assert packet["target_artifact_path_hint"] == "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json"
    assert packet["prediction_run_id"] == "real_candidate_run_1"
    assert "observed_hot_prediction_directory_missing_future_export_runner_must_create_it" in packet["warning_reasons"]
    assert "observed_expected_latest_prediction_result_artifact_missing" in packet["warning_reasons"]
    assert "observed_no_prediction_latest_json_candidates_under_hot_root" in packet["warning_reasons"]
    assert packet["blocked_reasons"] == []
    _assert_safe(packet)


def test_ps_q9x_rejects_wrong_root() -> None:
    packet = build_prediction_warroom_latest_payload_export_preflight_contract(
        prediction_result_payload=_sample_result(),
        hot_latest_root_hint="E:\\btc_ts",
        operator_acknowledged=True,
    ).to_dict()
    assert packet["contract_state"] == "latest_payload_export_preflight_blocked"
    assert "hot_latest_root_must_stay_under_D_btc_ts_hot" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9x_rejects_runtime_write_or_ui_requests_in_preflight() -> None:
    packet = build_prediction_warroom_latest_payload_export_preflight_contract(
        prediction_result_payload=_sample_result(),
        operator_acknowledged=True,
        requested_runtime_artifact_write=True,
        requested_warroom_ui_trigger=True,
        requested_approval_or_authorization=True,
        requested_ledger_append=True,
        requested_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "latest_payload_export_preflight_blocked"
    assert "runtime_artifact_write_not_allowed_by_preflight_contract_slice" in packet["blocked_reasons"]
    assert "warroom_ui_trigger_not_allowed_for_latest_payload_export" in packet["blocked_reasons"]
    assert "approval_or_authorization_not_allowed_for_latest_payload_export_preflight" in packet["blocked_reasons"]
    assert "ledger_append_not_allowed_for_latest_payload_export_preflight" in packet["blocked_reasons"]
    assert "autotrade_or_broker_not_allowed_for_latest_payload_export_preflight" in packet["blocked_reasons"]
    _assert_safe(packet)


def test_ps_q9x_rejects_incomplete_payload() -> None:
    packet = build_prediction_warroom_latest_payload_export_preflight_contract(
        prediction_result_payload={"run_identity": {"prediction_run_id": "run-only"}},
        operator_acknowledged=True,
    ).to_dict()
    assert packet["contract_state"] == "latest_payload_export_preflight_blocked"
    assert any(str(item).startswith("prediction_system_result_required_fields_missing:") for item in packet["blocked_reasons"])
    assert any(str(item).startswith("prediction_run_identity_required_fields_missing:") for item in packet["blocked_reasons"])
    _assert_safe(packet)


def main() -> int:
    test_ps_q9x_static_boundaries_and_markers()
    test_ps_q9x_not_mounted_in_warroom_ui()
    test_ps_q9x_default_blocks_without_payload_or_ack()
    test_ps_q9x_ready_for_future_export_runner_with_supplied_payload_only()
    test_ps_q9x_rejects_wrong_root()
    test_ps_q9x_rejects_runtime_write_or_ui_requests_in_preflight()
    test_ps_q9x_rejects_incomplete_payload()
    print("[OK] Prediction System PS-Q9X latest payload export preflight contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
