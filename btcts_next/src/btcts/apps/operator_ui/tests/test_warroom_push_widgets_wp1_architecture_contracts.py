# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp1_architecture_contracts.py
# desc: WP1 verifies WarRoom push-widget architecture contracts and no-send boundary.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp1_architecture_contracts import assert_wp1_no_send, build_wp1_reference_architecture_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP1_ARCHITECTURE_2026-07-05.md"


def test_wp1_architecture_packet_locks_required_contracts() -> None:
    packet = build_wp1_reference_architecture_packet()
    assert packet["wp1_completed"] is True
    assert packet["next_checkpoint"] == "WP2_Widget_registry_and_manifest"
    assert packet["first_priority"] == "independent_WebSocket_push_auto_updating_widgets"
    assert packet["widget_registry_ready"] is True
    assert packet["widget_manifest_contract_ready"] is True
    assert packet["topic_binding_contract_ready"] is True
    assert packet["per_widget_state_contract_ready"] is True
    assert packet["widget_update_reducer_contract_ready"] is True
    assert packet["widget_render_packet_contract_ready"] is True
    assert packet["widget_health_status_contract_ready"] is True
    assert packet["push_router_contract_ready"] is True
    assert packet["future_widget_extension_contract_seeded"] is True
    assert packet["registry"]["widget_count"] == 2
    assert packet["router"]["receive_only"] is True
    assert packet["router"]["send_enabled"] is False
    assert assert_wp1_no_send(packet)["ok"] is True
    assert assert_wp1_no_send(dict(packet, broker_send_enabled=True))["ok"] is False
    assert "wp1_completed=true" in DOC.read_text(encoding="utf-8-sig")
