# path: ./btc_trade_system/features/dash/tabs/audit.py
from __future__ import annotations
import streamlit as st
from ..providers import get_audit_rows

def render():
    st.subheader("監査ログ")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        q = st.text_input("キーワード", "", placeholder="event= / feature= / level= など")
    with c2:
        level = st.selectbox("レベル", ["ALL","INFO","WARN","ERROR"], index=0)
    with c3:
        limit = st.selectbox("件数", [200,500,1000], index=1)

    rows = get_audit_rows(limit=int(limit))
    def _match(r: dict) -> bool:
        if level != "ALL" and r.get("level") != level:
            return False
        if q:
            s = (r.get("event","") + " " + r.get("feature","") + " " + str(r.get("payload",""))).lower()
            return q.lower() in s
        return True

    rows = [r for r in rows if _match(r)]
    st.caption(f"{len(rows)} 件")
    if rows:
        # 表示用に主要カラムだけ
        view = [
            {
                "ts": r.get("ts"),
                "level": r.get("level"),
                "feature": r.get("feature"),
                "event": r.get("event"),
                "actor": r.get("actor"),
                "site": r.get("site"),
                "session": r.get("session"),
                "payload": r.get("payload"),
            }
            for r in rows
        ]
        st.dataframe(view, use_container_width=True, height=480)
    else:
        st.info("audit.jsonl が無いか、条件に一致する行がありません。")

