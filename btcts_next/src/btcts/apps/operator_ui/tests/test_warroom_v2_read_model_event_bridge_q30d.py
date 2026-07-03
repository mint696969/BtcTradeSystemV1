# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_read_model_event_bridge_q30d.py
# desc: PS-Q30D guards for WarRoom v2 read-model event bridge prototype.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_READ_MODEL_EVENT_BRIDGE_VERSION,
    build_warroom_v2_chart_review_update_event,
    build_warroom_v2_market_snapshot_update_event,
    build_warroom_v2_read_model_event_bridge_contract,
    build_warroom_v2_read_model_update_event,
    stable_payload_fingerprint,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
V2_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2"
INIT = V2_DIR / "__init__.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q30D_WARROOM_V2_READ_MODEL_EVENT_BRIDGE_2026-07-02.md"


def test_q30d_bridge_contract_is_disabled_transport_and_consumer_safe() -> None:
    packet = build_warroom_v2_read_model_event_bridge_contract()
    assert packet["read_model_event_bridge_version"] == WARROOM_V2_READ_MODEL_EVENT_BRIDGE_VERSION
    assert packet["bridge_kind"] == "local_read_model_event_bridge_prototype"
    assert packet["input_kind"] == "prebuilt_read_model_payload"
    assert packet["output_kind"] == "widget_update_event_envelope"
    assert packet["transport_implemented_now"] is False
    assert packet["bridge_starts_transport"] is False
    assert packet["bridge_reads_dhot"] is False
    assert packet["bridge_invokes_classifier"] is False
    assert packet["would_send_to_broker"] is False


def test_q30d_fingerprint_is_stable_and_change_sensitive() -> None:
    left = {"ltp": 1, "market": "BTC-FX-JPY"}
    reordered = {"market": "BTC-FX-JPY", "ltp": 1}
    changed = {"market": "BTC-FX-JPY", "ltp": 2}
    assert stable_payload_fingerprint(left) == stable_payload_fingerprint(reordered)
    assert stable_payload_fingerprint(left) != stable_payload_fingerprint(changed)
    assert len(stable_payload_fingerprint(left)) == 24


def test_q30d_market_snapshot_event_wraps_widget_event_and_envelope() -> None:
    packet = build_warroom_v2_market_snapshot_update_event(snapshot_payload={"ltp": 9900000}, generated_at="2026-07-02T12:00:00Z", previous_fingerprint="old", sequence=9)
    assert packet["widget_id"] == "market_snapshot_strip"
    assert packet["topic"] == "warroom.market.snapshot"
    assert packet["changed"] is True
    assert packet["event"]["read_model"]["payload"] == {"ltp": 9900000}
    assert packet["envelope"]["ui_patch_unit"] == "widget_dom_region"
    assert packet["transport_implemented_now"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q30d_chart_review_event_has_chart_topic_and_no_execution() -> None:
    packet = build_warroom_v2_chart_review_update_event(chart_payload={"timeframe": "5m", "rows": 240}, generated_at="2026-07-02T12:00:03Z", sequence=10)
    assert packet["widget_id"] == "chart_review_panel"
    assert packet["topic"] == "warroom.chart.review"
    assert packet["event"]["source_kind"] == "local_read_model_event_bridge_prototype"
    assert packet["envelope"]["broad_page_reload_required"] is False
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["would_send_to_broker"] is False


def test_q30d_generic_event_marks_unchanged_when_fingerprint_matches() -> None:
    payload = {"a": 1}
    fp = stable_payload_fingerprint(payload)
    packet = build_warroom_v2_read_model_update_event(widget_id="market_snapshot_strip", topic="warroom.market.snapshot", payload=payload, previous_fingerprint=fp, sequence=11)
    assert packet["changed"] is False
    assert packet["current_fingerprint"] == fp
    assert packet["event"]["changed"] is False


def test_q30d_exports_bridge_contracts() -> None:
    text = INIT.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_read_model_event_bridge_contract" in text
    assert "build_warroom_v2_market_snapshot_update_event" in text
    assert "build_warroom_v2_chart_review_update_event" in text
    assert "stable_payload_fingerprint" in text


def test_q30d_v2_files_remain_side_effect_free() -> None:
    forbidden = ("import streamlit", "from streamlit", "D:" + "\\", "E:" + "\\", "send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in V2_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"v2 file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q30d_doc_records_bridge_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "read_model_event_bridge_prototype=true" in text
    assert "input_kind=prebuilt_read_model_payload" in text
    assert "output_kind=widget_update_event_envelope" in text
    assert "transport_implemented_now=false" in text
    assert "would_send_to_broker=false" in text
