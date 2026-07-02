# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_metrics_only_fragment_refresh_q29z.py
# desc: PS-Q29Z guards for metrics-only default fragment refresh.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.auto_refresh_control import build_warroom_v2_auto_refresh_control_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.fragment_refresh import build_warroom_v2_fragment_refresh_packet, active_fragment_targets_from_refresh_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
FRAGMENT = RENDERER_DIR / "fragment_refresh.py"
CONTROL = RENDERER_DIR / "auto_refresh_control.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29Z_WARROOM_V2_METRICS_ONLY_FRAGMENT_REFRESH_2026-07-02.md"


def test_q29z_auto_refresh_defaults_to_metrics_only_targets() -> None:
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=3000, source="operator_sidebar")
    assert packet["active_fragment_targets"] == ["market_snapshot_strip"]
    assert packet["available_fragment_targets"] == ["market_snapshot_strip", "chart_review_panel"]
    assert packet["metrics_only_auto_refresh_default"] is True
    assert packet["chart_review_auto_refresh_enabled"] is False
    assert packet["page_reload_enabled"] is False


def test_q29z_fragment_packet_keeps_chart_available_but_inactive_by_default() -> None:
    refresh = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=3000, source="operator_sidebar")
    packet = build_warroom_v2_fragment_refresh_packet(refresh_packet=refresh)
    assert packet["refresh_targets"] == ["market_snapshot_strip", "chart_review_panel"]
    assert packet["active_refresh_targets"] == ["market_snapshot_strip"]
    assert packet["inactive_refresh_targets"] == ["chart_review_panel"]
    assert packet["chart_review_auto_refresh_enabled"] is False
    assert packet["browser_timer_reload_enabled"] is False


def test_q29z_active_targets_can_opt_in_chart_later_without_transport_change() -> None:
    assert active_fragment_targets_from_refresh_packet({"active_fragment_targets": ["market_snapshot_strip", "chart_review_panel"]}) == ["market_snapshot_strip", "chart_review_panel"]
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, active_fragment_targets=["market_snapshot_strip", "chart_review_panel"])
    assert packet["metrics_only_auto_refresh_default"] is False
    assert packet["chart_review_auto_refresh_enabled"] is True
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q29z_render_path_keeps_chart_block_but_target_policy_controls_refresh() -> None:
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    fragment_text = FRAGMENT.read_text(encoding="utf-8-sig")
    assert 'label="market_snapshot_strip"' in panel_text
    assert 'label="chart_review_panel"' in panel_text
    assert "target_refresh_enabled" in fragment_text
    assert "active_refresh_targets" in fragment_text
    assert "metrics-only default" in CONTROL.read_text(encoding="utf-8-sig")


def test_q29z_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29z_doc_records_metrics_only_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "metrics_only_auto_refresh_default=true" in text
    assert "active_fragment_targets=market_snapshot_strip" in text
    assert "chart_review_auto_refresh_enabled=false" in text
    assert "page_reload_enabled=false" in text
    assert "would_send_to_broker=false" in text
