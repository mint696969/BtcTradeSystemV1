# path: ./tools/test_prediction_system_ps_q5b_explanation_widget_groups_guard.py
# desc: Guard for PS-Q5B supplemental source-quality explanation widget group metadata. Display-only; no rendering, runtime reads, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_explanation_widget_groups import (
    build_prediction_warroom_explanation_widget_group_index,
    build_prediction_warroom_explanation_widget_group_packet,
)
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet
from btcts.apps.operator_ui.components.prediction_warroom_widget_groups import build_prediction_warroom_widget_group_packet_index

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_explanation_widget_groups.py"
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
)
FORBIDDEN_TOKENS = (
    "open(",
    "Path.read_text",
    "json.load",
    "json.loads",
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
    "would_load_hot_latest_artifacts=True",
    "would_read_runtime_file=True",
    "would_write_runtime_artifact=True",
    "would_send_to_broker=True",
    "broker_execution_requested=True",
    "mode_apply_requested=True",
    "command_ledger_append_requested=True",
)
BASE_Q4B_GROUPS = [
    "primary_signal_widget",
    "horizon_scenario_widgets",
    "family_detail_widgets",
    "source_quality_widget",
    "evidence_ledger_widget",
    "warning_refresh_widget",
]


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_ps_q5b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_explanation_widget_groups.ps_q5b.v1" in text
    assert "PredictionWarRoomExplanationWidgetGroupIndex" in text
    assert "build_prediction_warroom_explanation_widget_group_packet" in text
    assert "build_prediction_warroom_explanation_widget_group_index" in text
    assert "source_quality_explanation_widgets" in text
    assert "attach_after_widget_group_id" in text


def test_ps_q5b_builds_supplemental_group_without_changing_q4b_base_order() -> None:
    display_packet = build_prediction_warroom_sample_display_packet()
    base_index = build_prediction_warroom_widget_group_packet_index(display_packet)
    assert base_index["widget_group_order"] == BASE_Q4B_GROUPS
    packet = build_prediction_warroom_explanation_widget_group_packet(display_packet).to_dict()
    assert packet["packet_version"] == "prediction_warroom_explanation_widget_groups.ps_q5b.v1"
    assert packet["widget_group_id"] == "source_quality_explanation_widgets"
    assert packet["widget_group_kind"] == "source_quality_explanations"
    assert packet["refresh_group_id"] == "prediction_warroom:source_quality_explanation_widgets"
    assert packet["refresh_interval_sec"] == 30
    assert packet["refresh_priority"] == 45
    assert packet["independent_refresh_allowed"] is True
    assert packet["payload"]["attach_after_widget_group_id"] == "source_quality_widget"
    assert packet["payload"]["explanation_panel"]["panel_version"] == "prediction_warroom_source_quality_explanations.ps_q5a.v1"


def test_ps_q5b_index_exposes_auto_refresh_and_integration_contract() -> None:
    index = build_prediction_warroom_explanation_widget_group_index(build_prediction_warroom_sample_display_packet()).to_dict()
    assert index["index_version"] == "prediction_warroom_explanation_widget_groups.ps_q5b.v1"
    assert index["supplemental_widget_group_count"] == 1
    assert index["supplemental_widget_group_order"] == ["source_quality_explanation_widgets"]
    assert index["attach_after_widget_group_id"] == "source_quality_widget"
    assert index["auto_refresh_groups"][0]["refresh_group_id"] == "prediction_warroom:source_quality_explanation_widgets"
    assert index["auto_refresh_groups"][0]["attach_after_widget_group_id"] == "source_quality_widget"
    contract = index["integration_contract"]
    assert contract["base_widget_group_contract"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert contract["explanation_panel_contract"] == "prediction_warroom_source_quality_explanations.ps_q5a.v1"
    assert contract["does_not_modify_base_q4b_group_order"] is True
    assert contract["requires_hot_file_read"] is False
    assert contract["safe_to_render_without_side_effects"] is True


def test_ps_q5b_payload_carries_explanation_counts_and_safe_flags() -> None:
    index = build_prediction_warroom_explanation_widget_group_index(build_prediction_warroom_sample_display_packet()).to_dict()
    group = index["widget_groups"][0]
    payload = group["payload"]
    assert payload["signal_cap_explanation_count"] >= 1
    assert payload["missing_source_card_count"] >= 1
    assert payload["family_cap_card_count"] >= 1
    assert payload["source_quality_gate_card_count"] >= 1
    assert payload["watch_point_count"] >= 1
    assert payload["display_only"] is True
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
    assert group["read_only"] is True
    assert group["non_executing"] is True
    assert group["display_only"] is True
    assert group["would_load_hot_latest_artifacts"] is False
    assert group["would_read_runtime_file"] is False
    assert group["would_write_runtime_artifact"] is False
    assert group["would_send_to_broker"] is False
    assert group["broker_execution_requested"] is False
    assert group["mode_apply_requested"] is False
    assert group["command_ledger_append_requested"] is False
    assert index["read_only"] is True
    assert index["non_executing"] is True
    assert index["would_load_hot_latest_artifacts"] is False
    assert index["would_read_runtime_file"] is False
    assert index["would_write_runtime_artifact"] is False
    assert index["would_send_to_broker"] is False


def main() -> int:
    test_ps_q5b_static_boundaries_and_markers()
    test_ps_q5b_builds_supplemental_group_without_changing_q4b_base_order()
    test_ps_q5b_index_exposes_auto_refresh_and_integration_contract()
    test_ps_q5b_payload_carries_explanation_counts_and_safe_flags()
    print("[OK] Prediction System PS-Q5B explanation widget groups guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
