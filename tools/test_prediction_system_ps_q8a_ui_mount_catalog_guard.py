# path: ./tools/test_prediction_system_ps_q8a_ui_mount_catalog_guard.py
# desc: Guard for PS-Q8A Prediction WarRoom UI mount catalog. Mount planning metadata only; no rendering, page mutation, runtime reads, payload decode, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import build_prediction_warroom_handoff_catalog_visibility_entry
from btcts.apps.operator_ui.components.prediction_warroom_ui_mount_catalog import (
    build_prediction_warroom_ui_mount_catalog,
    build_prediction_warroom_ui_mount_catalog_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_ui_mount_catalog.py"
EXPECTED_ORDER = [
    "primary_signal_widget",
    "horizon_scenario_widgets",
    "family_detail_widgets",
    "source_quality_widget",
    "evidence_ledger_widget",
    "warning_refresh_widget",
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
    "streamlit_render_allowed: bool = True",
    "page_mutation_allowed: bool = True",
    "app_routing_mutation_allowed: bool = True",
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


def _assert_safe(payload: dict) -> None:
    assert payload["read_only"] is True
    assert payload["non_executing"] is True
    assert payload["display_only"] is True
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
    assert payload["streamlit_render_allowed"] is False
    assert payload["page_mutation_allowed"] is False
    assert payload["app_routing_mutation_allowed"] is False
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["actual_payload_decode_allowed_by_this_contract"] is False
    assert payload["would_load_hot_latest_artifacts"] is False
    assert payload["would_read_runtime_file"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False


def test_ps_q8a_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_ui_mount_catalog.ps_q8a.v1" in text
    assert "PredictionWarRoomUIMountCatalog" in text
    assert "build_prediction_warroom_ui_mount_catalog" in text
    assert "build_prediction_warroom_ui_mount_catalog_index" in text
    assert "does_not_call_streamlit" in text
    assert "does_not_mutate_warroom_page" in text


def test_ps_q8a_default_catalog_maps_all_twelve_widgets_without_rendering() -> None:
    catalog = build_prediction_warroom_ui_mount_catalog().to_dict()
    assert catalog["catalog_version"] == "prediction_warroom_ui_mount_catalog.ps_q8a.v1"
    assert catalog["mount_state"] == "ready_for_ui_mount_catalog_connection_render_disabled"
    assert catalog["visibility_state"] == "visible_read_only"
    assert catalog["handoff_state"] == "ready_for_read_only_warroom_handoff"
    assert catalog["base_widget_group_count"] == 6
    assert catalog["supplemental_widget_group_count"] == 6
    assert catalog["total_widget_group_count"] == 12
    assert catalog["visibility_group_count"] == 7
    assert catalog["mount_entry_count"] == 12
    assert [item["widget_group_id"] for item in catalog["mount_entries"]] == EXPECTED_ORDER
    assert catalog["mount_blockers"] == []
    metrics = catalog["mount_metrics"]
    assert metrics["counts_ok"] is True
    assert metrics["mount_entries_ready"] is True
    assert metrics["base_mount_entry_count"] == 6
    assert metrics["supplemental_mount_entry_count"] == 6
    assert metrics["mount_blocker_count"] == 0
    for payload in (catalog, catalog["boundaries"], catalog["integration_contract"], *catalog["mount_entries"]):
        _assert_safe(payload)


def test_ps_q8a_mount_entries_keep_expected_attach_and_zones() -> None:
    catalog = build_prediction_warroom_ui_mount_catalog().to_dict()
    entries = {item["widget_group_id"]: item for item in catalog["mount_entries"]}
    assert entries["source_quality_explanation_widgets"]["attach_after_widget_group_id"] == "source_quality_widget"
    assert entries["prediction_latest_payload_dry_run_status_widget"]["attach_after_widget_group_id"] == "warning_refresh_widget"
    assert entries["prediction_latest_payload_loader_authorization_widget"]["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert entries["prediction_latest_payload_loader_authorization_registry_summary_widget"]["attach_after_widget_group_id"] == "prediction_latest_payload_loader_authorization_widget"
    assert entries["prediction_authorization_handoff_status_widget"]["attach_after_widget_group_id"] == "prediction_latest_payload_loader_authorization_registry_summary_widget"
    assert entries["prediction_supplemental_handoff_readiness_summary_widget"]["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    assert entries["primary_signal_widget"]["mount_zone_id"] == "overview"
    assert entries["source_quality_widget"]["mount_zone_id"] == "primary_live"
    assert entries["prediction_supplemental_handoff_readiness_summary_widget"]["mount_zone_id"] == "operator_support"
    assert all(item["render_call_allowed_in_this_slice"] is False for item in entries.values())


def test_ps_q8a_index_is_compact_and_safe() -> None:
    index = build_prediction_warroom_ui_mount_catalog_index()
    assert index["mount_catalog_index_version"] == "prediction_warroom_ui_mount_catalog.ps_q8a.v1"
    assert index["mount_state"] == "ready_for_ui_mount_catalog_connection_render_disabled"
    assert index["mount_entry_count"] == 12
    assert index["mount_metrics"]["counts_ok"] is True
    assert index["mount_blockers"] == []
    assert index["integration_contract"]["requires_streamlit_rendering"] is False
    for payload in (index, index["boundaries"], index["integration_contract"], *index["mount_entries"]):
        _assert_safe(payload)


def test_ps_q8a_blocked_visibility_blocks_mount_without_rendering() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    entry["visibility_state"] = "hidden_blocked_by_preflight"
    entry["handoff_state"] = "blocked_before_read_only_warroom_handoff"
    catalog = build_prediction_warroom_ui_mount_catalog(catalog_entry=entry).to_dict()
    assert catalog["mount_state"] == "blocked_before_ui_mount_catalog_connection_render_disabled"
    assert catalog["mount_metrics"]["counts_ok"] is True
    assert catalog["mount_metrics"]["mount_entries_ready"] is True
    assert catalog["streamlit_render_allowed"] is False
    _assert_safe(catalog)


def test_ps_q8a_missing_visibility_group_blocks_specific_widget() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    entry["visibility_groups"] = [
        item
        for item in entry["visibility_groups"]
        if item["visibility_group_id"] != "prediction_warroom_supplemental_handoff_readiness_visibility"
    ]
    entry["visibility_group_count"] = 6
    catalog = build_prediction_warroom_ui_mount_catalog(catalog_entry=entry).to_dict()
    assert catalog["mount_state"] == "blocked_before_ui_mount_catalog_connection_render_disabled"
    assert catalog["mount_metrics"]["counts_ok"] is False
    assert any(item["issue_code"] == "widget_missing_visibility_group" for item in catalog["mount_blockers"])
    entries = {item["widget_group_id"]: item for item in catalog["mount_entries"]}
    assert entries["prediction_supplemental_handoff_readiness_summary_widget"]["mount_state"] == "mount_blocked_missing_visibility_or_attach_target"
    _assert_safe(catalog)


def main() -> int:
    test_ps_q8a_static_boundaries_and_markers()
    test_ps_q8a_default_catalog_maps_all_twelve_widgets_without_rendering()
    test_ps_q8a_mount_entries_keep_expected_attach_and_zones()
    test_ps_q8a_index_is_compact_and_safe()
    test_ps_q8a_blocked_visibility_blocks_mount_without_rendering()
    test_ps_q8a_missing_visibility_group_blocks_specific_widget()
    print("[OK] Prediction System PS-Q8A UI mount catalog guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
