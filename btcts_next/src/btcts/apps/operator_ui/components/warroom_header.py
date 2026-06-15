# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py
# desc: Replay / Research artifact を要約し、War Room 冒頭に現在の戦況サマリーを表示するヘッダーパネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.compact_metric_cards import (
    render_compact_metric_grid,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_summary_status_payload,
    load_execution_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    active_event_compact_reading_line,
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.warroom_header_state import (
    build_warroom_header_state,
)
from btcts.apps.operator_ui.ui_text import get_text


def _spread_state(spread: float | None, lang: str) -> str:
    if spread is None:
        return get_text(lang, "warroom_value_unknown")

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


def _risk_level(spread, imbalance, delta, wall_ratio):
    score = 0

    if isinstance(spread, (int, float)):
        if spread > 7000:
            score += 2
        elif spread > 4500:
            score += 1

    if isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if (imbalance > 0.2 and delta < 0) or (imbalance < -0.2 and delta > 0):
            score += 2

    if isinstance(wall_ratio, (int, float)):
        if abs(wall_ratio) > 0.45:
            score += 2
        elif abs(wall_ratio) > 0.25:
            score += 1

    if score >= 4:
        return "HIGH"
    if score >= 2:
        return "MEDIUM"
    return "LOW"


def _risk_label(level: str, lang: str) -> str:
    mapping = {
        "LOW": get_text(lang, "warroom_value_low"),
        "MEDIUM": get_text(lang, "warroom_value_medium"),
        "HIGH": get_text(lang, "warroom_value_high"),
    }
    return mapping.get(level, level)


def _ai_decision(regime: str, imbalance, delta, lang: str) -> str:
    decision = get_text(lang, "warroom_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            decision = get_text(lang, "warroom_value_long_bias")

    elif regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            decision = get_text(lang, "warroom_value_short_bias")

    return decision


def _regime_label(regime: str, lang: str) -> str:
    mapping = {
        "range": get_text(lang, "warroom_value_range"),
        "trend_up": get_text(lang, "warroom_value_trend"),
        "trend_down": get_text(lang, "warroom_value_trend"),
        "liquidity_vacuum": get_text(lang, "warroom_value_liquidity_vacuum"),
        "absorption_zone": get_text(lang, "warroom_value_absorption"),
    }
    return mapping.get(regime, regime or get_text(lang, "warroom_value_unknown"))


def build_warroom_market_reading_caption(
    *,
    state: dict | None,
) -> str:
    if not state:
        return "warroom_reading unavailable"

    regime = str(state.get("regime") or "unknown")
    source = str(state.get("source_label") or state.get("source") or "unknown")
    prediction_bias = str(state.get("prediction_bias") or "unknown")
    prediction_caution = str(state.get("prediction_caution") or "unknown")
    prediction_switch_hint = str(state.get("prediction_switch_hint") or "unknown")
    prediction_trace_summary = str(state.get("prediction_trace_summary") or "-")

    return (
        f"market_reading={regime} / "
        f"source={source} / "
        f"prediction_bias={prediction_bias} / "
        f"prediction_caution={prediction_caution} / "
        f"prediction_switch_hint={prediction_switch_hint} / "
        f"prediction_trace={prediction_trace_summary}"
    )


def build_warroom_operational_reading_caption(
    *,
    state: dict | None,
    summary_payload: dict | None,
) -> str:
    if not state and not summary_payload:
        return "operational_reading unavailable"

    state_map = dict(state or {})
    regime = str(state_map.get("regime") or "unknown")
    source = str(state_map.get("source_label") or state_map.get("source") or "unknown")
    prediction_bias = str(state_map.get("prediction_bias") or "unknown")
    prediction_caution = str(state_map.get("prediction_caution") or "unknown")
    active_event_line = active_event_compact_reading_line(summary_payload)

    return (
        f"operational_reading={regime} / "
        f"source={source} / "
        f"active_event={active_event_line} / "
        f"prediction_bias={prediction_bias} / "
        f"prediction_caution={prediction_caution} / "
        "review_mode=operator_review_only / "
        "execution=not_instruction"
    )


def _analyze_live_or_fallback():
    return build_warroom_header_state()


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'warroom_header_title')}")

    state = _analyze_live_or_fallback()
    if not state:
        st.warning(get_text(lang, "warroom_header_missing_data"))
        return

    summary_widget = load_execution_market_summary_widget_model()
    summary_payload = load_execution_market_summary_status_payload()

    regime = state.get("regime") or "unknown"
    best_strategy = state.get("best_strategy") or "-"

    spread = state.get("spread")
    imbalance = state.get("imbalance")
    pressure_bias = state.get("pressure_bias")
    wall_ratio = state.get("wall_ratio")
    delta = state.get("delta")

    spread_state = _spread_state(spread, lang)
    pressure = _pressure_label(pressure_bias, lang)
    risk_level = _risk_level(spread, imbalance, delta, wall_ratio)
    risk_label = _risk_label(risk_level, lang)
    ai_decision = _ai_decision(regime, imbalance, delta, lang)

    render_compact_metric_grid(
        (
            (get_text(lang, "warroom_header_regime"), _regime_label(regime, lang)),
            (get_text(lang, "warroom_header_spread_state"), spread_state),
            (get_text(lang, "warroom_header_pressure"), pressure),
            (
                get_text(lang, "warroom_header_trade_flow"),
                "-" if delta is None else round(float(delta), 4),
            ),
            (get_text(lang, "warroom_header_ai_decision"), ai_decision),
            (get_text(lang, "warroom_header_risk"), risk_label),
        ),
        min_width_px=110,
    )

    st.caption(
        get_text(lang, "warroom_header_summary_caption").format(
            best_strategy=best_strategy,
            spread=spread,
            imbalance=imbalance,
            wall_ratio=wall_ratio,
        )
    )
    live_shell.render_scrollable_text_block(
        build_warroom_market_reading_caption(
            state=state,
        ),
        max_height_px=120,
        monospace=True,
    )
    live_shell.render_scrollable_text_block(
        build_warroom_operational_reading_caption(
            state=state,
            summary_payload=summary_payload,
        ),
        max_height_px=140,
        monospace=True,
    )
    st.caption(
        get_text(lang, "warroom_generic_source_caption").format(
            source=state.get("source_label") or state.get("source", "unknown"),
        )
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()