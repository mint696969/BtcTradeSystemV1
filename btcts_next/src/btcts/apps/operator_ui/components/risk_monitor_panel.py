# path: ./btcts_next/src/btcts/apps/operator_ui/components/risk_monitor_panel.py
# desc: Replay / Research / Audit からリアルタイムリスクを評価する WarRoom Risk Monitor

from __future__ import annotations

import json
from pathlib import Path
import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    latest_trade_row,
    load_latest_replay_payload,
    tradeflow_metrics,
)
from btcts.apps.operator_ui.ui_text import get_text


AUDIT_LOG = Path(r"E:\btc_ts\logs\audit.jsonl")


def _recent_audit_latency(lines: int = 40):

    if not AUDIT_LOG.exists():
        return None

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

    rows = []

    for line in data.splitlines()[-lines:]:
        try:
            obj = json.loads(line)
            payload = obj.get("payload", {})
            if payload.get("elapsed_ms") is not None:
                rows.append(float(payload["elapsed_ms"]))
        except Exception:
            continue

    if not rows:
        return None

    return sum(rows) / len(rows)


def _risk_score(spread, imbalance, delta, wall_ratio, latency):

    score = 0

    # spread
    if spread and spread > 7000:
        score += 2
    elif spread and spread > 4500:
        score += 1

    # imbalance vs delta conflict
    if imbalance and delta:
        if (imbalance > 0.2 and delta < 0) or (imbalance < -0.2 and delta > 0):
            score += 2

    # liquidity wall
    if wall_ratio and abs(wall_ratio) > 0.45:
        score += 2
    elif wall_ratio and abs(wall_ratio) > 0.25:
        score += 1

    # latency
    if latency:
        if latency > 450:
            score += 2
        elif latency > 320:
            score += 1

    return score


def _risk_level(score, lang):

    if score >= 6:
        return get_text(lang, "risk_value_high")

    if score >= 3:
        return get_text(lang, "risk_value_medium")

    return get_text(lang, "risk_value_low")


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'risk_monitor_title')}")

    replay_payload = load_latest_replay_payload()

    board = board_signal_metrics(
        latest_board_row(replay_payload)
    )

    flow = tradeflow_metrics(
        latest_trade_row(replay_payload)
    )

    if not board or not flow:
        st.warning(get_text(lang, "risk_monitor_missing_data"))
        return

    spread = board.get("spread")
    imbalance = board.get("imbalance")
    wall_ratio = board.get("wall_ratio")

    delta = flow.get("trade_delta")

    latency = _recent_audit_latency()

    score = _risk_score(
        spread,
        imbalance,
        delta,
        wall_ratio,
        latency,
    )

    level = _risk_level(score, lang)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        get_text(lang, "risk_monitor_level"),
        level,
    )

    c2.metric(
        get_text(lang, "risk_monitor_score"),
        score,
    )

    c3.metric(
        get_text(lang, "risk_monitor_latency"),
        "-" if latency is None else round(latency, 1),
    )

    c4.metric(
        get_text(lang, "risk_monitor_spread"),
        "-" if spread is None else round(float(spread), 2),
    )

    st.caption(
        f"imbalance={imbalance} / delta={delta} / wall_ratio={wall_ratio}"
    )

    st.divider()