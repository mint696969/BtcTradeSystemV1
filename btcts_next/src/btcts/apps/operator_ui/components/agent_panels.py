# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_panels.py
# desc: Analyst AI / Strategy AI / Risk AI の役割別サマリーを並列表示する WarRoom エージェントパネル

import json
from pathlib import Path

import streamlit as st

from btcts.apps.operator_ui.ui_text import get_text

ORDERBOOK_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\orderbook")
TRADES_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\trades")
AUDIT_LOG = Path(r"E:\btc_ts\logs\audit.jsonl")


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


def _read_recent_audit(lines=40):

    if not AUDIT_LOG.exists():
        return []

    with open(AUDIT_LOG, "rb") as f:
        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0 and data.count(b"\n") < lines:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data

    out = []

    for line in data.splitlines()[-lines:]:
        try:
            obj = json.loads(line)
            payload = obj.get("payload", {})
            out.append(
                {
                    "event": obj.get("event"),
                    "latency_ms": payload.get("elapsed_ms"),
                    "topic": payload.get("topic"),
                }
            )
        except Exception:
            continue

    return out


def _analyst_view(lang, spread, imbalance, delta):

    regime = get_text(lang, "agent_value_range")

    if abs(imbalance) > 0.25:
        regime = get_text(lang, "agent_value_trend")

    pressure = get_text(lang, "agent_value_neutral")
    if delta > 0.2:
        pressure = get_text(lang, "agent_value_buy")
    elif delta < -0.2:
        pressure = get_text(lang, "agent_value_sell")

    spread_state = get_text(lang, "agent_value_normal")
    if spread > 7000:
        spread_state = get_text(lang, "agent_value_wide")
    elif spread < 3000:
        spread_state = get_text(lang, "agent_value_tight")

    return regime, spread_state, pressure


def _strategy_view(lang, imbalance, delta, wall_ratio):

    archetype = get_text(lang, "agent_value_observe")
    stance = get_text(lang, "agent_value_wait")

    if imbalance > 0.2 and delta > 0 and wall_ratio > 0:
        archetype = get_text(lang, "agent_value_breakout")
        stance = get_text(lang, "agent_value_long_bias")
    elif imbalance < -0.2 and delta < 0 and wall_ratio < 0:
        archetype = get_text(lang, "agent_value_liquidity_trap")
        stance = get_text(lang, "agent_value_short_bias")
    elif abs(imbalance) < 0.15 and abs(delta) < 0.15:
        archetype = get_text(lang, "agent_value_mean_reversion")
        stance = get_text(lang, "agent_value_wait")
    elif abs(delta) > 0.4 and abs(imbalance) < 0.15:
        archetype = get_text(lang, "agent_value_momentum_probe")
        stance = get_text(lang, "agent_value_prepare")

    return archetype, stance


def _risk_view(lang, spread, imbalance, delta, wall_ratio, audit_rows):

    latencies = [
        float(row["latency_ms"])
        for row in audit_rows
        if row.get("latency_ms") is not None
    ]
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 0.0

    risk = get_text(lang, "agent_value_low")

    score = 0

    if spread > 7000:
        score += 2
    elif spread > 4500:
        score += 1

    if avg_latency >= 450:
        score += 2
    elif avg_latency >= 320:
        score += 1

    if (imbalance > 0.15 and delta < 0) or (imbalance < -0.15 and delta > 0):
        score += 2

    if abs(wall_ratio) > 0.45:
        score += 2
    elif abs(wall_ratio) > 0.25:
        score += 1

    if score >= 6:
        risk = get_text(lang, "agent_value_high")
    elif score >= 3:
        risk = get_text(lang, "agent_value_medium")

    return risk, avg_latency


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'agent_panels_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)
    audit_rows = _read_recent_audit(lines=40)

    if not ob or not tr:
        st.warning(get_text(lang, "agent_panels_missing_data"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    items = tr.get("items", [])

    if not bids or not asks or not items:
        st.warning(get_text(lang, "agent_panels_unavailable"))
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

    analyst_regime, analyst_spread, analyst_pressure = _analyst_view(
        lang,
        spread,
        imbalance,
        delta,
    )
    strategy_arch, strategy_stance = _strategy_view(
        lang,
        imbalance,
        delta,
        wall_ratio,
    )
    risk_level, avg_latency = _risk_view(
        lang,
        spread,
        imbalance,
        delta,
        wall_ratio,
        audit_rows,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"#### {get_text(lang, 'agent_analyst_title')}")
        st.metric(get_text(lang, "agent_analyst_regime"), analyst_regime)
        st.metric(get_text(lang, "agent_analyst_spread"), analyst_spread)
        st.metric(get_text(lang, "agent_analyst_pressure"), analyst_pressure)

    with col2:
        st.markdown(f"#### {get_text(lang, 'agent_strategy_title')}")
        st.metric(get_text(lang, "agent_strategy_archetype"), strategy_arch)
        st.metric(get_text(lang, "agent_strategy_stance"), strategy_stance)
        st.metric(get_text(lang, "agent_strategy_delta"), round(delta, 3))

    with col3:
        st.markdown(f"#### {get_text(lang, 'agent_risk_title')}")
        st.metric(get_text(lang, "agent_risk_level"), risk_level)
        st.metric(get_text(lang, "agent_risk_latency"), avg_latency)
        st.metric(get_text(lang, "agent_risk_wall_ratio"), round(wall_ratio, 3))

    st.caption(
        f"{get_text(lang, 'agent_panels_snapshot')}: "
        f"spread={round(spread, 1)}, imbalance={round(imbalance, 3)}, "
        f"delta={round(delta, 3)}, wall_ratio={round(wall_ratio, 3)}"
    )

    st.divider()