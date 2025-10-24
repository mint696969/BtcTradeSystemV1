# path: ./btc_trade_system/features/audit_dev/summary_panels.py
# desc: dev_audit.jsonl を薄く集約して UI/スナップショットに使える要約ブロックを描画/生成

from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime, timezone
import streamlit as st

from .search import tail_lines as _tail_lines

_LEVEL_RANK = {"DEBUG":10,"INFO":20,"WARN":30,"WARNING":30,"ERROR":40,"CRIT":50,"CRITICAL":50}

def _jsonl_tail(path: Path, limit: int = 2000) -> list[dict]:
    rows: list[dict] = []
    for s in _tail_lines(path, limit=limit):
        s = (s or "").strip()
        if not s:
            continue
        try:
            rows.append(json.loads(s))
        except Exception:
            pass
    return rows

def _level_norm(v) -> str:
    if isinstance(v, (int,float)):
        n=int(v); return "CRIT" if n>=50 else "ERROR" if n>=40 else "WARN" if n>=30 else "INFO" if n>=20 else "DEBUG"
    s=str(v or "").upper()
    if s=="ERR": s="ERROR"
    if s=="WARNING": s="WARN"
    return s

# ---------- UI描画系（必要最小限） ----------
def render_health_panel(log_path: Path):
    st.subheader("Collector Health", divider="grey")
    rows=_jsonl_tail(log_path,1200)
    beats=[r for r in rows if str(r.get("event","")).endswith("collector.heartbeat")]
    if not beats:
        st.info("No heartbeat events."); return
    latest=beats[-1]; p=latest.get("payload") or {}
    lag_ms=int(p.get("lag_ms") or p.get("behind_ms") or 0)
    fetched=p.get("fetched"); dropped=p.get("dropped")
    c=st.columns(4)
    c[0].metric("alive","yes"); c[1].metric("behind (ms)",f"{lag_ms}")
    c[2].metric("fetched", "-" if fetched is None else f"{fetched}")
    c[3].metric("dropped", "-" if dropped is None else f"{dropped}")

def render_quota_panel(log_path: Path):
    st.subheader("API Quota", divider="grey")
    rows=_jsonl_tail(log_path,1500)
    q=[r for r in rows if str(r.get("event","")).endswith(("api.quota","api.retry","api.429"))]
    if not q: st.info("No quota events."); return
    quota=next((r for r in reversed(q) if str(r.get("event","")).endswith("api.quota")),None)
    retry=sum(1 for r in q if str(r.get("event","")).endswith("api.retry"))
    too_many=sum(1 for r in q if str(r.get("event","")).endswith("api.429"))
    c=st.columns(3)
    if quota:
        p=quota.get("payload") or {}
        c[0].metric("remaining", f"{p.get('remaining','-')}")
        c[1].metric("bucket", f"{p.get('bucket','-')}")
    else:
        c[0].metric("remaining","-"); c[1].metric("bucket","-")
    c[2].metric("retry/429", f"{retry}/{too_many}")

def render_orders_timeline(log_path: Path):
    st.subheader("Orders Timeline", divider="grey")
    rows=_jsonl_tail(log_path,1500)
    orders=[r for r in rows if str(r.get("event","")).startswith("dev.order.")]
    if not orders: st.info("No order events."); return
    for r in orders[-50:]:
        lvl=_level_norm(r.get("level")); ev=r.get("event","-").split(".")[-1]
        f=r.get("feature","-")
        tid=(r.get("trace_id") or (r.get("payload") or {}).get("trace_id") or "-")
        sym=(r.get("payload") or {}).get("symbol") or "-"
        st.code(f"[{lvl}] {ev:8s}  feature={f}  symbol={sym}  trace_id={tid}", language="text")
