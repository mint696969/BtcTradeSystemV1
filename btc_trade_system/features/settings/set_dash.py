# path: btc_trade_system/features/settings/set_dash.py
# desc: 「初期設定」タブのメインUI（配色・デモアラート・保存/既定/今回のみ適用・監査出力）

from __future__ import annotations
from typing import Any
from btc_trade_system.features.settings import settings_svc
from btc_trade_system.features.settings import ui_common as UI

# dev_audit 記録
from btc_trade_system.features.audit_dev import writer as W

# --- streamlit（無ければダミーで崩れないように） ---
try:
    import streamlit as st
except Exception:  # pragma: no cover
    import types as _t
    st = _t.SimpleNamespace(
        subheader=print, text_area=lambda *a, **k: "", button=lambda *a, **k: False,
        success=print, warning=print, error=print, info=print, caption=print, columns=lambda *a, **k: [None, None],
        write=print, checkbox=lambda *a, **k: False, color_picker=lambda *a, **k: "#000000", toast=print,
        divider=lambda *a, **k: None, markdown=print, selectbox=lambda *a, **k: None, rerun=lambda: None,
        metric=lambda *a, **k: None
    )

def _norm_hex(c: str, fallback: str) -> str:
    """#RRGGBB に正規化（失敗時は fallback）"""
    if isinstance(c, str):
        c = c.strip()
        if len(c) == 7 and c.startswith("#"):
            try:
                int(c[1:], 16)
                return c.upper()
            except Exception:
                pass
    return fallback

def _get_session_palette() -> dict:
    pal = (st.session_state.get("_alerts_palette_overrides") or {}) if hasattr(st, "session_state") else {}
    return pal if isinstance(pal, dict) else {}

def _apply_session_palette(new_pal: dict) -> None:
    # サービス層に委譲（内部で _alerts_palette_overrides を設定）
    settings_svc.apply_palette_once(new_pal)
    W.emit("settings.apply_once", level="INFO", feature="settings", payload={"overrides": new_pal})
    st.toast("アラート色を今回のセッションに適用しました", icon=None)

def _reset_session_palette() -> None:
    # サービス層に委譲（既定値を読み直してセッション上書きを解除）
    settings_svc.reset_palette_to_default()
    W.emit("settings.restore_default", level="INFO", feature="settings", payload={})
    # 絵文字不正で落ちないよう icon=None
    st.toast("アラート色を既定に戻しました（セッション適用解除）", icon=None)

def _toggle_demo_alerts():
    """デモアラートの投入/解除（即時反映は settings.py 側の dirty 監視で行う）"""
    if st.session_state.get("demo_alerts"):
        st.session_state["_alerts"] = [
            {"level": "urgent", "label": "緊急Y"},
            {"level": "crit",   "label": "重大X"},
            {"level": "warn",   "label": "注意A"},
            {"level": "more",   "label": "+1"},
        ]
        W.emit("settings.demo_alerts.enable", level="INFO", feature="settings", payload={"count": 4})
        # toast は“遅延表示”へ
        st.session_state["__toast"] = ("デモアラートを表示しました", None)
    else:
        st.session_state["_alerts"] = []
        W.emit("settings.demo_alerts.disable", level="INFO", feature="settings", payload={})
        # toast は“遅延表示”へ
        st.session_state["__toast"] = ("デモアラートを非表示にしました", None)

    # UI表示はせず、dirtyフラグだけ立てて settings.py に rerun を任せる
    st.session_state["__settings_dirty"] = True

def _exec_default():
    settings_svc.reset_to_default("dash")
    st.session_state["_alerts_palette_overrides"] = {}

def _exec_save():
    pal_save = {
        "urgent": {
            "fg": _norm_hex(st.session_state.get("set.basic.pick.urgent.fg", "#FFFFFF"), "#FFFFFF"),
            "bg": _norm_hex(st.session_state.get("set.basic.pick.urgent.bg", "#FF6B6B"), "#FF6B6B"),
        },
        "crit": {
            "fg": _norm_hex(st.session_state.get("set.basic.pick.crit.fg", "#FFFFFF"), "#FFFFFF"),
            "bg": _norm_hex(st.session_state.get("set.basic.pick.crit.bg", "#F9C8C8"), "#F9C8C8"),
        },
        "warn": {
            "fg": _norm_hex(st.session_state.get("set.basic.pick.warn.fg", "#000000"), "#000000"),
            "bg": _norm_hex(st.session_state.get("set.basic.pick.warn.bg", "#FDE8C8"), "#FDE8C8"),
        },
    }
    ok = bool(getattr(settings_svc, "save_palette")(pal_save))
    if not ok:
        st.error("保存に失敗しました（save_palette が未提供）")

def render():
    st.markdown("<div class='settings-tab'>", unsafe_allow_html=True)
    st.session_state["__settings_active_tab"] = "初期設定"

    st.subheader("初期設定（dash.yaml）")

    # ---- デモアラート投入（ヘッダーの表示確認用） ----
    st.divider()

    # on_change で即時反映トリガ（実処理は _toggle_demo_alerts → dirty フラグで rerun）
    st.checkbox(
        "デモアラートを投入",
        key="demo_alerts",
        on_change=_toggle_demo_alerts,
    )

    st.caption("※ ヘッダー右のチップ表示・配置の確認用途。保存は行いません。")

    # ---- アラート色（今回のみ適用） ----
    st.subheader("アラート色（今回のみ適用）")

    # サービスから「def → current → session override」を合成した最終配色を取得
    pal_eff = settings_svc.get_alert_palette()
    use = {
        k: {
            "fg": _norm_hex((pal_eff.get(k, {}) or {}).get("fg", "#000000"), "#000000"),
            "bg": _norm_hex((pal_eff.get(k, {}) or {}).get("bg", "#F5F5F5"), "#F5F5F5"),
        }
        for k in ["urgent", "crit", "warn"]
    }

    c_urgent, c_crit, c_warn = st.columns(3)
    with c_urgent:
        st.caption("緊急")
        u_fg = st.color_picker("文字", use["urgent"]["fg"], key="set.basic.pick.urgent.fg", label_visibility="collapsed")
        u_bg = st.color_picker("背景", use["urgent"]["bg"], key="set.basic.pick.urgent.bg", label_visibility="collapsed")
    with c_crit:
        st.caption("重大")
        c_fg = st.color_picker("文字", use["crit"]["fg"], key="set.basic.pick.crit.fg", label_visibility="collapsed")
        c_bg = st.color_picker("背景", use["crit"]["bg"], key="set.basic.pick.crit.bg", label_visibility="collapsed")
    with c_warn:
        st.caption("注意")
        w_fg = st.color_picker("文字", use["warn"]["fg"], key="set.basic.pick.warn.fg", label_visibility="collapsed")
        w_bg = st.color_picker("背景", use["warn"]["bg"], key="set.basic.pick.warn.bg", label_visibility="collapsed")

    # ボタン操作は上部（ハブ）に集約しました
    st.caption("操作は下部の『デフォルト／保存／閉じる』ボタンをご利用ください。")

    # === セクション専用ボタン（閉じる／デフォルト／保存） ===
    UI.render_section_controls(
        prefix="set.basic",
        on_default=_exec_default,
        on_save=_exec_save,
        key_base="set.basic.btn",
        labels=("閉じる","デフォルト","保存"),
        confirm_message="初期設定を更新します。よろしいですか？"
    )

    st.markdown("</div>", unsafe_allow_html=True)
