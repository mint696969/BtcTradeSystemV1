# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_transport_ownership_q30c.py
# desc: PS-Q30C guards for WarRoom v2 natural-update transport ownership contracts.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_TRANSPORT_OWNERSHIP_VERSION,
    build_warroom_v2_transport_event_envelope,
    build_warroom_v2_transport_ownership_contract,
    build_warroom_v2_transport_subscription_contract,
    build_warroom_v2_widget_topic_catalog,
    build_widget_update_event,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
V2_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2"
INIT = V2_DIR / "__init__.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q30C_WARROOM_V2_TRANSPORT_OWNERSHIP_2026-07-02.md"


def test_q30c_topic_catalog_includes_market_snapshot_and_chart_review() -> None:
    packet = build_warroom_v2_widget_topic_catalog()
    roles = {row["topic"]: row["role"] for row in packet["rows"]}
    assert roles["warroom.market.snapshot"] == "market_snapshot_strip"
    assert roles["warroom.chart.review"] == "chart_review_panel"
    assert packet["transport_implemented"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q30c_transport_owner_is_external_and_ui_is_consumer_only() -> None:
    packet = build_warroom_v2_transport_ownership_contract()
    assert packet["transport_ownership_version"] == WARROOM_V2_TRANSPORT_OWNERSHIP_VERSION
    assert packet["transport_owner"] == "external_read_model_event_bridge"
    assert packet["ui_role"] == "read_model_event_consumer_only"
    assert packet["page_owns_transport_source"] is False
    assert packet["widget_owns_transport_source"] is False
    assert packet["broad_page_reload_required"] is False
    assert packet["natural_update_goal"] is True
    assert packet["transport_implemented_now"] is False
    assert packet["would_send_to_broker"] is False


def test_q30c_subscription_contract_targets_widget_patch_unit() -> None:
    packet = build_warroom_v2_transport_subscription_contract(widget_id="market_snapshot_strip", topic="warroom.market.snapshot")
    assert packet["topic_known"] is True
    assert packet["ui_consumer_only"] is True
    assert packet["event_unit"] == "widget_topic"
    assert packet["patch_unit"] == "widget_dom_region"
    assert packet["broad_page_reload_required"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q30c_event_envelope_wraps_widget_update_event_without_enabling_transport() -> None:
    event = build_widget_update_event(widget_id="market_snapshot_strip", topic="warroom.market.snapshot", generated_at="2026-07-02T12:00:00Z", previous_fingerprint="old", current_fingerprint="new", sequence=42, title="Market Snapshot", payload={"ltp": 9900000})
    packet = build_warroom_v2_transport_event_envelope(widget_update_event=event, channel="future_ws_or_sse")
    assert packet["payload_kind"] == "widget_update_event"
    assert packet["topic"] == "warroom.market.snapshot"
    assert packet["widget_id"] == "market_snapshot_strip"
    assert packet["changed"] is True
    assert packet["ui_patch_unit"] == "widget_dom_region"
    assert packet["transport_implemented_now"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q30c_exports_transport_contracts() -> None:
    text = INIT.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_transport_ownership_contract" in text
    assert "build_warroom_v2_transport_subscription_contract" in text
    assert "build_warroom_v2_transport_event_envelope" in text


def test_q30c_v2_files_remain_side_effect_free() -> None:
    forbidden = ("import streamlit", "from streamlit", "D:" + "\\", "E:" + "\\", "send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in V2_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"v2 file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q30c_doc_records_transport_ownership_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "transport_owner=external_read_model_event_bridge" in text
    assert "ui_role=read_model_event_consumer_only" in text
    assert "natural_widget_update_goal=true" in text
    assert "transport_implemented_now=false" in text
    assert "would_send_to_broker=false" in text
