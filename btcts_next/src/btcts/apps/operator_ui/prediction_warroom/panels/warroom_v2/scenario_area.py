# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/scenario_area.py
# desc: WarRoom v2 Japanese scenario-area renderer. Placeholder-only.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION = "prediction_warroom.v2.scenario_area_renderer.ps_q29d.v1"


def render_warroom_v2_scenario_area(models: list[dict[str, Any]]) -> None:
    for model in models:
        with st.container(border=True):
            st.subheader(str(model.get("title") or "日本語シナリオ"))
            for line in model.get("payload", {}).get("scenario_lines", []):
                st.write(line)
