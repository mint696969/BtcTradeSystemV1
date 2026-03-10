# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_market_summary_panel.py
# desc: orderbook / trades の最新状態から市場状況を文章で要約する WarRoom パネル

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.ui_text import get_text

ORDERBOOK_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\orderbook")
TRADES_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\trades")


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


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_summary_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)

    if not ob or not tr:
        st.warning(get_text(lang, "ai_summary_missing_data"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    items = tr.get("items", [])

    if not bids or not asks or not items:
        st.warning(get_text(lang, "ai_summary_missing_data"))
        return

    best_bid = ob.get("best_bid", bids[0]["price"])
    best_ask = ob.get("best_ask", asks[0]["price"])
    spread = ob.get("spread", best_ask - best_bid)

    bid_vol = sum(b["size"] for b in bids[:10])
    ask_vol = sum(a["size"] for a in asks[:10])
    total = bid_vol + ask_vol
    imbalance = 0 if total == 0 else (bid_vol - ask_vol) / total

    buy_vol = sum(x["size"] for x in items if x.get("side") == "BUY")
    sell_vol = sum(x["size"] for x in items if x.get("side") == "SELL")
    delta = buy_vol - sell_vol

    if imbalance > 0.2:
        headline = get_text(lang, "ai_summary_value_buy_bias")
    elif imbalance < -0.2:
        headline = get_text(lang, "ai_summary_value_sell_bias")
    else:
        headline = get_text(lang, "ai_summary_value_neutral_bias")

    bullets = []

    if spread > 7000:
        bullets.append(get_text(lang, "ai_summary_value_wide_spread"))
    elif spread < 3000:
        bullets.append(get_text(lang, "ai_summary_value_tight_spread"))

    if delta > 0.2:
        bullets.append(get_text(lang, "ai_summary_value_buy_flow"))
    elif delta < -0.2:
        bullets.append(get_text(lang, "ai_summary_value_sell_flow"))

    if imbalance > 0.2 and delta > 0:
        outlook = get_text(lang, "ai_summary_value_long_watch")
    elif imbalance < -0.2 and delta < 0:
        outlook = get_text(lang, "ai_summary_value_short_watch")
    else:
        outlook = get_text(lang, "ai_summary_value_wait")

    st.markdown(f"**{get_text(lang, 'ai_summary_headline')}**")
    st.info(headline)

    st.markdown(f"**{get_text(lang, 'ai_summary_bullets')}**")
    if bullets:
        for item in bullets:
            st.markdown(f"- {item}")
    else:
        st.markdown("-")

    st.markdown(f"**{get_text(lang, 'ai_summary_outlook')}**")
    st.success(outlook)

    st.divider()