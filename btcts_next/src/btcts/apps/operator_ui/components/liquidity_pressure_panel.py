# path: ./btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_panel.py
# desc: orderbook の上位板から流動性の壁を算出し、Bid/Ask の圧力を表示する WarRoom パネル

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.ui_text import get_text

ORDERBOOK_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\orderbook")


def _read_latest_jsonl(dir_path):

    if not dir_path.exists():
        return None

    files = sorted(dir_path.glob("*.jsonl"))

    if not files:
        return None

    latest = files[-1]

    with open(latest, "rb") as f:

        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0:

            step = min(block, size)
            size -= step
            f.seek(size)

            data = f.read(step) + data

            if data.count(b"\n") >= 2:
                break

        line = data.splitlines()[-1]

    return json.loads(line)


def _badge_class(value: str) -> str:

    if value in ("BUY", "買い"):
        return "badge-buy"

    if value in ("SELL", "売り"):
        return "badge-sell"

    return "badge-neutral"


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'liquidity_pressure_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)

    if not ob:
        st.warning(get_text(lang, "liquidity_pressure_not_found"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])

    if not bids or not asks:
        st.warning(get_text(lang, "liquidity_pressure_empty"))
        return

    top_bid_wall = max(b["size"] for b in bids[:10])
    top_ask_wall = max(a["size"] for a in asks[:10])

    total_wall = top_bid_wall + top_ask_wall
    wall_ratio = 0 if total_wall == 0 else (top_bid_wall - top_ask_wall) / total_wall

    wall_bias = get_text(lang, "liquidity_pressure_value_neutral")

    if wall_ratio > 0.2:
        wall_bias = get_text(lang, "liquidity_pressure_value_buy")
    elif wall_ratio < -0.2:
        wall_bias = get_text(lang, "liquidity_pressure_value_sell")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "liquidity_pressure_top_bid_wall"), round(top_bid_wall, 4))
    c2.metric(get_text(lang, "liquidity_pressure_top_ask_wall"), round(top_ask_wall, 4))
    c3.metric(get_text(lang, "liquidity_pressure_wall_ratio"), round(wall_ratio, 3))
    c4.metric(get_text(lang, "liquidity_pressure_wall_bias"), wall_bias)

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_badge_class(wall_bias)}">
                {get_text(lang, 'badge_liquidity_bias')}: {wall_bias}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()