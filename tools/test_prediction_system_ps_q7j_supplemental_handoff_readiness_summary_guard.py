# path: ./tools/test_prediction_system_ps_q7j_supplemental_handoff_readiness_summary_guard.py
# desc: Guard for PS-Q7J supplemental handoff readiness summary. Metadata derivation only; no registry mutation, approval write, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import build_prediction_warroom_handoff_catalog_visibility_entry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_bundle import build_prediction_warroom_supplemental_handoff_bundle
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_readiness_summary import (
    build_prediction_warroom_supplemental_handoff_readiness_summary,
    build_prediction_warroom_supplemental_handoff_readiness_summary_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_readiness_summary.py"
EXPECTED_ORDER = [
    "source_quality_explanation_widgets",
    "prediction_latest_payload_dry_run_status_widget",
    "prediction_latest_payload_loader_authorization_widget",
    "prediction_latest_payload_loader_authorization_registry_summary_widget",
    "prediction_authorization_handoff_status_widget",
    "prediction_supplemental_handoff_readiness_summary_widget",
]
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
    assert payload.get("approval_granted_by_this_contract", False) is False
    assert payload.get("authorization_granted_by_this_contract", False) is False
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["actual_payload_decode_allowed_by_this_contract"] is False
    assert payload["would_load_hot_latest_artifacts"] is False
    assert payload["would_read_runtime_file"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False


def test_ps_q7j_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_supplemental_handoff_readiness_summary.ps_q7j.v1" in text
    assert "PredictionWarRoomSupplementalHandoffReadinessSummary" in text
    assert "build_prediction_warroom_supplemental_handoff_readiness_summary" in text
    assert "ready_supplemental_handoff_visible_loader_disabled" in text
    assert "does_not_register_widgets" in text


def test_ps_q7j_default_summary_is_ready_for_registered_six_widget_chain() -> None:
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary().to_dict()
    assert summary["summary_version"] == "prediction_warroom_supplemental_handoff_readiness_summary.ps_q7j.v1"
    assert summary["readiness_state"] == "ready_supplemental_handoff_visible_loader_disabled"
    assert summary["visibility_state"] == "visible_read_only"
    assert summary["handoff_state"] == "ready_for_read_only_warroom_handoff"
    metrics = summary["readiness_metrics"]
    assert metrics["base_widget_group_count"] == 6
    assert metrics["supplemental_widget_group_count"] == 6
    assert metrics["total_widget_group_count"] == 12
    assert metrics["visibility_group_count"] == 7
    assert metrics["counts_ok"] is True
    assert metrics["chain_ready"] is True
    assert metrics["ready_widget_count"] == 6
    assert metrics["blocker_count"] == 0
    assert [item["widget_group_id"] for item in summary["supplemental_chain_readiness"]] == EXPECTED_ORDER
    assert all(item["ready"] is True for item in summary["supplemental_chain_readiness"])
    assert summary["readiness_blockers"] == []
    for payload in (summary, summary["boundaries"], summary["integration_contract"], *summary["supplemental_chain_readiness"]):
        _assert_safe(payload)


def test_ps_q7j_index_is_compact_and_safe() -> None:
    index = build_prediction_warroom_supplemental_handoff_readiness_summary_index()
    assert index["summary_index_version"] == "prediction_warroom_supplemental_handoff_readiness_summary.ps_q7j.v1"
    assert index["readiness_state"] == "ready_supplemental_handoff_visible_loader_disabled"
    assert index["readiness_metrics"]["total_widget_group_count"] == 12
    assert index["readiness_metrics"]["expected_supplemental_chain_length"] == 6
    assert len(index["supplemental_chain_readiness"]) == 6
    assert index["readiness_blockers"] == []
    for payload in (index, index["boundaries"], index["integration_contract"], *index["supplemental_chain_readiness"]):
        _assert_safe(payload)


def test_ps_q7j_blocked_catalog_hides_readiness_without_enabling_loader() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    bundle["handoff_state"] = "blocked_before_read_only_warroom_handoff"
    bundle["supplemental_registry_preflight_report"] = {**bundle["supplemental_registry_preflight_report"], "valid": False, "preflight_state": "blocked_before_warroom_supplemental_handoff"}
    entry = build_prediction_warroom_handoff_catalog_visibility_entry(handoff_bundle=bundle).to_dict()
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary(catalog_entry=entry).to_dict()
    assert summary["visibility_state"] == "hidden_blocked_by_preflight"
    assert summary["readiness_state"] == "hidden_or_blocked_supplemental_handoff_loader_disabled"
    assert summary["readiness_metrics"]["chain_ready"] is True
    assert summary["actual_loader_execution_allowed"] is False
    _assert_safe(summary)


def test_ps_q7j_missing_status_widget_blocks_chain() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    entry["combined_widget_group_order"] = [item for item in entry["combined_widget_group_order"] if item not in {"prediction_authorization_handoff_status_widget", "prediction_supplemental_handoff_readiness_summary_widget"}]
    entry["visibility_groups"] = [
        {**item, "widget_group_ids": []}
        if item["visibility_group_id"] in {"prediction_warroom_authorization_handoff_status_visibility", "prediction_warroom_supplemental_handoff_readiness_visibility"}
        else item
        for item in entry["visibility_groups"]
    ]
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary(catalog_entry=entry).to_dict()
    assert summary["readiness_state"] == "blocked_supplemental_handoff_chain_mismatch_loader_disabled"
    assert summary["readiness_metrics"]["chain_ready"] is False
    assert summary["readiness_metrics"]["blocker_count"] >= 2
    codes = {item["issue_code"] for item in summary["readiness_blockers"]}
    assert "widget_missing_from_combined_order" in codes
    assert "widget_missing_from_visibility_group" in codes
    _assert_safe(summary)


def test_ps_q7j_bad_attach_blocks_chain() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    entry["visibility_groups"] = [
        {**item, "attach_after_widget_group_id": "prediction_latest_payload_loader_authorization_widget"}
        if item["visibility_group_id"] == "prediction_warroom_authorization_handoff_status_visibility"
        else item
        for item in entry["visibility_groups"]
    ]
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary(catalog_entry=entry).to_dict()
    assert summary["readiness_state"] == "blocked_supplemental_handoff_chain_mismatch_loader_disabled"
    codes = {item["issue_code"] for item in summary["readiness_blockers"]}
    assert "unexpected_attach_after_widget_group_id" in codes
    assert summary["actual_file_read_allowed_by_this_contract"] is False
    _assert_safe(summary)


def main() -> int:
    test_ps_q7j_static_boundaries_and_markers()
    test_ps_q7j_default_summary_is_ready_for_registered_six_widget_chain()
    test_ps_q7j_index_is_compact_and_safe()
    test_ps_q7j_blocked_catalog_hides_readiness_without_enabling_loader()
    test_ps_q7j_missing_status_widget_blocks_chain()
    test_ps_q7j_bad_attach_blocks_chain()
    print("[OK] Prediction System PS-Q7J supplemental handoff readiness summary guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
