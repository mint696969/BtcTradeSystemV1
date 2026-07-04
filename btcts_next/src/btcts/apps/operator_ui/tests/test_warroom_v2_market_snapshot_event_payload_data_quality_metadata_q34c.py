# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_snapshot_event_payload_data_quality_metadata_q34c.py
# desc: PS-Q34C guards for carrying market_snapshot_strip data-quality metadata through event payloads. No visible UI, no socket.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (  # noqa: E402
    WARROOM_V2_PANEL_EVENT_BRIDGE_ADAPTER_VERSION,
    build_warroom_v2_market_snapshot_strip_packet,
    build_warroom_v2_panel_event_bridge_packet,
    market_snapshot_event_payload_from_strip_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q34C_WARROOM_V2_MARKET_SNAPSHOT_STRIP_EVENT_PAYLOAD_CARRIES_DATA_QUALITY_METADATA_DEFAULT_OFF_NO_SOCKET_2026-07-04.md"
BRIDGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/panel_event_bridge.py"
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _strip(*, bid: float = 100.0, ask: float = 99.0, spread: float = -1.0) -> dict[str, object]:
    row = {"symbol_raw": "FX_BTC_JPY", "best_bid": bid, "best_ask": ask, "spread": spread, "mid_price": (bid + ask) / 2.0, "collector_ts": "2099-01-01T00:00:00Z"}
    source = build_warroom_v2_market_snapshot_dhot_read_model(row=row, diagnostics={"preferred_row_freshness": "LIVE"})
    return build_warroom_v2_market_snapshot_strip_packet(source_packet=source)


def test_q34c_market_payload_carries_data_quality_metadata_without_new_fields() -> None:
    payload = market_snapshot_event_payload_from_strip_packet(_strip())
    assert WARROOM_V2_PANEL_EVENT_BRIDGE_ADAPTER_VERSION == "prediction_warroom.v2.panel_event_bridge.ps_q34c.v1"
    assert payload["payload_schema"] == "warroom.market_snapshot_strip.event_payload.v1"
    assert payload["data_quality_metadata_carried"] is True
    assert payload["market_data_quality_state"] == "CROSSED_BOOK"
    assert payload["data_quality_diagnostics"]["bid_ask_crossed"] is True
    assert payload["data_quality_badge_policy"]["severity"] == "danger"
    assert payload["data_quality_badge_policy"]["badge_visible_default"] is False
    assert payload["data_quality_badge_policy"]["badge_render_allowed_default"] is False
    assert payload["data_quality_badge_policy"]["streamlit_badge_invoked"] is False
    assert "market_data_quality_state" not in payload["fields"]
    assert "data_quality_badge_policy" not in payload["fields"]
    assert payload["would_send_to_broker"] is False


def test_q34c_event_bridge_embeds_metadata_in_market_read_model_event_only() -> None:
    packet = build_warroom_v2_panel_event_bridge_packet(market_snapshot_packet=_strip(), generated_at="2026-07-04T00:00:00Z")
    event_payload = packet["market_snapshot_event"]["event"]["read_model"]["payload"]
    assert packet["panel_event_bridge_adapter_version"] == "prediction_warroom.v2.panel_event_bridge.ps_q34c.v1"
    assert event_payload["data_quality_metadata_carried"] is True
    assert event_payload["data_quality_badge_policy"]["badge_token"] == "crossed_book"
    assert event_payload["data_quality_badge_policy"]["visual_policy_only"] is True
    assert packet["market_snapshot_event"]["envelope"]["ui_patch_unit"] == "widget_dom_region"
    assert packet["transport_implemented_now"] is False
    assert packet["bridge_starts_transport"] is False
    assert packet["websocket_enabled"] is False
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["would_send_to_broker"] is False


def test_q34c_default_payload_has_empty_safe_metadata_shape() -> None:
    payload = market_snapshot_event_payload_from_strip_packet({})
    assert payload["data_quality_metadata_carried"] is False
    assert payload["market_data_quality_state"] == "NO_DATA"
    assert payload["data_quality_diagnostics"] == {}
    assert payload["data_quality_badge_policy"] == {}
    assert payload["read_only"] is True
    assert payload["display_only"] is True


def test_q34c_doc_and_renderer_files_preserve_no_visible_ui_boundary() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "event_payload_carries_data_quality_metadata=true" in doc
    assert "not_rendering_badge_now=true" in doc
    assert "not_modifying_warroom_page=true" in doc
    assert "not_opening_socket=true" in doc
    page = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "market_snapshot_event_payload_data_quality_metadata_q34c" not in page
    assert "data_quality_badge_policy" not in page
    bridge_text = BRIDGE.read_text(encoding="utf-8-sig")
    assert "st.badge" not in bridge_text
    assert "st.error" not in bridge_text
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 120, f"renderer file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
