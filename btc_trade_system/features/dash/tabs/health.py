# path: ./btc_trade_system/features/dash/tabs/health.py
# desc: Healthタブ（status.json読取／leader注釈）。UIは読取専用

from __future__ import annotations
import time
import streamlit as st
import matplotlib.pyplot as plt

from ...dashboard.providers import get_health_summary, get_health_table

PALE = {
    "OK":   {"fg":"#166534", "bg":"#ecfdf5"},
    "WARN": {"fg":"#92400e", "bg":"#fff7ed"},
    "CRIT": {"fg":"#991b1b", "bg":"#fef2f2"},
    "MUTED": "#6b7280",
    "BORDER": "rgba(0,0,0,.04)",
    "SHADOW": "0 1px 2px rgba(0,0,0,.05)",
}

def _css():
    st.markdown(f"""
    <style>
      div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        padding: 4px !important;
      }}
      .card {{
        width: 100%;
        border:1px solid {PALE['BORDER']};
        border-radius:16px;
        padding:20px 22px;
        box-shadow:{PALE['SHADOW']};
        transition: all .2s ease-in-out;
      }}
      .card:hover {{
        transform: translateY(-2px);
        box-shadow:0 3px 6px rgba(0,0,0,.08);
      }}
      .title {{ margin:0 0 8px 0; font-weight:700; }}
      .chip {{
        display:inline-block; padding:2px 8px; border-radius:999px;
        font-size:12px; font-weight:600; color:#fff;
      }}
      .muted {{ color:{PALE['MUTED']}; font-size:12px; }}
      .kv {{ margin-top:6px; font-size:18px; font-weight:600; }}
    </style>
    """, unsafe_allow_html=True)

def _timeline(ax, status:str, age_sec:float|None, window_s:int):
    age = max(0.0, float(age_sec or 0.0))
    age = min(age, float(window_s))
    ok_len = max(0.0, window_s - age)

    ok_color = "#e7f7ee"
    miss_color = {"OK":"#d9f5e3", "WARN":"#fff4d6", "CRIT":"#ffe4e6"}.get(status, "#eee")

    ax.barh([0], [ok_len], color=ok_color, height=0.5)
    ax.barh([0], [age], left=[ok_len], color=miss_color, height=0.5)

    ax.set_xlim(0, window_s); ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)

def _status_chip(status:str) -> str:
    fg = PALE.get(status, {}).get("fg", "#374151")
    return f"<span class='chip' style='background:{fg};opacity:.85'>{status}</span>"

def render():
    _css()
    st.subheader("コレクターの健全性")

    # --- ヘッダ（自動更新・期間） ---
    c1, c2, _ = st.columns([1, 1, 6])
    with c1:
        auto = st.toggle("自動更新（このタブ）", value=False)
    with c2:
        win_label = st.selectbox("期間", ["5分", "10分", "30分", "60分"], index=1)
    window_s = {"5分": 300, "10分": 600, "30分": 1800, "60分": 3600}[win_label]

    if auto:
        st.caption("自動更新: 5秒ごと")
        time.sleep(5)
        st.experimental_rerun()

    # --- データ取得 ---
    s = get_health_summary()
    st.caption(f"更新: {s['updated_at']} / all_ok={s['all_ok']}")

    # --- カード（1ブロックHTMLで描画） ---
    cols = st.columns(max(1, len(s["cards"])))
    for i, c in enumerate(s["cards"]):
        ex = c["exchange"]
        status = c["status"]
        age = c["age_sec"]
        notes = c.get("notes", "")
        bg = PALE.get(status, {}).get("bg", "#fff")
        fg = PALE.get(status, {}).get("fg", "#374151")
        chip = f"<span class='chip' style='background:{fg};opacity:.85'>{status}</span>"
        note_html = f"<div class='muted'>{notes}</div>" if notes else ""

        card_html = f"""
        <div class='card' style='background:{bg};'>
          <div class='title'>{ex} {chip}</div>
          <div class='muted'>更新遅延</div>
          <div class='kv'>{age:.1f}s</div>
          {note_html}
        </div>
        """
        with cols[i]:
            st.markdown(card_html, unsafe_allow_html=True)

    # --- タイムライン ---
    st.divider()
    st.write("タイムライン（右端=現在／塗り=未更新区間・淡色）")
    for c in s["cards"]:
        st.markdown(f"**{c['exchange']}**")
        fig, ax = plt.subplots(figsize=(8, 0.35), dpi=150)
        _timeline(ax, c["status"], c["age_sec"], window_s)
        st.pyplot(fig)
        plt.close(fig)

    # --- 詳細表 ---
    st.divider()
    st.write("詳細")
    table = get_health_table()
    if table:
        st.dataframe(table, width="stretch")
    else:
        st.info("status.json が見つかりません")
