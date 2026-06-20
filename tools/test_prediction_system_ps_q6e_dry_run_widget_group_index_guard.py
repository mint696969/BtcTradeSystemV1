# path: ./tools/test_prediction_system_ps_q6e_dry_run_widget_group_index_guard.py
# desc: Guard for PS-Q6E Prediction WarRoom latest-payload dry-run widget group index. Display grouping only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_dry_run_widget_groups import (
    build_prediction_warroom_latest_payload_dry_run_widget_group_index,
    build_prediction_warroom_latest_payload_dry_run_widget_group_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_dry_run_widget_groups.py"
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


def test_ps_q6e_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_dry_run_widget_groups.ps_q6e.v1" in text
    assert "PredictionWarRoomLatestPayloadDryRunWidgetGroupIndex" in text
    assert "build_prediction_warroom_latest_payload_dry_run_widget_group_packet" in text
    assert "build_prediction_warroom_latest_payload_dry_run_widget_group_index" in text
    assert "prediction_latest_payload_dry_run_status_widget" in text


def test_ps_q6e_default_widget_group_packet_is_display_only() -> None:
    group = build_prediction_warroom_latest_payload_dry_run_widget_group_packet().to_dict()
    assert group["packet_version"] == "prediction_warroom_latest_payload_dry_run_widget_groups.ps_q6e.v1"
    assert group["widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert group["widget_group_kind"] == "latest_payload_dry_run_status"
    assert group["refresh_group_id"] == "prediction_warroom:prediction_latest_payload_dry_run_status_widget"
    assert group["refresh_interval_sec"] == 30
    assert group["refresh_priority"] == 55
    assert group["payload"]["panel_state"] == "blocked_or_waiting_actual_loader_disabled"
    assert group["payload"]["actual_loader_execution_allowed"] is False
    assert group["payload"]["actual_file_read_allowed_by_this_contract"] is False
    assert group["payload"]["actual_payload_decode_allowed_by_this_contract"] is False
    assert group["payload"]["would_read_runtime_file"] is False
    assert group["payload"]["would_write_runtime_artifact"] is False
    assert group["would_write_runtime_artifact"] is False
    assert group["would_send_to_broker"] is False
    assert group["broker_execution_requested"] is False
    assert group["mode_apply_requested"] is False
    assert group["command_ledger_append_requested"] is False


def test_ps_q6e_index_registers_one_supplemental_auto_refresh_group() -> None:
    index = build_prediction_warroom_latest_payload_dry_run_widget_group_index().to_dict()
    assert index["index_version"] == "prediction_warroom_latest_payload_dry_run_widget_groups.ps_q6e.v1"
    assert index["supplemental_widget_group_count"] == 1
    assert index["attach_after_widget_group_id"] == "warning_refresh_widget"
    assert index["supplemental_widget_group_order"] == ["prediction_latest_payload_dry_run_status_widget"]
    assert len(index["widget_groups"]) == 1
    assert len(index["auto_refresh_groups"]) == 1
    refresh = index["auto_refresh_groups"][0]
    assert refresh["widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert refresh["attach_after_widget_group_id"] == "warning_refresh_widget"
    assert refresh["would_read_runtime_file"] is False
    assert refresh["would_write_runtime_artifact"] is False
    assert index["actual_loader_execution_allowed"] is False
    assert index["actual_file_read_allowed_by_this_contract"] is False
    assert index["actual_payload_decode_allowed_by_this_contract"] is False
    assert index["would_load_hot_latest_artifacts"] is False
    assert index["would_read_runtime_file"] is False
    assert index["would_write_runtime_artifact"] is False
    assert index["would_send_to_broker"] is False


def test_ps_q6e_candidate_metadata_flows_into_payload_without_enabling_loader() -> None:
    index = build_prediction_warroom_latest_payload_dry_run_widget_group_index(
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
    payload = index["widget_groups"][0]["payload"]
    assert payload["panel_state"] == "candidate_visible_actual_loader_disabled"
    assert payload["status_badge"]["badge_kind"] == "candidate_disabled"
    assert payload["summary_metrics"]["candidate_artifact_count"] == 1
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["would_read_runtime_file"] is False


def test_ps_q6e_integration_contract_is_supplemental_and_safe() -> None:
    index = build_prediction_warroom_latest_payload_dry_run_widget_group_index().to_dict()
    contract = index["integration_contract"]
    assert contract["contract_version"] == "prediction_warroom_latest_payload_dry_run_widget_groups.ps_q6e.v1"
    assert contract["dry_run_status_panel_contract"] == "prediction_warroom_latest_payload_dry_run_status_panel.ps_q6d.v1"
    assert contract["loader_dry_run_simulator_contract"] == "prediction_warroom_latest_payload_loader_dry_run_simulator.ps_q6c.v1"
    assert contract["integration_kind"] == "supplemental_widget_group_append_after_warning_refresh"
    assert contract["does_not_modify_base_q4b_group_order"] is True
    assert contract["requires_runtime_loader"] is False
    assert contract["requires_hot_file_read"] is False
    assert contract["requires_payload_decode"] is False
    assert contract["requires_streamlit_rendering"] is False
    assert contract["actual_loader_execution_allowed"] is False
    assert contract["actual_file_read_allowed_by_this_contract"] is False


def main() -> int:
    test_ps_q6e_static_boundaries_and_markers()
    test_ps_q6e_default_widget_group_packet_is_display_only()
    test_ps_q6e_index_registers_one_supplemental_auto_refresh_group()
    test_ps_q6e_candidate_metadata_flows_into_payload_without_enabling_loader()
    test_ps_q6e_integration_contract_is_supplemental_and_safe()
    print("[OK] Prediction System PS-Q6E dry-run widget group index guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
