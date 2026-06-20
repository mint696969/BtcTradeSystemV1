# path: ./tools/test_prediction_system_ps_q4d_warroom_sample_packets_guard.py
# desc: Guard for PS-Q4D synthetic WarRoom sample packets. Fixture-only; no prediction runtime, hot file load, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import (
    build_prediction_warroom_sample_display_packet,
    build_prediction_warroom_sample_packet_bundle,
    build_prediction_warroom_sample_packet_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_sample_packets.py"
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
EXPECTED_GROUPS = [
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


def test_ps_q4d_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_sample_packets.ps_q4d.v1" in text
    assert "PredictionWarRoomSamplePacketBundle" in text
    assert "build_prediction_warroom_sample_display_packet" in text
    assert "build_prediction_warroom_sample_packet_bundle" in text
    assert "build_prediction_warroom_sample_packet_index" in text
    assert "synthetic_only" in text
    assert "fixture_only" in text


def test_ps_q4d_sample_display_packet_matches_q4a_shape_without_runtime() -> None:
    packet = build_prediction_warroom_sample_display_packet()
    assert packet["packet_version"] == "prediction_warroom_display_packet.ps_q4a.v1"
    assert packet["synthetic_only"] is True
    assert packet["fixture_only"] is True
    assert packet["primary_signal_summary"]["summary_version"] == "prediction_signal_strength_bands.ps_q3c.v1"
    assert packet["horizon_cards"]
    assert packet["family_cards"]
    assert packet["source_quality_panel"]["tier0_source_quality_gate"]["gate_state"] == "passed"
    assert packet["evidence_panel"]["source_contribution_ledger_count"] == 2
    assert packet["boundaries"]["would_load_hot_latest_artifacts"] is False
    assert packet["boundaries"]["would_read_runtime_file"] is False
    assert packet["boundaries"]["would_write_runtime_artifact"] is False
    assert packet["would_send_to_broker"] is False


def test_ps_q4d_bundle_builds_widget_index_and_l4_adapter_contract_from_synthetic_packet() -> None:
    bundle = build_prediction_warroom_sample_packet_bundle().to_dict()
    assert bundle["sample_version"] == "prediction_warroom_sample_packets.ps_q4d.v1"
    assert bundle["synthetic_only"] is True
    assert bundle["fixture_only"] is True
    widget_index = bundle["widget_group_index"]
    assert widget_index["index_version"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert widget_index["widget_group_count"] == 6
    assert widget_index["widget_group_order"] == EXPECTED_GROUPS
    adapter = bundle["l4_latest_adapter_contract"]
    assert adapter["adapter_version"] == "prediction_warroom_l4_latest_adapter.ps_q4c.v1"
    assert adapter["adapter_state"] == "display_packet_supplied_widget_index_ready"
    assert adapter["display_packet_available"] is True
    assert adapter["widget_group_index_available"] is True
    assert adapter["would_load_hot_latest_artifacts"] is False
    assert adapter["would_read_runtime_file"] is False
    assert adapter["would_write_runtime_artifact"] is False


def test_ps_q4d_sample_index_is_compact_safe_and_non_executing() -> None:
    index = build_prediction_warroom_sample_packet_index()
    assert index["sample_index_version"] == "prediction_warroom_sample_packets.ps_q4d.v1"
    assert index["widget_group_count"] == 6
    assert index["widget_group_order"] == EXPECTED_GROUPS
    assert index["adapter_state"] == "display_packet_supplied_widget_index_ready"
    assert index["read_only"] is True
    assert index["non_executing"] is True
    assert index["synthetic_only"] is True
    assert index["fixture_only"] is True
    assert index["would_load_hot_latest_artifacts"] is False
    assert index["would_read_runtime_file"] is False
    assert index["would_collect_public_source"] is False
    assert index["would_write_runtime_artifact"] is False
    assert index["would_send_to_broker"] is False
    assert index["broker_execution_requested"] is False
    assert index["mode_apply_requested"] is False
    assert index["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_q4d_static_boundaries_and_markers()
    test_ps_q4d_sample_display_packet_matches_q4a_shape_without_runtime()
    test_ps_q4d_bundle_builds_widget_index_and_l4_adapter_contract_from_synthetic_packet()
    test_ps_q4d_sample_index_is_compact_safe_and_non_executing()
    print("[OK] Prediction System PS-Q4D WarRoom sample packets guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
