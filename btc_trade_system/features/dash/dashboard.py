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
    """
    深いマージ。ただし override が None/空文字/空dict/空list の場合は上書きしない（defaults を保持）。
    """
    if not isinstance(base, dict):
        return override if isinstance(override, dict) else {}
    out = dict(base)
    if not isinstance(override, dict):
        return out

    def _is_empty(v) -> bool:
        if v is None or v == "":
            return True
        if isinstance(v, (dict, list)) and len(v) == 0:
            return True
        return False

    for k, v in (override or {}).items():
        # 空値による“消し込み”を無効化
        if _is_empty(v):
            continue
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

    # order / tabs が空になった場合は defaults をフォールバック
    order = merged.get("order")
    if not order:
        order = base.get("order", [])

    tabs = merged.get("tabs")
    if not tabs:
        tabs = base.get("tabs", {})

    initial = order[0] if order else None
    return {"order": order, "tabs": tabs, "initial": initial}

def _clamp_dashboard_order(order: List[str]) -> List[str]:
    """
    tabs.yaml 側の定義を尊重し、ハードコード除外は行わない。
    main が含まれていれば先頭へ寄せる以外の変更はしない。
    """
    seq = list(order or [])
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

def _load_alert_palette_from_cfg(cfg_dash: dict) -> Optional[Dict[str, Dict[str, str]]]:
    """
    dash.yaml のアラート色設定から
      warn / crit / urgent の fg / bg を取り出してパレット dict を返す。

    想定スキーマ（例）:
      alert_palette:
        warn:   { fg: "#000000", bg: "#FFE4E4" }
        crit:   { fg: "#000000", bg: "#FFC0CB" }
        urgent: { fg: "#000000", bg: "#FFD700" }

    ※ キー名は alert_palette / alert_colors の両方に対応。
       必須レベル（warn/crit/urgent）が一つでも欠ける場合は None を返し、
       CSS デフォルトにフォールバックする。
    """
    if not isinstance(cfg_dash, dict):
        return None

    colors = cfg_dash.get("alert_palette") or cfg_dash.get("alert_colors") or {}
    if not isinstance(colors, dict):
        return None

    palette: Dict[str, Dict[str, str]] = {}
    for level in ("warn", "crit", "urgent"):
        lv = colors.get(level)
        if not isinstance(lv, dict):
            return None
        fg = (lv.get("fg") or lv.get("text") or lv.get("color") or "").strip()
        bg = (lv.get("bg") or lv.get("background") or lv.get("fill") or "").strip()
        if not (fg and bg):
            return None
        palette[level] = {"fg": fg, "bg": bg}

    # 3レベル揃っているときだけ有効
    if set(palette.keys()) != {"warn", "crit", "urgent"}:
        return None
    return palette

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

    # 念のため：初期化漏れに備えて prime（上流呼び出しが外れても安全）
    if "_active_dash_tab" not in st.session_state:
        _prime_active_tab()

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
    """
    ダッシュボード用UIモジュール名を返す。
    ここでは import を行わず、“名前決定”のみに責務を限定する。
    実際の import は _render_tabs() 側で1回だけ行う。
    """
    if dash_field is True:
        return f"btc_trade_system.features.dash.ui_{tab_key}"
    if isinstance(dash_field, str) and dash_field.strip():
        return f"btc_trade_system.features.dash.ui_{dash_field.strip()}"
    return None

