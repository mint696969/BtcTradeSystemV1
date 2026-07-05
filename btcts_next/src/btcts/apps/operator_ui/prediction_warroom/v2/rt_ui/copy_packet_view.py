# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/copy_packet_view.py
# desc: GPT copy-packet builder for WarRoom chart/scenario review. Keeps copy text compact and safe.

from __future__ import annotations

import json
from typing import Any, Mapping


def build_gpt_copy_packet(*, market_strip: Mapping[str, Any], guidance: Mapping[str, Any], chart_packet: Mapping[str, Any], cards_packet: Mapping[str, Any]) -> str:
    chart_rows = [row for row in chart_packet.get("chart_rows", []) if isinstance(row, Mapping)]
    live_rows = [row for row in chart_rows if row.get("freshness_label") == "live"]
    payload = {
        "schema_version": "warroom_gpt_review_packet.v1",
        "purpose": "manual trade observation review; read-only; no order action",
        "market": {
            "symbol": market_strip.get("symbol"),
            "best_bid": market_strip.get("best_bid"),
            "best_ask": market_strip.get("best_ask"),
            "spread": market_strip.get("spread"),
            "spread_bps": market_strip.get("spread_bps"),
            "source": market_strip.get("source"),
            "last_event_ts": market_strip.get("last_event_ts"),
        },
        "scenario_guidance": {
            "scenario": guidance.get("scenario"),
            "confidence": guidance.get("confidence"),
            "rationale": guidance.get("rationale"),
            "evidence": guidance.get("evidence", []),
            "observation_only": True,
        },
        "chart": {
            "row_count": chart_packet.get("chart_row_count"),
            "live_row_count": len(live_rows),
            "stale_row_count": chart_packet.get("stale_row_count"),
            "rows": live_rows[-12:],
        },
        "prediction_cards": [card for card in cards_packet.get("cards", []) if isinstance(card, Mapping)],
        "safety": {
            "websocket_send_enabled": False,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_gpt_copy_packet(text: str, st_api: Any) -> dict[str, Any]:
    with st_api.expander("GPT review copy packet", expanded=False):
        st_api.text_area("Copy for GPT analysis", value=text, height=260)
    return {"ok": True, "copy_packet_rendered": True, "copy_packet_chars": len(text), "read_only": True}
