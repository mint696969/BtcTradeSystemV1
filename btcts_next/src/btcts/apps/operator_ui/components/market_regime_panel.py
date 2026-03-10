# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_regime_panel.py
# desc: orderbook / trades の最新JSONLから市場レジームを簡易判定して表示する WarRoom パネル

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

    st.markdown(f"### {get_text(lang, 'market_regime_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)

    if not ob or not tr:
        st.warning(get_text(lang, "market_regime_missing_data"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])

    if not bids or not asks:
        st.warning(get_text(lang, "market_regime_orderbook_unavailable"))
        return

    best_bid = ob.get("best_bid", bids[0]["price"])
    best_ask = ob.get("best_ask", asks[0]["price"])
    spread = ob.get("spread", best_ask - best_bid)

    bid_vol = sum(b["size"] for b in bids[:10])
    ask_vol = sum(a["size"] for a in asks[:10])

    total = bid_vol + ask_vol
    imbalance = 0 if total == 0 else (bid_vol - ask_vol) / total

    items = tr.get("items", [])

    buy_vol = sum(x["size"] for x in items if x.get("side") == "BUY")
    sell_vol = sum(x["size"] for x in items if x.get("side") == "SELL")
    delta = buy_vol - sell_vol

    regime = get_text(lang, "market_regime_value_range")
    spread_state = get_text(lang, "market_regime_value_normal")
    pressure = get_text(lang, "market_regime_value_neutral")
    flow_agreement = get_text(lang, "market_regime_value_mixed")

    if spread > 7000:
        spread_state = get_text(lang, "market_regime_value_wide")
    elif spread < 3000:
        spread_state = get_text(lang, "market_regime_value_tight")

    if imbalance > 0.2:
        pressure = get_text(lang, "market_regime_value_buy")
    elif imbalance < -0.2:
        pressure = get_text(lang, "market_regime_value_sell")

    if delta > 0 and imbalance > 0:
        flow_agreement = get_text(lang, "market_regime_value_buy_confirm")
    elif delta < 0 and imbalance < 0:
        flow_agreement = get_text(lang, "market_regime_value_sell_confirm")

    if abs(imbalance) > 0.45:
        regime = get_text(lang, "market_regime_value_trend")
    elif spread_state == get_text(lang, "market_regime_value_wide") and abs(delta) < 0.05:
        regime = get_text(lang, "market_regime_value_liquidity_vacuum")
    elif abs(delta) > 0.3 and abs(imbalance) < 0.15:
        regime = get_text(lang, "market_regime_value_volatility_expansion")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "market_regime_regime"), regime)
    c2.metric(get_text(lang, "market_regime_spread_state"), spread_state)
    c3.metric(get_text(lang, "market_regime_pressure"), pressure)
    c4.metric(get_text(lang, "market_regime_flow_agreement"), flow_agreement)

    st.divider()