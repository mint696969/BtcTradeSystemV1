# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
# desc: WarRoom v2 realtime prediction-card context renderer. Reuses original WarRoom market-regime card shell first; no prediction/classifier/broker action.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (
    WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
    render_warroom_market_regime_card_shell,
)

ENTRY_GATE_VERSION = "warroom_v2_rt_entry_gate.2026_07_05.v1"
RT_MARKET_REGIME_CARD_BRIDGE_VERSION = "warroom_v2_rt_market_regime_card_bridge.2026_07_08.v1"
RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT = r"D:tc_ts_hot"
FUTURE_PREDICTION_CARD_ROWS = ("方向感", "反転候補", "ボラ警戒", "流動性 / 約定品質")


def _generated_at(packet: Mapping[str, Any]) -> str:
    for key in ("generated_at", "forecast_generated_at", "source_generated_at"):
        value = packet.get(key)
        if value:
            return str(value)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _render_prediction_boundary(packet: Mapping[str, Any], st_api: Any) -> None:
    generated_at = packet.get("generated_at") or packet.get("forecast_generated_at") or packet.get("source_generated_at")
    parts = [
        f"entry_gate={ENTRY_GATE_VERSION}",
        f"bridge={RT_MARKET_REGIME_CARD_BRIDGE_VERSION}",
        "prediction_cards_scope=market_regime_first",
        "original_warroom_market_regime_shell=true",
        "prediction_invoked=false",
        "classifier_invoked=false",
        "broker_action_allowed=false",
    ]
    if generated_at:
        parts.append(f"source_generated_at={generated_at}")
    st_api.caption(" / ".join(parts))


def _render_future_row_reservation(st_api: Any) -> None:
    st_api.caption(
        "次の予測カード行 追加枠: "
        + " / ".join(FUTURE_PREDICTION_CARD_ROWS)
        + "（未接続・今後追加）"
    )


def _render_context_packets(packet: Mapping[str, Any], st_api: Any) -> None:
    cards = [card for card in packet.get("cards", []) if isinstance(card, Mapping)]
    if not cards:
        return
    with st_api.expander("Prediction card context packets", expanded=False):
        st_api.dataframe([
            {
                "card": str(card.get("title") or ""),
                "market_state": str(card.get("market_state") or ""),
                "chart": str(card.get("chart_summary") or ""),
                "operator_note": str(card.get("operator_note") or ""),
                "stale_guard": str(card.get("stale_guard") or ""),
                "read_only": bool(card.get("read_only", True)),
                "prediction_invoked": bool(card.get("prediction_invoked", False)),
                "classifier_invoked": bool(card.get("classifier_invoked", False)),
            }
            for card in cards
        ], width="stretch")


def render_rt_prediction_cards(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    _render_prediction_boundary(packet, st_api)
    render_warroom_market_regime_card_shell(
        preview_enabled=True,
        hot_root=RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT,
        generated_at=_generated_at(packet),
    )
    _render_future_row_reservation(st_api)
    _render_context_packets(packet, st_api)
    return {
        "ok": True,
        "entry_gate_version": ENTRY_GATE_VERSION,
        "rt_market_regime_card_bridge_version": RT_MARKET_REGIME_CARD_BRIDGE_VERSION,
        "renderer_version": WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
        "market_regime_card_shell_rendered": True,
        "market_regime_first": True,
        "future_prediction_rows_reserved": True,
        "future_prediction_card_rows": list(FUTURE_PREDICTION_CARD_ROWS),
        "rendered_prediction_card_count": 1,
        "read_only": True,
        "prediction_invoked": False,
        "classifier_invoked": False,
        "broker_action_allowed": False,
        "prediction_card_enrichment_deferred": True,
    }
