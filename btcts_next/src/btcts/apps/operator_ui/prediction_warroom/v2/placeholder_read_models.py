# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/placeholder_read_models.py
# desc: WarRoom v2 placeholder widget read models for shell preview. No live data, Streamlit, or transport behavior.

from __future__ import annotations

from typing import Any

from .card_axis_policy import WARROOM_V2_HORIZON_LABELS
from .contracts import build_empty_widget_read_model

WARROOM_V2_PLACEHOLDER_READ_MODELS_VERSION = "prediction_warroom.v2.placeholder_read_models.ps_q29f.v1"

_WIDGET_TITLES: dict[str, str] = {
    "current_state_mini_bar": "現在状態",
    "safety_mini_bar": "安全境界",
    "alert_summary": "アラート",
    "prediction_card_market_regime": "地合い",
    "prediction_card_trend_bias": "方向感",
    "prediction_card_reversal_zone": "反転候補",
    "prediction_card_volatility_risk": "ボラ警戒",
    "prediction_card_liquidity": "流動性 / 約定品質",
    "prediction_card_breakout_false_break": "ブレイク / だまし",
    "prediction_card_cross_venue": "市場間確認",
    "prediction_card_human_technical": "人間テクニカル",
    "prediction_scenario_ja": "日本語シナリオ",
}


def _placeholder_detail_payload() -> dict[str, Any]:
    return {
        "detail_lines": [
            "このカードは placeholder です。実データ評価はまだ接続していません。",
            "将来は read model builder が理由をここへ渡します。",
        ],
        "source_lines": [
            "source=placeholder_read_model",
            "transport=not_connected",
        ],
        "warning_lines": [
            "売買判断には使わないでください。",
            "D-hot / classifier / push は未接続です。",
        ],
        "invalidation_lines": [
            "runtime_connected=false",
            "freshness_badge=NO_DATA",
        ],
    }


def _placeholder_horizon_cards(widget_id: str, topic: str) -> list[dict[str, Any]]:
    detail = _placeholder_detail_payload()
    cards: list[dict[str, Any]] = []
    for order, horizon in enumerate(WARROOM_V2_HORIZON_LABELS):
        cards.append({
            "horizon": horizon,
            "horizon_order": order,
            "primary_label": "未接続",
            "confidence_or_score": "--",
            "short_tag": "PREVIEW_ONLY",
            "freshness_badge": "NO_DATA",
            "background_tone": "unknown",
            "evidence_quality": "MISSING",
            "card_shape": "horizontal_rectangle",
            "card_body_lines": ["未接続", "--", "PREVIEW_ONLY"],
            "placeholder_only": True,
            "runtime_connected": False,
            "push_connected": False,
            "widget_id": widget_id,
            "topic": topic,
            **detail,
        })
    return cards


def build_warroom_v2_placeholder_read_models(*, generated_at: str = "") -> list[dict[str, Any]]:
    from .layout_policy import build_warroom_v2_layout_policy

    layout = build_warroom_v2_layout_policy()
    models: list[dict[str, Any]] = []
    for row in layout["widgets"]:
        widget_id = str(row["widget_id"])
        topic = str(row["topic"])
        zone = str(row["zone"])
        payload: dict[str, Any] = {
            "zone": zone,
            "order": row["order"],
            "default_visible": bool(row["default_visible"]),
            "placeholder_only": True,
            "runtime_connected": False,
            "push_connected": False,
        }
        if zone == "prediction_cards":
            horizon_cards = _placeholder_horizon_cards(widget_id, topic)
            payload.update({
                "row_axis": "prediction_item",
                "column_axis": "horizon",
                "horizon_labels": list(WARROOM_V2_HORIZON_LABELS),
                "horizon_cards": horizon_cards,
                "horizon_card_count": len(horizon_cards),
                "card_row_layout": "horizontal_time_axis_cards",
                "cards_do_not_shrink": True,
                "horizontal_scroll_required": True,
                "card_shape": "horizontal_rectangle",
                "freshness_badge": "NO_DATA",
                "detail_disclosure_mode": "card_overlay",
                **_placeholder_detail_payload(),
            })
        if zone == "scenario":
            payload.update({
                "scenario_lines": [
                    "ここに全予測カードを統合した日本語シナリオを表示します。",
                    "まだ実データ・push・D-hot 読み込みには接続していません。",
                ],
                "scenario_area_below_cards": True,
            })
        models.append(
            build_empty_widget_read_model(
                widget_id=widget_id,
                topic=topic,
                generated_at=generated_at,
                title=_WIDGET_TITLES.get(widget_id, widget_id),
                payload=payload,
                freshness="not_connected",
                detail_available=zone == "prediction_cards",
                scenario_area=zone == "scenario",
                debug_payload_available=False,
            )
        )
    return models


def build_warroom_v2_placeholder_read_models_packet(*, generated_at: str = "") -> dict[str, Any]:
    models = build_warroom_v2_placeholder_read_models(generated_at=generated_at)
    return {
        "ok": True,
        "placeholder_read_models_version": WARROOM_V2_PLACEHOLDER_READ_MODELS_VERSION,
        "generated_at": generated_at,
        "placeholder_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "horizon_labels": list(WARROOM_V2_HORIZON_LABELS),
        "read_model_count": len(models),
        "read_models": models,
        "widget_ids": [model["widget_id"] for model in models],
        "topics": [model["topic"] for model in models],
    }
