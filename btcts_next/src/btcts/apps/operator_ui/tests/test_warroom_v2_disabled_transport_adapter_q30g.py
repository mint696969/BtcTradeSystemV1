# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_disabled_transport_adapter_q30g.py
# desc: PS-Q30G guards for WarRoom v2 disabled transport adapter payload contract.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION,
    build_warroom_v2_disabled_transport_adapter_contract,
    build_warroom_v2_disabled_transport_outbox,
    build_warroom_v2_local_event_queue_state,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_outbound_message_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
V2_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2"
INIT = V2_DIR / "__init__.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q30G_WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_2026-07-02.md"


def test_q30g_adapter_contract_is_disabled_and_side_effect_free() -> None:
    packet = build_warroom_v2_disabled_transport_adapter_contract()
    assert packet["disabled_transport_adapter_version"] == WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION
    assert packet["adapter_kind"] == "disabled_outbound_transport_payload_adapter"
    assert packet["input_kind"] == "local_event_queue_state"
    assert packet["output_kind"] == "outbound_message_payload_contract"
    assert packet["transport_implemented_now"] is False
    assert packet["adapter_sends_messages"] is False
    assert packet["adapter_opens_socket"] is False
    assert packet["would_send_to_broker"] is False


def test_q30g_outbound_message_payload_wraps_event_envelope_without_sending() -> None:
    event = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 1}, sequence=3)
    message = build_warroom_v2_outbound_message_payload(event_packet=event, transport_kind="disabled_ws_payload")
    assert message["message_type"] == "warroom_v2_widget_update"
    assert message["payload_kind"] == "widget_update_event_envelope"
    assert message["topic"] == "warroom.market.snapshot"
    assert message["widget_id"] == "market_snapshot_strip"
    assert message["sequence"] == 3
    assert message["ui_patch_unit"] == "widget_dom_region"
    assert message["adapter_sends_messages"] is False
    assert message["websocket_enabled"] is False
    assert message["sse_enabled"] is False
    assert json.loads(message["json_payload"])["topic"] == "warroom.market.snapshot"


def test_q30g_disabled_outbox_is_bounded_and_contains_messages() -> None:
    events = [build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": i}, sequence=i) for i in range(5)]
    queue = build_warroom_v2_local_event_queue_state(events=events, max_events=5)
    outbox = build_warroom_v2_disabled_transport_outbox(queue_state=queue, transport_kind="disabled_future_stream", max_messages=2)
    assert outbox["message_count"] == 2
    assert outbox["topics"] == ["warroom.market.snapshot", "warroom.market.snapshot"]
    assert [message["sequence"] for message in outbox["messages"]] == [3, 4]
    assert outbox["adapter_opens_socket"] is False
    assert outbox["transport_implemented_now"] is False
    assert outbox["would_send_to_broker"] is False


def test_q30g_exports_disabled_transport_adapter_helpers() -> None:
    text = INIT.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_disabled_transport_adapter_contract" in text
    assert "build_warroom_v2_disabled_transport_outbox" in text
    assert "build_warroom_v2_outbound_message_payload" in text
    assert "WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION" in text


def test_q30g_v2_files_remain_side_effect_free() -> None:
    forbidden = ("import streamlit", "from streamlit", "D:" + "\\", "E:" + "\\", "send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in V2_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"v2 file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q30g_doc_records_disabled_transport_adapter_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "disabled_outbound_transport_payload_adapter=true" in text
    assert "input_kind=local_event_queue_state" in text
    assert "output_kind=outbound_message_payload_contract" in text
    assert "adapter_sends_messages=false" in text
    assert "would_send_to_broker=false" in text
