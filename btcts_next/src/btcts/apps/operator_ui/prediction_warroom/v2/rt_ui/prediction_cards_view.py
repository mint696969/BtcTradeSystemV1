# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
# desc: WarRoom v2 realtime prediction-card context renderer. Compact important-order cards without invoking prediction/classifier.

from __future__ import annotations

from typing import Any, Mapping

_IMPORTANCE = {"market_context_card": 10, "risk_context_card": 20, "manual_review_card": 30, "scenario_guidance_card": 15}


def _badge(state: str) -> str:
    if state in {"live", "ready", "normal"}:
        return f"🟢 {state}"
    if state in {"attention", "review", "not_ready"}:
        return f"🟡 {state}"
    return f"⚪ {state or 'waiting'}"


def _container(st_api: Any) -> Any:
    try:
        return st_api.container(border=True)
    except TypeError:
        return st_api.container()


def _sort_cards(cards: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(cards, key=lambda card: _IMPORTANCE.get(str(card.get("context_id") or ""), 99))


def render_rt_prediction_cards(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    cards = _sort_cards([card for card in packet.get("cards", []) if isinstance(card, Mapping)])
    st_api.caption("Prediction cards: important context first / read-only / no prediction invocation")
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
            column.caption(f"stale={card.get('stale_guard')} / read_only={bool(card.get('read_only', True))}")
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
