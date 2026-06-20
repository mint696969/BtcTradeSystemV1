# path: ./tools/test_prediction_system_ps_q7b_loader_authorization_widget_group_guard.py
# desc: Guard for PS-Q7B latest payload loader authorization request widget group. Display metadata only; no approval write, loader execution, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_authorization_request import build_prediction_warroom_latest_payload_loader_authorization_request
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_authorization_widget_groups import (
    build_prediction_warroom_latest_payload_loader_authorization_widget_group_index,
    build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_permission_contract import build_prediction_warroom_latest_payload_loader_permission_contract

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_authorization_widget_groups.py"
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


def test_ps_q7b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1" in text
    assert "PredictionWarRoomLatestPayloadLoaderAuthorizationWidgetGroupIndex" in text
    assert "build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet" in text
    assert "build_prediction_warroom_latest_payload_loader_authorization_widget_group_index" in text
    assert "prediction_latest_payload_loader_authorization_widget" in text


def test_ps_q7b_default_widget_packet_wraps_q7a_request() -> None:
    group = build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet().to_dict()
    payload = group["payload"]
    assert group["packet_version"] == "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1"
    assert group["widget_group_id"] == "prediction_latest_payload_loader_authorization_widget"
    assert group["widget_group_kind"] == "latest_payload_loader_authorization_status"
    assert group["refresh_group_id"] == "prediction_warroom:prediction_latest_payload_loader_authorization_widget"
    assert group["refresh_interval_sec"] == 60
    assert group["refresh_priority"] == 58
    assert group["ui_mount_hint"] == "warroom_prediction:latest_payload_loader_authorization_status"
    assert payload["source_authorization_request_version"] == "prediction_warroom_latest_payload_loader_authorization_request.ps_q7a.v1"
    assert payload["authorization_request_state"] == "prepared_for_human_review_actual_read_disabled"
    assert payload["status_badge"]["badge_kind"] == "review_ready_loader_disabled"
    assert payload["summary_metrics"]["requested_path_rule_count"] == 4
    assert payload["summary_metrics"]["required_artifact_count"] == 1
    assert payload["summary_metrics"]["optional_artifact_count"] == 3
    _assert_safe(payload)
    _assert_safe(payload["status_badge"])


def test_ps_q7b_index_appends_after_dry_run_widget_and_is_safe() -> None:
    index = build_prediction_warroom_latest_payload_loader_authorization_widget_group_index().to_dict()
    assert index["index_version"] == "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1"
    assert index["supplemental_widget_group_count"] == 1
    assert index["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert index["supplemental_widget_group_order"] == ["prediction_latest_payload_loader_authorization_widget"]
    assert len(index["widget_groups"]) == 1
    assert len(index["auto_refresh_groups"]) == 1
    group = index["widget_groups"][0]
    refresh = index["auto_refresh_groups"][0]
    assert refresh["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert refresh["refresh_group_id"] == group["refresh_group_id"]
    assert "q7a.latest_payload_loader_authorization_request" in refresh["data_dependencies"]
    for payload in (index, group, group["payload"], refresh, index["integration_contract"]):
        _assert_safe(payload)
    assert index["integration_contract"]["does_not_grant_approval"] is True
    assert index["integration_contract"]["does_not_grant_authorization"] is True
    assert index["integration_contract"]["requires_hot_file_read"] is False
    assert index["integration_contract"]["requires_payload_decode"] is False


def test_ps_q7b_review_and_failure_cards_are_display_only() -> None:
    group = build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet().to_dict()
    payload = group["payload"]
    assert len(payload["authorization_review_cards"]) == 10
    assert len(payload["authorization_failure_behavior_cards"]) == 10
    assert payload["authorization_review_cards"][0]["review_item"] == "review_q6b_permission_contract"
    assert payload["authorization_failure_behavior_cards"][0]["failure_behavior"] == "do_not_execute_loader"
    for card in payload["authorization_review_cards"] + payload["authorization_failure_behavior_cards"]:
        _assert_safe(card)


def test_ps_q7b_blocked_authorization_request_uses_blocked_badge_without_enabling_loader() -> None:
    permission = build_prediction_warroom_latest_payload_loader_permission_contract().to_dict()
    permission["actual_file_read_allowed_by_this_contract"] = True
    request = build_prediction_warroom_latest_payload_loader_authorization_request(permission_contract=permission).to_dict()
    group = build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet(authorization_request=request).to_dict()
    payload = group["payload"]
    assert payload["authorization_request_state"] == "blocked_permission_contract_unsafe"
    assert payload["status_badge"]["badge_kind"] == "blocked_loader_disabled"
    assert payload["summary_metrics"]["request_ready_for_human_review"] is False
    assert payload["summary_metrics"]["permission_contract_safe_for_request"] is False
    _assert_safe(payload)


def test_ps_q7b_custom_hot_root_flows_without_read() -> None:
    group = build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet(hot_latest_root_hint="D:\\btc_ts_hot_custom").to_dict()
    payload = group["payload"]
    assert payload["permission_contract_summary"]["hot_latest_root_hint"] == "D:\\btc_ts_hot_custom"
    assert payload["authorization_request_state"] == "prepared_for_human_review_actual_read_disabled"
    _assert_safe(payload)


def main() -> int:
    test_ps_q7b_static_boundaries_and_markers()
    test_ps_q7b_default_widget_packet_wraps_q7a_request()
    test_ps_q7b_index_appends_after_dry_run_widget_and_is_safe()
    test_ps_q7b_review_and_failure_cards_are_display_only()
    test_ps_q7b_blocked_authorization_request_uses_blocked_badge_without_enabling_loader()
    test_ps_q7b_custom_hot_root_flows_without_read()
    print("[OK] Prediction System PS-Q7B loader authorization widget group guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
