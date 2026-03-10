# path: ./btcts_next/src/btcts/apps/operator_ui/components/trade_flow_monitor.py
# desc: trades JSONL から最新約定群を読み、BUY/SELL volume と delta を表示する WarRoom パネル

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.ui_text import get_text

DATA_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\trades")


def read_latest_trades():

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

    st.markdown(f"### {get_text(lang, 'trade_flow_title')}")

    tr = read_latest_trades()

    if not tr:
        st.warning(get_text(lang, "trade_flow_not_found"))
        return

    items = tr.get("items", [])

    if not items:
        st.warning(get_text(lang, "trade_flow_empty"))
        return

    buy_vol = sum(x["size"] for x in items if x.get("side") == "BUY")
    sell_vol = sum(x["size"] for x in items if x.get("side") == "SELL")
    delta = buy_vol - sell_vol

    c1, c2, c3 = st.columns(3)

    c1.metric(get_text(lang, "trade_flow_buy_volume"), round(buy_vol, 4))
    c2.metric(get_text(lang, "trade_flow_sell_volume"), round(sell_vol, 4))
    c3.metric(get_text(lang, "trade_flow_delta"), round(delta, 4))

    st.caption(f"{get_text(lang, 'trade_flow_recent_count')}: {len(items)}")
    st.divider()