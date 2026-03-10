# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor.py
# desc: orderbook JSONL から最新スナップショットを読み BTC market metrics を表示

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.ui_text import get_text

DATA_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\orderbook")


def read_latest_orderbook():

    if not DATA_DIR.exists():
        return None

    files = sorted(DATA_DIR.glob("*.jsonl"))

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


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'market_monitor_title')}")

    ob = read_latest_orderbook()

    if not ob:
        st.warning(get_text(lang, "market_monitor_not_found"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])

    if not bids or not asks:
        st.warning(get_text(lang, "market_monitor_empty"))
        return

    best_bid = ob.get("best_bid", bids[0]["price"])
    best_ask = ob.get("best_ask", asks[0]["price"])
    spread = ob.get("spread", best_ask - best_bid)

    bid_vol = sum(b["size"] for b in bids[:10])
    ask_vol = sum(a["size"] for a in asks[:10])

    total = bid_vol + ask_vol
    imbalance = 0 if total == 0 else (bid_vol - ask_vol) / total

    c1, c2, c3 = st.columns(3)

    c1.metric(get_text(lang, "market_monitor_spread"), round(spread, 2))
    c2.metric(get_text(lang, "market_monitor_bid_volume"), round(bid_vol, 4))
    c3.metric(get_text(lang, "market_monitor_ask_volume"), round(ask_vol, 4))

    st.metric(get_text(lang, "market_monitor_imbalance"), round(imbalance, 3))

    st.divider()