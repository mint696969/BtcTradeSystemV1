# path: ./tools/test_prediction_system_ps_q6i_handoff_catalog_visibility_guard.py
# desc: Guard for PS-Q6I Prediction WarRoom handoff catalog visibility contract. Discovery metadata only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import (
    build_prediction_warroom_handoff_catalog_visibility_entry,
    build_prediction_warroom_handoff_catalog_visibility_index,
)
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_bundle import build_prediction_warroom_supplemental_handoff_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_handoff_catalog_visibility.py"
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


def _assert_safe(payload: dict) -> None:
    assert payload["read_only"] is True
    assert payload["non_executing"] is True
    assert payload["display_only"] is True
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["actual_payload_decode_allowed_by_this_contract"] is False
    assert payload["would_load_hot_latest_artifacts"] is False
    assert payload["would_read_runtime_file"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False


def test_ps_q6i_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_handoff_catalog_visibility.ps_q6i.v1" in text
    assert "PredictionWarRoomHandoffCatalogVisibilityEntry" in text
    assert "build_prediction_warroom_handoff_catalog_visibility_entry" in text
    assert "build_prediction_warroom_handoff_catalog_visibility_index" in text
    assert "visible_read_only" in text
    assert "hidden_blocked_by_preflight" in text


def test_ps_q6i_default_entry_is_visible_and_indexes_q6h_bundle() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    assert entry["catalog_version"] == "prediction_warroom_handoff_catalog_visibility.ps_q6i.v1"
    assert entry["catalog_entry_kind"] == "prediction_warroom_read_only_handoff_visibility_contract"
    assert entry["visibility_state"] == "visible_read_only"
    assert entry["handoff_bundle_version"] == "prediction_warroom_supplemental_handoff_bundle.ps_q6h.v1"
    assert entry["handoff_state"] == "ready_for_read_only_warroom_handoff"
    assert entry["consumer_hint"] == "WarRoom"
    assert entry["visibility_group_count"] == 6
    assert entry["base_widget_group_count"] == 6
    assert entry["supplemental_widget_group_count"] == 5
    assert entry["total_widget_group_count"] == 11
    assert len(entry["combined_widget_group_order"]) == 11
    assert entry["combined_widget_group_order"][-5:] == ["source_quality_explanation_widgets", "prediction_latest_payload_dry_run_status_widget", "prediction_latest_payload_loader_authorization_widget", "prediction_latest_payload_loader_authorization_registry_summary_widget", "prediction_authorization_handoff_status_widget"]


def test_ps_q6i_visibility_groups_have_expected_mount_and_attach_contracts() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    groups = {item["visibility_group_id"]: item for item in entry["visibility_groups"]}
    assert groups["prediction_warroom_base_widget_groups_visibility"]["widget_group_count"] == 6
    assert groups["prediction_warroom_base_widget_groups_visibility"]["attach_after_widget_group_id"] is None
    assert groups["prediction_warroom_base_widget_groups_visibility"]["order_strategy"] == "render_in_q4b_base_widget_group_order"
    assert groups["prediction_warroom_source_explanation_visibility"]["widget_group_ids"] == ["source_quality_explanation_widgets"]
    assert groups["prediction_warroom_source_explanation_visibility"]["attach_after_widget_group_id"] == "source_quality_widget"
    assert groups["prediction_warroom_latest_payload_dry_run_visibility"]["widget_group_ids"] == ["prediction_latest_payload_dry_run_status_widget"]
    assert groups["prediction_warroom_latest_payload_dry_run_visibility"]["attach_after_widget_group_id"] == "warning_refresh_widget"
    assert groups["prediction_warroom_loader_authorization_visibility"]["widget_group_ids"] == ["prediction_latest_payload_loader_authorization_widget"]
    assert groups["prediction_warroom_loader_authorization_visibility"]["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert groups["prediction_warroom_loader_authorization_registry_summary_visibility"]["widget_group_ids"] == ["prediction_latest_payload_loader_authorization_registry_summary_widget"]
    assert groups["prediction_warroom_loader_authorization_registry_summary_visibility"]["attach_after_widget_group_id"] == "prediction_latest_payload_loader_authorization_widget"
    assert groups["prediction_warroom_authorization_handoff_status_visibility"]["widget_group_ids"] == ["prediction_authorization_handoff_status_widget"]
    assert groups["prediction_warroom_authorization_handoff_status_visibility"]["attach_after_widget_group_id"] == "prediction_latest_payload_loader_authorization_registry_summary_widget"
    for group in groups.values():
        _assert_safe(group)
        assert group["visibility_state_when_handoff_ready"] == "visible_read_only"
        assert group["visibility_state_when_handoff_blocked"] == "hidden_blocked_by_preflight"


def test_ps_q6i_entry_index_and_contract_are_safe() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    index = build_prediction_warroom_handoff_catalog_visibility_index()
    for payload in (entry, index, entry["integration_contract"], entry["boundaries"], index["integration_contract"], index["boundaries"]):
        _assert_safe(payload)
    assert entry["integration_contract"]["catalog_entry_discovery_only"] is True
    assert entry["integration_contract"]["does_not_modify_handoff_bundle_payloads"] is True
    assert entry["integration_contract"]["requires_runtime_loader"] is False
    assert entry["integration_contract"]["requires_hot_file_read"] is False
    assert entry["integration_contract"]["requires_payload_decode"] is False
    assert entry["integration_contract"]["requires_streamlit_rendering"] is False
    assert index["visibility_state"] == "visible_read_only"
    assert index["total_widget_group_count"] == 11


def test_ps_q6i_blocked_bundle_hides_catalog_entry_without_side_effects() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    bundle["handoff_state"] = "blocked_before_read_only_warroom_handoff"
    bundle["supplemental_registry_preflight_report"] = {**bundle["supplemental_registry_preflight_report"], "valid": False, "preflight_state": "blocked_before_warroom_supplemental_handoff"}
    entry = build_prediction_warroom_handoff_catalog_visibility_entry(handoff_bundle=bundle).to_dict()
    assert entry["visibility_state"] == "hidden_blocked_by_preflight"
    assert entry["handoff_state"] == "blocked_before_read_only_warroom_handoff"
    assert entry["base_widget_group_count"] == 6
    assert entry["supplemental_widget_group_count"] == 5
    _assert_safe(entry)
    _assert_safe(entry["integration_contract"])


def test_ps_q6i_candidate_metadata_keeps_catalog_visible_without_loader() -> None:
    entry = build_prediction_warroom_handoff_catalog_visibility_entry(
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
        )
    ).to_dict()
    assert entry["visibility_state"] == "visible_read_only"
    assert entry["total_widget_group_count"] == 11
    _assert_safe(entry)


def main() -> int:
    test_ps_q6i_static_boundaries_and_markers()
    test_ps_q6i_default_entry_is_visible_and_indexes_q6h_bundle()
    test_ps_q6i_visibility_groups_have_expected_mount_and_attach_contracts()
    test_ps_q6i_entry_index_and_contract_are_safe()
    test_ps_q6i_blocked_bundle_hides_catalog_entry_without_side_effects()
    test_ps_q6i_candidate_metadata_keeps_catalog_visible_without_loader()
    print("[OK] Prediction System PS-Q6I handoff catalog visibility guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
