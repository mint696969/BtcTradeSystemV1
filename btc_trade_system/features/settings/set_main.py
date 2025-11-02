# path: btc_trade_system/features/settings/set_main.py
# desc: 「初期設定」タブのメインUI（配色・デモアラート・保存/既定/今回のみ適用・監査出力）

from __future__ import annotations
import json
import os
from typing import Any, Callable, Tuple
from btc_trade_system.features.settings import settings_svc
from pathlib import Path
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

# --- yaml は任意（無ければ JSON で代替） ---
try:
    import yaml  # type: ignore
    def _to_text(obj: Any) -> str:
        return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    def _from_text(text: str) -> Any:
        return yaml.safe_load(text) if text.strip() else {}
except Exception:  # pragma: no cover
    def _to_text(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    def _from_text(text: str) -> Any:
        return json.loads(text) if text.strip() else {}

# --- svc_settings の API を多段で解決（settings 配下の svc を参照） ---
def _resolve_api() -> Tuple[Callable[[], Any], Callable[[Any], None]]:
    from importlib import import_module
    svc = import_module("btc_trade_system.features.settings.settings_svc")

    load_candidates = ["load_for_ui", "load", "load_monitoring", "read", "read_monitoring", "get_monitoring"]
    save_candidates = ["save_from_ui", "save", "save_monitoring", "write", "write_monitoring", "put_monitoring"]

    load_fn = next((getattr(svc, n) for n in load_candidates if callable(getattr(svc, n, None))), None)
    if load_fn is None:
        def _load_stub(): return {}
        load_fn = _load_stub

    save_fn = next((getattr(svc, n) for n in save_candidates if callable(getattr(svc, n, None))), None)
    if save_fn is None:
        def _save_stub(_obj: Any) -> None:
            raise RuntimeError("settings_svc に保存用APIが見つかりません")
        save_fn = _save_stub

    return load_fn, save_fn

def render():
    st.markdown("<div class='settings-tab'>", unsafe_allow_html=True)
    st.session_state["__settings_active_tab"] = "初期設定"

    st.subheader("設定（monitoring.yaml）")

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
        u_fg = st.color_picker("文字", use["urgent"]["fg"], key="pick_urgent_fg", label_visibility="collapsed")
        u_bg = st.color_picker("背景", use["urgent"]["bg"], key="pick_urgent_bg", label_visibility="collapsed")
    with c_crit:
        st.caption("重大")
        c_fg = st.color_picker("文字", use["crit"]["fg"], key="pick_crit_fg", label_visibility="collapsed")
        c_bg = st.color_picker("背景", use["crit"]["bg"], key="pick_crit_bg", label_visibility="collapsed")
    with c_warn:
        st.caption("注意")
        w_fg = st.color_picker("文字", use["warn"]["fg"], key="pick_warn_fg", label_visibility="collapsed")
        w_bg = st.color_picker("背景", use["warn"]["bg"], key="pick_warn_bg", label_visibility="collapsed")

    # ボタン操作は上部（ハブ）に集約しました
    st.caption("操作は上部の『デフォルト／保存』ボタンをご利用ください。")

    st.markdown("</div>", unsafe_allow_html=True)

# ---- ハブ(settings.py)からディスパッチされる公開フック ----
def supports_default() -> bool:
    """
    このタブが「デフォルトに戻す」に対応しているかを返す。
    dash_def.yaml（将来: main_def.yaml）の存在で判定。無ければ従来の exists/load_yaml でも可。
    """

    try:
        from btc_trade_system.features.settings import settings_svc
        # まずは明示パス（DASH_DEF_PATH）があればそれを優先
        p = getattr(settings_svc, "DASH_DEF_PATH", None)
        if getattr(p, "exists", lambda: False)():
            return True

        # 後方互換（exists / load_yaml）
        exists = getattr(settings_svc, "exists", None)
        if callable(exists) and (exists("dash_def.yaml") or exists("main_def.yaml")):
            return True

        load = getattr(settings_svc, "load_yaml", None)
        if callable(load) and (load("dash_def.yaml") or load("main_def.yaml")):
            return True
    except Exception:
        pass
    return False

def on_default() -> None:
    """
    デフォルト（開いているタブのみ適用）：
      - 定義済みなら _reset_session_palette() を使って配色を既定に戻す
      - その後 dirty/toast を積んでヘッダーへ即反映
    """
    import streamlit as st
    try:
        # set_main.py 内にある既存のヘルパーが優先
        _reset = globals().get("_reset_session_palette")
        if callable(_reset):
            _reset()
        else:
            # 最低限のフォールバック：配色ピッカーのセッションキーを消す
            for k in list(st.session_state.keys()):
                if str(k).startswith("pick_"):
                    st.session_state.pop(k, None)
        st.session_state["__settings_dirty"] = True
        st.session_state["__toast"] = ("初期設定（配色）を既定に戻しました", None)
    except Exception as e:
        st.session_state["__toast"] = (f"初期化に失敗しました: {e}", "⚠️")

def on_save() -> None:
    """
    保存（開いているタブのみ適用）：
      - 現在のピッカー値を dash.yaml に永続化（サービスI/F経由）
      - 保存後 dirty/toast を積んでヘッダーへ即反映
    """

    import streamlit as st
    try:
        from btc_trade_system.features.settings import settings_svc

        # ピッカーの現在値（キー名は現状の set_main.py に合わせる）
        def _norm_hex(s: str, default: str) -> str:
            if not isinstance(s, str) or not s.startswith("#") or len(s) not in (4, 7):
                return default
            return s.upper()

        pal_save = {
            "urgent": {
                "fg": _norm_hex(st.session_state.get("pick_urgent_fg", "#FFFFFF"), "#FFFFFF"),
                "bg": _norm_hex(st.session_state.get("pick_urgent_bg", "#FF6B6B"), "#FF6B6B"),
            },
            "crit": {
                "fg": _norm_hex(st.session_state.get("pick_crit_fg", "#FFFFFF"), "#FFFFFF"),
                "bg": _norm_hex(st.session_state.get("pick_crit_bg", "#F9C8C8"), "#F9C8C8"),
            },
            "warn": {
                "fg": _norm_hex(st.session_state.get("pick_warn_fg", "#000000"), "#000000"),
                "bg": _norm_hex(st.session_state.get("pick_warn_bg", "#FDE8C8"), "#FDE8C8"),
            },
        }

        # 公開I/Fで保存（原子的置換は settings_svc 側に委譲）
        ok = False
        save = getattr(settings_svc, "save_palette", None)
        if callable(save):
            ok = bool(save(pal_save))
        else:
            # 後方互換フォールバック（もし別名が用意されている場合だけ呼ぶ）
            write = getattr(settings_svc, "write_palette", None)
            if callable(write):
                ok = bool(write(pal_save))

        if ok:
            # 一時上書きをクリアし、次描画でファイル値をそのまま反映
            st.session_state["_alerts_palette_overrides"] = {}
            try:
                from btc_trade_system.features.audit_dev import writer as W
                W.emit("settings.save_click", level="INFO", feature="settings",
                       payload={"file": "dash.yaml", "keys": ["alert_palette"], "source": "modal-top"})
            except Exception:
                pass
            st.session_state["__settings_dirty"] = True
            st.session_state["__toast"] = ("保存しました（dash.yaml に反映）", None)

        else:
            st.session_state["__toast"] = ("保存に失敗しました（save_palette が未提供）", None)

    except Exception as e:
        st.session_state["__toast"] = (f"保存に失敗しました: {e}", None)
