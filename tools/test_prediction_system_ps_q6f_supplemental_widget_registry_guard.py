# path: ./tools/test_prediction_system_ps_q6f_supplemental_widget_registry_guard.py
# desc: Guard for PS-Q6F Prediction WarRoom supplemental widget registry. Display grouping only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry import (
    build_prediction_warroom_supplemental_widget_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry.py"
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


def _sample_display_packet() -> dict:
    return build_prediction_warroom_sample_display_packet()


def test_ps_q6f_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_supplemental_widget_registry.ps_q6f.v1" in text
    assert "PredictionWarRoomSupplementalWidgetRegistryPacket" in text
    assert "build_prediction_warroom_supplemental_widget_registry" in text
    assert "composite_supplemental_widget_registry" in text
    assert "honor_each_supplemental_attach_after_widget_group_id" in text


def test_ps_q6f_default_registry_combines_q5b_q6e_and_q7b_safely() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    assert registry["registry_version"] == "prediction_warroom_supplemental_widget_registry.ps_q6f.v1"
    assert registry["registry_kind"] == "prediction_warroom_composite_supplemental_widget_registry"
    assert registry["base_widget_group_contract"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert registry["supplemental_index_count"] == 3
    assert registry["supplemental_widget_group_count"] == 3
    assert registry["supplemental_widget_group_order"] == ["source_quality_explanation_widgets", "prediction_latest_payload_dry_run_status_widget", "prediction_latest_payload_loader_authorization_widget"]
    assert len(registry["supplemental_indexes"]) == 3
    assert len(registry["auto_refresh_groups"]) == 3
    assert len(registry["widget_groups"]) == 3
    assert registry["actual_loader_execution_allowed"] is False
    assert registry["actual_file_read_allowed_by_this_contract"] is False
    assert registry["actual_payload_decode_allowed_by_this_contract"] is False
    assert registry["would_load_hot_latest_artifacts"] is False
    assert registry["would_read_runtime_file"] is False
    assert registry["would_write_runtime_artifact"] is False
    assert registry["would_send_to_broker"] is False
    assert registry["boundaries"]["would_read_runtime_file"] is False


def test_ps_q6f_auto_refresh_groups_preserve_attach_points() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    refresh_by_group = {item["widget_group_id"]: item for item in registry["auto_refresh_groups"]}
    assert refresh_by_group["source_quality_explanation_widgets"]["attach_after_widget_group_id"] == "source_quality_widget"
    assert refresh_by_group["prediction_latest_payload_dry_run_status_widget"]["attach_after_widget_group_id"] == "warning_refresh_widget"
    assert refresh_by_group["prediction_latest_payload_loader_authorization_widget"]["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    for item in refresh_by_group.values():
        assert item["would_read_runtime_file"] is False
        assert item["would_write_runtime_artifact"] is False
        assert item["would_send_to_broker"] is False
        assert item["actual_loader_execution_allowed"] is False


def test_ps_q6f_candidate_metadata_flows_only_to_dry_run_widget() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(
        display_packet=_sample_display_packet(),
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
        ),
    ).to_dict()
    widgets = {item["widget_group_id"]: item for item in registry["widget_groups"]}
    dry_run_payload = widgets["prediction_latest_payload_dry_run_status_widget"]["payload"]
    authorization_payload = widgets["prediction_latest_payload_loader_authorization_widget"]["payload"]
    explanation_payload = widgets["source_quality_explanation_widgets"]["payload"]
    assert dry_run_payload["panel_state"] == "candidate_visible_actual_loader_disabled"
    assert dry_run_payload["summary_metrics"]["candidate_artifact_count"] == 1
    assert dry_run_payload["actual_loader_execution_allowed"] is False
    assert dry_run_payload["actual_file_read_allowed_by_this_contract"] is False
    assert authorization_payload["authorization_request_state"] == "prepared_for_human_review_actual_read_disabled"
    assert authorization_payload["approval_granted_by_this_contract"] is False
    assert authorization_payload["actual_file_read_allowed_by_this_contract"] is False
    assert explanation_payload["not_loaded_as_runtime_display_source"] is True
    assert explanation_payload["would_read_runtime_file"] is False


def test_ps_q6f_include_flags_can_build_each_side_independently() -> None:
    only_q5b = build_prediction_warroom_supplemental_widget_registry(
        display_packet=_sample_display_packet(),
        include_latest_payload_dry_run=False,
        include_latest_payload_loader_authorization=False,
    ).to_dict()
    assert only_q5b["supplemental_widget_group_order"] == ["source_quality_explanation_widgets"]
    assert only_q5b["supplemental_index_count"] == 1
    only_q6e = build_prediction_warroom_supplemental_widget_registry(
        display_packet=_sample_display_packet(),
        include_source_quality_explanations=False,
    ).to_dict()
    assert only_q6e["supplemental_index_count"] == 2
    assert only_q6e["supplemental_widget_group_order"] == ["prediction_latest_payload_dry_run_status_widget", "prediction_latest_payload_loader_authorization_widget"]
    only_q7b = build_prediction_warroom_supplemental_widget_registry(
        display_packet=_sample_display_packet(),
        include_source_quality_explanations=False,
        include_latest_payload_dry_run=False,
    ).to_dict()
    assert only_q7b["supplemental_widget_group_order"] == ["prediction_latest_payload_loader_authorization_widget"]
    assert only_q7b["supplemental_index_count"] == 1
    assert only_q6e["actual_loader_execution_allowed"] is False
    assert only_q6e["would_read_runtime_file"] is False


def test_ps_q6f_integration_contract_is_composite_and_safe() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=_sample_display_packet()).to_dict()
    contract = registry["integration_contract"]
    assert contract["contract_version"] == "prediction_warroom_supplemental_widget_registry.ps_q6f.v1"
    assert contract["base_widget_group_contract"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert contract["source_quality_explanation_widget_contract"] == "prediction_warroom_explanation_widget_groups.ps_q5b.v1"
    assert contract["latest_payload_dry_run_widget_contract"] == "prediction_warroom_latest_payload_dry_run_widget_groups.ps_q6e.v1"
    assert contract["latest_payload_loader_authorization_widget_contract"] == "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1"
    assert contract["integration_kind"] == "composite_supplemental_widget_registry"
    assert contract["does_not_modify_base_q4b_group_order"] is True
    assert contract["requires_runtime_loader"] is False
    assert contract["requires_hot_file_read"] is False
    assert contract["requires_payload_decode"] is False
    assert contract["requires_streamlit_rendering"] is False
    assert contract["safe_to_render_without_side_effects"] is True
    assert contract["actual_loader_execution_allowed"] is False
    assert contract["actual_file_read_allowed_by_this_contract"] is False


def main() -> int:
    test_ps_q6f_static_boundaries_and_markers()
    test_ps_q6f_default_registry_combines_q5b_q6e_and_q7b_safely()
    test_ps_q6f_auto_refresh_groups_preserve_attach_points()
    test_ps_q6f_candidate_metadata_flows_only_to_dry_run_widget()
    test_ps_q6f_include_flags_can_build_each_side_independently()
    test_ps_q6f_integration_contract_is_composite_and_safe()
    print("[OK] Prediction System PS-Q6F supplemental widget registry guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
