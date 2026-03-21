# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_signal_panel.py
# desc: Replay / Research artifact を基に簡易 AI シグナルを生成する WarRoom パネル

from __future__ import annotations

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
from btcts.apps.operator_ui.ui_text import get_text

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)


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

    experiment_payload = load_latest_experiment_payload()

    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)

    source_label = "replay_board+tradeflow + research_experiment"
    replay_ts = None

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
            "event_ts": live_board.get("event_ts"),
        }
        flow = {
            "trade_delta": float(live_delta),
            "event_ts": live_flow.get("event_ts"),
        }
        source_label = "live_canonical + research_experiment"
        replay_ts = flow.get("event_ts")

    if not board or not flow:
        replay_payload = load_latest_replay_payload()
        board = board_signal_metrics(latest_board_row(replay_payload))
        flow = tradeflow_metrics(latest_trade_row(replay_payload))
        replay_ts = flow.get("event_ts") if flow else None

    if not board or not flow:
        st.warning(get_text(lang, "ai_signal_missing_data"))
        return

    imbalance = board.get("imbalance")
    delta = flow.get("trade_delta")
    regime = latest_regime_name(experiment_payload)
    best_strategy = latest_best_strategy_name(experiment_payload)

    regime_label = get_text(lang, "ai_signal_value_range")
    if regime in {"trend_up", "trend_down"}:
        regime_label = get_text(lang, "ai_signal_value_trend")
    elif regime == "liquidity_vacuum":
        regime_label = "Liquidity Vacuum"
    elif regime == "absorption_zone":
        regime_label = "Absorption Zone"

    decision = get_text(lang, "ai_signal_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            decision = get_text(lang, "ai_signal_value_long_bias")

    elif regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            decision = get_text(lang, "ai_signal_value_short_bias")

    elif regime == "absorption_zone":
        if best_strategy in {"microstructure_v1", "regime_aware_microstructure_v1"}:
            if isinstance(delta, (int, float)) and delta < 0:
                decision = get_text(lang, "ai_signal_value_short_bias")
            elif isinstance(delta, (int, float)) and delta > 0:
                decision = get_text(lang, "ai_signal_value_long_bias")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "ai_signal_market_regime"), regime_label)
    c2.metric(
        get_text(lang, "ai_signal_orderbook_bias"),
        "-" if imbalance is None else round(float(imbalance), 3),
    )
    c3.metric(
        get_text(lang, "ai_signal_trade_delta"),
        "-" if delta is None else round(float(delta), 4),
    )
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

    st.caption(
        f"best_strategy={best_strategy} / replay_ts={replay_ts} / "
        f"source={source_label}"
    )

    st.divider()