# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_disabled_transport_simulator_q31b.py
# desc: PS-Q31B guards for WarRoom v2 disabled in-process transport simulator contract.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_chart_review_update_event,
    build_warroom_v2_local_event_queue_state,
    build_warroom_v2_market_snapshot_update_event,
)
from btcts.apps.operator_ui.prediction_warroom.v2.disabled_transport_adapter import build_warroom_v2_outbound_message_payload  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.topics import WARROOM_V2_WIDGET_TOPICS  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport import (  # noqa: E402
    WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_VERSION,
    WARROOM_V2_DISPLAY_TARGET_TOPICS,
    build_warroom_v2_disabled_transport_simulation_frame,
    build_warroom_v2_disabled_transport_simulation_from_queue,
    build_warroom_v2_disabled_transport_simulator_contract,
    filter_warroom_v2_display_target_messages,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
ROADMAP = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31_ROADMAP_WARROOM_V2_SEAMLESS_WARROOM_DISPLAY_UPDATES_2026-07-03.md"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31B_WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_CONTRACT_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def test_q31b_contract_is_disabled_and_targets_whole_warroom_display() -> None:
    packet = build_warroom_v2_disabled_transport_simulator_contract()
    assert packet["simulator_version"] == WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_VERSION
    assert packet["target_goal"] == "seamless_whole_warroom_display_updates"
    assert packet["whole_warroom_display_update_target"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["target_topics"] == list(WARROOM_V2_WIDGET_TOPICS)
    assert packet["target_topics"] == list(WARROOM_V2_DISPLAY_TARGET_TOPICS)
    assert "warroom.market.snapshot" in packet["target_topics"]
    assert "warroom.chart.review" in packet["target_topics"]
    assert "warroom.prediction.market_regime" in packet["target_topics"]
    assert "warroom.prediction.scenario_ja" in packet["target_topics"]
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False
    assert packet["transport_enabled"] is False
    assert packet["simulator_sends_messages"] is False
    assert packet["simulator_opens_socket"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q31b_filter_keeps_top_prediction_and_bottom_display_targets() -> None:
    messages = [
        {"topic": "warroom.current_state", "widget_id": "current_state_mini_bar", "sequence": 1},
        {"topic": "warroom.market.snapshot", "widget_id": "market_snapshot_strip", "sequence": 2},
        {"topic": "warroom.prediction.market_regime", "widget_id": "prediction_card.market_regime", "sequence": 3},
        {"topic": "warroom.chart.review", "widget_id": "chart_review_panel", "sequence": 4},
        {"topic": "outside.topic", "widget_id": "outside", "sequence": 5},
    ]
    filtered = filter_warroom_v2_display_target_messages(messages)
    assert [item["topic"] for item in filtered] == [
        "warroom.current_state",
        "warroom.market.snapshot",
        "warroom.prediction.market_regime",
        "warroom.chart.review",
    ]
    assert all(item["ui_patch_unit"] == "widget_dom_region" for item in filtered)


def test_q31b_simulation_frame_is_in_process_shadow_only() -> None:
    frame = build_warroom_v2_disabled_transport_simulation_frame(
        messages=[
            {"topic": "warroom.alerts", "widget_id": "operator_alert_summary", "sequence": 1},
            {"topic": "warroom.prediction.trend_bias", "widget_id": "prediction_card.trend_bias", "sequence": 2},
            {"topic": "warroom.safety", "widget_id": "safety_boundary_summary", "sequence": 3},
        ],
        frame_id="unit-test-frame",
    )
    assert frame["frame_id"] == "unit-test-frame"
    assert frame["frame_kind"] == "disabled_in_process_transport_shadow_frame"
    assert frame["topics"] == ["warroom.alerts", "warroom.prediction.trend_bias", "warroom.safety"]
    assert frame["would_patch_unit"] == "widget_dom_region"
    assert frame["broad_page_reload_required"] is False
    assert frame["transport_enabled"] is False
    assert frame["websocket_enabled"] is False
    assert frame["sse_enabled"] is False
    assert frame["runtime_connected"] is False
    assert frame["classifier_invoked"] is False
    assert frame["prediction_generation_invoked"] is False
    assert frame["prediction_inference_invoked"] is False


def test_q31b_simulation_from_q30g_queue_preserves_payload_shape_without_sending() -> None:
    market_event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 1}, sequence=10)
    chart_event = build_warroom_v2_chart_review_update_event(chart_payload={"rows": 3}, sequence=11)
    queue = build_warroom_v2_local_event_queue_state(events=[market_event, chart_event], max_events=4)
    frame = build_warroom_v2_disabled_transport_simulation_from_queue(queue_state=queue, frame_id="queue-shadow")
    assert frame["source_outbox_kind"] == "disabled_outbound_transport_payload_adapter"
    assert frame["source_message_count"] == 2
    assert frame["topics"] == ["warroom.market.snapshot", "warroom.chart.review"]
    assert frame["widget_ids"] == ["market_snapshot_strip", "chart_review_panel"]
    assert frame["messages"][0]["payload_kind"] == "widget_update_event_envelope"
    assert frame["messages"][0]["message_type"] == "warroom_v2_widget_update"
    assert frame["simulator_sends_messages"] is False


def test_q31b_can_wrap_q30g_message_payload_directly() -> None:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 2}, sequence=12)
    message = build_warroom_v2_outbound_message_payload(event_packet=event, transport_kind="disabled_future_stream")
    frame = build_warroom_v2_disabled_transport_simulation_frame(messages=[message])
    assert frame["message_count"] == 1
    assert frame["messages"][0]["payload_kind"] == "widget_update_event_envelope"
    assert frame["messages"][0]["ui_patch_unit"] == "widget_dom_region"


def test_q31b_docs_record_roadmap_and_no_live_transport_boundary() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8-sig")
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "goal=seamless_warroom_display_updates" in roadmap
    assert "prediction_cards_display_update_target=true" in roadmap
    assert "prediction_generation_out_of_scope=true" in roadmap
    assert "PS-Q31B: disabled in-process transport simulator contract" in roadmap
    assert "disabled_in_process_transport_simulator=true" in doc
    assert "simulator_transport_enabled=false" in doc
    assert "target_top_topics=warroom.current_state,warroom.alerts,warroom.safety,warroom.market.snapshot" in doc
    assert "target_prediction_display_topics=warroom.prediction.market_regime" in doc
    assert "target_bottom_topics=warroom.chart.review" in doc
    assert "prediction_inference_invoked=false" in doc


def test_q31b_transport_package_files_stay_small_and_side_effect_free() -> None:
    forbidden = (
        "import streamlit",
        "from streamlit",
        "websocket.",
        "sse.",
        "send_to_broker(",
        "append_ledger(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "run_prediction(",
        "invoke_classifier(",
        "D:" + chr(92),
        "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
