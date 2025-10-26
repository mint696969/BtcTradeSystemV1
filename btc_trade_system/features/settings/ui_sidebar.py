# path: ./btc_trade_system/features/settings/ui_sidebar.py
# desc: 設定サイドバー（最小実装）：basic.yaml / tabs.yaml を読み書き。HEXカラーはテキストで簡易入力。

from __future__ import annotations

import pathlib, datetime, shutil
import streamlit as st
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]  # repo root 推定: btc_trade_system/features/settings/ から3つ上
CFG_DIR = ROOT / "btc_trade_system" / "config" / "ui"
BASIC_YAML = CFG_DIR / "basic.yaml"
TABS_YAML = CFG_DIR / "tabs.yaml"
TMP_DIR = ROOT / "tmp" / "settings_bak"
TMP_DIR.mkdir(parents=True, exist_ok=True)

def _load_yaml(p: pathlib.Path) -> dict:
    try:
        with p.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.warning(f"設定の読み込みに失敗: {p.name} / {e}")
        return {}

def _save_yaml(p: pathlib.Path, data: dict) -> None:
    # 退避（タイムスタンプでユニーク化）
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(p, TMP_DIR / f"{p.name}.{ts}.bak")
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def open_sidebar() -> None:
    """右サイドバーに最小の設定UIを表示。保存で YAML を直書き反映。"""
    with st.sidebar:
        st.markdown("### 設定")
        st.caption("※ シンプルな編集用。HEXカラーは `#RRGGBB` を直接入力。")

        # ---- basic.yaml ----
        basic = _load_yaml(BASIC_YAML)
        colors = basic.get("colors", {}) or {}
        tab = colors.get("tab", {}) or {}
        chip = colors.get("alert_chip", {}) or {}

        st.markdown("#### 基本設定（basic.yaml）")

        # 言語/時間
        lang = st.selectbox("言語", ["ja", "en"], index=(0 if (basic.get("language") or "ja") == "ja" else 1))
        time_cfg = basic.get("time", {}) or {}
        fmt = st.selectbox("時間フォーマット", ["24h", "ampm"], index=(0 if (time_cfg.get("format") or "24h") == "24h" else 1))
        disp = st.text_input("表示形式", value=time_cfg.get("display") or "HH:MM:SS")

        st.markdown("##### タブの文字色（HEX）")
        t_normal = st.text_input("非選択", value=tab.get("text_normal") or "#000000")
        t_active = st.text_input("選択中", value=tab.get("text_active") or "#FF5722")
        t_hover  = st.text_input("ホバー", value=tab.get("text_hover")  or "#FF7F27")

        st.markdown("##### アラート・チップ（HEX）")
        def _chip_pair(section: str, default_fg: str, default_bg: str):
            s = chip.get(section, {}) or {}
            fg = st.text_input(f"{section} 前景色", value=s.get("fg") or default_fg, key=f"{section}_fg")
            bg = st.text_input(f"{section} 背景色", value=s.get("bg") or default_bg, key=f"{section}_bg")
            return fg, bg

        warn_fg, warn_bg = _chip_pair("warn",   "#000000", "#FFF2CC")
        crit_fg, crit_bg = _chip_pair("crit",   "#FFFFFF", "#FFCCCC")
        urg_fg,  urg_bg  = _chip_pair("urgent", "#FFFFFF", "#FF6666")

        st.divider()

        # ---- tabs.yaml ----
        tabs = _load_yaml(TABS_YAML)
        st.markdown("#### タブ設定（tabs.yaml）")
        order = tabs.get("order") or ["main", "health", "audit"]
        enabled = tabs.get("enabled") or {"main": True, "health": True, "audit": True}
        initial = tabs.get("initial") or "main"

        st.caption("※ 並び順は設定ファイルで管理（UIからの順序変更は現状非対応）")
        st.text_input("表示順（参考）", value=", ".join(order), disabled=True)
        e_main = st.checkbox("main を表示", value=bool(enabled.get("main", True)))
        e_health = st.checkbox("health を表示", value=bool(enabled.get("health", True)))
        e_audit = st.checkbox("audit を表示", value=bool(enabled.get("audit", True)))
        init = st.selectbox("初期タブ", options=order, index=max(0, order.index(initial) if initial in order else 0))

        # ---- 保存ボタン ----
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("保存", type="primary", use_container_width=True):
                # basic.yaml 反映
                basic["language"] = lang
                basic["time"] = {"format": fmt, "display": disp}
                basic.setdefault("colors", {})
                basic["colors"].setdefault("tab", {})
                basic["colors"]["tab"].update({
                    "text_normal": t_normal, "text_active": t_active, "text_hover": t_hover
                })
                basic["colors"].setdefault("alert_chip", {})
                basic["colors"]["alert_chip"]["warn"]   = {"fg": warn_fg, "bg": warn_bg}
                basic["colors"]["alert_chip"]["crit"]   = {"fg": crit_fg,  "bg": crit_bg}
                basic["colors"]["alert_chip"]["urgent"] = {"fg": urg_fg,   "bg": urg_bg}
                _save_yaml(BASIC_YAML, basic)
                # tabs.yaml 反映（順序は据え置き、表示フラグと初期タブのみ）
                tabs["enabled"] = {"main": e_main, "health": e_health, "audit": e_audit}
                tabs["initial"] = init
                _save_yaml(TABS_YAML, tabs)
                st.success("保存しました（YAML に反映）。必要なら手動で再読み込みしてください。")

        with col2:
            if st.button("閉じる", use_container_width=True):
                st.session_state["settings_open"] = False
                st.rerun()
