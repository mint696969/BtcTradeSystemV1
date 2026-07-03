# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_local_event_queue_q30f.py
# desc: PS-Q30F guards for WarRoom v2 disabled local event queue/state holder.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_LOCAL_EVENT_QUEUE_VERSION,
    build_warroom_v2_local_event_queue_contract,
    build_warroom_v2_local_event_queue_state,
    build_warroom_v2_market_snapshot_update_event,
    extract_changed_event_packets,
    update_warroom_v2_local_event_queue_from_bridge,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
V2_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2"
INIT = V2_DIR / "__init__.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q30F_WARROOM_V2_LOCAL_EVENT_QUEUE_2026-07-02.md"


def test_q30f_queue_contract_is_disabled_and_side_effect_free() -> None:
    packet = build_warroom_v2_local_event_queue_contract()
    assert packet["local_event_queue_version"] == WARROOM_V2_LOCAL_EVENT_QUEUE_VERSION
    assert packet["queue_kind"] == "disabled_local_event_queue_state_holder"
    assert packet["input_kind"] == "read_model_event_bridge_packet"
    assert packet["event_filter"] == "changed_only"
    assert packet["transport_implemented_now"] is False
    assert packet["queue_starts_transport"] is False
    assert packet["queue_reads_dhot"] is False
    assert packet["would_send_to_broker"] is False


def test_q30f_extracts_only_changed_events_from_bridge_packet() -> None:
    changed = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 1}, previous_fingerprint="old")
    unchanged = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 2}, previous_fingerprint="")
    unchanged["changed"] = False
    packet = {"market_snapshot_event": changed, "chart_review_event": unchanged}
    events = extract_changed_event_packets(packet)
    assert len(events) == 1
    assert events[0]["topic"] == "warroom.market.snapshot"


def test_q30f_queue_state_is_bounded_and_tracks_latest_fingerprints() -> None:
    events = [build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": i}, sequence=i) for i in range(5)]
    state = build_warroom_v2_local_event_queue_state(events=events, max_events=3)
    assert state["event_count"] == 3
    assert [event["event"]["sequence"] for event in state["events"]] == [2, 3, 4]
    assert state["fingerprints"]["market_snapshot_strip"] == events[-1]["current_fingerprint"]
    assert state["transport_implemented_now"] is False


def test_q30f_update_queue_from_bridge_appends_changed_events() -> None:
    bridge = {"market_snapshot_event": build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 1}, sequence=1)}
    state = update_warroom_v2_local_event_queue_from_bridge(queue_state=None, bridge_packet=bridge, max_events=8)
    assert state["event_count"] == 1
    assert state["topics"] == ["warroom.market.snapshot"]
    state2 = update_warroom_v2_local_event_queue_from_bridge(queue_state=state, bridge_packet=bridge, max_events=8)
    assert state2["event_count"] == 2
    assert state2["websocket_enabled"] is False
    assert state2["sse_enabled"] is False


def test_q30f_exports_queue_helpers() -> None:
    text = INIT.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_local_event_queue_contract" in text
    assert "build_warroom_v2_local_event_queue_state" in text
    assert "update_warroom_v2_local_event_queue_from_bridge" in text
    assert "extract_changed_event_packets" in text


def test_q30f_v2_files_remain_side_effect_free() -> None:
    forbidden = ("import streamlit", "from streamlit", "D:" + "\\", "E:" + "\\", "send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in V2_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"v2 file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q30f_doc_records_queue_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "disabled_local_event_queue_state_holder=true" in text
    assert "event_filter=changed_only" in text
    assert "bounded_max_events=true" in text
    assert "transport_implemented_now=false" in text
    assert "would_send_to_broker=false" in text
