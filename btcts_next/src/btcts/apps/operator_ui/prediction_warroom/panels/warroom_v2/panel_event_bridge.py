# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/panel_event_bridge.py
# desc: WarRoom v2 panel-packet to read-model event bridge adapter. No Streamlit, D-hot reads, sockets, or execution behavior.

from __future__ import annotations

from typing import Any

from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_chart_review_update_event, build_warroom_v2_market_snapshot_update_event, stable_payload_fingerprint

WARROOM_V2_PANEL_EVENT_BRIDGE_ADAPTER_VERSION = "prediction_warroom.v2.panel_event_bridge.ps_q30e.v1"


def market_snapshot_event_payload_from_strip_packet(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(packet or {})
    fields = {str(row.get("key")): row.get("value") for row in list(data.get("fields") or []) if isinstance(row, dict)}
    return {"payload_schema": "warroom.market_snapshot_strip.event_payload.v1", "market": data.get("market"), "exchange": data.get("exchange"), "data_state": data.get("data_state"), "invalidation_watch": data.get("invalidation_watch"), "fields": fields, "raw_values": dict(data.get("raw_values") or {}), "data_connected": bool(data.get("data_connected")), "placeholder_only": bool(data.get("placeholder_only")), "read_only": True, "display_only": True, "would_send_to_broker": False}


def chart_review_event_payload_from_panel_packet(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(packet or {})
    payload = dict(data.get("payload") or {})
    chart_series = dict(data.get("chart_series") or {})
    return {"payload_schema": "warroom.chart_review_panel.event_payload.v1", "selected_timeframe": data.get("selected_timeframe"), "chart_window": dict(data.get("chart_window") or {}), "market_snapshot": dict(payload.get("market_snapshot") or {}), "range_summary": dict(payload.get("range_summary") or {}), "chart_series_connected": bool(data.get("chart_series_connected")), "chart_row_count": len(list(chart_series.get("chart_rows") or [])), "data_connected": bool(data.get("data_connected")), "read_only": True, "display_only": True, "would_send_to_broker": False}


def build_warroom_v2_panel_event_bridge_packet(*, market_snapshot_packet: dict[str, Any] | None = None, chart_review_packet: dict[str, Any] | None = None, generated_at: str = "", previous_fingerprints: dict[str, str] | None = None, sequence_base: int = 0) -> dict[str, Any]:
    previous = dict(previous_fingerprints or {})
    market_payload = market_snapshot_event_payload_from_strip_packet(market_snapshot_packet)
    chart_payload = chart_review_event_payload_from_panel_packet(chart_review_packet)
    market_event = build_warroom_v2_market_snapshot_update_event(snapshot_payload=market_payload, generated_at=generated_at, previous_fingerprint=str(previous.get("market_snapshot_strip", "")), sequence=int(sequence_base))
    chart_event = build_warroom_v2_chart_review_update_event(chart_payload=chart_payload, generated_at=generated_at, previous_fingerprint=str(previous.get("chart_review_panel", "")), sequence=int(sequence_base) + 1)
    return {"ok": True, "panel_event_bridge_adapter_version": WARROOM_V2_PANEL_EVENT_BRIDGE_ADAPTER_VERSION, "input_kind": "existing_panel_packets", "output_kind": "read_model_event_bridge_packet", "generated_at": str(generated_at), "market_snapshot_event": market_event, "chart_review_event": chart_event, "fingerprints": {"market_snapshot_strip": market_event["current_fingerprint"], "chart_review_panel": chart_event["current_fingerprint"]}, "stable_payload_fingerprint_available": callable(stable_payload_fingerprint), "transport_implemented_now": False, "bridge_starts_transport": False, "bridge_reads_dhot": False, "bridge_invokes_classifier": False, "websocket_enabled": False, "sse_enabled": False, "runtime_connected": False, "push_connected": False, "read_only": True, "display_only": True, "would_send_to_broker": False}
