# path: btc_trade_system/features/settings/settings.py
# desc: 右上の歯車から開く設定モーダルの“ハブ”（タブ配列：初期設定/健全性/監査）

from __future__ import annotations
import streamlit as st

# dev_audit へ設定操作を記録
from btc_trade_system.features.audit_dev import writer as W

# 設定ダイアログの開閉状態（セッション専用・永続化なし）
_SETTINGS_FLAG = "__settings_open"

# 健全性タブ（説明・監視系UI）
from btc_trade_system.features.settings import set_health as settings_tab
# 初期設定タブ（配色・デモアラート・保存/既定/今回のみ適用）
from btc_trade_system.features.settings import set_dash

# Streamlit の dialog API（正式 or experimental）を吸収
_DLG = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)

def _safe_toast(msg: str, icon):
    """Streamlit の絵文字検証に引っかからないように常に安全表示"""
    try:
        # 1文字の絵文字以外は icon を使わない
        if isinstance(icon, str) and len(icon) == 1:
            st.toast(msg, icon=icon)
        else:
            st.toast(msg)
    except Exception:
        # 保険（まれに icon 判定をすり抜けた場合でも落とさない）
        try:
            st.toast(msg)
        except Exception:
            pass

if _DLG is None:
    # 古いStreamlitの場合のフォールバック（サイドバー）
    def settings_gear():
        # 単独ボタン。列を作らない
        if st.button("⚙️", use_container_width=False, key="gear_fallback"):
            st.session_state[_SETTINGS_FLAG] = True
            W.emit("settings.open", level="INFO", feature="settings", payload={"source": "gear_fallback"})
            st.sidebar.header("設定")
            tabs = st.sidebar.tabs(["初期設定", "健全性", "監査"])
            with tabs[0]:
                set_dash.render()
            with tabs[1]:
                settings_tab.render()
            with tabs[2]:
                st.subheader("監査（将来）")
                st.write("・監査ログの保存期間、サイズ上限、サンプリング等")
            if st.sidebar.button("保存", key="settings_save_fallback"):
                W.emit("settings.save_click", level="INFO", feature="settings", payload={"source": "sidebar"})
                st.sidebar.success("設定を保存しました")

else:
    # ダイアログ本体
    @_DLG("設定")
    def _open_settings_dialog():
        # --- 上部ボタン（あとで“最新タブ”を見て描画するためのプレースホルダ） ---
        _topbar = st.container()  # ここに後段でボタンを描画する
        st.session_state.setdefault("__settings_active_tab", "初期設定")

        # タブ順：先頭＝初期設定（ここで配色ピッカーを表示）
        tabs = st.tabs(["初期設定", "健全性", "監査"])

        # --- 初期設定：配色ピッカー ---
        with tabs[0]:
            st.session_state["__settings_active_tab"] = "初期設定"
            set_dash.render()

        # --- 健全性（説明・監視系UI） ---
        with tabs[1]:
            # アクティブ判定は上部ボタンでは使わない（上書きしない）
            settings_tab.render()

        # --- 監査（将来拡張） ---
        with tabs[2]:
            # アクティブ判定は上部ボタンでは使わない（上書きしない）
            st.subheader("監査（将来）")
            st.write("・監査ログの保存期間、サイズ上限、サンプリング等")

        # === ここで最新のアクティブタブを確定させてから、上部ボタンを描画する ===
        def _supports_default(tab_key: str) -> bool:
            # タブごとに“デフォルト対応”を問い合わせ（未実装なら False）
            if tab_key == "初期設定":
                from btc_trade_system.features.settings import set_dash as _m
                fn = getattr(_m, "supports_default", None)

                try:
                    return bool(fn()) if callable(fn) else False
                except Exception:
                    return False
            if tab_key == "健全性":
                from btc_trade_system.features.settings import set_health as _h
                fn = getattr(_h, "supports_default", None)
                try:
                    return bool(fn()) if callable(fn) else False
                except Exception:
                    return False
            return False  # 監査ほか未対応

        active_key = st.session_state.get("__settings_active_tab", "初期設定")

        with _topbar:
            col_a, col_b, col_c = st.columns([1, 1, 1])

            with col_a:
                if st.button("閉じる", key="dlg_top_close", use_container_width=True):
                    W.emit("settings.close", level="INFO", feature="settings", payload={"source": "modal-top"})
                    st.session_state[_SETTINGS_FLAG] = False
                    st.rerun()

            with col_b:
                disabled = not _supports_default(active_key)
                if st.button(
                    "デフォルト", key="dlg_top_default",
                    use_container_width=True, disabled=disabled,
                    help=("このタブはデフォルト未対応です" if disabled else None),
                ):
                    if active_key == "初期設定":
                        from btc_trade_system.features.settings import set_dash as _m
                        getattr(_m, "on_default", lambda: None)()

                    elif active_key == "健全性":
                        from btc_trade_system.features.settings import set_health as _h
                        getattr(_h, "on_default", lambda: None)()
                    st.session_state["__settings_dirty"] = True
                    st.rerun()

            with col_c:
                if st.button("保存", key="dlg_top_save", use_container_width=True):
                    if active_key == "初期設定":
                        from btc_trade_system.features.settings import set_dash as _m
                        getattr(_m, "on_save", lambda: None)()

                    elif active_key == "健全性":
                        from btc_trade_system.features.settings import set_health as _h
                        getattr(_h, "on_save", lambda: None)()
                    W.emit("settings.save_click", level="INFO", feature="settings", payload={"source": "modal-top"})
                    st.session_state["__settings_dirty"] = True
                    # 保存後もモーダルは開いたまま。即時反映は下の rerun 分岐で
                    st.rerun()

        # 設定UIで変更があったら即反映（ダイアログを開いたまま rerun）
        if st.session_state.get("__settings_dirty"):
            st.session_state[_SETTINGS_FLAG] = True
            st.session_state["__settings_dirty"] = False
            st.rerun()

        # on_change コールバックで積んだ遅延toastを通常レンダで表示
        t = st.session_state.pop("__toast", None)
        if t:
            msg, icon = t
            _safe_toast(msg, icon)

def settings_gear():
    # ギアは単独ボタンとして描画（列を作らない＝無駄な空白を出さない）
    if st.button("⚙️", use_container_width=False, key="gear_dialog"):
        W.emit("settings.open", level="INFO", feature="settings", payload={"source": "gear"})
        st.session_state[_SETTINGS_FLAG] = True
        _open_settings_dialog()
    elif st.session_state.get(_SETTINGS_FLAG):
        _open_settings_dialog()
