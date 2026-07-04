# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp8_first_real_push_widget_set.py
# desc: WP8 first real push widget set. Builds read-only market/receiver/summary widget push messages and render packets without page mount, socket, send, broker, order, or prediction.

from __future__ import annotations

from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp7_widget_health_freshness import run_widget_health_freshness_pipeline

WP8_VERSION = "warroom.manual_trade_support.push_widgets.wp8.first_real_push_widget_set.v1"


def _safe_value(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(k): v for k, v in value.items() if k not in {"raw", "raw_payload", "endpoint", "token", "callable"}}


def build_market_depth_push(symbol: str, *, bid: float, ask: float, received_at_ms: int, sequence: int) -> dict[str, Any]:
    return {"topic_key": "market.depth", "value": _safe_value({"symbol": symbol, "best_bid": bid, "best_ask": ask, "spread": round(ask - bid, 2)}), "received_at_ms": received_at_ms, "sequence": sequence}


def build_recent_trades_push(symbol: str, *, last_price: float, last_size: float, side: str, received_at_ms: int, sequence: int) -> dict[str, Any]:
    return {"topic_key": "market.trades", "value": _safe_value({"symbol": symbol, "last_price": last_price, "last_size": last_size, "side": side}), "received_at_ms": received_at_ms, "sequence": sequence}


def build_spread_liquidity_pushes(symbol: str, *, spread_bps: float, depth_score: float, received_at_ms: int, sequence: int) -> list[dict[str, Any]]:
    return [
        {"topic_key": "market.spread", "value": _safe_value({"symbol": symbol, "spread_bps": spread_bps}), "received_at_ms": received_at_ms, "sequence": sequence},
        {"topic_key": "market.liquidity", "value": _safe_value({"symbol": symbol, "depth_score": depth_score, "liquidity_state": "normal"}), "received_at_ms": received_at_ms + 1, "sequence": sequence + 1},
    ]


def build_receiver_lifecycle_push(*, status: str, lag_ms: int, received_at_ms: int, sequence: int) -> dict[str, Any]:
    return {"topic_key": "receiver.lifecycle", "value": _safe_value({"status": status, "lag_ms": lag_ms, "receive_only": True}), "received_at_ms": received_at_ms, "sequence": sequence}


def build_summary_alert_pushes(*, summary: str, alert_count: int, received_at_ms: int, sequence: int) -> list[dict[str, Any]]:
    return [
        {"topic_key": "warroom.summary", "value": _safe_value({"summary": summary, "manual_trade_support": True}), "received_at_ms": received_at_ms, "sequence": sequence},
        {"topic_key": "warroom.alerts", "value": _safe_value({"alert_count": alert_count, "highest_level": "info"}), "received_at_ms": received_at_ms + 1, "sequence": sequence + 1},
    ]


def build_first_real_push_widget_messages(symbol: str = "BTC_JPY", *, base_ms: int = 10_000) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = [
        build_market_depth_push(symbol, bid=100.0, ask=101.0, received_at_ms=base_ms, sequence=1),
        build_recent_trades_push(symbol, last_price=100.5, last_size=0.12, side="buy", received_at_ms=base_ms + 10, sequence=1),
    ]
    messages.extend(build_spread_liquidity_pushes(symbol, spread_bps=9.9, depth_score=0.82, received_at_ms=base_ms + 20, sequence=1))
    messages.append(build_receiver_lifecycle_push(status="receiving", lag_ms=42, received_at_ms=base_ms + 30, sequence=1))
    messages.extend(build_summary_alert_pushes(summary="Market widgets receiving", alert_count=0, received_at_ms=base_ms + 40, sequence=1))
    return messages


def build_wp8_first_real_push_widget_set_packet() -> dict[str, Any]:
    messages = build_first_real_push_widget_messages()
    pipeline = run_widget_health_freshness_pipeline(messages, now_ms=10_100)
    widget_ids = sorted(pipeline["render_packets"].keys())
    live_widget_ids = sorted([widget_id for widget_id, packet in pipeline["render_packets"].items() if packet["freshness_label"] == "live"])
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp8_first_real_push_widget_set_packet",
        "version": WP8_VERSION,
        "wp8_completed": True,
        "next_checkpoint": "WP9_WarRoom_page_mount_for_push_widgets",
        "first_real_push_widget_set_ready": True,
        "market_depth_push_widget_ready": True,
        "recent_trades_push_widget_ready": True,
        "spread_liquidity_push_widget_ready": True,
        "receiver_lifecycle_push_widget_ready": True,
        "summary_alerts_push_widget_ready": True,
        "all_initial_widgets_update_from_push_ready": True,
        "health_enriched_first_widget_set_ready": True,
        "read_only_render_packets_ready": True,
        "message_count": len(messages),
        "widget_count": len(widget_ids),
        "live_widget_count": len(live_widget_ids),
        "widget_ids": widget_ids,
        "live_widget_ids": live_widget_ids,
        "messages": messages,
        "render_packets": pipeline["render_packets"],
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_mount_added"] = False
    packet["websocket_opened"] = False
    packet["websocket_receive_loop_started"] = False
    packet["websocket_send_enabled"] = False
    return packet
