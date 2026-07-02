# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/top_bar.py
# desc: WarRoom v2 top-zone renderer. Display-only placeholder widgets.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_TOP_BAR_RENDERER_VERSION = "prediction_warroom.v2.top_bar_renderer.ps_q29d.v1"


def render_warroom_v2_top_bar(models: list[dict[str, Any]]) -> None:
    cols = st.columns(max(1, len(models)))
    for col, model in zip(cols, models):
        payload = model.get("payload", {})
        with col:
            st.metric(str(model.get("title") or model.get("widget_id")), payload.get("state_label", "未接続"))
            st.caption(str(model.get("topic", "")))
