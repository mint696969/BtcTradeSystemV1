# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/realtime_read_surface.py
# desc: WarRoom v2 realtime Japanese read surface contract. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any

from .topic_policy import list_warroom_v2_topic_policies

WARROOM_V2_REALTIME_READ_SURFACE_VERSION = "prediction_warroom.v2.transport.realtime_read_surface.ps_q31x.v1"

_JA_LABEL_BY_TOPIC: dict[str, str] = {
    "warroom.current_state": "地合い・現在状態",
    "warroom.alerts": "警告",
    "warroom.safety": "安全境界",
    "warroom.market.snapshot": "現在価格・板・鮮度",
    "warroom.chart.review": "チャート確認",
    "warroom.prediction.market_regime": "地合い予測",
    "warroom.prediction.trend_bias": "方向感",
    "warroom.prediction.reversal_zone": "反転候補",
    "warroom.prediction.volatility_risk": "ボラティリティ警戒",
    "warroom.prediction.liquidity_execution_quality": "流動性・約定品質",
    "warroom.prediction.breakout_false_break": "ブレイク・だまし警戒",
    "warroom.prediction.cross_venue_confirmation": "複数市場確認",
    "warroom.prediction.human_technical_structure": "人間のテクニカル確認",
    "warroom.prediction.scenario_ja": "シナリオ日本語要約",
}

_READING_ORDER: tuple[dict[str, Any], ...] = (
    {"order": 1, "surface": "top_information", "label_ja": "地合い・安全境界", "topics": ["warroom.current_state", "warroom.alerts", "warroom.safety"]},
    {"order": 2, "surface": "top_information", "label_ja": "現在価格・板・鮮度", "topics": ["warroom.market.snapshot"]},
    {"order": 3, "surface": "prediction_display", "label_ja": "予測カード", "topics": [topic for topic in _JA_LABEL_BY_TOPIC if topic.startswith("warroom.prediction.") and topic != "warroom.prediction.scenario_ja"]},
    {"order": 4, "surface": "prediction_display", "label_ja": "シナリオ日本語要約", "topics": ["warroom.prediction.scenario_ja"]},
    {"order": 5, "surface": "bottom_chart", "label_ja": "チャート確認", "topics": ["warroom.chart.review"]},
    {"order": 6, "surface": "operator_support", "label_ja": "操作判断メモ", "topics": []},
)


def _target_rows() -> list[dict[str, Any]]:
    policies = {str(row.get("topic")): dict(row) for row in list_warroom_v2_topic_policies()}
    rows: list[dict[str, Any]] = []
    for topic, label in _JA_LABEL_BY_TOPIC.items():
        policy = policies.get(topic, {})
        rows.append(
            {
                "topic": topic,
                "label_ja": label,
                "surface": str(policy.get("surface") or "operator_support"),
                "patch_unit": str(policy.get("patch_unit") or "widget_dom_region"),
                "cadence_hint_ms": int(policy.get("cadence_hint_ms") or 0),
                "websocket_display_push_target": True,
                "japanese_readable_target": True,
                "manual_trading_information_board_target": True,
                "prediction_generation_invoked": False,
                "prediction_inference_invoked": False,
                "order_intent_submitted": False,
                "would_send_to_broker": False,
            }
        )
    return rows


def build_warroom_v2_realtime_japanese_read_surface_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "surface_version": WARROOM_V2_REALTIME_READ_SURFACE_VERSION,
        "contract_kind": "warroom_v2_realtime_japanese_read_surface_contract",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "websocket_display_push_required": True,
        "bidirectional_websocket_premise": True,
        "read_model_push_plane": "server_to_warroom_ui",
        "command_intent_plane": "warroom_ui_or_autotrade_to_order_intent_gateway",
        "japanese_readable_now_target": True,
        "manual_trading_information_board": True,
        "prediction_enrichment_deferred": True,
        "trading_logic_deferred": True,
        "order_logic_deferred": True,
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_reload_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_realtime_japanese_read_surface_packet() -> dict[str, Any]:
    rows = _target_rows()
    return {
        **build_warroom_v2_realtime_japanese_read_surface_contract(),
        "packet_kind": "warroom_v2_realtime_japanese_read_surface_packet",
        "reading_order": [dict(item) for item in _READING_ORDER],
        "reading_order_labels_ja": [str(item["label_ja"]) for item in _READING_ORDER],
        "target_count": len(rows),
        "targets": rows,
        "target_topics": [row["topic"] for row in rows],
        "all_targets_have_ja_label": all(bool(row["label_ja"]) for row in rows),
        "all_targets_are_ws_display_push_targets": all(bool(row["websocket_display_push_target"]) for row in rows),
        "prediction_card_topics": [row["topic"] for row in rows if str(row["topic"]).startswith("warroom.prediction.") and row["topic"] != "warroom.prediction.scenario_ja"],
        "scenario_ja_topic": "warroom.prediction.scenario_ja",
        "market_snapshot_topic": "warroom.market.snapshot",
        "chart_review_topic": "warroom.chart.review",
    }
