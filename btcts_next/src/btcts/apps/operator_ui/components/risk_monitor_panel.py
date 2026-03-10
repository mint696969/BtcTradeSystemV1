# path: ./btcts_next/src/btcts/apps/operator_ui/components/risk_monitor_panel.py
# desc: orderbook / trades / audit の直近状態から WarRoom 用の総合リスクを表示する専用パネル

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


def _risk_badge_class(value: str) -> str:

    if value in ("高", "HIGH"):
        return "badge-risk-high"

    if value in ("低", "LOW"):
        return "badge-risk-low"

    return "badge-neutral"


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'risk_monitor_title')}")

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)
    audit_rows = _read_recent_audit(lines=40)

    if not ob or not tr:
        st.warning(get_text(lang, "risk_monitor_missing_data"))
        return

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    items = tr.get("items", [])

    if not bids or not asks or not items:
        st.warning(get_text(lang, "risk_monitor_unavailable"))
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

    latencies = [
        float(row["latency_ms"])
        for row in audit_rows
        if row.get("latency_ms") is not None
    ]
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 0.0

    spread_risk = get_text(lang, "risk_monitor_value_low")
    latency_risk = get_text(lang, "risk_monitor_value_low")
    flow_risk = get_text(lang, "risk_monitor_value_low")
    liquidity_risk = get_text(lang, "risk_monitor_value_low")

    risk_score = 0

    if spread > 7000:
        spread_risk = get_text(lang, "risk_monitor_value_high")
        risk_score += 2
    elif spread > 4500:
        spread_risk = get_text(lang, "risk_monitor_value_medium")
        risk_score += 1

    if avg_latency >= 450:
        latency_risk = get_text(lang, "risk_monitor_value_high")
        risk_score += 2
    elif avg_latency >= 320:
        latency_risk = get_text(lang, "risk_monitor_value_medium")
        risk_score += 1

    if (imbalance > 0.15 and delta < 0) or (imbalance < -0.15 and delta > 0):
        flow_risk = get_text(lang, "risk_monitor_value_high")
        risk_score += 2
    elif abs(delta) < 0.1 and abs(imbalance) < 0.1:
        flow_risk = get_text(lang, "risk_monitor_value_medium")
        risk_score += 1

    if abs(wall_ratio) > 0.45:
        liquidity_risk = get_text(lang, "risk_monitor_value_high")
        risk_score += 2
    elif abs(wall_ratio) > 0.25:
        liquidity_risk = get_text(lang, "risk_monitor_value_medium")
        risk_score += 1

    overall_risk = get_text(lang, "risk_monitor_value_low")
    if risk_score >= 6:
        overall_risk = get_text(lang, "risk_monitor_value_high")
    elif risk_score >= 3:
        overall_risk = get_text(lang, "risk_monitor_value_medium")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(get_text(lang, "risk_monitor_overall"), overall_risk)
    c2.metric(get_text(lang, "risk_monitor_spread"), spread_risk)
    c3.metric(get_text(lang, "risk_monitor_latency"), latency_risk)
    c4.metric(get_text(lang, "risk_monitor_flow"), flow_risk)
    c5.metric(get_text(lang, "risk_monitor_liquidity"), liquidity_risk)

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_risk_badge_class(overall_risk)}">
                {get_text(lang, 'risk_monitor_badge_overall')}: {overall_risk}
            </span>
            <span class="warroom-badge {_risk_badge_class(spread_risk)}">
                {get_text(lang, 'risk_monitor_badge_spread')}: {spread_risk}
            </span>
            <span class="warroom-badge {_risk_badge_class(latency_risk)}">
                {get_text(lang, 'risk_monitor_badge_latency')}: {latency_risk}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"{get_text(lang, 'risk_monitor_snapshot')}: "
        f"spread={round(spread, 1)}, avg_latency={avg_latency}, "
        f"imbalance={round(imbalance, 3)}, delta={round(delta, 3)}, wall_ratio={round(wall_ratio, 3)}"
    )

    st.divider()