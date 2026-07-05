# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_rt_ui_polish1.py
# desc: Verifies WarRoom v2 RT UI polish 1 modularizes renderers and restores chart graph + prediction cards.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
RT_UI = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_UI_POLISH1_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.chart_view import chart_rows_to_frame  # noqa: E402
from btcts.apps.operator_ui.views.warroom_v2_page import build_warroom_v2_page_mount_packet  # noqa: E402


def test_warroom_v2_page_delegates_to_modular_rt_ui_renderers() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert "from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.chart_view import render_rt_bottom_chart_graph" in text
    assert "render_rt_prediction_cards" in text
    assert "render_rt_top_layout_and_widgets" in text
    assert "render_rt_debug_packets" in text
    assert "render_wp12_bottom_chart_layout" not in text
    assert "render_wp13_prediction_card_connection" not in text
    assert "rt_ui_polish1_modularized" in text


def test_rt_ui_module_files_are_small_and_separated() -> None:
    expected = {"runtime_env.py", "status_view.py", "top_widgets_view.py", "chart_view.py", "prediction_cards_view.py", "debug_view.py"}
    assert expected.issubset({path.name for path in RT_UI.glob("*.py")})
    for name in expected:
        text = (RT_UI / name).read_text(encoding="utf-8-sig")
        assert text.startswith("# path: ./")
        assert len(text.splitlines()) < 130


def test_chart_rows_to_frame_extracts_live_price_series() -> None:
    frame = chart_rows_to_frame({
        "chart_rows": [
            {"topic_key": "market.depth", "updated_at_ms": 1000, "sequence": 1, "price": 100.0, "value_label": "best_ask=101.0, best_bid=100.0", "freshness_label": "live"},
            {"topic_key": "market.trades", "updated_at_ms": 1001, "sequence": 1, "price": 100.5, "value_label": "last_price=100.5", "freshness_label": "live"},
        ]
    })
    assert not frame.empty
    assert set(frame["topic"]) >= {"market.depth", "market.trades", "market.depth.best_ask", "market.trades.last_price"}


def test_page_mount_packet_marks_polish1_and_no_action_boundary() -> None:
    packet = build_warroom_v2_page_mount_packet(runtime_status={"receiver_runtime_started": True, "socket_opened": True, "receive_loop_started": True}, bridge_packet={"messages_applied": 2})
    assert packet["rt_ui_polish1_modularized"] is True
    assert packet["runtime_connected"] is True
    assert packet["push_connected"] is True
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_doc_markers() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_rt_ui_polish1_done=true" in doc
    assert "rt_ui_modules_split=true" in doc
    assert "bottom_chart_graph_restored=true" in doc
    assert "prediction_cards_card_shape_restored=true" in doc
