# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp2_widget_registry_manifest.py
# desc: WP2 verifies stable WarRoom push-widget registry and manifest with no-send boundary.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp2_widget_registry_manifest import PushWidgetManifest, build_wp2_registry_manifest_packet  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP2_REGISTRY_MANIFEST_2026-07-05.md"


def test_wp2_registry_manifest_default_catalog_is_stable_and_read_only() -> None:
    packet = build_wp2_registry_manifest_packet()
    assert packet["wp2_completed"] is True
    assert packet["next_checkpoint"] == "WP3_Per_widget_state_store"
    assert packet["widget_registry_manifest_ready"] is True
    assert packet["stable_registry_ready"] is True
    assert packet["manifest_driven_widgets_ready"] is True
    assert packet["topic_bindings_ready"] is True
    assert packet["future_widget_extension_metadata_ready"] is True
    assert packet["validation"]["widget_count"] == 5
    assert packet["validation"]["topic_binding_count"] == 7
    assert set(packet["routes_by_topic"]) >= {"market.depth", "market.trades", "market.spread", "market.liquidity"}
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["warroom_page_modified"] is False
    assert "wp2_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp2_registry_manifest_rejects_duplicate_widget_id() -> None:
    duplicate = PushWidgetManifest("market_depth_widget", "Duplicate", "bad", ("bad.topic",), "bad_reducer", "bad_render", "core_grid", 99)
    packet = build_wp2_registry_manifest_packet(manifests=(duplicate, duplicate), bindings=())
    assert packet["wp2_completed"] is False
    assert "duplicate_widget_id:market_depth_widget" in packet["validation"]["errors"]
