# path: ./btc_trade_system/features/dash/dashboard.py
# desc: ダッシュボード（ヘッダー＋タブのハブ）。tabs.yamlで並び順/有効化/初期タブを制御

from __future__ import annotations
import importlib
import pathlib
from typing import Dict, List, Optional

import streamlit as st
import yaml

# ─────────────────────────────────────────────────────────────
# 基本設定
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG_UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"
TABS_CFG_PATH = CONFIG_UI_DIR / "tabs.yaml"  # defaultsはローダ側で結合予定

# ─────────────────────────────────────────────────────────────
# ユーティリティ
def _load_yaml(path: pathlib.Path) -> Dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _get_chip_palette() -> Dict[str, Dict[str, str]]:
    """basic.yaml の colors.alert_chip（fg/bg）を読み、なければ既定色を返す。"""
    basic = _load_yaml(CONFIG_UI_DIR / "basic.yaml")
    chip = ((basic.get("colors") or {}).get("alert_chip") or {})
    def _pair(sec, fg, bg):
        s = chip.get(sec) or {}
        return {"fg": s.get("fg", fg), "bg": s.get("bg", bg)}
    return {
        "warn":   _pair("warn",   "#000000", "#FFF2CC"),
        "crit":   _pair("crit",   "#FFFFFF", "#FFCCCC"),
        "urgent": _pair("urgent", "#FFFFFF", "#FF6666"),
    }

def _css_from_basic() -> str:
    basic = _load_yaml(CONFIG_UI_DIR / "basic.yaml")
    colors = (basic.get("colors") or {}).get("tab", {})
    normal = colors.get("text_normal", "#000000")
    active = colors.get("text_active", "#FF5722")
    hover  = colors.get("text_hover",  "#FF7F27")
    inactive_bg = colors.get("bg_inactive", "#F5F5F5")

    return f"""
    <style>
    /* ヘッダーの上下余白を極小に */
    .stApp > header {{ margin: 0 !important; padding: 0 !important; }}
    [data-testid="stHorizontalBlock"] h1, 
    [data-testid="stHorizontalBlock"] h2, 
    [data-testid="stHorizontalBlock"] h3 {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.0 !important;
    }}

    /* タブ文字色（Streamlit tabsのボタンに適用） */
    div[data-baseweb="tab-list"] button p {{
        color: {normal} !important;
    }}
    div[data-baseweb="tab-list"] button[aria-selected="true"] p {{
        color: {active} !important;
        font-weight: 700 !important;
        text-underline-offset: 6px;
    }}
    div[data-baseweb="tab-list"] button:hover p {{
        color: {hover} !important;
    }}
    /* タブ列の下線・余白を薄く */
    div[data-baseweb="tab-list"] > div {{
        border-bottom: 1px solid {inactive_bg};
        margin-bottom: 4px;
    }}

    /* 歯車ボタンの枠と影を消す（押下時ズレ防止の微調整） */
    .stButton > button {{
        box-shadow: none !important;
        outline: none !important;
        padding: 0.2rem 0.45rem !important;
        border: 1px solid transparent !important;
        background: transparent !important;
    }}
    .stButton > button:focus {{
        box-shadow: none !important;
        outline: none !important;
    }}
    </style>
    """

def _render_alert_chips(alerts: List[Dict]) -> None:
    """ヘッダー右側のアラートチップ（最大3件 + more）。色は basic.yaml から取得。"""
    if not alerts:
        return
    pal = _get_chip_palette()

    # 重要度: urgent > crit > warn の順で並べ替え
    priority = {"urgent": 3, "crit": 2, "warn": 1}
    alerts = sorted(alerts, key=lambda a: priority.get(a.get("level", "warn"), 0), reverse=True)

    shown = alerts[:3]
    more = len(alerts) - len(shown)
    html = []
    for a in shown:
        lv = a.get("level", "warn")
        label = a.get("label") or lv.upper()
        sty = pal.get(lv, pal["warn"])
        fg, bg = sty.get("fg", "#000000"), sty.get("bg", "#FFF2CC")
        html.append(
            f'<span style="display:inline-flex;align-items:center;'
            f'padding:.12rem .5rem;border-radius:999px;'
            f'font-size:12px;font-weight:600;'
            f'color:{fg};background:{bg};'
            f'border:1px solid rgba(0,0,0,0.06);white-space:nowrap;">{label}</span>'
        )
    if more > 0:
        html.append(
            '<span style="display:inline-flex;align-items:center;'
            'padding:.12rem .5rem;border-radius:999px;'
            'font-size:12px;font-weight:600;'
            'color:#222;background:#EEE;'
            'border:1px solid rgba(0,0,0,0.06);white-space:nowrap;">'
            f'+{more}</span>'
        )
    st.markdown('<div style="display:flex;justify-content:flex-end;gap:.35rem;align-items:center;">'
                + " ".join(html) + "</div>", unsafe_allow_html=True)

def _settings_gear() -> None:
    """歯車ボタンと設定ポップオーバー（Streamlit 1.50対応）。"""
    with st.popover("⚙", use_container_width=False):
        st.markdown("#### 設定")
        st.write("設定内容は後続フェーズで作り込みます。")

def _render_header(title: str = "BtcTradeSystem V1 ダッシュボード") -> None:
    # 1行ヘッダー：左=タイトル / 中=チップ / 右=歯車（縦圧縮）
    left, mid, right = st.columns([7, 4, 1], gap="small")
    with left:
        st.markdown(f"<h3 style='margin:0;padding:0;line-height:1.0;'>{title}</h3>", unsafe_allow_html=True)
    with mid:
        alerts = st.session_state.get("_alerts", [])
        _render_alert_chips(alerts)
    with right:
        _settings_gear()

def _resolve_tab_module(tab_key: str) -> Optional[str]:
    """
    タブキーからUIモジュール名を解決。
    'main' -> 'ui_main', 'health' -> 'ui_health', 'audit' -> 'ui_audit' 等
    """
    name = f"btc_trade_system.features.dash.ui_{tab_key}"
    try:
        importlib.import_module(name)
        return name
    except Exception:
        return None

def _render_tabs() -> None:
    cfg = _load_yaml(TABS_CFG_PATH)
    order = cfg.get("order") or ["main", "health", "audit"]
    enabled = cfg.get("enabled") or {k: True for k in order}
    labels = []
    keys = []
    for k in order:
        if enabled.get(k, True):
            labels.append({"main": "メイン", "health": "コレクターの健全性", "audit": "開発監査"}.get(k, k))
            keys.append(k)

    if not keys:
        st.info("表示可能なタブがありません（tabs.yaml を確認してください）。")
        return

    tabs = st.tabs(labels)
    for i, k in enumerate(keys):
        with tabs[i]:
            mname = _resolve_tab_module(k)
            if not mname:
                st.info(f"「{k}」タブのUIは未実装です。後続フェーズで実装します。")
                continue
            try:
                mod = importlib.import_module(mname)
                render = getattr(mod, "render", None)
                if callable(render):
                    render()
                else:
                    st.info(f"{mname}.render() が見つかりません。")
            except Exception as e:
                st.error(f"{k} タブの描画に失敗しました: {e}")

def main() -> None:
    st.set_page_config(page_title="BtcTradeSystem V1", layout="wide")
    st.markdown(_css_from_basic(), unsafe_allow_html=True)
    _render_header()
    _render_tabs()

if __name__ == "__main__":
    main()
