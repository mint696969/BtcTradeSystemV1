# path: ./tools/test_prediction_system_ps_q6h_supplemental_handoff_bundle_guard.py
# desc: Guard for PS-Q6H Prediction WarRoom supplemental handoff bundle. Pure packaging only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_bundle import (
    build_prediction_warroom_supplemental_handoff_bundle,
    build_prediction_warroom_supplemental_handoff_bundle_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_bundle.py"
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


def test_ps_q6h_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_supplemental_handoff_bundle.ps_q6h.v1" in text
    assert "PredictionWarRoomSupplementalHandoffBundle" in text
    assert "build_prediction_warroom_supplemental_handoff_bundle" in text
    assert "build_prediction_warroom_supplemental_handoff_bundle_index" in text
    assert "ready_for_read_only_warroom_handoff" in text


def test_ps_q6h_default_bundle_is_ready_and_contains_expected_sections() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    assert bundle["handoff_bundle_version"] == "prediction_warroom_supplemental_handoff_bundle.ps_q6h.v1"
    assert bundle["handoff_state"] == "ready_for_read_only_warroom_handoff"
    assert bundle["handoff_kind"] == "prediction_warroom_read_only_supplemental_handoff_bundle"
    assert bundle["sample_bundle"]["sample_version"] == "prediction_warroom_sample_packets.ps_q4d.v1"
    assert bundle["display_packet"]["packet_version"] == "prediction_warroom_display_packet.ps_q4a.v1"
    assert bundle["base_widget_group_index"]["index_version"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert bundle["supplemental_widget_registry"]["registry_version"] == "prediction_warroom_supplemental_widget_registry.ps_q6f.v1"
    assert bundle["supplemental_registry_preflight_report"]["report_version"] == "prediction_warroom_supplemental_widget_registry_preflight.ps_q6g.v1"
    assert bundle["supplemental_registry_preflight_report"]["valid"] is True
    assert bundle["supplemental_registry_preflight_report"]["preflight_state"] == "ready_for_warroom_supplemental_handoff"
    assert bundle["handoff_index"]["base_widget_group_count"] == 6
    assert bundle["handoff_index"]["supplemental_widget_group_count"] == 3
    assert bundle["handoff_index"]["total_widget_group_count"] == 9


def test_ps_q6h_combined_order_appends_supplemental_after_base() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    order = bundle["handoff_index"]["combined_widget_group_order"]
    assert order[:6] == [
        "primary_signal_widget",
        "horizon_scenario_widgets",
        "family_detail_widgets",
        "source_quality_widget",
        "evidence_ledger_widget",
        "warning_refresh_widget",
    ]
    assert order[-3:] == ["source_quality_explanation_widgets", "prediction_latest_payload_dry_run_status_widget", "prediction_latest_payload_loader_authorization_widget"]
    assert bundle["supplemental_widget_registry"]["supplemental_widget_group_order"] == ["source_quality_explanation_widgets", "prediction_latest_payload_dry_run_status_widget", "prediction_latest_payload_loader_authorization_widget"]


def test_ps_q6h_bundle_and_index_are_safe() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    index = build_prediction_warroom_supplemental_handoff_bundle_index()
    for payload in (bundle, index, bundle["handoff_index"], bundle["integration_contract"], bundle["boundaries"]):
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
    assert index["handoff_state"] == "ready_for_read_only_warroom_handoff"
    assert index["preflight_valid"] is True
    assert index["total_widget_group_count"] == 9


def test_ps_q6h_candidate_metadata_flows_to_bundle_without_enabling_loader() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle(
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
    dry_run = {item["widget_group_id"]: item for item in bundle["supplemental_widget_registry"]["widget_groups"]}["prediction_latest_payload_dry_run_status_widget"]
    assert dry_run["payload"]["panel_state"] == "candidate_visible_actual_loader_disabled"
    assert dry_run["payload"]["summary_metrics"]["candidate_artifact_count"] == 1
    assert bundle["handoff_state"] == "ready_for_read_only_warroom_handoff"
    assert bundle["actual_loader_execution_allowed"] is False
    assert bundle["would_read_runtime_file"] is False


def test_ps_q6h_custom_display_packet_is_used_for_prediction_run_id() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle(
        display_packet={
            **build_prediction_warroom_supplemental_handoff_bundle().to_dict()["display_packet"],
            "prediction_run_id": "custom_prediction_run",
            "packet_id": "custom_packet",
        }
    ).to_dict()
    assert bundle["prediction_run_id"] == "custom_prediction_run"
    assert bundle["handoff_index"]["prediction_run_id"] == "custom_prediction_run"
    assert bundle["display_packet"]["packet_id"] == "custom_packet"


def main() -> int:
    test_ps_q6h_static_boundaries_and_markers()
    test_ps_q6h_default_bundle_is_ready_and_contains_expected_sections()
    test_ps_q6h_combined_order_appends_supplemental_after_base()
    test_ps_q6h_bundle_and_index_are_safe()
    test_ps_q6h_candidate_metadata_flows_to_bundle_without_enabling_loader()
    test_ps_q6h_custom_display_packet_is_used_for_prediction_run_id()
    print("[OK] Prediction System PS-Q6H supplemental handoff bundle guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
