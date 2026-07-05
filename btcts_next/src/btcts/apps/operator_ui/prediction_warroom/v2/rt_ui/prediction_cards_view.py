# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
# desc: WarRoom v2 realtime prediction-card context renderer. Compact important-order cards without invoking prediction/classifier.

from __future__ import annotations

from typing import Any, Mapping

ENTRY_GATE_VERSION = "warroom_v2_rt_entry_gate.2026_07_05.v1"
_IMPORTANCE = {"market_context_card": 10, "risk_context_card": 20, "manual_review_card": 30, "scenario_guidance_card": 15}


def _badge(state: str) -> str:
    if state in {"live", "ready", "normal"}:
        return f"🟢 {state}"
    if state in {"attention", "review", "not_ready", "stale"}:
        return f"🟡 {state}"
    return f"⚪ {state or 'waiting'}"


def _container(st_api: Any) -> Any:
    try:
        return st_api.container(border=True)
    except TypeError:
        return st_api.container()


def _sort_cards(cards: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(cards, key=lambda card: _IMPORTANCE.get(str(card.get("context_id") or ""), 99))


def _card_state(card: Mapping[str, Any]) -> str:
    stale_guard = str(card.get("stale_guard") or "").lower()
    state = str(card.get("market_state") or "unknown")
    if stale_guard in {"stale", "expired", "old"}:
        return "stale"
    return state


def _render_prediction_boundary(packet: Mapping[str, Any], st_api: Any) -> None:
    generated_at = packet.get("generated_at") or packet.get("forecast_generated_at") or packet.get("source_generated_at")
    parts = [
        f"entry_gate={ENTRY_GATE_VERSION}",
        "prediction_cards_scope=context_only",
        "prediction_invoked=false",
        "classifier_invoked=false",
        "broker_action_allowed=false",
        "next_thread_target=prediction_card_enrichment",
    ]
    if generated_at:
        parts.append(f"source_generated_at={generated_at}")
    st_api.caption(" / ".join(parts))


def render_rt_prediction_cards(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    cards = _sort_cards([card for card in packet.get("cards", []) if isinstance(card, Mapping)])
    st_api.caption("Prediction cards: context-only / read-only / no prediction invocation / enrichment deferred")
    _render_prediction_boundary(packet, st_api)
    if not cards:
        st_api.info("Prediction card context is not available yet. This does not block non-prediction WarRoom widget polish.")
        return {"ok": True, "rendered_prediction_card_count": 0, "read_only": True, "prediction_invoked": False, "classifier_invoked": False}
    columns = st_api.columns(len(cards))
    for column, card in zip(columns, cards, strict=False):
        with _container(column):
            state = _card_state(card)
            column.markdown(f"**{card.get('title', '')}**")
            column.metric("state", _badge(state))
            column.caption(str(card.get("chart_summary") or ""))
            column.write(str(card.get("operator_note") or ""))
            column.caption(f"stale={card.get('stale_guard')} / read_only={bool(card.get('read_only', True))}")
    with st_api.expander("Prediction card context packets", expanded=False):
        st_api.dataframe([
            {
                "card": str(card.get("title") or ""),
                "market_state": _card_state(card),
                "chart": str(card.get("chart_summary") or ""),
                "operator_note": str(card.get("operator_note") or ""),
                "stale_guard": str(card.get("stale_guard") or ""),
                "read_only": bool(card.get("read_only", True)),
                "prediction_invoked": bool(card.get("prediction_invoked", False)),
                "classifier_invoked": bool(card.get("classifier_invoked", False)),
            }
            for card in cards
        ], width="stretch")
    return {
        "ok": True,
        "entry_gate_version": ENTRY_GATE_VERSION,
        "rendered_prediction_card_count": len(cards),
        "card_style_rendered": True,
        "read_only": True,
        "prediction_invoked": False,
        "classifier_invoked": False,
        "prediction_card_enrichment_deferred": True,
    }
