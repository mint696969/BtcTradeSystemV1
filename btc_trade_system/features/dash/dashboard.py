# path: btc_trade_system/features/dash/dashboard.py
# desc: ダッシュボード（ヘッダー＋タブのハブ）。tabs.yamlで並び順/有効化/初期タブを制御

from __future__ import annotations
import importlib
import pathlib
from pathlib import Path
import os
from typing import Dict, List, Optional
import yaml
import streamlit as st
from btc_trade_system.features.settings import settings_svc as settings
from btc_trade_system.features.settings import settings as settings_hub
from btc_trade_system.features.audit_dev import writer as W
from btc_trade_system.features.settings import settings_svc as _S  # demo_alerts設定反映用

# 基本設定
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

def _config_dir() -> pathlib.Path:
    env = os.environ.get("BTC_TS_CONFIG_DIR")
    if env:
        p = pathlib.Path(env)
        p.mkdir(parents=True, exist_ok=True)
        return p
    p = REPO_ROOT / "btc_trade_system" / "config"
    p.mkdir(parents=True, exist_ok=True)
    return p

TABS_DEF_PATH = REPO_ROOT / "btc_trade_system" / "features" / "dash" / "config" / "tabs_def.yaml"
TABS_CFG_PATH = _config_dir() / "tabs.yaml"

def _load_yaml(path: pathlib.Path) -> Dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _deep_merge(base: dict, override: dict) -> dict:
    if not isinstance(base, dict):
        return override if isinstance(override, dict) else {}
    out = dict(base)
    for k, v in (override or {}).items():
        bv = out.get(k)
        if isinstance(bv, dict) and isinstance(v, dict):
            out[k] = _deep_merge(bv, v)
        else:
            out[k] = v
    return out

def _filter_by_schema(data: dict, schema: dict) -> dict:
    if not isinstance(data, dict) or not isinstance(schema, dict):
        return {}
    out = {}
    for k, v in (data or {}).items():
        if k not in schema:
            continue
        sv = schema[k]
        if isinstance(v, dict) and isinstance(sv, dict):
            sub = _filter_by_schema(v, sv)
            if sub:
                out[k] = sub
        else:
            out[k] = v
    return out

def _load_tabs_cfg() -> Dict:
    base = _load_yaml(TABS_DEF_PATH) or {}
    cur  = _load_yaml(TABS_CFG_PATH) or {}
    cur = _filter_by_schema(cur, base)
    merged = _deep_merge(base, cur)
    order = merged.get("order") or []
    tabs  = merged.get("tabs") or {}
    initial = order[0] if order else None
    return {"order": order, "tabs": tabs, "initial": initial}

def _clamp_dashboard_order(order: List[str]) -> List[str]:
    seq = [k for k in order if k not in ("collector", "basic")]
    if "main" in seq:
        seq = ["main"] + [k for k in seq if k != "main"]
    return seq

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

def _demo_default_items() -> list[dict]:
    return [
        {"level": "urgent", "label": "緊急Y"},
        {"level": "crit",   "label": "重大X"},
        {"level": "warn",   "label": "注意A"},
        {"level": "more",   "label": "+1"},
    ]

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

    cfg_dash = _S.load_yaml("dash")
    demo = (cfg_dash.get("demo_alerts") or {})
    if bool(demo.get("enabled", False)):
        alerts = demo.get("items") if isinstance(demo.get("items"), list) else _demo_default_items()
    else:
        alerts = []

    active_key: Optional[str] = st.session_state.get("_active_dash_tab")
    col_title, col_chips, col_gear = st.columns([9, 6, 1], gap="small")

    with col_title:
        st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)

    with col_chips:
        if alerts:
            _render_alert_chips(alerts)
        else:
            st.markdown("<div class='chip-row chip-row--ghost'></div>", unsafe_allow_html=True)

    with col_gear:
        if active_key:
            st.session_state["active_tab"] = active_key
            st.session_state["_gear_target"] = active_key
        settings_hub.settings_gear()

def _resolve_tab_module(tab_key: str, dash_field) -> Optional[str]:
    if dash_field is True:
        name = f"btc_trade_system.features.dash.ui_{tab_key}"
    elif isinstance(dash_field, str) and dash_field.strip():
        name = f"btc_trade_system.features.dash.ui_{dash_field.strip()}"
    else:
        return None
    try:
        importlib.import_module(name)
        return name
    except Exception:
        return None

def _render_tabs() -> None:
    cfg = _load_tabs_cfg()
    order = _clamp_dashboard_order(cfg["order"])
    tabs_def = cfg["tabs"]
    initial = cfg["initial"]

    keys, labels = [], []
    for k in order:
        t = tabs_def.get(k, {})
        if not t or not t.get("enabled", True):
            continue
        keys.append(k)
        labels.append(t.get("title_dash") or k)

    if not keys:
        st.info("表示可能なタブがありません（tabs.yaml / tabs_def.yaml を確認してください）。")
        return

    preferred = st.session_state.get("active_tab") or initial
    if preferred in keys and keys[0] != preferred:
        idx = keys.index(preferred)
        keys = [keys[idx]] + keys[:idx] + keys[idx+1:]
        labels = [labels[idx]] + labels[:idx] + labels[idx+1:]

    st.session_state["_active_dash_tab"] = keys[0]
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = keys[0]

    tabs = st.tabs(labels)
    try:
        W.emit("dash.tab.open", level="INFO", feature="dash", payload={"key": keys[0], "title": labels[0] if labels else keys[0]})
    except Exception:
        pass

    for i, k in enumerate(keys):
        with tabs[i]:
            t = tabs_def.get(k, {})
            mname = _resolve_tab_module(k, t.get("dashboard", True))
            if not mname:
                st.info(f"「{k}」タブのUIは未実装です（ui_* を確認）。")
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
    for name in ["dashboard_header.css", "tab_main.css", "tab_health.css", "tab_audit_dev.css", "settings.css"]:
        _load_css(styles_dir / name)

    _render_header(title=f"{title_base} ダッシュボード")
    _render_tabs()

    if st.session_state.pop("_dash_require_rerun", False):
        st.experimental_rerun()

if __name__ == "__main__":
    main()