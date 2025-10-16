# path: btc_trade_system/features/dash/health_ui.py
# path: ./btc_trade_system/features/dash/health_ui.py
# desc: HealthタブのUI（表示専用）— svc_* 集計を描画

from __future__ import annotations
import time

# --- streamlit ---
try:
    import streamlit as st  # type: ignore
except ImportError:
    import types as _t
    st = _t.SimpleNamespace(
        markdown=print,
        subheader=print,
        columns=lambda *a, **k: [None],
        divider=lambda: None,
        write=print,
        dataframe=print,
        info=print,
        caption=print,
        selectbox=lambda *a, **k: "10分",
        toggle=lambda *a, **k: False,
        experimental_rerun=lambda: None,
        pyplot=lambda *a, **k: None,
    )

# --- matplotlib ---
try:
    import matplotlib.pyplot as plt  # type: ignore
except ImportError:
    class _DummyPlot:
        def subplots(self, *a, **k): return (None, None)
        def close(self, *a, **k): pass
    plt = _DummyPlot()

# --- services（features 平置きの正式ルート） ---
from btc_trade_system.features.dash.providers import (
    get_health_summary,
    get_health_table,
)

from btc_trade_system.features.dash.leader_annotations import load_status_with_leader  # noqa: E402

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

    if ax is None: return
    ax.barh([0], [ok_len], color=ok_color, height=0.5)
    ax.barh([0], [age], left=[ok_len], color=miss_color, height=0.5)

    ax.set_xlim(0, window_s); ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)

def render():
    _css()
    st.subheader("コレクターの健全性")

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

    s = get_health_summary()
    st.caption(f"更新: {s['updated_at']} / all_ok={s['all_ok']}")

    # storage メタはデバッグ時のみキャプション表示（通常は非表示）
    try:
        import json as _json, os as _os
        from pathlib import Path as _P
        _sp = _P(_os.environ.get("BTC_TS_DATA_DIR", "data")) / "collector" / "status.json"
        _raw = _json.loads(_sp.read_text(encoding="utf-8"))
        _stg = _raw.get("storage") or {}
        if _stg and _os.environ.get("BTC_TS_DEBUG_UI") == "1":
            st.caption(
                "storage: "
                f"primary_ok={_stg.get('primary_ok')} / "
                f"logs_root={_stg.get('logs_root')} / "
                f"data_root={_stg.get('data_root')}"
            )
    except Exception:
        pass

    cols = st.columns(max(1, len(s.get("cards", []))))
    for i, c in enumerate(s.get("cards", [])):
        ex = c.get("exchange", "?")
        status = c.get("status", "-")
        age_val = c.get("age_sec", None)
        notes = c.get("notes", "")
        bg = PALE.get(status, {}).get("bg", "#fff")
        fg = PALE.get(status, {}).get("fg", "#374151")
        chip = f"<span class='chip' style='background:{fg};opacity:.85'>{status}</span>"
        note_html = f"<div class='muted'>{notes}</div>" if notes else ""
        try:
            age_display = f"{float(age_val):.1f}s"
        except Exception:
            age_display = "-"

        card_html = f"""
        <div class='card' style='background:{bg};'>
          <div class='title'>{ex} {chip}</div>
          <div class='muted'>更新遅延</div>
          <div class='kv'>{age_display}</div>
          {note_html}
        </div>
        """
        
        if cols[i]:
            st.markdown(card_html, unsafe_allow_html=True)

    st.divider()
    st.write("タイムライン（右端=現在／塗り=未更新区間・淡色）")
    for c in s.get("cards", []):
        st.markdown(f"**{c.get('exchange','?')}**")
        fig, ax = (plt.subplots(figsize=(8, 0.35), dpi=150) if hasattr(plt, 'subplots') else (None, None))
        _timeline(ax, c.get("status"), c.get("age_sec"), window_s)
        if hasattr(st, 'pyplot') and fig is not None:
            st.pyplot(fig)
        if hasattr(plt, 'close'):
            plt.close(fig)

    st.divider()
    st.write("詳細")
    table = get_health_table()

    try:
        # leader メタのみ利用（items は UI 側で既に整形済みのため未使用）
        _leader = load_status_with_leader()[1]
        host = _leader.get("host") if _leader else None
        hb_ms = int(_leader.get("heartbeat_ms", 0) or 0) if _leader else 0
        import time as _t
        age_sec = int(max(0, (_t.time() * 1000 - hb_ms)) / 1000) if hb_ms else None

        if table:
            if hasattr(table, "columns"):
                if "leader.host" not in getattr(table, "columns", []):
                    table["leader.host"] = host
                if "leader_age_sec" not in getattr(table, "columns", []):
                    table["leader_age_sec"] = age_sec
            elif isinstance(table, list):
                for row in table:
                    row["leader.host"] = host
                    row["leader_age_sec"] = age_sec

    except Exception:
        pass

    # storage 注釈（status.json の storage ブロックを読んで付与）
    try:
        import json as _json, os as _os
        from pathlib import Path as _P
        _sp = _P(_os.environ.get("BTC_TS_DATA_DIR", "data")) / "collector" / "status.json"
        _raw = _json.loads(_sp.read_text(encoding="utf-8"))
        _stg = _raw.get("storage") or {}
        s_primary = _stg.get("primary_ok")
        s_logs = _stg.get("logs_root")
        s_data = _stg.get("data_root")

        if table:
            if hasattr(table, "columns"):
                if "storage.primary_ok" not in getattr(table, "columns", []):
                    table["storage.primary_ok"] = s_primary
                if "storage.logs_root" not in getattr(table, "columns", []):
                    table["storage.logs_root"] = s_logs
                if "storage.data_root" not in getattr(table, "columns", []):
                    table["storage.data_root"] = s_data
            elif isinstance(table, list):
                for row in table:
                    row["storage.primary_ok"] = s_primary
                    row["storage.logs_root"] = s_logs
                    row["storage.data_root"] = s_data
    except Exception:
        pass

    # 並び替え（DataFrame のときのみ／list[dict] はそのまま）
    try:
        if hasattr(table, "sort_values") and "leader_age_sec" in getattr(table, "columns", []):
            table = table.sort_values(
                ["leader_age_sec", "exchange", "topic"],
                ascending=[True, True, True],
                na_position="last",
            )
    except Exception:
        pass

    if table:
        st.dataframe(table, width="stretch")
    else:
        st.info("status.json が見つかりません")


