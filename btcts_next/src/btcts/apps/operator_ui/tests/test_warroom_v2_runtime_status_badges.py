# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_runtime_status_badges.py
# desc: Structural and packet guards for WarRoom v2 runtime badge compaction and bottom diagnostics.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
COMPACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/compact_layout_view.py"
STATUS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/status_view.py"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.status_view import build_rt_runtime_status_view_model  # noqa: E402


def test_runtime_view_model_uses_colored_badges_and_gray_safe_off_states() -> None:
    model = build_rt_runtime_status_view_model(
        {
            "receiver_runtime_started": True,
            "receive_loop_started": True,
            "socket_opened": True,
            "pending_message_count": 0,
            "received_message_count": 42,
            "drained_message_count": 7,
            "latest_message_at_ms": 0,
            "broker_send_enabled": False,
            "prediction_invoked": False,
        },
        {"messages_applied": 7},
        display_source="live",
        auto_refresh_packet={"auto_refresh_enabled": True, "interval_ms": 3000},
    )
    badges = model["badges"]
    labels = [badge["label"] for badge in badges]
    tones = {badge["label"]: badge["tone"] for badge in badges}
    assert "Runtime connected" in labels
    assert "broker OFF" in labels
    assert "prediction OFF" in labels
    assert tones["broker OFF"] == "gray"
    assert tones["prediction OFF"] == "gray"
    assert tones["pending 0"] == "green"
    assert any(str(label).startswith("recv ") for label in labels)
    assert any(str(label).startswith("applied ") for label in labels)
    assert any("compact viewport" in line for line in model["diagnostic_lines"])
    assert any("cockpit_auto_refresh=on" in line for line in model["diagnostic_lines"])
    assert any("display_source=live" in line for line in model["diagnostic_lines"])


def test_runtime_long_diagnostics_are_bottom_expander_not_top_captions() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    status = STATUS.read_text(encoding="utf-8-sig")
    compact = COMPACT.read_text(encoding="utf-8-sig")

    assert "build_rt_runtime_status_view_model" in page
    assert "render_rt_runtime_diagnostics" in page
    assert 'with st.expander("Runtime diagnostics", expanded=False):' in page
    assert "render_cockpit_auto_refresh_tick(auto_refresh_packet, st)" in page
    assert "display_source={snapshot['display_source']}" not in page
    assert "st_api.caption" not in compact or "compact viewport" not in compact
    assert "status_badges" in compact
    assert "margin:0.50rem 0 0.42rem 0;" in compact
    assert "broker OFF" in status
    assert "prediction OFF" in status

    chart_pos = page.index("_render_chart_and_gpt_copy(_build_cockpit_snapshot())")
    details_pos = page.index('with st.expander("Realtime widget details", expanded=False):')
    debug_pos = page.index('with st.expander("RT debug packets", expanded=False):')
    diagnostics_pos = page.index('with st.expander("Runtime diagnostics", expanded=False):')
    footer_pos = page.index("st.caption(compact_footer_caption())")
    assert chart_pos < details_pos < debug_pos < diagnostics_pos < footer_pos


def test_runtime_status_top_renderer_no_long_metrics_or_diagnostic_captions() -> None:
    status = STATUS.read_text(encoding="utf-8-sig")
    assert 'c1.metric("Runtime"' not in status
    assert 'c2.metric("Push lane"' not in status
    assert "_render_boundary_caption" not in status
    assert "render_rt_runtime_diagnostics" in status
