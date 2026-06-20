# path: ./tools/test_prediction_system_ps_q7k_supplemental_handoff_readiness_widget_group_guard.py
# desc: Guard for PS-Q7K supplemental handoff readiness widget group. Display grouping only; no registry mutation, approval write, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import build_prediction_warroom_handoff_catalog_visibility_entry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_readiness_summary import build_prediction_warroom_supplemental_handoff_readiness_summary
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_readiness_widget_groups import (
    build_prediction_warroom_supplemental_handoff_readiness_widget_group_index,
    build_prediction_warroom_supplemental_handoff_readiness_widget_group_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_readiness_widget_groups.py"
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


def _assert_q4b_packet_safe(payload: dict) -> None:
    assert payload["read_only"] is True
    assert payload["non_executing"] is True
    assert payload["display_only"] is True
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
    assert payload["would_collect_public_source"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False
    assert payload["broker_execution_requested"] is False
    assert payload["mode_apply_requested"] is False
    assert payload["command_ledger_append_requested"] is False
    assert payload["approval_append_requested"] is False


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


def test_ps_q7k_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_supplemental_handoff_readiness_widget_groups.ps_q7k.v1" in text
    assert "PredictionWarRoomSupplementalHandoffReadinessWidgetGroupIndex" in text
    assert "build_prediction_warroom_supplemental_handoff_readiness_widget_group_packet" in text
    assert "build_prediction_warroom_supplemental_handoff_readiness_widget_group_index" in text
    assert "does_not_register_into_q6f_registry_in_this_slice" in text


def test_ps_q7k_default_packet_wraps_q7j_summary() -> None:
    group = build_prediction_warroom_supplemental_handoff_readiness_widget_group_packet().to_dict()
    assert group["packet_version"] == "prediction_warroom_supplemental_handoff_readiness_widget_groups.ps_q7k.v1"
    assert group["widget_group_id"] == "prediction_supplemental_handoff_readiness_summary_widget"
    assert group["widget_group_kind"] == "supplemental_handoff_readiness_summary"
    assert group["refresh_interval_sec"] == 60
    assert group["refresh_priority"] == 62
    assert group["ui_mount_hint"] == "warroom_prediction:supplemental_handoff_readiness_summary"
    payload = group["payload"]
    assert payload["source_readiness_summary_version"] == "prediction_warroom_supplemental_handoff_readiness_summary.ps_q7j.v1"
    assert payload["readiness_state"] == "ready_supplemental_handoff_visible_loader_disabled"
    assert payload["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    assert payload["readiness_metrics"]["total_widget_group_count"] == 12
    assert payload["readiness_metrics"]["ready_widget_count"] == 6
    assert payload["readiness_metrics"]["blocker_count"] == 0
    assert len(payload["supplemental_chain_readiness"]) == 6
    _assert_q4b_packet_safe(group)
    _assert_safe(payload)


def test_ps_q7k_index_is_supplemental_and_safe() -> None:
    index = build_prediction_warroom_supplemental_handoff_readiness_widget_group_index().to_dict()
    assert index["index_version"] == "prediction_warroom_supplemental_handoff_readiness_widget_groups.ps_q7k.v1"
    assert index["supplemental_widget_group_count"] == 1
    assert index["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    assert index["supplemental_widget_group_order"] == ["prediction_supplemental_handoff_readiness_summary_widget"]
    assert len(index["widget_groups"]) == 1
    assert len(index["auto_refresh_groups"]) == 1
    group = index["widget_groups"][0]
    refresh = index["auto_refresh_groups"][0]
    contract = index["integration_contract"]
    assert group["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    assert refresh["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    assert contract["readiness_summary_contract"] == "prediction_warroom_supplemental_handoff_readiness_summary.ps_q7j.v1"
    assert contract["does_not_register_into_q6f_registry_in_this_slice"] is True
    assert contract["requires_runtime_loader"] is False
    assert contract["requires_hot_file_read"] is False
    assert contract["requires_payload_decode"] is False
    for payload in (index, group, group["payload"], refresh, contract):
        _assert_safe(payload)


def test_ps_q7k_custom_summary_flows_without_loader_or_approval() -> None:
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary().to_dict()
    summary = {**summary, "readiness_state": "blocked_supplemental_handoff_chain_mismatch_loader_disabled"}
    summary["readiness_metrics"] = {**summary["readiness_metrics"], "chain_ready": False, "blocker_count": 1}
    summary["readiness_blockers"] = [{"issue_code": "synthetic_chain_mismatch", "severity": "blocker", **{key: value for key, value in summary["boundaries"].items() if isinstance(value, bool)}}]
    group = build_prediction_warroom_supplemental_handoff_readiness_widget_group_packet(readiness_summary=summary).to_dict()
    assert group["payload"]["readiness_state"] == "blocked_supplemental_handoff_chain_mismatch_loader_disabled"
    assert group["payload"]["readiness_metrics"]["chain_ready"] is False
    assert group["payload"]["readiness_metrics"]["blocker_count"] == 1
    assert group["payload"]["approval_granted_by_this_contract"] is False
    assert group["payload"]["actual_file_read_allowed_by_this_contract"] is False
    _assert_q4b_packet_safe(group)
    _assert_safe(group["payload"])


def test_ps_q7k_catalog_entry_can_be_supplied_without_enabling_loader() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    entry["visibility_groups"] = [
        {**item, "attach_after_widget_group_id": "prediction_latest_payload_loader_authorization_widget"}
        if item["visibility_group_id"] == "prediction_warroom_authorization_handoff_status_visibility"
        else item
        for item in entry["visibility_groups"]
    ]
    index = build_prediction_warroom_supplemental_handoff_readiness_widget_group_index(catalog_entry=entry).to_dict()
    payload = index["widget_groups"][0]["payload"]
    assert payload["readiness_state"] == "blocked_supplemental_handoff_chain_mismatch_loader_disabled"
    assert payload["readiness_metrics"]["chain_ready"] is False
    assert any(item["issue_code"] == "unexpected_attach_after_widget_group_id" for item in payload["readiness_blockers"])
    assert payload["actual_loader_execution_allowed"] is False
    _assert_safe(index)
    _assert_safe(payload)


def main() -> int:
    test_ps_q7k_static_boundaries_and_markers()
    test_ps_q7k_default_packet_wraps_q7j_summary()
    test_ps_q7k_index_is_supplemental_and_safe()
    test_ps_q7k_custom_summary_flows_without_loader_or_approval()
    test_ps_q7k_catalog_entry_can_be_supplied_without_enabling_loader()
    print("[OK] Prediction System PS-Q7K supplemental handoff readiness widget group guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
