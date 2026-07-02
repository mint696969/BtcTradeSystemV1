# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_push_ready_widget_contract_q29a.py
# desc: PS-Q29A guards for WarRoom v2 push-ready widget read-model architecture. Contract-only; legacy WarRoom untouched.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LAYOUT_POLICY_VERSION,
    WARROOM_V2_TOPIC_CATALOG_VERSION,
    WARROOM_V2_WIDGET_READ_MODEL_VERSION,
    WARROOM_V2_WIDGET_UPDATE_EVENT_VERSION,
    build_empty_widget_read_model,
    build_warroom_v2_layout_policy,
    build_warroom_v2_widget_topic_catalog,
    build_widget_update_event,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29A_WARROOM_V2_PUSH_READY_WIDGET_CONTRACT_POLICY_2026-07-02.md"
V2_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q29a_topic_catalog_defines_widget_update_units() -> None:
    packet = build_warroom_v2_widget_topic_catalog()
    assert packet["topic_catalog_version"] == WARROOM_V2_TOPIC_CATALOG_VERSION
    assert packet["topic_count"] == len(packet["topics"])
    assert len(packet["topics"]) == len(set(packet["topics"]))
    assert "warroom.prediction.market_regime" in packet["topics"]
    assert "warroom.prediction.scenario_ja" in packet["topics"]
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["broad_page_reload_target"] is False
    assert all(row["widget_update_unit"] is True for row in packet["rows"])
    assert all(row["future_websocket_compatible"] is True for row in packet["rows"])
    assert packet["would_send_to_broker"] is False


def test_q29a_widget_read_model_is_consumer_only_and_display_safe() -> None:
    packet = build_empty_widget_read_model(
        widget_id="prediction_card_market_regime",
        topic="warroom.prediction.market_regime",
        generated_at="2026-07-02T04:00:00Z",
        title="地合い",
        payload={"regime_code": "RANGE"},
        freshness="live",
        fingerprint="abc",
        detail_available=True,
    )
    assert packet["version"] == WARROOM_V2_WIDGET_READ_MODEL_VERSION
    assert packet["read_model_consumer_only"] is True
    assert packet["widget_owns_artifact_scanning"] is False
    assert packet["widget_owns_classifier_invocation"] is False
    assert packet["widget_owns_cache_invalidation"] is False
    assert packet["future_push_compatible"] is True
    assert packet["payload"] == {"regime_code": "RANGE"}
    assert packet["safety"]["read_only"] is True
    assert packet["safety"]["would_send_to_broker"] is False


def test_q29a_widget_update_event_changed_flag_and_transport_boundary() -> None:
    changed = build_widget_update_event(
        widget_id="prediction_card_market_regime",
        topic="warroom.prediction.market_regime",
        generated_at="2026-07-02T04:00:01Z",
        previous_fingerprint="old",
        current_fingerprint="new",
        sequence=7,
        title="地合い",
    )
    unchanged = build_widget_update_event(
        widget_id="prediction_card_market_regime",
        topic="warroom.prediction.market_regime",
        generated_at="2026-07-02T04:00:02Z",
        previous_fingerprint="same",
        current_fingerprint="same",
        sequence=8,
    )
    assert changed["event_version"] == WARROOM_V2_WIDGET_UPDATE_EVENT_VERSION
    assert changed["changed"] is True
    assert unchanged["changed"] is False
    assert changed["event_source_replaceable"] is True
    assert changed["current_source_can_be_poll_fingerprint"] is True
    assert changed["future_websocket_compatible"] is True
    assert changed["future_sse_compatible"] is True
    assert changed["read_model"]["widget_owns_artifact_scanning"] is False
    assert changed["safety"]["would_send_to_broker"] is False


def test_q29a_layout_policy_keeps_page_as_shell_and_scenario_below_cards() -> None:
    packet = build_warroom_v2_layout_policy()
    assert packet["layout_policy_version"] == WARROOM_V2_LAYOUT_POLICY_VERSION
    assert packet["warroom_v2_layout_shell_only"] is True
    assert packet["warroom_legacy_retained_as_reference"] is True
    assert packet["warroom_v2_page_added"] is False
    assert packet["scenario_zone_after_cards"] is True
    assert packet["debug_default_collapsed"] is True
    assert packet["page_owns_artifact_scanning"] is False
    assert packet["page_owns_cache_invalidation"] is False
    assert packet["page_owns_classifier_invocation"] is False
    assert packet["page_owns_transport_source"] is False
    zones = {row["zone"] for row in packet["widgets"]}
    assert {"top", "prediction_cards", "scenario"} <= zones
    scenario_order = next(row["order"] for row in packet["widgets"] if row["widget_id"] == "prediction_scenario_ja")
    card_orders = [row["order"] for row in packet["widgets"] if row["zone"] == "prediction_cards"]
    assert min(card_orders) < scenario_order


def test_q29a_doc_records_new_warroom_v2_decision_and_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "Keep the current `warroom_page.py` as **WarRoom Legacy**" in text
    assert "WarRoom v2 is a read-model consumer" in text
    assert "widget_topic_update_unit=true" in text
    assert "future_websocket_sse_compatible=true" in text
    assert "not_rewriting_current_warroom_now=true" in text
    assert "not_enabling_websocket_now=true" in text
    assert "would_send_to_broker=false" in text


def test_q29a_v2_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "import streamlit",
        "from streamlit",
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in V2_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"v2 file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29a_legacy_warroom_page_is_not_touched_by_v2_contract() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "prediction_warroom.v2" not in text
    assert "build_warroom_v2_layout_policy" not in text
    assert "build_warroom_v2_widget_topic_catalog" not in text
    assert "WidgetUpdateEvent" not in text
    assert "WebSocket" not in text
    assert "SSE" not in text
