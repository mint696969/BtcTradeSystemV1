# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_signal_panel.py
# desc: Market / Trade Flow を基に簡易 AI シグナルを生成する WarRoom パネル

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


def _badge_class(value: str) -> str:

    if value in ("LONG BIAS", "ロング寄り"):
        return "badge-buy"

    if value in ("SHORT BIAS", "ショート寄り"):
        return "badge-sell"

    if value in ("WAIT", "待機"):
        return "badge-wait"

    return "badge-neutral"


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_signal_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)

    if not ob or not tr:
        st.warning(get_text(lang, "ai_signal_missing_data"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])

    if not bids or not asks:
        st.warning(get_text(lang, "ai_signal_orderbook_unavailable"))
        return

    bid_vol = sum(b["size"] for b in bids[:10])
    ask_vol = sum(a["size"] for a in asks[:10])

    imbalance = 0
    total = bid_vol + ask_vol

    if total > 0:
        imbalance = (bid_vol - ask_vol) / total

    items = tr.get("items", [])

    buy_vol = sum(x["size"] for x in items if x.get("side") == "BUY")
    sell_vol = sum(x["size"] for x in items if x.get("side") == "SELL")

    delta = buy_vol - sell_vol

    regime = get_text(lang, "ai_signal_value_range")

    if abs(imbalance) > 0.25:
        regime = get_text(lang, "ai_signal_value_trend")

    decision = get_text(lang, "ai_signal_value_wait")

    if imbalance > 0.2 and delta > 0:
        decision = get_text(lang, "ai_signal_value_long_bias")

    if imbalance < -0.2 and delta < 0:
        decision = get_text(lang, "ai_signal_value_short_bias")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "ai_signal_market_regime"), regime)
    c2.metric(get_text(lang, "ai_signal_orderbook_bias"), round(imbalance, 3))
    c3.metric(get_text(lang, "ai_signal_trade_delta"), round(delta, 4))
    c4.metric(get_text(lang, "ai_signal_decision"), decision)

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_badge_class(decision)}">
                {get_text(lang, 'badge_ai_decision')}: {decision}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()