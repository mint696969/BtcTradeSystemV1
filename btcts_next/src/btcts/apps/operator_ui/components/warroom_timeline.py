# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_timeline.py
# desc: Replay / Research artifact から War Room 用の最新状況変化ログを組み立てて表示するタイムラインパネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_regime_name,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    replay_tail_rows,
    tradeflow_metrics,
)
from btcts.apps.operator_ui.ui_text import get_text


def _append_if_changed(timeline: list[dict], ts: str, label: str, value: str | float | None, previous):
    if value is None:
        return previous

    if previous != value:
        timeline.append(
            {
                "ts": ts,
                "label": label,
                "value": value,
            }
        )

    return value


def _spread_state(spread: float | None, lang: str) -> str | None:
    if spread is None:
        return None
    if spread >= 7000:
        return get_text(lang, "warroom_value_wide")
    if spread <= 3000:
        return get_text(lang, "warroom_value_tight")
    return get_text(lang, "warroom_value_normal")


def _pressure_label(pressure_bias: str | None, lang: str) -> str:
    if pressure_bias == "buy_pressure":
        return get_text(lang, "warroom_value_buy")
    if pressure_bias == "sell_pressure":
        return get_text(lang, "warroom_value_sell")
    return get_text(lang, "warroom_value_neutral")


def _regime_label(regime: str | None, lang: str) -> str | None:
    if not regime or regime == "unknown":
        return None

    mapping = {
        "range": get_text(lang, "warroom_value_range"),
        "trend_up": get_text(lang, "warroom_value_trend"),
        "trend_down": get_text(lang, "warroom_value_trend"),
        "liquidity_vacuum": get_text(lang, "warroom_value_liquidity_vacuum"),
        "absorption_zone": get_text(lang, "warroom_value_absorption"),
    }
    return mapping.get(regime, regime)


def _decision_label(regime: str | None, imbalance, delta, lang: str) -> str:
    decision = get_text(lang, "warroom_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            return get_text(lang, "warroom_value_long_bias")

    if regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            return get_text(lang, "warroom_value_short_bias")

    return decision


def _build_timeline(lang: str, replay_payload, experiment_payload) -> list[dict]:
    timeline: list[dict] = []

    tail = replay_tail_rows(replay_payload, limit=20)

    prev_regime = None
    prev_spread_state = None
    prev_pressure = None
    prev_decision = None

    current_board = None
    current_flow = None

    regime_raw = latest_regime_name(experiment_payload)
    regime_label = _regime_label(regime_raw, lang)

    for row in tail:
        if not isinstance(row, dict):
            continue

        kind = row.get("kind")
        ts = str(row.get("event_ts") or row.get("ts") or row.get("timestamp") or "-")

        if kind == "board":
            board = board_signal_metrics(row)
            if board:
                current_board = board

        elif kind == "trade":
            flow = tradeflow_metrics(row)
            if flow:
                current_flow = flow

        if current_board is None:
            continue

        spread = current_board.get("spread")
        imbalance = current_board.get("imbalance")
        pressure = _pressure_label(current_board.get("pressure_bias"), lang)
        spread_state = _spread_state(spread, lang)
        delta = current_flow.get("trade_delta") if isinstance(current_flow, dict) else None
        decision = _decision_label(regime_raw, imbalance, delta, lang)

        prev_regime = _append_if_changed(
            timeline,
            ts,
            get_text(lang, "warroom_timeline_regime"),
            regime_label,
            prev_regime,
        )
        prev_spread_state = _append_if_changed(
            timeline,
            ts,
            get_text(lang, "warroom_timeline_spread"),
            spread_state,
            prev_spread_state,
        )
        prev_pressure = _append_if_changed(
            timeline,
            ts,
            get_text(lang, "warroom_timeline_pressure"),
            pressure,
            prev_pressure,
        )
        prev_decision = _append_if_changed(
            timeline,
            ts,
            get_text(lang, "warroom_timeline_decision"),
            decision,
            prev_decision,
        )

    return timeline[-20:]


def _build_live_timeline(lang: str, experiment_payload) -> list[dict]:
    timeline: list[dict] = []

    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)

    spread = live_board.get("spread")
    bid_depth = live_board.get("bid_depth")
    ask_depth = live_board.get("ask_depth")
    delta = live_flow.get("delta")
    ts = str(live_flow.get("event_ts") or live_board.get("event_ts") or "-")

    if spread is None:
        return []

    imbalance = None
    if bid_depth is not None and ask_depth is not None:
        try:
            bid_f = float(bid_depth)
            ask_f = float(ask_depth)
            denom = bid_f + ask_f
            if denom > 0:
                imbalance = (bid_f - ask_f) / denom
        except Exception:
            imbalance = None

    regime_raw = latest_regime_name(experiment_payload)
    regime_label = _regime_label(regime_raw, lang)
    spread_state = _spread_state(float(spread), lang) if spread is not None else None

    pressure_bias = "neutral_bias"
    if isinstance(imbalance, (int, float)):
        if imbalance > 0.2:
            pressure_bias = "buy_pressure"
        elif imbalance < -0.2:
            pressure_bias = "sell_pressure"

    pressure = _pressure_label(pressure_bias, lang)
    decision = _decision_label(regime_raw, imbalance, delta, lang)

    if regime_label is not None:
        timeline.append(
            {"ts": ts, "label": get_text(lang, "warroom_timeline_regime"), "value": regime_label}
        )
    if spread_state is not None:
        timeline.append(
            {"ts": ts, "label": get_text(lang, "warroom_timeline_spread"), "value": spread_state}
        )
    timeline.append(
        {"ts": ts, "label": get_text(lang, "warroom_timeline_pressure"), "value": pressure}
    )
    timeline.append(
        {"ts": ts, "label": get_text(lang, "warroom_timeline_decision"), "value": decision}
    )

    return timeline[-20:]


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'warroom_timeline_title')}")

    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    timeline = _build_live_timeline(lang, experiment_payload)
    timeline_is_live = bool(timeline)
    if not timeline:
        timeline = _build_timeline(lang, replay_payload, experiment_payload)
        timeline_is_live = False

    if not timeline:
        st.info(get_text(lang, "warroom_timeline_empty"))
        st.divider()
        return

    for idx, item in enumerate(reversed(timeline)):
        c1, c2 = st.columns([6, 1])

        with c1:
            st.markdown(
                f"**{item['ts']}**  "
                f"{item['label']} → `{item['value']}`"
            )

        with c2:
            if not timeline_is_live:
                if st.button(
                    "Replay",
                    key=f"warroom_timeline_replay_{idx}",
                ):
                    st.session_state.replay_jump_ts = str(item["ts"])
                    st.session_state.ui_selected_page = get_text(lang, "page_replay")
                    st.rerun()

    if timeline and str(timeline[0].get("ts", "")).startswith("2026-03-20"):
        st.caption("live_canonical / research_experiment ソースから検出した最新の変化です。")
    else:
        st.caption(get_text(lang, "warroom_timeline_caption"))
    st.divider()