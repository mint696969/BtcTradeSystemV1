# path: ./btcts_next/src/btcts/apps/operator_ui/components/strategy_state_panel.py
# desc: Market / Liquidity / Trade Flow から現在の戦略状態を簡易判定して表示する WarRoom パネル

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


def _mode_badge_class(value: str) -> str:

    if value in ("上昇トレンド", "LONG TREND"):
        return "badge-buy"

    if value in ("下降トレンド", "SHORT TREND"):
        return "badge-sell"

    if value in ("中立", "NEUTRAL"):
        return "badge-neutral"

    return "badge-wait"


def _risk_badge_class(value: str) -> str:

    if value in ("高", "HIGH"):
        return "badge-risk-high"

    if value in ("低", "LOW"):
        return "badge-risk-low"

    return "badge-neutral"


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'strategy_state_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)

    if not ob or not tr:
        st.warning(get_text(lang, "strategy_state_missing_data"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    items = tr.get("items", [])

    if not bids or not asks or not items:
        st.warning(get_text(lang, "strategy_state_unavailable"))
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

    top_bid_wall = max(b["size"] for b in bids[:10])
    top_ask_wall = max(a["size"] for a in asks[:10])
    wall_total = top_bid_wall + top_ask_wall
    wall_ratio = 0 if wall_total == 0 else (top_bid_wall - top_ask_wall) / wall_total

    strategy_mode = get_text(lang, "strategy_state_value_neutral")
    risk_state = get_text(lang, "strategy_state_value_medium")
    confidence = 0.50
    recommended_archetype = get_text(lang, "strategy_state_value_observe")

    if spread > 7000:
        risk_state = get_text(lang, "strategy_state_value_high")
    elif spread < 3000:
        risk_state = get_text(lang, "strategy_state_value_low")

    if imbalance > 0.2 and delta > 0 and wall_ratio > 0:
        strategy_mode = get_text(lang, "strategy_state_value_long_trend")
        recommended_archetype = get_text(lang, "strategy_state_value_breakout")
        confidence = 0.72

    elif imbalance < -0.2 and delta < 0 and wall_ratio < 0:
        strategy_mode = get_text(lang, "strategy_state_value_short_trend")
        recommended_archetype = get_text(lang, "strategy_state_value_liquidity_trap")
        confidence = 0.74

    elif abs(imbalance) < 0.15 and abs(delta) < 0.15:
        strategy_mode = get_text(lang, "strategy_state_value_range_scalp")
        recommended_archetype = get_text(lang, "strategy_state_value_mean_reversion")
        confidence = 0.63

    elif abs(delta) > 0.4 and abs(imbalance) < 0.15:
        strategy_mode = get_text(lang, "strategy_state_value_volatility_watch")
        recommended_archetype = get_text(lang, "strategy_state_value_momentum_probe")
        confidence = 0.61

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "strategy_state_mode"), strategy_mode)
    c2.metric(get_text(lang, "strategy_state_risk"), risk_state)
    
    archetype_label_map = {
        get_text(lang, "strategy_state_value_observe"): get_text(lang, "strategy_state_value_observe_label"),
        get_text(lang, "strategy_state_value_breakout"): get_text(lang, "strategy_state_value_breakout_label"),
        get_text(lang, "strategy_state_value_liquidity_trap"): get_text(lang, "strategy_state_value_liquidity_trap_label"),
        get_text(lang, "strategy_state_value_mean_reversion"): get_text(lang, "strategy_state_value_mean_reversion_label"),
        get_text(lang, "strategy_state_value_momentum_probe"): get_text(lang, "strategy_state_value_momentum_probe_label"),
    }

    c3.metric(
        get_text(lang, "strategy_state_archetype"),
        archetype_label_map.get(recommended_archetype, recommended_archetype),
    )

    c4.metric(get_text(lang, "strategy_state_confidence"), round(confidence, 2))

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_mode_badge_class(strategy_mode)}">
                {get_text(lang, 'badge_strategy_mode')}: {strategy_mode}
            </span>
            <span class="warroom-badge {_risk_badge_class(risk_state)}">
                {get_text(lang, 'badge_risk_state')}: {risk_state}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()