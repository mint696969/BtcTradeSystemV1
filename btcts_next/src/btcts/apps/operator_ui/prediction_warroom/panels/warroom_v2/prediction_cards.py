# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py
# desc: WarRoom v2 prediction-card grid renderer. Placeholder-only; no live data ownership.

from __future__ import annotations

from typing import Any

import streamlit as st

from .card_detail_balloon import render_warroom_v2_card_detail_balloon

WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION = "prediction_warroom.v2.prediction_cards_renderer.ps_q29e.v1"


def _chunk(models: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [models[index : index + size] for index in range(0, len(models), size)]


def render_warroom_v2_prediction_cards(models: list[dict[str, Any]]) -> None:
    st.subheader("Prediction cards")
    for row in _chunk(models, 4):
        cols = st.columns(len(row))
        for col, model in zip(cols, row):
            payload = model.get("payload", {})
            with col:
                with st.container(border=True):
                    st.subheader(str(model.get("title") or model.get("widget_id")))
                    st.metric(payload.get("state_label", "未接続"), payload.get("confidence_label", "--"))
                    st.caption(f"{payload.get('freshness_badge', 'NO_DATA')} / {payload.get('short_tag', 'PREVIEW_ONLY')}")
                    render_warroom_v2_card_detail_balloon(model)
