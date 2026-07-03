# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_consumer_state_replay_q31d.py
# desc: PS-Q31D guards for WarRoom v2 consumer state, dedup, replay, and reconnect helpers.

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
from btcts.apps.operator_ui.prediction_warroom.v2.transport import (  # noqa: E402
    apply_warroom_v2_consumer_message,
    build_empty_warroom_v2_consumer_state,
    build_warroom_v2_consumer_state_contract,
    build_warroom_v2_latest_snapshot_by_topic,
    build_warroom_v2_reconnect_request,
    build_warroom_v2_replay_contract,
    build_warroom_v2_replay_cursor_from_consumer_state,
    build_warroom_v2_replay_response,
    decide_warroom_v2_consumer_message_action,
    select_warroom_v2_replay_events_after_cursor,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31D_WARROOM_V2_CONSUMER_STATE_DEDUP_REPLAY_HELPERS_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def _message(sequence: int, ltp: int = 1) -> dict[str, object]:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": ltp}, sequence=sequence)
    message = build_warroom_v2_outbound_message_payload(event_packet=event)
    message["current_fingerprint"] = event["current_fingerprint"]
    return message


def test_q31d_contracts_are_disabled_and_display_only() -> None:
    consumer = build_warroom_v2_consumer_state_contract()
    replay = build_warroom_v2_replay_contract()
    for packet in [consumer, replay]:
        assert packet["whole_warroom_display_update_target"] is True
        assert packet["prediction_cards_display_update_target"] is True
        assert packet["prediction_generation_invoked"] is False
        assert packet["prediction_inference_invoked"] is False
        assert packet["transport_enabled"] is False
        assert packet["websocket_enabled"] is False
        assert packet["sse_enabled"] is False
        assert packet["would_send_to_broker"] is False


def test_q31d_consumer_state_applies_first_and_drops_duplicate_fingerprint() -> None:
    state = build_empty_warroom_v2_consumer_state()
    first = apply_warroom_v2_consumer_message(consumer_state=state, message=_message(1, 1), received_at="t1")
    duplicate = apply_warroom_v2_consumer_message(consumer_state=first["consumer_state"], message=_message(1, 1), received_at="t2")
    assert first["applied"] is True
    assert first["decision"]["reason"] == "first_message"
    assert duplicate["applied"] is False
    assert duplicate["decision"]["reason"] == "duplicate_fingerprint"
    assert duplicate["consumer_state"]["dropped_count"] == 1


def test_q31d_consumer_state_drops_lower_sequence_but_allows_same_sequence_changed_fingerprint() -> None:
    state = apply_warroom_v2_consumer_message(consumer_state=build_empty_warroom_v2_consumer_state(), message=_message(3, 1))["consumer_state"]
    stale = decide_warroom_v2_consumer_message_action(consumer_state=state, message=_message(2, 2))
    changed = decide_warroom_v2_consumer_message_action(consumer_state=state, message=_message(3, 3))
    assert stale["apply"] is False
    assert stale["reason"] == "stale_sequence"
    assert changed["apply"] is True
    assert changed["reason"] == "same_sequence_changed_fingerprint"


def test_q31d_replay_cursor_is_derived_from_consumer_state() -> None:
    state = build_empty_warroom_v2_consumer_state()
    state = apply_warroom_v2_consumer_message(consumer_state=state, message=_message(5), received_at="t5")["consumer_state"]
    cursor = build_warroom_v2_replay_cursor_from_consumer_state(state)
    request = build_warroom_v2_reconnect_request(consumer_state=state, subscribed_topics=["warroom.market.snapshot"])
    assert cursor == {"warroom.market.snapshot": 5}
    assert request["cursor"] == {"warroom.market.snapshot": 5}
    assert request["transport_enabled"] is False


def test_q31d_replay_selects_events_after_cursor_and_latest_snapshot() -> None:
    messages = [_message(1, 1), _message(2, 2), _message(3, 3)]
    selected = select_warroom_v2_replay_events_after_cursor(messages=messages, cursor={"warroom.market.snapshot": 1}, max_events=4)
    latest = build_warroom_v2_latest_snapshot_by_topic(messages)
    assert [item["sequence"] for item in selected] == [2, 3]
    assert latest["warroom.market.snapshot"]["sequence"] == 3


def test_q31d_replay_response_is_bounded_and_marks_gap() -> None:
    response = build_warroom_v2_replay_response(messages=[_message(1), _message(2), _message(3)], cursor={"warroom.market.snapshot": 0}, max_events=2)
    assert response["replay_event_count"] == 2
    assert response["gap_marker"] is True
    assert response["latest_snapshots"]["warroom.market.snapshot"]["sequence"] == 3
    assert response["websocket_enabled"] is False
    assert response["sse_enabled"] is False


def test_q31d_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "consumer_state_module=" in doc
    assert "replay_module=" in doc
    assert "not_enabling_websocket=true" in doc
    assert "not_invoking_prediction_inference=true" in doc
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
