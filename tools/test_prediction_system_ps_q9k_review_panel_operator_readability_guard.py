# path: ./tools/test_prediction_system_ps_q9k_review_panel_operator_readability_guard.py
# desc: Focused guard for PS-Q9K operator readability rows in lowered display-packet review panel.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel import (
    PANEL_OPERATOR_READABILITY_VERSION,
    _operator_readiness_card_rows,
    _operator_widget_card_rows,
)
from btcts.apps.operator_ui.components.prediction_warroom_synthetic_review_packet_session_state_harness import build_prediction_warroom_synthetic_lowered_display_packet_review_packet
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import resolve_prediction_warroom_lowered_display_packet_visibility_review_source

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "json",
    "pathlib",
)
FORBIDDEN_PANEL_TOKENS = (
    "open(",
    "Path(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    ".exists(",
    ".stat(",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "st.file_uploader",
    "st.text_input",
    "st.number_input",
    "load_prediction",
    "latest_payload",
    "hot_latest",
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
    "persist=True",
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


def test_ps_q9k_panel_static_boundaries_and_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    imports = _imports_from(PANEL)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    assert "streamlit" in imports
    for token in FORBIDDEN_PANEL_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_lowered_display_packet_visibility_readability.ps_q9k.v1" in text
    assert "_operator_readiness_card_rows" in text
    assert "_operator_widget_card_rows" in text
    assert "operator_readability_cards" in text
    assert "operator_widget_cards" in text
    assert "review_only_no_execution" in text


def test_ps_q9k_warroom_page_stays_folded_and_not_moved() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    q8_marker = 'with live_shell.render_folded_section("Prediction WarRoom mount review", expanded=False):'
    q9_marker = 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=False):'
    diagnostics_marker = 'get_text(lang, "ui_slot_diagnostics_title")'
    assert q8_marker in text
    assert q9_marker in text
    assert text.count(q9_marker) == 1
    assert text.index(q8_marker) < text.index(q9_marker) < text.index(diagnostics_marker)
    assert 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=True):' not in text


def test_ps_q9k_operator_readiness_cards_for_ready_packet() -> None:
    review_packet = build_prediction_warroom_synthetic_lowered_display_packet_review_packet()
    source = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        explicit_review_packet=review_packet,
    ).to_dict()
    rows = _operator_readiness_card_rows(review_packet, source)
    assert [row["card_id"] for row in rows] == [
        "source_handoff",
        "display_packet",
        "widget_visibility",
        "blockers_and_warnings",
        "next_operator_action",
    ]
    assert rows[0]["state"] == "review_source_handoff_ready"
    assert rows[1]["state"] == "valid"
    assert rows[2]["state"] == "6/6"
    assert rows[3]["state"].startswith("blockers=0")
    assert rows[4]["state"] == "review_only_no_execution"
    assert all(row["read_only"] is True for row in rows)
    assert all(row["execution"] == "false" for row in rows)


def test_ps_q9k_operator_widget_cards_for_ready_packet() -> None:
    review_packet = build_prediction_warroom_synthetic_lowered_display_packet_review_packet()
    rows = _operator_widget_card_rows(review_packet)
    assert len(rows) == 6
    assert rows[0]["widget_group_id"] == "primary_signal_widget"
    assert rows[0]["operator_focus_ja"] == "主要シグナルを最初に確認"
    assert rows[-1]["widget_group_id"] == "warning_refresh_widget"
    assert rows[-1]["operator_focus_ja"] == "警告と更新要否を確認"
    assert all(row["render"] == "review_only" for row in rows)
    assert all(row["execution"] == "false" for row in rows)
    assert all(row["autotrade"] == "false" for row in rows)
    assert all(row["broker"] == "false" for row in rows)


def test_ps_q9k_operator_rows_for_blocked_packet_remain_read_only() -> None:
    source = resolve_prediction_warroom_lowered_display_packet_visibility_review_source().to_dict()
    packet = source["review_packet"]
    rows = _operator_readiness_card_rows(packet, source)
    assert rows[0]["state"] == "review_source_handoff_fallback_blocked"
    assert rows[1]["state"] == "blocked"
    assert rows[2]["state"] == "0/0"
    assert rows[3]["state"].startswith("blockers=")
    assert rows[4]["state"] == "review_only_no_execution"
    assert _operator_widget_card_rows(packet) == []


def test_ps_q9k_panel_version_is_stable() -> None:
    assert PANEL_OPERATOR_READABILITY_VERSION == "prediction_warroom_lowered_display_packet_visibility_readability.ps_q9k.v1"


def main() -> int:
    test_ps_q9k_panel_static_boundaries_and_markers()
    test_ps_q9k_warroom_page_stays_folded_and_not_moved()
    test_ps_q9k_operator_readiness_cards_for_ready_packet()
    test_ps_q9k_operator_widget_cards_for_ready_packet()
    test_ps_q9k_operator_rows_for_blocked_packet_remain_read_only()
    test_ps_q9k_panel_version_is_stable()
    print("[OK] Prediction System PS-Q9K review panel operator readability guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
