# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_receive_only_topic_routing.py
# desc: MR-VS6.3 guards canonical receive-only MarketRegime topic registration and bounded state routing.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp2_widget_registry_manifest import (  # noqa: E402
    build_wp2_registry_manifest_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp3_per_widget_state_store import (  # noqa: E402
    apply_widget_state_update,
    build_initial_widget_state_store,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp5_topic_routing_subscription_plan import (  # noqa: E402
    build_topic_route_plans,
    build_wp5_subscription_plan_packet,
)

TOPIC_KEY = "prediction.family.market_regime"
WIDGET_ID = "market_regime_prediction_widget"


def test_market_regime_topic_is_registered_once_as_receive_only() -> None:
    packet = build_wp2_registry_manifest_packet()
    bindings = [item for item in packet["topic_bindings"] if item["topic_key"] == TOPIC_KEY]
    manifests = [item for item in packet["manifests"] if item["widget_id"] == WIDGET_ID]

    assert len(bindings) == 1
    assert len(manifests) == 1
    assert bindings[0]["widget_id"] == WIDGET_ID
    assert bindings[0]["topic_pattern"] == TOPIC_KEY
    assert bindings[0]["receive_only"] is True
    assert manifests[0]["read_only"] is True
    assert manifests[0]["topic_keys"] == [TOPIC_KEY]
    assert packet["routes_by_topic"][TOPIC_KEY] == WIDGET_ID


def test_market_regime_route_is_intent_only_and_never_subscribed_here() -> None:
    routes = [route for route in build_topic_route_plans() if route.topic_key == TOPIC_KEY]
    assert len(routes) == 1
    route = routes[0]
    assert route.channel_group == "prediction"
    assert route.receive_only is True
    assert route.subscribe_intent_only is True
    assert route.subscribe_invoked is False

    packet = build_wp5_subscription_plan_packet()
    assert "prediction" in packet["channel_groups"]
    assert packet["plan"]["websocket_opened"] is False
    assert packet["plan"]["subscribe_invoked"] is False
    assert packet["websocket_subscribe_invoked"] is False
    assert packet["websocket_send_enabled"] is False


def test_market_regime_is_registered_for_state_but_not_mounted_before_mr_vs6_5() -> None:
    from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp6_independent_widget_update_pipeline import (
        build_render_packets_from_store,
    )

    registry = build_wp2_registry_manifest_packet()
    manifest = next(item for item in registry["manifests"] if item["widget_id"] == WIDGET_ID)
    store = build_initial_widget_state_store()
    render_packets = build_render_packets_from_store(store)

    assert manifest["mount_enabled"] is False
    assert WIDGET_ID in store["widgets"]
    assert WIDGET_ID not in render_packets


def test_market_regime_state_update_is_bounded_and_isolated() -> None:
    store = build_initial_widget_state_store()
    before_other = store["widgets"]["market_depth_widget"]
    updated = apply_widget_state_update(
        store,
        topic_key=TOPIC_KEY,
        updated_at_ms=123456,
        sequence=9,
        value={
            "prediction_family_id": "market_regime",
            "run_id": "run-1",
            "prediction_id": "prediction-1",
            "horizon_count": 8,
            "raw_payload": {"must": "drop"},
            "callable": object(),
        },
    )

    target = updated["widgets"][WIDGET_ID]
    value = target["snapshots"][TOPIC_KEY]["value"]
    assert target["sequence"] == 9
    assert value == {
        "prediction_family_id": "market_regime",
        "run_id": "run-1",
        "prediction_id": "prediction-1",
        "horizon_count": 8,
    }
    assert updated["widgets"]["market_depth_widget"] == before_other
    assert store["widgets"][WIDGET_ID]["sequence"] == 0
