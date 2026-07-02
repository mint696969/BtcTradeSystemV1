# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py
# desc: WarRoom v2 prediction-card horizon matrix renderer. Placeholder-only; no live data ownership.

from __future__ import annotations

from typing import Any

import streamlit as st

from .card_detail_balloon import render_warroom_v2_card_detail_balloon

WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION = "prediction_warroom.v2.prediction_cards_renderer.ps_q29f.v1"


def _horizon_card_model(parent: dict[str, Any], horizon_card: dict[str, Any]) -> dict[str, Any]:
    payload = dict(parent.get("payload", {}))
    payload.update(horizon_card)
    return {
        "widget_id": parent.get("widget_id", ""),
        "topic": parent.get("topic", ""),
        "title": parent.get("title", ""),
        "payload": payload,
    }


def _render_horizon_card(parent: dict[str, Any], horizon_card: dict[str, Any]) -> None:
    model = _horizon_card_model(parent, horizon_card)
    payload = model["payload"]
    with st.container(border=True):
        cols = st.columns([3, 1])
        cols[0].caption(str(payload.get("horizon", "")))
        cols[1].caption(str(payload.get("freshness_badge", "NO_DATA")))
        st.subheader(str(payload.get("primary_label", "未接続")))
        st.metric("", payload.get("confidence_or_score", "--"))
        st.caption(str(payload.get("short_tag", "PREVIEW_ONLY")))
        render_warroom_v2_card_detail_balloon(model)


def render_warroom_v2_prediction_cards(models: list[dict[str, Any]]) -> None:
    st.subheader("Prediction cards")
    for model in models:
        payload = model.get("payload", {})
        st.markdown(f"### {model.get('title') or model.get('widget_id')}")
        horizon_cards = list(payload.get("horizon_cards") or [])
        cols = st.columns(max(1, len(horizon_cards)))
        for col, horizon_card in zip(cols, horizon_cards):
            with col:
                _render_horizon_card(model, dict(horizon_card))
