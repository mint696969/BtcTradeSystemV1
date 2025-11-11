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
_LABELS = {"main": "メイン", "health": "健全性", "audit_dev": "開発監査", "collector": "コレクター", "basic": "初期設定", "exchanges": "取引所"}
def _has_settings(key: str) -> bool:
    """当該ダッシュキーの設定UIが存在するか（basicは常にTrue）。"""
    if key == "basic":
        return True
    target = _get_settings_target_key(key)
    if not target:
        return False
    return _resolve_settings_module(target) is not None

def _closed_then_discard_if_needed() -> None:
    """
    直近で開いていたが現在は閉じている（=外側クリック or タブ遷移）と判断できる場合、
    未保存UI値（set.*.*）を破棄する。
    """
    prev = bool(st.session_state.get("__settings_prev_open"))
    cur  = bool(st.session_state.get("__settings_open"))
    if prev and not cur:
        _discard_all_pending()
    # 次回比較用に保存
    st.session_state["__settings_prev_open"] = cur

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

def _get_settings_target_key(dash_key: str) -> str | None:
    """
    tabs.yaml の定義を尊重して、設定セクションの“実ターゲットkey”を返す。
      - settings: true       → dash_key（= set_<dash_key>.py）
      - settings: "<alias>"  → alias    （= set_<alias>.py）
      - settings: false/未定 → None
    """
    cfg = dash._load_tabs_cfg()
    t = (cfg.get("tabs") or {}).get(dash_key) or {}
    s = t.get("settings", False)
    if s is True:
        return dash_key
    if isinstance(s, str) and s.strip():
        return s.strip()
    return None

def _get_label_from_tabs(tabs_def: dict, key: str) -> str:
    t = tabs_def.get(key) or {}
    # 設定タブの表示名は title_set を優先、なければ title_dash、その次に既定ラベル/キー
    return t.get("title_set") or t.get("title_dash") or _LABELS.get(key) or key

def _load_settings_keys() -> List[str]:
    """
    tabs.yaml 準拠で“設定を持つ”キーを order 順に返す。
    dashboard._load_tabs_cfg() の戻り値は { order: [...], tabs: {key: {...}}, initial }。
    """
    cfg = dash._load_tabs_cfg()
    order = cfg.get("order") or []
    tabs_def = cfg.get("tabs") or {}
    keys: List[str] = []

    for k in order:
        t = tabs_def.get(k) or {}
        s = t.get("settings", False)
        # settings: true → set_<k>.py、文字列 → set_<name>.py
        target = k if s is True else (s.strip() if isinstance(s, str) and s.strip() else None)
        if not target:
            continue
        has_module = _resolve_settings_module(target) is not None
        if has_module:
            keys.append(k)

    # 初期設定（basic）は常に最後へ
    if "basic" not in keys:
        keys.append("basic")
    else:
        keys = [x for x in keys if x != "basic"] + ["basic"]
    return keys

def _discard_unsaved_for(key: str):
    """タブ切替時に key の未保存 UI 値を破棄（規約：set.<key>.* をクリア）。"""
    if not key:
        return
    dead = [k for k in st.session_state.keys() if k.startswith(f"set.{key}.")]
    for k in dead:
        st.session_state.pop(k, None)

def _discard_all_pending():
    """全設定セクションの未保存UI値（set.*.*）を破棄する。"""
    dead = [k for k in st.session_state.keys() if k.startswith("set.")]
    for k in dead:
        st.session_state.pop(k, None)

def _get_header_alert_active() -> bool:
    """
    ダッシュボードのヘッダーにアラートが出ているかを安全に参照。
    dash 側に get_header_alert_active() が無ければ False。
    """
    fn = getattr(dash, "get_header_alert_active", None)
    try:
        return bool(fn()) if callable(fn) else False
    except Exception:
        return False

# ===== UI: 設定ダイアログ本体（タブUI） =====
if _DLG is None:
    # Dialog 非対応ストリーム：簡易サイドバー版
    def settings_gear():
        _closed_then_discard_if_needed()

        target_key: str = st.session_state.get("_gear_target") or "dash"
        eff_key = _get_settings_target_key(target_key)
        disabled = (eff_key is None) or (not _has_settings(target_key))

        clicked = st.button("⚙️", use_container_width=False, key="gear_fallback", disabled=disabled)
        if not clicked:
            return
        if disabled:
            st.toast("このタブには設定がありません", icon="⚠️")
            return

        _discard_all_pending()
        st.session_state.pop("__toast", None)
        st.session_state.pop("__settings_error", None)
        st.session_state["set.basic.demo_alert_default"] = _get_header_alert_active()
        W.emit("settings.open", level="INFO", feature="settings", payload={"source": "gear_fallback"})
        st.session_state[_SETTINGS_FLAG] = True
        st.session_state["__settings_open"] = True
        # eff_key を優先
        st.session_state.setdefault(_ACTIVE_KEY, eff_key if eff_key else "basic")

        with st.sidebar:
            st.header("設定")
            _render_settings_body()

else:
    @_DLG("設定")
    def _open_settings_dialog():
        st.session_state.setdefault(_ACTIVE_KEY, "basic")
        _render_settings_body()

# Dialog 環境にのみ定義（_DLG が無い場合は、前段の fallback 定義を温存）
if _DLG is not None:
    def settings_gear():
        # 直前が open で今は閉じている場合の残骸破棄（外側クリック・タブ遷移検知）
        _closed_then_discard_if_needed()

        target_key: str = st.session_state.get("_gear_target") or "dash"
        eff_key = _get_settings_target_key(target_key)
        disabled = (eff_key is None) or (not _has_settings(target_key))

        clicked = st.button("⚙️", use_container_width=False, key="gear_dialog", disabled=disabled)

        if not clicked:
            return
        if disabled:
            st.toast("このタブには設定がありません", icon="⚠️")
            return

        _discard_all_pending()
        st.session_state["set.basic.demo_alert_default"] = _get_header_alert_active()

        st.session_state[_SETTINGS_FLAG] = False
        st.session_state["__settings_open"] = False
        st.session_state[_SETTINGS_FLAG] = True
        st.session_state["__settings_open"] = True
        # 初期アクティブは解決後 key を優先
        st.session_state.setdefault(_ACTIVE_KEY, eff_key if eff_key else "basic")

        _open_settings_dialog()

# ===== 共通本体：タブ＋アクティブ検知（切替＝未保存破棄） =====
def _render_settings_body():
    cfg = dash._load_tabs_cfg()
    tabs_def = cfg.get("tabs") or {}
    keys = _load_settings_keys()

    # タブラベル作成（title_set / title_dash）
    labels = [_get_label_from_tabs(tabs_def, k) for k in keys]
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
                set_dash.render()
                continue

            eff_key = _get_settings_target_key(key)
            if not eff_key:
                st.info("この機能に設定はありません。")
                continue

            modname = _resolve_settings_module(eff_key)
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

    # ---- 保存/既定の確定検知（set_* 側が確定時に __settings_dirty=True を置く想定） ----
    if st.session_state.pop("__settings_dirty", False):
        _discard_all_pending()  # 確定後はUI上の残骸を掃除
        st.session_state[_SETTINGS_FLAG] = False
        st.session_state["__settings_open"] = False
        st.session_state["_dash_require_rerun"] = True  # ダッシュ側で1回だけrerun→即時反映
        st.rerun()
    # ---- 入力変更は閉じない（再描画のみ）----
    elif st.session_state.pop("__settings_changed", False):
        st.rerun()
