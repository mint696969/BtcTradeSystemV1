# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp10_widget_extension_contract.py
# desc: WP10 verifies future widget extension contract and no-action boundary.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP10_WIDGET_EXTENSION_CONTRACT_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp2_widget_registry_manifest import PushWidgetManifest, PushWidgetTopicBinding  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp10_widget_extension_contract import WidgetExtensionContract, build_example_safe_widget_extension_contract, build_wp10_widget_extension_contract_packet, validate_widget_extension_contract  # noqa: E402


def test_wp10_packet_marks_extension_contract_ready_and_safe() -> None:
    packet = build_wp10_widget_extension_contract_packet()
    assert packet["wp10_completed"] is True
    assert packet["next_checkpoint"] == "WP11_Top_layout_push_widget_polish"
    assert packet["widget_extension_contract_ready"] is True
    assert packet["extension_validator_ready"] is True
    assert packet["future_widget_addition_ready"] is True
    assert packet["extension_without_page_edit_ready"] is True
    assert packet["extension_no_action_boundary_ready"] is True
    assert packet["base_widget_count"] == 5
    assert packet["warroom_page_modified"] is False
    assert packet["websocket_opened"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert "wp10_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp10_safe_example_contract_validates() -> None:
    contract = build_example_safe_widget_extension_contract()
    validation = validate_widget_extension_contract(contract, sample_value={"symbol": "BTC_JPY", "imbalance": 0.1})
    assert validation["ok"] is True
    assert validation["topic_count"] == 1
    assert validation["errors"] == []


def test_wp10_rejects_duplicate_widget_and_action_flags() -> None:
    manifest = PushWidgetManifest("market_depth_widget", "Duplicate", "bad", ("market.depth",), "bad_reducer", "bad_render", "core_grid", 99)
    binding = PushWidgetTopicBinding("market_depth_widget", "market.depth", "market.depth.BTC_JPY")
    contract = WidgetExtensionContract("bad.extension", manifest, (binding,), send_allowed=True, broker_allowed=True, order_allowed=True)
    validation = validate_widget_extension_contract(contract, sample_value={"raw_payload": {"x": 1}})
    assert validation["ok"] is False
    assert "duplicate_widget_id:market_depth_widget" in validation["errors"]
    assert "duplicate_topic_key" in validation["errors"]
    assert "send_allowed" in validation["errors"]
    assert "broker_allowed" in validation["errors"]
    assert "order_allowed" in validation["errors"]
    assert "forbidden_sample_key:raw_payload" in validation["errors"]
