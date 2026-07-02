# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_chart_refresh_opt_in_q30a.py
# desc: PS-Q30A guards for WarRoom v2 chart refresh opt-in.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.auto_refresh_control import (  # noqa: E402
    CHART_OPT_IN_SESSION_KEY,
    active_fragment_targets_from_chart_opt_in,
    build_warroom_v2_auto_refresh_control_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CONTROL = RENDERER_DIR / "auto_refresh_control.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q30A_WARROOM_V2_CHART_REFRESH_OPT_IN_2026-07-02.md"


def test_q30a_default_refresh_targets_remain_metrics_only() -> None:
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True)
    assert packet["active_fragment_targets"] == ["market_snapshot_strip"]
    assert packet["metrics_only_auto_refresh_default"] is True
    assert packet["chart_refresh_opt_in_available"] is True
    assert packet["chart_refresh_opt_in_enabled"] is False
    assert packet["chart_review_auto_refresh_enabled"] is False
    assert packet["page_reload_enabled"] is False


def test_q30a_chart_opt_in_adds_chart_target_without_transport_change() -> None:
    assert active_fragment_targets_from_chart_opt_in(chart_enabled=True) == ["market_snapshot_strip", "chart_review_panel"]
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, chart_refresh_opt_in=True)
    assert packet["active_fragment_targets"] == ["market_snapshot_strip", "chart_review_panel"]
    assert packet["metrics_only_auto_refresh_default"] is False
    assert packet["chart_refresh_opt_in_enabled"] is True
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q30a_render_control_exposes_checkbox_and_session_key() -> None:
    text = CONTROL.read_text(encoding="utf-8-sig")
    assert CHART_OPT_IN_SESSION_KEY in text
    assert "st.checkbox" in text
    assert "Chart Review も自動更新する" in text
    assert "chart opt-in" in text
    assert "_inject_browser_timer" not in text.split("def render_warroom_v2_auto_refresh_control", 1)[1]


def test_q30a_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q30a_doc_records_opt_in_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "chart_refresh_opt_in_available=true" in text
    assert "chart_refresh_opt_in_enabled_default=false" in text
    assert "metrics_only_auto_refresh_default=true" in text
    assert "page_reload_enabled=false" in text
    assert "would_send_to_broker=false" in text
