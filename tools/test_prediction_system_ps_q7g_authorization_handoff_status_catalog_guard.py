# path: ./tools/test_prediction_system_ps_q7g_authorization_handoff_status_catalog_guard.py
# desc: Guard for PS-Q7G authorization/supplemental handoff status catalog. Display-only status derivation; no approval write, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_authorization_handoff_status_catalog import (
    build_prediction_warroom_authorization_handoff_status_catalog,
    build_prediction_warroom_authorization_handoff_status_catalog_index,
)
from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import build_prediction_warroom_handoff_catalog_visibility_entry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_bundle import build_prediction_warroom_supplemental_handoff_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_authorization_handoff_status_catalog.py"
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


def test_ps_q7g_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_authorization_handoff_status_catalog.ps_q7g.v1" in text
    assert "PredictionWarRoomAuthorizationHandoffStatusCatalog" in text
    assert "build_prediction_warroom_authorization_handoff_status_catalog" in text
    assert "ready_authorization_handoff_status_visible_loader_disabled" in text
    assert "does_not_register_widgets" in text


def test_ps_q7g_default_catalog_summarizes_q7i_handoff() -> None:
    catalog = build_prediction_warroom_authorization_handoff_status_catalog().to_dict()
    assert catalog["catalog_version"] == "prediction_warroom_authorization_handoff_status_catalog.ps_q7g.v1"
    assert catalog["status_state"] == "ready_authorization_handoff_status_visible_loader_disabled"
    assert catalog["visibility_state"] == "visible_read_only"
    assert catalog["handoff_state"] == "ready_for_read_only_warroom_handoff"
    assert catalog["summary_metrics"]["base_widget_group_count"] == 6
    assert catalog["summary_metrics"]["supplemental_widget_group_count"] == 6
    assert catalog["summary_metrics"]["total_widget_group_count"] == 12
    assert catalog["summary_metrics"]["visibility_group_count"] == 7
    assert catalog["summary_metrics"]["counts_ok"] is True
    assert catalog["summary_metrics"]["authorization_widget_present"] is True
    assert catalog["summary_metrics"]["authorization_registry_summary_widget_present"] is True
    assert catalog["summary_metrics"]["authorization_chain_order_ok"] is True
    assert catalog["authorization_chain"]["authorization_chain_ready"] is True
    assert catalog["authorization_chain"]["combined_widget_group_order_tail"] == [
        "source_quality_explanation_widgets",
        "prediction_latest_payload_dry_run_status_widget",
        "prediction_latest_payload_loader_authorization_widget",
        "prediction_latest_payload_loader_authorization_registry_summary_widget",
        "prediction_authorization_handoff_status_widget",
        "prediction_supplemental_handoff_readiness_summary_widget",
    ]
    for payload in (catalog, catalog["boundaries"], catalog["integration_contract"], catalog["authorization_chain"], *catalog["visibility_group_summaries"]):
        _assert_safe(payload)


def test_ps_q7g_index_is_compact_and_safe() -> None:
    index = build_prediction_warroom_authorization_handoff_status_catalog_index()
    assert index["catalog_index_version"] == "prediction_warroom_authorization_handoff_status_catalog.ps_q7g.v1"
    assert index["status_state"] == "ready_authorization_handoff_status_visible_loader_disabled"
    assert index["summary_metrics"]["total_widget_group_count"] == 12
    assert index["authorization_chain"]["authorization_registry_summary_attach_after_widget_group_id"] == "prediction_latest_payload_loader_authorization_widget"
    assert len(index["visibility_group_summaries"]) == 2
    for payload in (index, index["boundaries"], index["integration_contract"], index["authorization_chain"], *index["visibility_group_summaries"]):
        _assert_safe(payload)


def test_ps_q7g_blocked_bundle_hides_status_without_enabling_loader() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    bundle["handoff_state"] = "blocked_before_read_only_warroom_handoff"
    bundle["supplemental_registry_preflight_report"] = {**bundle["supplemental_registry_preflight_report"], "valid": False, "preflight_state": "blocked_before_warroom_supplemental_handoff"}
    entry = build_prediction_warroom_handoff_catalog_visibility_entry(handoff_bundle=bundle).to_dict()
    catalog = build_prediction_warroom_authorization_handoff_status_catalog(catalog_entry=entry).to_dict()
    assert catalog["visibility_state"] == "hidden_blocked_by_preflight"
    assert catalog["status_state"] == "hidden_or_blocked_authorization_handoff_status_loader_disabled"
    assert catalog["summary_metrics"]["authorization_widget_present"] is True
    assert catalog["summary_metrics"]["authorization_registry_summary_widget_present"] is True
    _assert_safe(catalog)


def test_ps_q7g_missing_summary_visibility_blocks_status() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    entry["visibility_groups"] = [item for item in entry["visibility_groups"] if item["visibility_group_id"] != "prediction_warroom_loader_authorization_registry_summary_visibility"]
    catalog = build_prediction_warroom_authorization_handoff_status_catalog(catalog_entry=entry).to_dict()
    assert catalog["status_state"] == "blocked_authorization_summary_widget_missing_loader_disabled"
    assert catalog["summary_metrics"]["authorization_registry_summary_widget_present"] is False
    assert catalog["summary_metrics"]["actual_loader_execution_allowed"] is False
    _assert_safe(catalog)


def test_ps_q7g_bad_summary_attach_blocks_status() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    groups = []
    for group in entry["visibility_groups"]:
        if group["visibility_group_id"] == "prediction_warroom_loader_authorization_registry_summary_visibility":
            group = {**group, "attach_after_widget_group_id": "prediction_latest_payload_dry_run_status_widget"}
        groups.append(group)
    entry["visibility_groups"] = groups
    catalog = build_prediction_warroom_authorization_handoff_status_catalog(catalog_entry=entry).to_dict()
    assert catalog["status_state"] == "blocked_authorization_widget_chain_attach_mismatch_loader_disabled"
    assert catalog["summary_metrics"]["authorization_registry_summary_attach_ok"] is False
    _assert_safe(catalog)


def main() -> int:
    test_ps_q7g_static_boundaries_and_markers()
    test_ps_q7g_default_catalog_summarizes_q7i_handoff()
    test_ps_q7g_index_is_compact_and_safe()
    test_ps_q7g_blocked_bundle_hides_status_without_enabling_loader()
    test_ps_q7g_missing_summary_visibility_blocks_status()
    test_ps_q7g_bad_summary_attach_blocks_status()
    print("[OK] Prediction System PS-Q7G authorization handoff status catalog guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
