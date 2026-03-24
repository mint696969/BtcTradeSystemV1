# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_panels.py
# desc: Live canonical / Research / Audit 優先で Analyst AI / Strategy AI / Risk AI を表示する WarRoom エージェントパネル

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_board_row,
    latest_regime_name,
    latest_trade_row,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    tradeflow_metrics,
)

import os
from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)

from btcts.apps.operator_ui.ui_text import get_text

def _audit_log_path() -> Path:
    logs_dir = os.environ.get("BTC_TS_LOGS_DIR", r"E:\btc_ts\logs")
    return Path(logs_dir) / "audit.jsonl"


def _read_recent_audit(lines=40):

    audit_log = _audit_log_path()

    if not audit_log.exists():
        return []

    with open(audit_log, "rb") as f:
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


def _analyst_view(lang, regime, spread, pressure_bias):

    regime_label = get_text(lang, "agent_value_range")
    if regime in {"trend_up", "trend_down"}:
        regime_label = get_text(lang, "agent_value_trend")
    elif regime == "absorption_zone":
        regime_label = get_text(lang, "warroom_value_absorption")
    elif regime == "liquidity_vacuum":
        regime_label = get_text(lang, "warroom_value_liquidity_vacuum")

    pressure = get_text(lang, "agent_value_neutral")
    if pressure_bias == "buy_pressure":
        pressure = get_text(lang, "agent_value_buy")
    elif pressure_bias == "sell_pressure":
        pressure = get_text(lang, "agent_value_sell")

    spread_state = get_text(lang, "agent_value_normal")
    if isinstance(spread, (int, float)):
        if spread > 7000:
            spread_state = get_text(lang, "agent_value_wide")
        elif spread < 3000:
            spread_state = get_text(lang, "agent_value_tight")

    return regime_label, spread_state, pressure


def _strategy_view(lang, regime, best_strategy, imbalance, delta):

    archetype = best_strategy
    stance = get_text(lang, "agent_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            stance = get_text(lang, "agent_value_long_bias")

    elif regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            stance = get_text(lang, "agent_value_short_bias")

    elif regime == "absorption_zone":
        if isinstance(delta, (int, float)) and delta < 0:
            stance = get_text(lang, "agent_value_short_bias")
        elif isinstance(delta, (int, float)) and delta > 0:
            stance = get_text(lang, "agent_value_long_bias")
        else:
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

    if isinstance(spread, (int, float)):
        if spread > 7000:
            score += 2
        elif spread > 4500:
            score += 1

    if avg_latency >= 450:
        score += 2
    elif avg_latency >= 320:
        score += 1

    if isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if (imbalance > 0.15 and delta < 0) or (imbalance < -0.15 and delta > 0):
            score += 2

    if isinstance(wall_ratio, (int, float)):
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

    experiment_payload = load_latest_experiment_payload()
    audit_rows = _read_recent_audit(lines=40)

    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)

    source_label = "replay_board+tradeflow + research_experiment + audit_latency"

    board = None
    flow = None

    live_spread = live_board.get("spread")
    live_delta = live_flow.get("delta")

    if live_spread is not None and live_delta is not None:
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")

        imbalance = None
        if bid_depth is not None and ask_depth is not None:
            try:
                bid_depth_f = float(bid_depth)
                ask_depth_f = float(ask_depth)
                denom = bid_depth_f + ask_depth_f
                if denom > 0:
                    imbalance = (bid_depth_f - ask_depth_f) / denom
            except Exception:
                imbalance = None

        board = {
            "spread": float(live_spread),
            "imbalance": imbalance,
            "pressure_bias": "live_orderbook",
            "wall_ratio": None,
        }
        flow = {
            "trade_delta": float(live_delta),
        }
        source_label = "live_canonical + research_experiment + audit_latency"

    if not board or not flow:
        replay_payload = load_latest_replay_payload()
        board = board_signal_metrics(latest_board_row(replay_payload))
        flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        st.warning(get_text(lang, "agent_panels_missing_data"))
        return

    regime = latest_regime_name(experiment_payload)
    best_strategy = latest_best_strategy_name(experiment_payload)

    spread = board.get("spread")
    imbalance = board.get("imbalance")
    pressure_bias = board.get("pressure_bias")
    wall_ratio = board.get("wall_ratio")
    delta = flow.get("trade_delta")

    analyst_regime, analyst_spread, analyst_pressure = _analyst_view(
        lang,
        regime,
        spread,
        pressure_bias,
    )

    strategy_arch, strategy_stance = _strategy_view(
        lang,
        regime,
        best_strategy,
        imbalance,
        delta,
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
        st.metric(
            get_text(lang, "agent_strategy_delta"),
            "-" if delta is None else round(float(delta), 4),
        )

    with col3:
        st.markdown(f"#### {get_text(lang, 'agent_risk_title')}")
        st.metric(get_text(lang, "agent_risk_level"), risk_level)
        st.metric(get_text(lang, "agent_risk_latency"), avg_latency)
        st.metric(
            get_text(lang, "agent_risk_wall_ratio"),
            "-" if wall_ratio is None else round(float(wall_ratio), 3),
        )

    st.caption(
        f"{get_text(lang, 'agent_panels_snapshot')}: "
        f"regime={regime}, spread={spread}, imbalance={imbalance}, "
        f"delta={delta}, wall_ratio={wall_ratio}, best={best_strategy} / "
        f"source={source_label}"
    )

    st.divider()