def _prime_active_tab() -> None:
    """
    ヘッダー描画より前に、tabs.yaml と defaults から“有効タブの並び”と
    “初期タブ（または前回選択）”を決め、session_state に下記をプライムする。
      - active_tab
      - _gear_target
      - _active_dash_tab

    追加仕様：
      settings 側が st.session_state["_dash_force_main"] を True にして Close した場合、
      次回描画時は main（存在すれば）を優先選択してから通常運用へ戻す。

    注意：
      tabs.yaml で dashboard: false のタブは“物理的に非表示”とする（候補から除外）。
    """
    cfg = _load_tabs_cfg()
    order = _clamp_dashboard_order(cfg["order"])
    tabs_def = cfg["tabs"]
    initial = cfg["initial"]

    keys = []
    for k in order:
        t = tabs_def.get(k, {}) or {}
        # 有効・かつ dashboard が False でないもののみタブ候補に採用
        if not t.get("enabled", True):
            continue
        if t.get("dashboard", True) is False:
            continue
        keys.append(k)

    if not keys:
        for k in ("active_tab", "_gear_target", "_active_dash_tab"):
            st.session_state.pop(k, None)
        return

    # --- Close→Main固定の指示を一度だけ受け取る ---
    if st.session_state.pop("_dash_force_main", False):
        preferred = "main" if "main" in keys else keys[0]
    else:
        preferred = st.session_state.get("active_tab") or initial or keys[0]
        if preferred not in keys:
            preferred = keys[0]

    st.session_state["active_tab"] = preferred
    st.session_state["_gear_target"] = preferred
    st.session_state["_active_dash_tab"] = preferred

def _render_tabs() -> None:
    # タブ評価ごとにコミット済みフラグをクリア（切替時に再同期するため）
    st.session_state.pop("_dash_active_committed", None)

    cfg = _load_tabs_cfg()
    order = _clamp_dashboard_order(cfg["order"])
    tabs_def = cfg["tabs"]
    initial = cfg["initial"]

    keys, labels = [], []
    for k in order:
        t = tabs_def.get(k, {}) or {}
        # dashboard:false は“タブ自体を非表示”
        if not t.get("enabled", True):
            continue
        if t.get("dashboard", True) is False:
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

    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = keys[0]

    tabs = st.tabs(labels)

    for i, k in enumerate(keys):
        t = tabs_def.get(k, {}) 
        with tabs[i]:
            # Active tab 同期（初回タブ評価時にヘッダーへ反映）
            if st.session_state.get("_dash_active_committed") is not True:
                prev = st.session_state.get("_gear_target")
                st.session_state["_active_dash_tab"] = k
                st.session_state["active_tab"] = k
                st.session_state["_gear_target"] = k
                st.session_state["_dash_active_committed"] = True

                try:
                    W.emit("dash.tab.active", level="DEBUG", feature="dash",
                           payload={"active": k})
                except Exception:
                    pass

                if prev is not None and prev != k:
                    st.session_state["_dash_require_rerun"] = True

            # 名前解決のみ（import はここで1回だけ）
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
    title_base = _S.get_ui_title("BtcTradeSystem V1")

    # Main設定のタイトルがあればそれを最優先
    try:
        _cfg_main = _S.load_yaml("main") or {}
        _t = (_cfg_main.get("title") or "").strip()
        header_title = _t or title_base
    except Exception:
        header_title = title_base

    # dash.yaml の colors.alert_chip からアラートチップ用パレットを注入
    try:
        cfg_dash = _S.load_yaml("dash") or {}
        colors = (cfg_dash.get("colors") or {}).get("alert_chip") or {}
        palette = {}
        for level in ("warn", "crit", "urgent"):
            lv = colors.get(level) or {}
            if not isinstance(lv, dict):
                break
            fg = (lv.get("fg") or "#000000").strip()
            bg = (lv.get("bg") or "").strip()
            if not bg:
                break
            palette[level] = {"fg": fg, "bg": bg}

        # 3レベルすべて揃っているときのみ CSS 変数を上書き
        if set(palette.keys()) == {"warn", "crit", "urgent"}:
            _inject_alert_palette_vars(palette)
    except Exception:
        # 設定不備や読み込みエラー時はデフォルトCSSにフォールバック
        pass

    # 1) ページ設定（ブラウザのタブ題名）
    st.set_page_config(
        page_title=header_title,
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="⚙︎",
    )

    # ヘッダー専用CSSを注入（chipスタイル含む）
    css_path = REPO_ROOT / "btc_trade_system" / "features" / "dash" / "styles" / "dashboard_header.css"
    _load_css(css_path)

    # 2) ヘッダー描画（右側のデモアラートやギア活性もここで決まる）
    _render_header(title=f"{header_title} ダッシュボード")

    # 3) タブ描画
    _render_tabs()

    # 4) 要求時のみ軽リラン
    if st.session_state.pop("_dash_require_rerun", False):
        st.rerun()

if __name__ == "__main__":
    main()