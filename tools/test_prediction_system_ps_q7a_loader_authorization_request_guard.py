# path: ./tools/test_prediction_system_ps_q7a_loader_authorization_request_guard.py
# desc: Guard for PS-Q7A latest payload loader authorization request contract. Request metadata only; no loader execution, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_authorization_request import (
    build_prediction_warroom_latest_payload_loader_authorization_request,
    build_prediction_warroom_latest_payload_loader_authorization_request_index,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_permission_contract import build_prediction_warroom_latest_payload_loader_permission_contract

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_authorization_request.py"
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
    "approval_granted_by_this_contract: bool = True",
    "authorization_granted_by_this_contract: bool = True",
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


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _assert_safe(payload: dict) -> None:
    assert payload["read_only"] is True
    assert payload["non_executing"] is True
    assert payload["display_only"] is True
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
    assert payload["approval_granted_by_this_contract"] is False
    assert payload["authorization_granted_by_this_contract"] is False
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["actual_payload_decode_allowed_by_this_contract"] is False
    assert payload["would_load_hot_latest_artifacts"] is False
    assert payload["would_read_runtime_file"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False


def test_ps_q7a_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_loader_authorization_request.ps_q7a.v1" in text
    assert "PredictionWarRoomLatestPayloadLoaderAuthorizationRequestPacket" in text
    assert "build_prediction_warroom_latest_payload_loader_authorization_request" in text
    assert "build_prediction_warroom_latest_payload_loader_authorization_request_index" in text
    assert "prepared_for_human_review_actual_read_disabled" in text
    assert "blocked_permission_contract_unsafe" in text


def test_ps_q7a_default_request_is_prepared_but_not_authorized() -> None:
    request = build_prediction_warroom_latest_payload_loader_authorization_request().to_dict()
    assert request["authorization_request_version"] == "prediction_warroom_latest_payload_loader_authorization_request.ps_q7a.v1"
    assert request["authorization_request_state"] == "prepared_for_human_review_actual_read_disabled"
    assert request["authorization_request_kind"] == "prediction_warroom_latest_payload_loader_authorization_request"
    assert request["permission_contract_version"] == "prediction_warroom_latest_payload_loader_permission_contract.ps_q6b.v1"
    assert request["loader_permission_state"] == "contract_only_actual_read_not_allowed"
    assert request["hot_latest_root_hint"] == "D:\\btc_ts_hot"
    assert request["request_ready_for_human_review"] is True
    assert request["permission_contract_safe_for_request"] is True
    assert request["approval_granted_by_this_contract"] is False
    assert request["authorization_granted_by_this_contract"] is False
    _assert_safe(request)


def test_ps_q7a_request_scopes_expected_artifacts_and_sequences() -> None:
    request = build_prediction_warroom_latest_payload_loader_authorization_request().to_dict()
    assert request["requested_artifact_roles"] == EXPECTED_ROLES
    assert request["requested_path_rule_count"] == 4
    assert request["required_artifact_count"] == 1
    assert request["optional_artifact_count"] == 3
    assert request["authorization_review_sequence"] == [
        "review_q6b_permission_contract",
        "verify_hot_latest_root_scope_is_d_btc_ts_hot",
        "verify_expected_artifact_roles_and_json_extensions",
        "verify_file_size_check_required_before_payload_parse",
        "verify_freshness_check_required_before_display",
        "verify_q5c_schema_validation_required_before_display",
        "verify_q6a_preflight_status_update_required",
        "verify_fail_closed_keep_last_good_packet_on_failure",
        "verify_no_runtime_write_no_autotrade_no_broker",
        "approve_future_loader_implementation_slice_separately",
    ]
    assert "do_not_execute_loader" in request["authorization_failure_behavior_sequence"]
    assert "do_not_read_hot_latest_file" in request["authorization_failure_behavior_sequence"]
    assert "do_not_decode_payload" in request["authorization_failure_behavior_sequence"]
    assert "path_scope_check_under_hot_latest_root" in request["inherited_validation_sequence"]
    assert "payload_decode_after_explicit_loader_authorization" in request["inherited_validation_sequence"]
    assert "do_not_trigger_autotrade" in request["inherited_failure_behavior_sequence"]


def test_ps_q7a_gates_approval_contract_summary_and_index_are_safe() -> None:
    request = build_prediction_warroom_latest_payload_loader_authorization_request().to_dict()
    index = build_prediction_warroom_latest_payload_loader_authorization_request_index()
    for payload in (request, index, request["authorization_gates"], request["approval_contract"], request["boundaries"], index["authorization_gates"], index["approval_contract"], index["boundaries"]):
        _assert_safe(payload)
    gates = request["authorization_gates"]
    assert gates["permission_contract_safe_for_request"] is True
    assert gates["schema_validation_required_before_display"] is True
    assert gates["q6a_preflight_status_update_required"] is True
    assert gates["separate_loader_implementation_slice_required"] is True
    assert gates["separate_loader_guard_required"] is True
    approval = request["approval_contract"]
    assert approval["human_review_required"] is True
    assert approval["human_approval_required_before_actual_read"] is True
    assert approval["future_approval_must_define_single_read_window"] is True
    assert approval["future_approval_must_not_enable_autotrade_or_broker"] is True
    summary = request["permission_contract_summary"]
    assert summary["path_rule_count"] == 4
    assert summary["actual_file_read_allowed_by_this_contract"] is False
    assert summary["runtime_file_read_enabled"] is False
    assert index["authorization_request_state"] == "prepared_for_human_review_actual_read_disabled"


def test_ps_q7a_unsafe_permission_contract_blocks_request() -> None:
    permission = build_prediction_warroom_latest_payload_loader_permission_contract().to_dict()
    permission["actual_file_read_allowed_by_this_contract"] = True
    request = build_prediction_warroom_latest_payload_loader_authorization_request(permission_contract=permission).to_dict()
    assert request["authorization_request_state"] == "blocked_permission_contract_unsafe"
    assert request["request_ready_for_human_review"] is False
    assert request["permission_contract_safe_for_request"] is False
    assert request["authorization_gates"]["permission_contract_safe_for_request"] is False
    assert request["approval_granted_by_this_contract"] is False
    assert request["authorization_granted_by_this_contract"] is False
    assert request["actual_loader_execution_allowed"] is False
    assert request["would_read_runtime_file"] is False


def test_ps_q7a_custom_hot_root_flows_without_enabling_read() -> None:
    request = build_prediction_warroom_latest_payload_loader_authorization_request(hot_latest_root_hint="D:\\btc_ts_hot_custom").to_dict()
    assert request["hot_latest_root_hint"] == "D:\\btc_ts_hot_custom"
    assert request["permission_contract_summary"]["hot_latest_root_hint"] == "D:\\btc_ts_hot_custom"
    assert all(path.startswith("D:\\btc_ts_hot_custom\\prediction\\") for path in request["permission_contract_summary"]["allowed_path_hints"])
    assert request["authorization_request_state"] == "prepared_for_human_review_actual_read_disabled"
    _assert_safe(request)


def main() -> int:
    test_ps_q7a_static_boundaries_and_markers()
    test_ps_q7a_default_request_is_prepared_but_not_authorized()
    test_ps_q7a_request_scopes_expected_artifacts_and_sequences()
    test_ps_q7a_gates_approval_contract_summary_and_index_are_safe()
    test_ps_q7a_unsafe_permission_contract_blocks_request()
    test_ps_q7a_custom_hot_root_flows_without_enabling_read()
    print("[OK] Prediction System PS-Q7A loader authorization request guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
