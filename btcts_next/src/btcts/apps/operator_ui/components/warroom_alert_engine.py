# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_engine.py
# desc: War Room 向けの軽量アラートエンジン。replay / research artifact を基に重要な状態変化とリスク上昇を表示する。

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_regime_name,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    replay_tail_rows,
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


def _spread_state(spread: float | None) -> str | None:
    if spread is None:
        return None
    if spread >= 7000:
        return "wide"
    if spread <= 3000:
        return "tight"
    return "normal"


def _decision_label(regime: str | None, imbalance, delta) -> str:
    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            return "long_bias"

    if regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            return "short_bias"

    return "wait"


def _risk_score(spread, imbalance, delta, wall_ratio, latency):
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

    if isinstance(latency, (int, float)):
        if latency > 450:
            score += 2
        elif latency > 320:
            score += 1

    return score


def _risk_level(score: int) -> str:
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


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


def _build_alerts(lang: str) -> list[dict]:
    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    tail = replay_tail_rows(replay_payload, limit=20)
    if not tail:
        return []

    board_snapshots = []
    trade_snapshots = []

    for row in tail:
        if not isinstance(row, dict):
            continue

        kind = row.get("kind")
        if kind == "board":
            board = board_signal_metrics(row)
            if board:
                board_snapshots.append(board)
        elif kind == "trade":
            flow = tradeflow_metrics(row)
            if flow:
                trade_snapshots.append(flow)

    if not board_snapshots:
        return []

    latest_board = board_snapshots[-1]
    previous_board = board_snapshots[-2] if len(board_snapshots) >= 2 else None

    latest_flow = trade_snapshots[-1] if trade_snapshots else None

    regime = latest_regime_name(experiment_payload)
    best_strategy = latest_best_strategy_name(experiment_payload)

    spread = latest_board.get("spread")
    imbalance = latest_board.get("imbalance")
    pressure_bias = latest_board.get("pressure_bias")
    wall_ratio = latest_board.get("wall_ratio")
    delta = latest_flow.get("trade_delta") if isinstance(latest_flow, dict) else None

    alert_ts = (
        str(latest_board.get("event_ts"))
        if latest_board.get("event_ts")
        else str(latest_flow.get("event_ts"))
        if isinstance(latest_flow, dict) and latest_flow.get("event_ts")
        else None
    )

    latency = _recent_audit_latency()
    risk_score = _risk_score(spread, imbalance, delta, wall_ratio, latency)
    risk_level = _risk_level(risk_score)

    alerts: list[dict] = []

    if previous_board:
        prev_spread_state = _spread_state(previous_board.get("spread"))
        current_spread_state = _spread_state(spread)

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

    decision = _decision_label(regime, imbalance, delta)
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
    if prev_risk_level != risk_level and risk_level == "high":
        _append_alert(
            alerts,
            "critical",
            "risk_spike",
            get_text(lang, "warroom_alert_risk_spike"),
            ts=alert_ts,
        )
    st.session_state.warroom_prev_risk_level = risk_level

    if best_strategy != "unknown":
        _append_alert(
            alerts,
            "info",
            "strategy_snapshot",
            get_text(lang, "warroom_alert_strategy_snapshot").format(strategy=best_strategy),
            ts=alert_ts,
        )

    severity_order = {
        "critical": 0,
        "warning": 1,
        "info": 2,
    }
    alerts.sort(key=lambda x: severity_order.get(x["severity"], 9))
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
            ts_text = f" ({alert['ts']})" if alert.get("ts") else ""
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
                    st.session_state.ui_selected_page = get_text(lang, "page_replay")
                    st.rerun()

    st.caption(get_text(lang, "warroom_alert_caption"))
    st.divider()