# path: ./btcts_next/src/btcts/apps/operator_ui/components/risk_monitor_panel.py
# desc: Execution-market signal / Audit からリアルタイムリスクを評価する WarRoom Risk Monitor

from __future__ import annotations

import json
from pathlib import Path
import streamlit as st


from btcts.core import paths as core_paths

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.risk_monitor_state import (
    build_risk_monitor_state,
)
from btcts.apps.operator_ui.ui_text import get_text


def _audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


def _recent_audit_latency(lines: int = 40):

    audit_log = _audit_log_path()

    if not audit_log.exists():
        return None

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

    state = build_risk_monitor_state()
    if not state:
        st.warning(get_text(lang, "risk_monitor_missing_data"))
        return

    spread = state.get("spread")
    imbalance = state.get("imbalance")
    wall_ratio = state.get("wall_ratio")
    delta = state.get("delta")
    source_label = state.get("source_label") or "unknown"

    summary_widget = load_execution_market_summary_widget_model()

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
        f"imbalance={imbalance} / delta={delta} / wall_ratio={wall_ratio} / "
        f"source={source_label}"
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()