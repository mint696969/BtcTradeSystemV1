# path: ./tools/test_prediction_system_ps_q9m_future_top_ux_readiness_gate_guard.py
# desc: Focused guard for PS-Q9M future top/default-expanded UX readiness gate.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel import (
    PANEL_FUTURE_TOP_UX_GATE_VERSION,
    _prediction_future_top_default_expanded_gate_rows,
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
EXPECTED_GATE_IDS = [
    "compact_summary_ready",
    "source_handoff_ready",
    "display_packet_ready",
    "execution_boundary_clean",
    "real_payload_required_for_top_default",
    "warroom_layout_change",
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


def test_ps_q9m_panel_static_boundaries_and_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    imports = _imports_from(PANEL)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    assert "streamlit" in imports
    for token in FORBIDDEN_PANEL_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_future_top_default_expanded_gate.ps_q9m.v1" in text
    assert "_prediction_future_top_default_expanded_gate_rows" in text
    assert "future_top_default_expanded_gate" in text
    assert "layout_change_not_applied" in text
    assert "real_payload_required" in text


def test_ps_q9m_warroom_page_stays_folded_and_not_moved() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    q8_marker = 'with live_shell.render_folded_section("Prediction WarRoom mount review", expanded=False):'
    q9_marker = 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=False):'
    diagnostics_marker = 'get_text(lang, "ui_slot_diagnostics_title")'
    assert q8_marker in text
    assert q9_marker in text
    assert text.count(q9_marker) == 1
    assert text.index(q8_marker) < text.index(q9_marker) < text.index(diagnostics_marker)
    assert 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=True):' not in text
    assert "future_top_default_expanded_gate" not in text


def test_ps_q9m_gate_rows_for_synthetic_ready_packet_fail_closed_for_top_default() -> None:
    packet = build_prediction_warroom_synthetic_lowered_display_packet_review_packet()
    source = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        explicit_review_packet=packet,
    ).to_dict()
    rows = _prediction_future_top_default_expanded_gate_rows(packet, source)
    assert [row["gate_id"] for row in rows] == EXPECTED_GATE_IDS
    assert rows[0]["state"] == "ready"
    assert rows[1]["state"] == "ready"
    assert rows[2]["state"] == "ready"
    assert rows[3]["state"] == "ready"
    assert rows[4]["state"] == "blocked_synthetic_fixture"
    assert rows[5]["state"] == "deferred_no_page_mutation"
    assert all(row["read_only"] is True for row in rows)
    assert all(row["execution"] == "false" for row in rows)
    assert all(row["warroom_page_mutation"] == "false" for row in rows)
    assert all(row["default_expanded_applied"] == "false" for row in rows)


def test_ps_q9m_gate_rows_for_blocked_packet_are_not_ready() -> None:
    source = resolve_prediction_warroom_lowered_display_packet_visibility_review_source().to_dict()
    packet = source["review_packet"]
    rows = _prediction_future_top_default_expanded_gate_rows(packet, source)
    assert [row["gate_id"] for row in rows] == EXPECTED_GATE_IDS
    assert rows[0]["state"] == "not_ready"
    assert rows[1]["state"] == "blocked"
    assert rows[2]["state"] == "blocked"
    assert rows[3]["state"] == "blocked"
    assert rows[4]["state"] == "blocked_missing_real_payload"
    assert rows[5]["state"] == "deferred_no_page_mutation"
    assert all(row["read_only"] is True for row in rows)
    assert all(row["execution"] == "false" for row in rows)


def test_ps_q9m_panel_version_is_stable() -> None:
    assert PANEL_FUTURE_TOP_UX_GATE_VERSION == "prediction_warroom_future_top_default_expanded_gate.ps_q9m.v1"


def main() -> int:
    test_ps_q9m_panel_static_boundaries_and_markers()
    test_ps_q9m_warroom_page_stays_folded_and_not_moved()
    test_ps_q9m_gate_rows_for_synthetic_ready_packet_fail_closed_for_top_default()
    test_ps_q9m_gate_rows_for_blocked_packet_are_not_ready()
    test_ps_q9m_panel_version_is_stable()
    print("[OK] Prediction System PS-Q9M future top UX readiness gate guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
