# path: ./tools/test_prediction_system_ps_q8b_ui_mount_presenter_guard.py
# desc: Guard for PS-Q8B Prediction WarRoom UI mount presenter packet. Presentation metadata only; no rendering, page mutation, runtime reads, payload decode, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_ui_mount_catalog import build_prediction_warroom_ui_mount_catalog
from btcts.apps.operator_ui.components.prediction_warroom_ui_mount_presenter import (
    build_prediction_warroom_ui_mount_presenter_index,
    build_prediction_warroom_ui_mount_presenter_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_ui_mount_presenter.py"
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
    "ui_rendering_allowed: bool = True",
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
    assert payload["ui_rendering_allowed"] is False
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


def test_ps_q8b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_ui_mount_presenter.ps_q8b.v1" in text
    assert "PredictionWarRoomUIMountPresenterPacket" in text
    assert "build_prediction_warroom_ui_mount_presenter_packet" in text
    assert "build_prediction_warroom_ui_mount_presenter_index" in text
    assert "does_not_call_streamlit" in text
    assert "does_not_mutate_warroom_page" in text


def test_ps_q8b_default_presenter_packet_is_ready_and_display_only() -> None:
    packet = build_prediction_warroom_ui_mount_presenter_packet().to_dict()
    assert packet["presenter_version"] == "prediction_warroom_ui_mount_presenter.ps_q8b.v1"
    assert packet["mount_catalog_version"] == "prediction_warroom_ui_mount_catalog.ps_q8a.v1"
    assert packet["display_state"] == "ready_for_operator_review_render_disabled"
    assert packet["mount_state"] == "ready_for_ui_mount_catalog_connection_render_disabled"
    assert packet["zone_section_count"] == 3
    assert packet["mount_entry_row_count"] == 12
    assert packet["blocked_entry_row_count"] == 0
    assert [item["widget_group_id"] for item in packet["mount_entry_rows"]] == EXPECTED_ORDER
    assert packet["compact_line"] == "prediction_warroom_ui_mount_presenter=ready:true;entries:12;zones:3;blocked:0;render:false;page_mutation:false"
    metrics = packet["presenter_metrics"]
    assert metrics["presenter_ready"] is True
    assert metrics["base_entry_row_count"] == 6
    assert metrics["supplemental_entry_row_count"] == 6
    for payload in (packet, packet["boundaries"], packet["integration_contract"], *packet["mount_entry_rows"], *packet["zone_sections"]):
        _assert_safe(payload)


def test_ps_q8b_zone_sections_are_stable_and_grouped() -> None:
    packet = build_prediction_warroom_ui_mount_presenter_packet().to_dict()
    sections = {item["zone_id"]: item for item in packet["zone_sections"]}
    assert list(sections) == ["overview", "primary_live", "operator_support"]
    assert sections["overview"]["entry_count"] == 1
    assert sections["primary_live"]["entry_count"] == 4
    assert sections["operator_support"]["entry_count"] == 7
    assert sections["overview"]["widget_group_ids"] == ["primary_signal_widget"]
    assert "source_quality_explanation_widgets" in sections["primary_live"]["supplemental_widget_group_ids"]
    assert "prediction_supplemental_handoff_readiness_summary_widget" in sections["operator_support"]["supplemental_widget_group_ids"]
    assert all(item["section_state"] == "ready_read_only" for item in sections.values())
    assert all(item["streamlit_render_allowed"] is False for item in sections.values())


def test_ps_q8b_index_is_compact_and_safe() -> None:
    index = build_prediction_warroom_ui_mount_presenter_index()
    assert index["presenter_index_version"] == "prediction_warroom_ui_mount_presenter.ps_q8b.v1"
    assert index["display_state"] == "ready_for_operator_review_render_disabled"
    assert index["mount_entry_row_count"] == 12
    assert index["zone_section_count"] == 3
    assert index["blocked_entry_row_count"] == 0
    assert index["presenter_metrics"]["presenter_ready"] is True
    assert index["integration_contract"]["requires_streamlit_rendering"] is False
    for payload in (index, index["boundaries"], index["integration_contract"], *index["mount_entry_rows"], *index["zone_sections"]):
        _assert_safe(payload)


def test_ps_q8b_blocked_catalog_flows_to_presenter_without_rendering() -> None:
    catalog = build_prediction_warroom_ui_mount_catalog().to_dict()
    catalog["mount_state"] = "blocked_before_ui_mount_catalog_connection_render_disabled"
    packet = build_prediction_warroom_ui_mount_presenter_packet(mount_catalog=catalog).to_dict()
    assert packet["display_state"] == "blocked_for_operator_review_render_disabled"
    assert packet["presenter_metrics"]["catalog_mount_state_ready"] is False
    assert packet["presenter_metrics"]["presenter_ready"] is False
    assert packet["blocked_entry_row_count"] == 0
    assert packet["ui_rendering_allowed"] is False
    _assert_safe(packet)


def test_ps_q8b_blocked_entry_is_surfaced_in_rows_and_zone() -> None:
    catalog = build_prediction_warroom_ui_mount_catalog().to_dict()
    rows = list(catalog["mount_entries"])
    rows[-1] = {**rows[-1], "mount_state": "mount_blocked_missing_visibility_or_attach_target"}
    catalog["mount_entries"] = rows
    packet = build_prediction_warroom_ui_mount_presenter_packet(mount_catalog=catalog).to_dict()
    assert packet["display_state"] == "blocked_for_operator_review_render_disabled"
    assert packet["blocked_entry_row_count"] == 1
    assert packet["blocked_entry_rows"][0]["widget_group_id"] == "prediction_supplemental_handoff_readiness_summary_widget"
    sections = {item["zone_id"]: item for item in packet["zone_sections"]}
    assert sections["operator_support"]["blocked_entry_count"] == 1
    assert sections["operator_support"]["section_state"] == "blocked_read_only"
    _assert_safe(packet)


def main() -> int:
    test_ps_q8b_static_boundaries_and_markers()
    test_ps_q8b_default_presenter_packet_is_ready_and_display_only()
    test_ps_q8b_zone_sections_are_stable_and_grouped()
    test_ps_q8b_index_is_compact_and_safe()
    test_ps_q8b_blocked_catalog_flows_to_presenter_without_rendering()
    test_ps_q8b_blocked_entry_is_surfaced_in_rows_and_zone()
    print("[OK] Prediction System PS-Q8B UI mount presenter guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
