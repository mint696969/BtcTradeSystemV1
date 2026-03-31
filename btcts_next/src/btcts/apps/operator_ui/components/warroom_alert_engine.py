# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_engine.py
# desc: War Room 向けの軽量アラートエンジン。replay / research artifact を基に重要な状態変化とリスク上昇を表示する。

from __future__ import annotations

import streamlit as st
from btcts.apps.operator_ui.components.warroom_alert_logic import (
    decision_label,
    risk_level,
    risk_score,
    spread_state,
)
from btcts.apps.operator_ui.components.warroom_alert_presenter import (
    live_probe_message,
    pressure_bias_from_imbalance,
    severity_order_value,
    strategy_label,
)
from btcts.apps.operator_ui.components.warroom_alert_state import (
    build_live_alert_state,
    build_replay_alert_state,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def _append_alert(
    alerts: list[dict],
    severity: str,
    code: str,
    message: str,
    ts: str | None = None,
):
    alerts.append(
        {
            "severity": severity,
            "code": code,
            "message": message,
            "ts": ts,
        }
    )


def _severity_label(lang: str, severity: str) -> str:
    mapping = {
        "critical": get_text(lang, "warroom_alert_severity_critical"),
        "warning": get_text(lang, "warroom_alert_severity_warning"),
        "info": get_text(lang, "warroom_alert_severity_info"),
    }
    return mapping.get(severity, severity)


def _build_live_alerts(lang: str) -> list[dict]:
    state = build_live_alert_state()
    if not state:
        return []

    spread = state["spread"]
    imbalance = state["imbalance"]
    delta = state["delta"]
    alert_ts = state["alert_ts"]
    regime = state["regime"]
    best_strategy = state["best_strategy"]
    latency = state["latency"]

    pressure_bias = pressure_bias_from_imbalance(imbalance)
    current_risk_score = risk_score(spread, imbalance, delta, None, latency)
    current_risk_level = risk_level(current_risk_score)

    alerts: list[dict] = []

    current_spread_state = spread_state(spread)
    prev_spread_state = st.session_state.get("warroom_live_prev_spread_state")
    if prev_spread_state != current_spread_state and current_spread_state is not None:
        _append_alert(
            alerts,
            "warning" if current_spread_state == "wide" else "info",
            "spread_state_change",
            get_text(lang, "warroom_alert_spread_state_changed").format(
                state=get_text(lang, f"warroom_alert_value_{current_spread_state}")
            ),
            ts=str(alert_ts) if alert_ts else None,
        )
    st.session_state.warroom_live_prev_spread_state = current_spread_state

    prev_pressure = st.session_state.get("warroom_live_prev_pressure")
    if prev_pressure != pressure_bias:
        _append_alert(
            alerts,
            "warning",
            "pressure_flip",
            get_text(lang, "warroom_alert_pressure_changed").format(
                state=get_text(lang, f"warroom_alert_value_{pressure_bias}")
            ),
            ts=str(alert_ts) if alert_ts else None,
        )
    st.session_state.warroom_live_prev_pressure = pressure_bias

    decision = decision_label(regime, imbalance, delta)
    prev_decision = st.session_state.get("warroom_prev_decision")
    if prev_decision != decision:
        _append_alert(
            alerts,
            "info",
            "ai_decision_change",
            get_text(lang, "warroom_alert_ai_decision_changed").format(
                state=get_text(lang, f"warroom_alert_value_{decision}")
            ),
            ts=str(alert_ts) if alert_ts else None,
        )
    st.session_state.warroom_prev_decision = decision

    prev_risk_level = st.session_state.get("warroom_prev_risk_level")
    if prev_risk_level != current_risk_level and current_risk_level == "high":
        _append_alert(
            alerts,
            "critical",
            "risk_spike",
            get_text(lang, "warroom_alert_risk_spike"),
            ts=str(alert_ts) if alert_ts else None,
        )
    st.session_state.warroom_prev_risk_level = current_risk_level

    current_strategy_label = strategy_label(best_strategy)

    _append_alert(
        alerts,
        "info",
        "strategy_snapshot",
        get_text(lang, "warroom_alert_strategy_snapshot").format(strategy=current_strategy_label),
        ts=str(alert_ts) if alert_ts else None,
    )

    alerts.sort(key=lambda x: severity_order_value(x["severity"]))

    if not alerts:
        _append_alert(
            alerts,
            "info",
            "live_probe",
            live_probe_message(spread, delta, best_strategy, regime),
            ts=str(alert_ts) if alert_ts else None,
        )

    return alerts[:6]


def _build_alerts(lang: str) -> list[dict]:
    # current runtime policy:
    # warroom alert stream is live-first.
    # replay/research alerts are preserved in _build_replay_alerts() for future switchback.
    return _build_live_alerts(lang)


def _build_replay_alerts(lang: str) -> list[dict]:
    # reserved fallback path:
    # currently not used by render(), kept for future replay-driven alert mode.
    state = build_replay_alert_state()
    if not state:
        return []

    previous_board = state["previous_board"]
    spread = state["spread"]
    imbalance = state["imbalance"]
    pressure_bias = state["pressure_bias"]
    wall_ratio = state["wall_ratio"]
    delta = state["delta"]
    alert_ts = state["alert_ts"]
    regime = state["regime"]
    best_strategy = state["best_strategy"]
    latency = state["latency"]
    current_risk_score = risk_score(spread, imbalance, delta, wall_ratio, latency)
    current_risk_level = risk_level(current_risk_score)

    alerts: list[dict] = []

    if previous_board:
        prev_spread_state = spread_state(previous_board.get("spread"))
        current_spread_state = spread_state(spread)

        if prev_spread_state != current_spread_state and current_spread_state is not None:
            _append_alert(
                alerts,
                "warning" if current_spread_state == "wide" else "info",
                "spread_state_change",
                get_text(lang, "warroom_alert_spread_state_changed").format(
                    state=get_text(lang, f"warroom_alert_value_{current_spread_state}")
                ),
                ts=alert_ts,
            )

        prev_pressure = previous_board.get("pressure_bias")
        if prev_pressure != pressure_bias and pressure_bias is not None:
            _append_alert(
                alerts,
                "warning",
                "pressure_flip",
                get_text(lang, "warroom_alert_pressure_changed").format(
                    state=get_text(lang, f"warroom_alert_value_{pressure_bias}")
                ),
                ts=alert_ts,
            )

    decision = decision_label(regime, imbalance, delta)
    prev_decision = st.session_state.get("warroom_prev_decision")
    if prev_decision != decision:
        _append_alert(
            alerts,
            "info",
            "ai_decision_change",
            get_text(lang, "warroom_alert_ai_decision_changed").format(
                state=get_text(lang, f"warroom_alert_value_{decision}")
            ),
            ts=alert_ts,
        )
    st.session_state.warroom_prev_decision = decision

    prev_risk_level = st.session_state.get("warroom_prev_risk_level")
    if prev_risk_level != current_risk_level and current_risk_level == "high":
        _append_alert(
            alerts,
            "critical",
            "risk_spike",
            get_text(lang, "warroom_alert_risk_spike"),
            ts=alert_ts,
        )
    st.session_state.warroom_prev_risk_level = current_risk_level

    if best_strategy != "unknown":
        _append_alert(
            alerts,
            "info",
            "strategy_snapshot",
            get_text(lang, "warroom_alert_strategy_snapshot").format(strategy=best_strategy),
            ts=alert_ts,
        )

    alerts.sort(key=lambda x: severity_order_value(x["severity"]))

    if not alerts and best_strategy != "unknown":
        _append_alert(
            alerts,
            "info",
            "strategy_snapshot",
            get_text(lang, "warroom_alert_strategy_snapshot").format(strategy=best_strategy),
            ts=str(alert_ts) if alert_ts else None,
        )

    return alerts[:6]


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'warroom_alert_title')}")

    alerts = _build_alerts(lang)
    if not alerts:
        st.info(get_text(lang, "warroom_alert_empty"))
        st.divider()
        return

    for idx, alert in enumerate(alerts):
        severity_label = _severity_label(lang, alert["severity"])

        c1, c2 = st.columns([6, 1])

        with c1:
            ts_text = f" ({format_ui_ts(alert['ts'], lang)})" if alert.get("ts") else ""
            st.markdown(
                f"**[{severity_label}]** {alert['message']}{ts_text}",
            )

        with c2:
            if alert.get("ts"):
                if st.button(
                    "Replay",
                    key=f"warroom_alert_replay_{idx}",
                ):
                    st.session_state.replay_jump_ts = str(alert["ts"])
                    st.session_state.ui_selected_page_key = "replay"
                    st.rerun()

    st.caption(get_text(lang, "warroom_alert_runtime_caption"))
    st.divider()