# path: ./btcts_next/src/btcts/apps/operator_ui/components/trade_flow_monitor.py
# desc: Replay tradeflow から BUY/SELL volume と delta を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    latest_trade_row,
    load_latest_replay_payload,
    tradeflow_metrics,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts

from btcts.apps.operator_ui.components.live_bridge import (
    recent_live_tradeflow_metrics,
)


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'trade_flow_title')}")

    live_flow = recent_live_tradeflow_metrics(lines=80)
    source_label = "live_canonical"

    if live_flow:
        flow = {
            "buy_volume": live_flow.get("buy_size"),
            "sell_volume": live_flow.get("sell_size"),
            "trade_delta": live_flow.get("delta"),
            "trade_count": live_flow.get("trade_count"),
            "event_ts": live_flow.get("event_ts"),
            "micro_event_names": [],
        }
    else:
        replay_payload = load_latest_replay_payload()
        flow = tradeflow_metrics(latest_trade_row(replay_payload))
        source_label = "replay_tradeflow"

    if not flow:
        st.warning(get_text(lang, "trade_flow_not_found"))
        return

    buy_vol = flow.get("buy_volume")
    sell_vol = flow.get("sell_volume")
    delta = flow.get("trade_delta")
    trade_count = flow.get("trade_count")

    c1, c2, c3 = st.columns(3)

    c1.metric(get_text(lang, "trade_flow_buy_volume"), "-" if buy_vol is None else round(float(buy_vol), 4))
    c2.metric(get_text(lang, "trade_flow_sell_volume"), "-" if sell_vol is None else round(float(sell_vol), 4))
    c3.metric(get_text(lang, "trade_flow_delta"), "-" if delta is None else round(float(delta), 4))

    st.caption(f"{get_text(lang, 'trade_flow_recent_count')}: {trade_count}")

    st.caption(
        f"source={source_label} / ts={format_ui_ts(flow.get('event_ts'), lang)}"
    )

    micro_names = flow.get("micro_event_names") or []
    if micro_names:
        st.caption("microstructure: " + ", ".join(micro_names[:5]))

    st.divider()