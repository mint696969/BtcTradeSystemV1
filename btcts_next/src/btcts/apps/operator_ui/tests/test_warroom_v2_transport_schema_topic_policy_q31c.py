# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_transport_schema_topic_policy_q31c.py
# desc: PS-Q31C guards for WarRoom v2 transport schema and topic policy modules.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
)
from btcts.apps.operator_ui.prediction_warroom.v2.topics import WARROOM_V2_WIDGET_TOPICS  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.transport import (  # noqa: E402
    BOTTOM_CHART_TOPICS,
    PREDICTION_DISPLAY_TOPICS,
    TOP_INFORMATION_TOPICS,
    WARROOM_V2_MESSAGE_TYPE,
    WARROOM_V2_PATCH_UNIT,
    WARROOM_V2_PAYLOAD_KIND,
    build_warroom_v2_topic_policy,
    build_warroom_v2_topic_policy_contract,
    build_warroom_v2_transport_schema_contract,
    is_warroom_v2_display_topic,
    list_warroom_v2_topic_policies,
    normalize_warroom_v2_transport_message,
    validate_warroom_v2_transport_message,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31C_WARROOM_V2_TRANSPORT_SCHEMA_AND_TOPIC_POLICY_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def test_q31c_schema_contract_preserves_disabled_q30g_shape() -> None:
    packet = build_warroom_v2_transport_schema_contract()
    assert packet["message_type"] == WARROOM_V2_MESSAGE_TYPE == "warroom_v2_widget_update"
    assert packet["payload_kind"] == WARROOM_V2_PAYLOAD_KIND == "widget_update_event_envelope"
    assert packet["patch_unit"] == WARROOM_V2_PATCH_UNIT == "widget_dom_region"
    assert packet["q30g_payload_compatible"] is True
    assert packet["q31b_simulator_compatible"] is True
    assert packet["prediction_cards_display_update_target"] is True
    assert packet["prediction_generation_invoked"] is False
    assert packet["prediction_inference_invoked"] is False
    assert packet["transport_enabled"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_q31c_schema_normalizes_q30g_message_without_enabling_transport() -> None:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 1}, sequence=7)
    message = build_warroom_v2_outbound_message_payload(event_packet=event)
    normalized = normalize_warroom_v2_transport_message(message)
    validated = validate_warroom_v2_transport_message(message)
    assert validated["ok"] is True
    assert normalized["message_type"] == "warroom_v2_widget_update"
    assert normalized["payload_kind"] == "widget_update_event_envelope"
    assert normalized["topic"] == "warroom.market.snapshot"
    assert normalized["widget_id"] == "market_snapshot_strip"
    assert normalized["sequence"] == 7
    assert normalized["ui_patch_unit"] == "widget_dom_region"
    assert normalized["broad_page_reload_required"] is False
    assert normalized["transport_enabled"] is False
    assert normalized["prediction_generation_invoked"] is False
    assert normalized["would_send_to_broker"] is False


def test_q31c_topic_policy_covers_whole_warroom_display() -> None:
    contract = build_warroom_v2_topic_policy_contract()
    assert contract["policy_scope"] == "whole_warroom_display"
    assert contract["topic_count"] == len(WARROOM_V2_WIDGET_TOPICS)
    assert contract["topics"] == list(WARROOM_V2_WIDGET_TOPICS)
    assert set(TOP_INFORMATION_TOPICS) <= set(contract["topics"])
    assert set(PREDICTION_DISPLAY_TOPICS) <= set(contract["topics"])
    assert set(BOTTOM_CHART_TOPICS) <= set(contract["topics"])
    assert "warroom.prediction.market_regime" in contract["prediction_display_topics"]
    assert "warroom.prediction.scenario_ja" in contract["prediction_display_topics"]
    assert contract["prediction_cards_display_update_target"] is True
    assert contract["prediction_generation_out_of_scope"] is True
    assert contract["prediction_inference_out_of_scope"] is True
    assert contract["websocket_enabled"] is False
    assert contract["sse_enabled"] is False


def test_q31c_topic_policy_assigns_cadence_by_surface() -> None:
    market = build_warroom_v2_topic_policy("warroom.market.snapshot")
    safety = build_warroom_v2_topic_policy("warroom.safety")
    prediction = build_warroom_v2_topic_policy("warroom.prediction.trend_bias")
    scenario = build_warroom_v2_topic_policy("warroom.prediction.scenario_ja")
    chart = build_warroom_v2_topic_policy("warroom.chart.review")
    assert market["surface"] == "top_information"
    assert market["update_class"] == "fastest_safe"
    assert safety["priority"] == 100
    assert prediction["surface"] == "prediction_display"
    assert prediction["update_class"] == "evidence_change_or_moderate_frequency"
    assert scenario["stale_policy"] == "preserve_last_scenario_text_with_generated_at"
    assert chart["surface"] == "bottom_chart"
    assert chart["update_class"] == "medium_or_operator_opt_in"
    assert all(policy["broad_page_reload_required"] is False for policy in [market, safety, prediction, scenario, chart])
    assert all(policy["prediction_generation_invoked"] is False for policy in [market, safety, prediction, scenario, chart])


def test_q31c_display_topic_helper_matches_topic_catalog() -> None:
    assert all(is_warroom_v2_display_topic(topic) for topic in WARROOM_V2_WIDGET_TOPICS)
    assert is_warroom_v2_display_topic("outside.topic") is False
    assert len(list_warroom_v2_topic_policies()) == len(WARROOM_V2_WIDGET_TOPICS)


def test_q31c_doc_records_schema_policy_and_no_inference_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "transport_schema_module=" in text
    assert "topic_policy_module=" in text
    assert "whole_warroom_display_update_target=true" in text
    assert "prediction_cards_display_update_target=true" in text
    assert "prediction_generation_out_of_scope=true" in text
    assert "not_invoking_prediction_inference=true" in text
    assert "websocket_enabled=false" in text
    assert "sse_enabled=false" in text


def test_q31c_transport_modules_stay_small_and_side_effect_free() -> None:
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
