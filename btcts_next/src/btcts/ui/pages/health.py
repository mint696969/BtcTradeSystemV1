# path: ./btcts_next/src/btcts/ui/pages/health.py
# desc: Healthページ（UI）。btcts.health.svc を呼び出して結果を表示する。UI→health の一方向に固定し循環importを防ぐ。

from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import streamlit as st
from btcts.core import env as ENV
from btcts.core import paths as PATHS


def _env(k: str) -> str:
    return os.environ.get(k, "") or ""


def render_health_page() -> None:
    st.subheader("Health")

    # 遅延import（UI import時の副作用を避ける）
    from btcts.health.svc import read_health

    # refresh
    c1, c2 = st.columns([1, 3])
    with c1:
        refresh = st.button("Refresh", width="stretch")

    if "health_summary" not in st.session_state:
        st.session_state["health_summary"] = None
        st.session_state["health_err"] = ""
        st.session_state["health_ts"] = 0.0

    def _load() -> None:
        try:
            st.session_state["health_summary"] = read_health()
            st.session_state["health_err"] = ""
        except Exception as e:
            st.session_state["health_summary"] = None
            st.session_state["health_err"] = f"read_health() failed: {type(e).__name__}: {e}"
        st.session_state["health_ts"] = time.time()

    should_load = refresh or (st.session_state["health_summary"] is None and not st.session_state["health_err"])
    if should_load:
        _load()

    err = st.session_state.get("health_err", "")
    hs = st.session_state.get("health_summary")
    ts = st.session_state.get("health_ts", 0.0)
    age = max(0.0, time.time() - ts) if ts else 0.0

    if err:
        st.error(err)
        st.caption(f"age={age:.1f}s")
        return

    if hs is None:
        st.warning("no health data")
        st.caption(f"age={age:.1f}s")
        return

    # Paths (根拠：svc が参照したもの)
    refs = getattr(hs, "refs", {}) or {}
    with st.expander("Refs (evidence)", expanded=False):
        st.write(refs)

    # summary
    counts = getattr(hs, "counts", {}) or {}
    updated_at = getattr(hs, "updated_at", None)
    overall = getattr(hs, "overall", "")
    st.caption(
        f"updated_at={updated_at} / overall={overall} / "
        f"OK={counts.get('OK', 0)} WARN={counts.get('WARN', 0)} CRIT={counts.get('CRIT', 0)} / age={age:.1f}s"
    )

    items = getattr(hs, "items", []) or []
    if not items:
        st.info("Health items is empty. status.json / 設定(endpoints/exchanges) / audit.jsonl を確認してください。")
    else:
        rows: List[Dict[str, Any]] = []
        for it in items:
            if hasattr(it, "model_dump"):
                rows.append(it.model_dump())
            elif hasattr(it, "__dict__"):
                rows.append(dict(it.__dict__))
            elif isinstance(it, dict):
                rows.append(it)
            else:
                rows.append({"value": str(it)})

        st.dataframe(rows, width="stretch", hide_index=True)

    # reasons
    reasons = getattr(hs, "reasons", []) or []
    if reasons:
        with st.expander("Reasons (facts)", expanded=False):
            for r in reasons:
                st.write(f"- {r}")

    # audit tail（根拠：そのまま提示、解釈しない）
    audit_tail = getattr(hs, "audit_tail", []) or []
    if audit_tail:
        with st.expander("Audit tail (raw)", expanded=False):
            st.dataframe(audit_tail, width="stretch", hide_index=True)
