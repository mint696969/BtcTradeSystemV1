# path: ./tools/test_prediction_system_ps_q9v_warroom_top_default_expanded_ui_layout_guard.py
# desc: Focused guard for PS-Q9V WarRoom top/default-expanded UI-only layout patch.

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
EXPECTED_TOP_SECTION = 'with live_shell.render_folded_section("Prediction WarRoom real payload review", expanded=True):'
OLD_BOTTOM_SECTION = 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=False):'
UNSAFE_PREDICTION_UI_TOKENS = (
    "load_prediction_warroom_latest_payload_read_only",
    "build_prediction_warroom_actual_read_operator_runner_scaffold",
    "build_prediction_warroom_actual_observation_runbook_contract",
    "build_prediction_warroom_actual_observation_stdout_review_parser",
    "build_prediction_warroom_actual_observation_ui_handoff_readiness_contract",
    "build_prediction_warroom_top_default_expanded_layout_preflight_contract",
    "allow_actual_read=True",
    "operator_acknowledged=True",
    "execute_actual_read=True",
    "prediction_warroom_actual_read_operator_runner_scaffold",
    "prediction_warroom_latest_payload_read_only_loader",
    "prediction_warroom_actual_observation_runbook_contract",
    "prediction_warroom_actual_observation_stdout_review_parser",
    "prediction_warroom_actual_observation_ui_handoff_readiness_contract",
    "prediction_warroom_top_default_expanded_layout_preflight_contract",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "place_order(",
    "send_order(",
    "create_order(",
    "ccxt",
    "pybitflyer",
    "websocket",
)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _render_folded_sections(tree: ast.AST) -> list[tuple[str, bool | None]]:
    sections: list[tuple[str, bool | None]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            call = item.context_expr
            if not isinstance(call, ast.Call) or _call_name(call.func) != "live_shell.render_folded_section":
                continue
            label = ""
            expanded: bool | None = None
            if call.args and isinstance(call.args[0], ast.Constant):
                label = str(call.args[0].value)
            for keyword in call.keywords:
                if keyword.arg == "expanded" and isinstance(keyword.value, ast.Constant):
                    expanded = bool(keyword.value.value)
            sections.append((label, expanded))
    return sections


def test_ps_q9v_warroom_top_section_is_default_expanded_and_before_overview() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert EXPECTED_TOP_SECTION in text
    assert OLD_BOTTOM_SECTION not in text
    assert text.index(EXPECTED_TOP_SECTION) < text.index('with live_shell.zone_container(\n        label=get_text(lang, "ui_label_overview")')
    assert text.count("_render_prediction_warroom_lowered_display_packet_visibility_review_section()") == 2
    assert "Prediction WarRoom real payload review is top/default-expanded and read-only" in text
    assert "no loader, no file read, no payload decode, no approval, no AutoTrade, no broker" in text


def test_ps_q9v_folded_section_shape_is_single_top_review() -> None:
    tree = ast.parse(WARROOM_PAGE.read_text(encoding="utf-8"))
    sections = _render_folded_sections(tree)
    real_sections = [item for item in sections if item[0] == "Prediction WarRoom real payload review"]
    lowered_sections = [item for item in sections if item[0] == "Prediction WarRoom lowered display packet review"]
    assert real_sections == [("Prediction WarRoom real payload review", True)]
    assert lowered_sections == []


def test_ps_q9v_does_not_add_prediction_runtime_or_loader_execution_to_page() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    for token in UNSAFE_PREDICTION_UI_TOKENS:
        assert token not in text, token
    assert "st.button" not in text
    assert "st.form" not in text
    assert "st.toggle" not in text


def test_ps_q9v_panel_remains_read_only_and_not_mutated_by_marker() -> None:
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "prediction_warroom_top_default_expanded_layout_preflight_contract" not in panel_text
    assert "Prediction WarRoom real payload review" not in panel_text
    assert "no loader, no file read, no payload decode, no approval, no AutoTrade, no broker" in panel_text
    assert "append_decision_jsonl" not in panel_text
    assert "append_command_ledger_record" not in panel_text
    assert "place_order(" not in panel_text
    assert "send_order(" not in panel_text
    assert "create_order(" not in panel_text


def main() -> int:
    test_ps_q9v_warroom_top_section_is_default_expanded_and_before_overview()
    test_ps_q9v_folded_section_shape_is_single_top_review()
    test_ps_q9v_does_not_add_prediction_runtime_or_loader_execution_to_page()
    test_ps_q9v_panel_remains_read_only_and_not_mutated_by_marker()
    print("[OK] Prediction System PS-Q9V WarRoom top/default-expanded UI layout guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
