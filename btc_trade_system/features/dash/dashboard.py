# path: btc_trade_system/features/dash/dashboard.py
# desc: ダッシュボード（ヘッダー＋タブのハブ）。tabs.yamlで並び順/有効化/初期タブを制御

from __future__ import annotations
import importlib
import pathlib
from pathlib import Path
from typing import Dict, List, Optional
import os
import yaml
import streamlit as st
from btc_trade_system.features.settings import settings_svc as settings
from btc_trade_system.features.settings import settings as settings_hub
from btc_trade_system.features.audit_dev import writer as W

# 基本設定
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
CONFIG_UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"
TABS_CFG_PATH = CONFIG_UI_DIR / "tabs.yaml"  # defaultsはローダ側で結合予定
TABS_DEF_PATH = CONFIG_UI_DIR / "tabs_def.yaml"  # 既定（*_def.yaml 命名ルール）

# ─────────────────────────────────────────────────────────────
# ユーティリティ
def _load_yaml(path: pathlib.Path) -> Dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _load_tabs_cfg() -> Dict:
    base = _load_yaml(TABS_DEF_PATH)
    cur  = _load_yaml(TABS_CFG_PATH)
    order = (cur.get("order") or base.get("order") or ["main", "health", "audit"])
    enabled = {k: True for k in order}
    enabled.update(base.get("enabled", {}))
    enabled.update(cur.get("enabled", {}))
    initial = cur.get("initial") or base.get("initial") or (order[0] if order else None)
    return {"order": order, "enabled": enabled, "initial": initial}

def _inject_tokens(toolbar_h_px: int = 32, header_h_px: int = 44,
                   tab_text_normal: str = "#000000",
                   tab_text_active: str = "#FF5722",
                   tab_text_hover: str = "#FF7F27",
                   tab_bg_inactive: str = "#F5F5F5") -> None:
    st.markdown(
        f"<style>:root{{--tb-h:{toolbar_h_px}px;--hdr-h:{header_h_px}px;"
        f"--tab-text-normal:{tab_text_normal};--tab-text-active:{tab_text_active};"
        f"--tab-text-hover:{tab_text_hover};--tab-bg-inactive:{tab_bg_inactive};}}</style>",
        unsafe_allow_html=True,
    )

def _load_css(css_path: Path) -> None:
    try:
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"CSS load failed: {css_path.name} ({e})")

def _inject_alert_palette_vars(pal: Dict[str, Dict[str, str]]) -> None:
    warn_fg = pal["warn"]["fg"]; warn_bg = pal["warn"]["bg"]
    crit_fg = pal["crit"]["fg"]; crit_bg = pal["crit"]["bg"]
    urg_fg = pal["urgent"]["fg"]; urg_bg = pal["urgent"]["bg"]
    st.markdown(
        f"<style>:root{{--chip-warn-fg:{warn_fg};--chip-warn-bg:{warn_bg};"
        f"--chip-crit-fg:{crit_fg};--chip-crit-bg:{crit_bg};"
        f"--chip-urgent-fg:{urg_fg};--chip-urgent-bg:{urg_bg};}}</style>",
        unsafe_allow_html=True,
    )

def _render_alert_chips(alerts: List[Dict]) -> None:
    if not alerts:
        return
    priority = {"urgent": 3, "crit": 2, "warn": 1}
    alerts = sorted(alerts, key=lambda a: priority.get(a.get("level", "warn"), 0), reverse=True)
    shown = alerts[:3]
    more = len(alerts) - len(shown)
    html = []
    for a in shown:
        lv = a.get("level", "warn")
        label = (a.get("label") or lv.upper())
        cls = {"warn": "chip--warn", "crit": "chip--crit", "urgent": "chip--urgent"}.get(lv, "chip--warn")
        html.append(f'<span class="chip {cls}">{label}</span>')
    if more > 0:
        html.append(f'<span class="chip chip--more">+{more}</span>')
    st.markdown('<div class="chip-row">' + " ".join(html) + "</div>", unsafe_allow_html=True)

def _render_header(title: str = "BtcTradeSystem V1 ダッシュボード") -> None:
    st.markdown("<div id='app-header-row'></div>", unsafe_allow_html=True)
    alerts: list[dict] = st.session_state.get("_alerts", [])
    has_chips: bool = bool(alerts)
    col_title, col_chips, col_gear = st.columns([9, 6, 1], gap="small")

    with col_title:
        st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)

    with col_chips:
        if has_chips:
            _render_alert_chips(alerts)
        else:
            st.markdown("<div class='chip-row chip-row--ghost'></div>", unsafe_allow_html=True)

    with col_gear:
        settings_hub.settings_gear()

def _resolve_tab_module(tab_key: str) -> Optional[str]:
    name = f"btc_trade_system.features.dash.ui_{tab_key}"
    try:
        importlib.import_module(name)
        return name
    except Exception:
        return None

def _render_tabs() -> None:
    cfg = _load_tabs_cfg()
    order = cfg["order"]
    initial = cfg["initial"]
    preferred = st.session_state.get("active_tab") or initial
    enabled = cfg["enabled"]
    keys, labels = [], []
    for k in order:
        if enabled.get(k, True):
            keys.append(k)
            labels.append({"main": "メイン", "health": "コレクターの健全性", "audit": "開発監査"}.get(k, k))
    if not keys:
        st.info("表示可能なタブがありません（tabs.yaml / tabs_def.yaml を確認してください）。")
        return
    for i, k in enumerate(keys):
        try:
            W.emit("dash.tab.register", level="INFO", feature="dash", payload={"key": k, "title": labels[i] if i < len(labels) else k})
        except Exception as e:
            st.caption(f"⚠ dash.tab.register emit failed: {e}")
    active0 = preferred
    if active0 in keys and keys[0] != active0:
        idx = keys.index(active0)
        keys = [keys[idx]] + keys[:idx] + keys[idx+1:]
        labels = [labels[idx]] + labels[:idx] + labels[idx+1:]
    tabs = st.tabs(labels)
    try:
        W.emit("dash.tab.open", level="INFO", feature="dash", payload={"key": keys[0], "title": labels[0] if labels else keys[0]})
    except Exception as e:
        st.caption(f"⚠ dash.tab.open emit failed: {e}")
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
    title_base = settings.get_ui_title("BtcTradeSystem V1")
    st.set_page_config(page_title=title_base, layout="wide", initial_sidebar_state="collapsed", page_icon="⚙︎")
    _inject_tokens(toolbar_h_px=32, header_h_px=44)
    _inject_alert_palette_vars(settings.get_alert_palette())
    styles_dir = Path(__file__).resolve().parent / "styles"
    for name in ["dashboard_header.css", "tab_main.css", "tab_health.css", "tab_audit.css", "settings.css"]:
        _load_css(styles_dir / name)
    st.session_state.setdefault("_alerts", [])
    _render_header(title=f"{title_base} ダッシュボード")
    _render_tabs()

if __name__ == "__main__":
    main()
