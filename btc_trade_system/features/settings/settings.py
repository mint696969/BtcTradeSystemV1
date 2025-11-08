# path: btc_trade_system/features/settings/settings.py
# desc: 設定ハブUI（v2）— タブUIを採用。束ねタブ内のみ各 set_* 側でアコーディオン（排他展開）を実装。保存/デフォルト/閉じるは各セクション専用ボタン。

from __future__ import annotations
import streamlit as st
import importlib
from typing import List

# tabs.yaml（order / enabled / labels 等）の読込（ダッシュ側の薄い入口を再利用）
from btc_trade_system.features.dash import dashboard as dash

# dev_audit（操作ログはハブ、実保存は SVC 側で emit）
from btc_trade_system.features.audit_dev import writer as W

# 初期設定（basic）は set_dash が受け持つ
from btc_trade_system.features.settings import set_dash

# 設定ダイアログの開閉フラグ
_SETTINGS_FLAG = "__settings_open"
# 現在アクティブな設定タブ key（"basic"=初期設定）
_ACTIVE_KEY = "__settings_active_key"

# Dialog API 吸収
_DLG = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)

# ラベルのフォールバック
_LABELS = {"main": "メイン", "health": "健全性", "audit": "開発監査", "collector": "コレクター", "basic": "初期設定", "exchanges": "取引所"}

# --- モジュール解決（規約に従って探索） ---
def _resolve_settings_module(key: str) -> str | None:
    """設定セクションのモジュールを規約順で探索。未実装なら None を返す。"""
    if key == "basic":  # 初期設定は set_dash 固定
        return "btc_trade_system.features.settings.set_dash"
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

def _get_label(cfg_labels: dict, key: str) -> str:
    return (cfg_labels.get(key) or _LABELS.get(key) or key)

def _load_settings_keys() -> List[str]:
    """tabs.yaml を読み、設定セクションとして有効な key を order 順に返す（末尾に basic を固定）。"""
    cfg = dash._load_tabs_cfg()  # {order, enabled, labels?}
    keys = []
    for k in cfg["order"]:
        if not cfg["enabled"].get(k, True):
            continue
        # 設定セクションを持つものだけ（モジュール解決できたら対象）
        if _resolve_settings_module(k):
            keys.append(k)
    # 初期設定（basic）は常に最後（最右）に固定（order=200 想定）
    if "basic" not in keys:
        keys.append("basic")
    else:
        # 念のため末尾へ移動
        keys = [k for k in keys if k != "basic"] + ["basic"]
    return keys

def _discard_unsaved_for(key: str):
    """タブ切替時に key の未保存 UI 値を破棄（規約：set.<key>.* をクリア）。"""
    if not key:
        return
    dead = [k for k in st.session_state.keys() if k.startswith(f"set.{key}.")]
    for k in dead:
        st.session_state.pop(k, None)

# ===== UI: 設定ダイアログ本体（タブUI） =====
if _DLG is None:
    # Dialog 非対応ストリーム：簡易サイドバー版
    def settings_gear():
        if st.button("⚙️", use_container_width=False, key="gear_fallback"):
            W.emit("settings.open", level="INFO", feature="settings", payload={"source": "gear_fallback"})
            st.session_state[_SETTINGS_FLAG] = True
            st.session_state.setdefault(_ACTIVE_KEY, "basic")
            with st.sidebar:
                st.header("設定")
                _render_settings_body()
        elif st.session_state.get(_SETTINGS_FLAG):
            with st.sidebar:
                st.header("設定")
                _render_settings_body()
else:
    @_DLG("設定")
    def _open_settings_dialog():
        st.session_state.setdefault(_ACTIVE_KEY, "basic")
        _render_settings_body()

    def settings_gear():
        if st.button("⚙️", use_container_width=False, key="gear_dialog"):
            W.emit("settings.open", level="INFO", feature="settings", payload={"source": "gear"})
            st.session_state[_SETTINGS_FLAG] = True
            _open_settings_dialog()
        elif st.session_state.get(_SETTINGS_FLAG):
            _open_settings_dialog()

# ===== 共通本体：タブ＋アクティブ検知（切替＝未保存破棄） =====
def _render_settings_body():
    cfg = dash._load_tabs_cfg()
    cfg_labels = (cfg.get("labels") or {})
    keys = _load_settings_keys()

    # タブラベル作成
    labels = [_get_label(cfg_labels, k) for k in keys]
    tabs = st.tabs(labels)

    # 直前のアクティブキー
    prev = st.session_state.get(_ACTIVE_KEY, "basic")

    # 各タブの描画（選択されたタブのみUIが効く仕様。切替検知→他キーの未保存破棄）
    for key, tab in zip(keys, tabs):
        with tab:
            # タブ切替時（=前回と異なるタブへ入ったタイミング）に、前タブの未保存を破棄
            if key != prev and st.session_state.get(_ACTIVE_KEY) != key:
                _discard_unsaved_for(prev if prev != "basic" else "basic")
                st.session_state[_ACTIVE_KEY] = key

            # --- アクティブタブの内容 ---
            if key == "basic":
                # 初期設定セクション（set_dash 側にセクション専用ボタンを実装）
                set_dash.render()
                continue

            modname = _resolve_settings_module(key)
            if not modname:
                st.info("この機能に設定はありません。")
                continue

            try:
                mod = importlib.import_module(modname)
                render = getattr(mod, "render", None)
                if callable(render):
                    # ※ 複数機能を束ねる場合のアコーディオンは set_*.py 側で実装（ここではタブのみ）
                    render()
                else:
                    st.info(f"{modname}.render() が見つかりません。")
            except Exception as e:
                st.error(f"設定モジュールの読み込みに失敗しました: {key}\n{e}")

def settings_gear():
    # ギアは単独ボタンとして描画（列を作らない＝無駄な空白を出さない）
    if st.button("⚙️", use_container_width=False, key="gear_dialog"):
        W.emit("settings.open", level="INFO", feature="settings", payload={"source": "gear"})
        st.session_state[_SETTINGS_FLAG] = True
        _open_settings_dialog()
    elif st.session_state.get(_SETTINGS_FLAG):
        _open_settings_dialog()
