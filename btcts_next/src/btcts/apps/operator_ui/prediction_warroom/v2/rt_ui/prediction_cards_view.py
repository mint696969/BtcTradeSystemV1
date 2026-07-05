# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
# desc: WarRoom v2 realtime prediction-card context renderer. Restores card-style layout without invoking prediction/classifier.

from __future__ import annotations

from typing import Any, Mapping


def _badge(state: str) -> str:
    if state == "live":
        return "🟢 live"
    if state in {"review", "not_ready"}:
        return "🟡 review"
    return "⚪ waiting"


def _container(st_api: Any) -> Any:
    try:
        return st_api.container(border=True)
    except TypeError:
        return st_api.container()


def render_rt_prediction_cards(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    cards = [card for card in packet.get("cards", []) if isinstance(card, Mapping)]
    st_api.caption("WarRoom prediction cards: realtime market/chart context / read-only / no prediction invocation")
    if not cards:
        st_api.info("Prediction card context is not available yet.")
        return {"ok": True, "rendered_prediction_card_count": 0, "read_only": True, "prediction_invoked": False, "classifier_invoked": False}
    columns = st_api.columns(len(cards))
    for column, card in zip(columns, cards, strict=False):
        with _container(column):
            state = str(card.get("market_state") or "unknown")
            column.markdown(f"**{card.get('title', '')}**")
            column.metric("state", _badge(state))
            column.caption(str(card.get("chart_summary") or ""))
            column.write(str(card.get("operator_note") or ""))
            column.caption(f"stale_guard={card.get('stale_guard')} / read_only={bool(card.get('read_only', True))}")
    with st_api.expander("Prediction card context packets", expanded=False):
        st_api.dataframe([
            {
                "card": str(card.get("title") or ""),
                "market_state": str(card.get("market_state") or ""),
                "chart": str(card.get("chart_summary") or ""),
                "operator_note": str(card.get("operator_note") or ""),
                "stale_guard": str(card.get("stale_guard") or ""),
                "read_only": bool(card.get("read_only", True)),
            }
            for card in cards
        ], width="stretch")
    return {"ok": True, "rendered_prediction_card_count": len(cards), "card_style_rendered": True, "read_only": True, "prediction_invoked": False, "classifier_invoked": False}
