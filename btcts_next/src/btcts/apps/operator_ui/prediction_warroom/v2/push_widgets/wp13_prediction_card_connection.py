# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp13_prediction_card_connection.py
# desc: WP13 prediction card connection and updates. Connects prediction card display to push-widget/chart context without invoking prediction, classifier, socket send, broker, order, or ledger.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp12_bottom_chart_layout import build_wp12_bottom_chart_layout_packet

WP13_VERSION = "warroom.manual_trade_support.push_widgets.wp13.prediction_card_connection.v1"
WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY = "warroom_push_widget_wp13_prediction_card_packet"


@dataclass(frozen=True)
class PredictionCardContext:
    context_id: str
    title: str
    market_state: str
    chart_summary: str
    widget_summary: str
    operator_note: str
    stale_guard: str
    read_only: bool = True
    prediction_invoked: bool = False
    classifier_invoked: bool = False
    broker_action_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _state_from_overlays(packet: Mapping[str, Any], overlay_id: str) -> str:
    for overlay in packet.get("overlays", []):
        if isinstance(overlay, Mapping) and str(overlay.get("overlay_id")) == overlay_id:
            return str(overlay.get("state") or "unknown")
    return "unknown"


def _latest_price_label(packet: Mapping[str, Any]) -> str:
    prices = [row.get("price") for row in packet.get("chart_rows", []) if isinstance(row, Mapping) and isinstance(row.get("price"), (int, float))]
    if not prices:
        return "price unavailable"
    return f"latest_price={float(prices[-1]):.2f}"


def build_prediction_card_contexts(bottom_chart_packet: Mapping[str, Any]) -> tuple[PredictionCardContext, ...]:
    market_state = _state_from_overlays(bottom_chart_packet, "market_status")
    risk_state = _state_from_overlays(bottom_chart_packet, "risk_cues")
    decision_state = _state_from_overlays(bottom_chart_packet, "manual_decision_context")
    chart_summary = f"rows={bottom_chart_packet.get('chart_row_count')} overlays={bottom_chart_packet.get('overlay_count')} {_latest_price_label(bottom_chart_packet)}"
    stale_guard = "clear" if int(bottom_chart_packet.get("stale_row_count", 0)) == 0 else "review_stale_rows"
    return (
        PredictionCardContext(
            "market_context_card",
            "Market context for prediction card",
            market_state,
            chart_summary,
            "push widgets live before prediction review",
            "read prediction as review context only",
            stale_guard,
        ),
        PredictionCardContext(
            "risk_context_card",
            "Risk cues for prediction card",
            risk_state,
            chart_summary,
            "liquidity and alert cues connected",
            "manual operator decision remains separate",
            stale_guard,
        ),
        PredictionCardContext(
            "manual_review_card",
            "Manual review context",
            decision_state,
            chart_summary,
            "summary and alerts available",
            "no broker/order/auto-trade action is connected",
            stale_guard,
        ),
    )


def build_wp13_prediction_card_connection_packet() -> dict[str, Any]:
    bottom_chart = build_wp12_bottom_chart_layout_packet()
    cards = build_prediction_card_contexts(bottom_chart)
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp13_prediction_card_connection_packet",
        "version": WP13_VERSION,
        "wp13_completed": True,
        "roadmap_completed": True,
        "next_checkpoint": "WP13_DONE_CC_and_operator_acceptance",
        "prediction_card_connection_ready": True,
        "prediction_card_update_ready": True,
        "prediction_card_market_context_ready": True,
        "prediction_card_chart_context_ready": True,
        "prediction_card_manual_review_ready": True,
        "prediction_card_read_only_ready": True,
        "prediction_card_no_action_boundary_ready": True,
        "prediction_invocation_guard_ready": True,
        "classifier_invocation_guard_ready": True,
        "prediction_card_count": len(cards),
        "bottom_chart_row_count": int(bottom_chart["chart_row_count"]),
        "bottom_chart_overlay_count": int(bottom_chart["overlay_count"]),
        "cards": [card.to_dict() for card in cards],
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_modified"] = True
    packet["warroom_page_mount_added"] = True
    packet["websocket_opened"] = False
    packet["websocket_receive_loop_started"] = False
    packet["websocket_send_enabled"] = False
    packet["broker_send_enabled"] = False
    packet["order_intent_submitted"] = False
    packet["prediction_invoked"] = False
    packet["classifier_invoked"] = False
    packet["auto_trading_enabled"] = False
    packet["roadmap_wp1_wp13_complete"] = True
    return packet


def render_wp13_prediction_card_connection(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("WarRoom prediction cards: connected to push-widget market context / read-only / no action")
    rows: list[dict[str, Any]] = []
    for card in packet.get("cards", []):
        if not isinstance(card, Mapping):
            continue
        rows.append({
            "card": str(card.get("title", "")),
            "market_state": str(card.get("market_state", "")),
            "chart": str(card.get("chart_summary", "")),
            "operator_note": str(card.get("operator_note", "")),
            "stale_guard": str(card.get("stale_guard", "")),
            "read_only": bool(card.get("read_only", True)),
        })
    if rows and hasattr(st_api, "dataframe"):
        st_api.dataframe(rows, width="stretch")
    elif rows and hasattr(st_api, "json"):
        st_api.json(rows)
    return {"ok": True, "rendered_prediction_card_count": len(rows), "read_only": True, "controls_added": False, "prediction_invoked": False, "classifier_invoked": False}
