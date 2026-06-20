# path: ./tools/test_prediction_system_ps_q5a_source_quality_explanations_guard.py
# desc: Guard for PS-Q5A Prediction WarRoom source-quality explanation panel. Display-only; no runtime reads, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet
from btcts.apps.operator_ui.components.prediction_warroom_source_quality_explanations import build_prediction_warroom_source_quality_explanation_panel

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_quality_explanations.py"
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


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_ps_q5a_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_source_quality_explanations.ps_q5a.v1" in text
    assert "PredictionWarRoomSourceQualityExplanationPanel" in text
    assert "build_prediction_warroom_source_quality_explanation_panel" in text
    assert "signal_cap_explanations" in text
    assert "missing_source_cards" in text
    assert "family_cap_cards" in text
    assert "operator_action_kind" in text


def test_ps_q5a_builds_explanation_panel_from_sample_packet() -> None:
    panel = build_prediction_warroom_source_quality_explanation_panel(build_prediction_warroom_sample_display_packet()).to_dict()
    assert panel["panel_version"] == "prediction_warroom_source_quality_explanations.ps_q5a.v1"
    assert panel["prediction_run_id"] == "synthetic_prediction_run_20260620T000000Z"
    assert panel["signal_cap_explanations"]
    assert panel["source_quality_gate_cards"]
    assert panel["missing_source_cards"]
    assert panel["family_cap_cards"]
    assert panel["watch_points"]
    assert "参考度制限理由" in panel["operator_summary_ja"]


def test_ps_q5a_explains_missing_sources_and_family_caps() -> None:
    panel = build_prediction_warroom_source_quality_explanation_panel(build_prediction_warroom_sample_display_packet()).to_dict()
    reason_codes = {card["reason_code"] for card in panel["signal_cap_explanations"]}
    assert "context_profile_family_minimum_sources_missing" in reason_codes
    missing_sources: set[str] = set()
    for card in panel["missing_source_cards"]:
        missing_sources.update(str(item) for item in card.get("missing_source_ids", []))
    assert "bitflyer_trades" in missing_sources
    assert "bitflyer_board_summary" in missing_sources
    family_cards = panel["family_cap_cards"]
    assert family_cards[0]["family"] == "trend_bias"
    assert family_cards[0]["signal_strength_cap_reason"] == "context_profile_family_minimum_sources_missing"
    assert family_cards[0]["operator_action_kind"] == "observe_only"


def test_ps_q5a_panel_is_display_only_and_non_executing() -> None:
    panel = build_prediction_warroom_source_quality_explanation_panel(build_prediction_warroom_sample_display_packet()).to_dict()
    assert panel["read_only"] is True
    assert panel["non_executing"] is True
    assert panel["display_only"] is True
    assert panel["render_intent_only"] is True
    assert panel["not_loaded_as_runtime_display_source"] is True
    assert panel["would_load_hot_latest_artifacts"] is False
    assert panel["would_read_runtime_file"] is False
    assert panel["would_collect_public_source"] is False
    assert panel["would_write_runtime_artifact"] is False
    assert panel["would_send_to_broker"] is False
    assert panel["broker_execution_requested"] is False
    assert panel["mode_apply_requested"] is False
    assert panel["command_ledger_append_requested"] is False
    assert panel["approval_append_requested"] is False
    for section in ("signal_cap_explanations", "source_quality_gate_cards", "missing_source_cards", "family_cap_cards", "watch_points"):
        for card in panel[section]:
            assert card["read_only"] is True
            assert card["non_executing"] is True
            assert card["operator_action_kind"] == "observe_only"


def main() -> int:
    test_ps_q5a_static_boundaries_and_markers()
    test_ps_q5a_builds_explanation_panel_from_sample_packet()
    test_ps_q5a_explains_missing_sources_and_family_caps()
    test_ps_q5a_panel_is_display_only_and_non_executing()
    print("[OK] Prediction System PS-Q5A source-quality explanations guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
