# path: ./tools/test_prediction_system_ps_q9l_prediction_compact_summary_card_guard.py
# desc: Focused guard for PS-Q9L compact prediction summary card in lowered display-packet review panel.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel import (
    PANEL_PREDICTION_COMPACT_SUMMARY_VERSION,
    _prediction_compact_summary_card_rows,
)
from btcts.apps.operator_ui.components.prediction_warroom_synthetic_review_packet_session_state_harness import build_prediction_warroom_synthetic_lowered_display_packet_review_packet

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
EXPECTED_CARD_IDS = [
    "prediction_headline",
    "signal_strength",
    "source_quality",
    "horizon_scenario",
    "warning_state",
    "execution_boundary",
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


def test_ps_q9l_panel_static_boundaries_and_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    imports = _imports_from(PANEL)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    assert "streamlit" in imports
    for token in FORBIDDEN_PANEL_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_prediction_compact_summary.ps_q9l.v1" in text
    assert "_prediction_compact_summary_card_rows" in text
    assert "prediction_compact_summary_cards" in text
    assert "already_lowered_review_payload_only" in text
    assert "review_only_no_execution" in text


def test_ps_q9l_warroom_page_stays_folded_and_not_moved() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    q8_marker = 'with live_shell.render_folded_section("Prediction WarRoom mount review", expanded=False):'
    q9_marker = 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=False):'
    diagnostics_marker = 'get_text(lang, "ui_slot_diagnostics_title")'
    assert q8_marker in text
    assert q9_marker in text
    assert text.count(q9_marker) == 1
    assert text.index(q8_marker) < text.index(q9_marker) < text.index(diagnostics_marker)
    assert 'with live_shell.render_folded_section("Prediction WarRoom lowered display packet review", expanded=True):' not in text


def test_ps_q9l_compact_summary_rows_for_ready_packet() -> None:
    packet = build_prediction_warroom_synthetic_lowered_display_packet_review_packet()
    rows = _prediction_compact_summary_card_rows(packet)
    assert [row["card_id"] for row in rows] == EXPECTED_CARD_IDS
    assert rows[0]["state"] == "Synthetic: 短期は上方向優勢、参考度59%。"
    assert rows[0]["market_uid"] == "BTC_JPY:bitFlyer"
    assert rows[0]["prediction_run_id"] == "synthetic_prediction_run_20260620T000000Z"
    assert rows[1]["state"] == "59% / 参考になる"
    assert rows[1]["operator_note_ja"] == "主要シグナルの強さと参考度を確認"
    assert rows[2]["state"] == "passed / incomplete"
    assert rows[3]["state"] == "short_horizon / continuation_bias / medium"
    assert rows[4]["state"] == "warnings=1;blockers=0"
    assert rows[5]["state"] == "review_only_no_execution"
    assert all(row["read_only"] is True for row in rows)
    assert all(row["execution"] == "false" for row in rows)
    assert all(row["autotrade"] == "false" for row in rows)
    assert all(row["broker"] == "false" for row in rows)


def test_ps_q9l_compact_summary_rows_for_blocked_packet_are_safe() -> None:
    rows = _prediction_compact_summary_card_rows({})
    assert [row["card_id"] for row in rows] == EXPECTED_CARD_IDS
    assert rows[0]["state"] == "not_available"
    assert rows[1]["state"] == "0% / unknown"
    assert rows[2]["state"] == "unknown / unknown"
    assert rows[3]["state"] == "unknown / unknown / unknown"
    assert rows[4]["state"] == "warnings=0;blockers=0"
    assert rows[5]["state"] == "review_only_no_execution"
    assert all(row["read_only"] is True for row in rows)
    assert all(row["execution"] == "false" for row in rows)


def test_ps_q9l_panel_version_is_stable() -> None:
    assert PANEL_PREDICTION_COMPACT_SUMMARY_VERSION == "prediction_warroom_prediction_compact_summary.ps_q9l.v1"


def main() -> int:
    test_ps_q9l_panel_static_boundaries_and_markers()
    test_ps_q9l_warroom_page_stays_folded_and_not_moved()
    test_ps_q9l_compact_summary_rows_for_ready_packet()
    test_ps_q9l_compact_summary_rows_for_blocked_packet_are_safe()
    test_ps_q9l_panel_version_is_stable()
    print("[OK] Prediction System PS-Q9L compact prediction summary card guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
