# path: btc_trade_system/features/settings/settings.py
# desc: 右上の歯車から開く設定モーダルの“ハブ”（タブ配列：初期設定/健全性/監査）

from __future__ import annotations
import streamlit as st
import importlib
from btc_trade_system.features.dash import dashboard as dash  # _load_tabs_cfg を使用

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

# tabs.yaml の key → 日本語ラベル
_LABELS = {"main": "メイン", "health": "健全性", "audit": "開発監査"}

def _resolve_settings_module(key: str) -> str | None:
    """
    設定UIのモジュールを命名規約で探索して最初に見つかったものを返す。
      1) features/settings/set_{key}.py  …推奨（render()/on_save()/on_default()）
      2) features/{key}/settings_ui.py   …機能内に持たせる代替
      3) features/{key}/config/settings_ui.py …将来用
    無ければ None を返す。
    """
    candidates = [
        f"btc_trade_system.features.settings.set_{key}",
        f"btc_trade_system.features.{key}.settings_ui",
        f"btc_trade_system.features.{key}.config.settings_ui",
    ]
    for name in candidates:
        try:
            importlib.import_module(name)
            return name
        except Exception:
            pass
    return None

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
        _topbar = st.container()
        st.session_state.setdefault("__settings_active_key", "init")  # keyで持つ（"init" が 200）

        # tabs.yaml を読み、ダッシュボードと同じ順序/有効化を採用＋末尾に "init" を追加
        cfg = dash._load_tabs_cfg()  # {order, enabled, initial}
        tab_keys = [k for k in cfg["order"] if cfg["enabled"].get(k, True)]
        tab_keys.append("init")  # 200: 初期設定（設定だけに出す）

        labels = [("初期設定" if k == "init" else _LABELS.get(k, k)) for k in tab_keys]
        tabs = st.tabs(labels)

        # 各タブを描画（描画されたタブがアクティブ＝ここで key を記録）
        for i, key in enumerate(tab_keys):
            with tabs[i]:
                st.session_state["__settings_active_key"] = key
                if key == "init":
                    # 初期設定 (= set_dash)
                    set_dash.render()
                    continue
                modname = _resolve_settings_module(key)
                if not modname:
                    st.info("この機能に設定はありません。")
                    continue
                mod = importlib.import_module(modname)
                render = getattr(mod, "render", None)
                if callable(render):
                    render()
                else:
                    st.info(f"{modname}.render() が見つかりません。")

        # === ここで最新のアクティブタブを確定させてから、上部ボタンを描画する ===
        # === ここで最新のアクティブタブを確定させてから、上部ボタンを描画する ===
        def _supports_default(key: str) -> bool:
            try:
                if key == "init":
                    fn = getattr(set_dash, "supports_default", None)
                    return bool(fn()) if callable(fn) else False
                if key == "health":
                    from btc_trade_system.features.settings import set_health as _h
                    fn = getattr(_h, "supports_default", None)
                    return bool(fn()) if callable(fn) else False
                # それ以外は未対応
                return False
            except Exception:
                return False

        active_key = st.session_state.get("__settings_active_key", "init")

        with _topbar:
            col_a, col_b, col_c = st.columns([1, 1, 1])

            with col_a:
                if st.button("閉じる", key="dlg_top_close", use_container_width=True):
                    W.emit("settings.close", level="INFO", feature="settings", payload={"source": "modal-top"})
                    st.session_state[_SETTINGS_FLAG] = False
                    st.rerun()

            with col_b:
                disabled = not _supports_default(active_key)
                if st.button("デフォルト", key="dlg_top_default",
                            use_container_width=True, disabled=disabled,
                            help=("このタブはデフォルト未対応です" if disabled else None)):
                    try:
                        if active_key == "init":
                            getattr(set_dash, "on_default", lambda: None)()
                        elif active_key == "health":
                            from btc_trade_system.features.settings import set_health as _h
                            getattr(_h, "on_default", lambda: None)()
                    finally:
                        st.session_state["__settings_dirty"] = True
                        st.rerun()

        with col_c:
            if st.button("保存", key="dlg_top_save", use_container_width=True):
                try:
                    if active_key == "init":
                        getattr(set_dash, "on_save", lambda: None)()
                    elif active_key == "health":
                        from btc_trade_system.features.settings import set_health as _h
                        getattr(_h, "on_save", lambda: None)()
                finally:
                    # ログ出し
                    W.emit("settings.save_click", level="INFO", feature="settings", payload={"source": "modal-top"})
                    # 可能ならその場でトースト（表示後に閉じる）
                    try:
                        st.toast("設定を保存しました", icon="✅")
                    except Exception:
                        pass
                    # モーダルを閉じてリラン
                    st.session_state["__settings_dirty"] = False   # 再オープン抑止
                    st.session_state[_SETTINGS_FLAG] = False       # モーダル閉じる
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
