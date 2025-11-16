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

# --- dev_audit: 安全な薄いラッパ ---
def _audit(event: str, level: str = "DEBUG", **payload):
    try:
        W.emit(event, level=level, feature="settings", payload=payload)
    except Exception:
        pass

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
    未保存UI値を破棄し、ダッシュ側に「次描画は Main 固定」を指示する。
    """
    prev = bool(st.session_state.get("__settings_prev_open"))
    cur  = bool(st.session_state.get("__settings_open"))
    if prev and not cur:
        _discard_all_pending()
        # --- ダッシュボードに Main 固定リランを依頼 ---
        st.session_state["_dash_force_main"] = True
        st.session_state["_dash_require_rerun"] = True
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

def _gear_state(dash_key: str) -> dict:
    """
    歯車ボタンの有効/無効と根拠を返す。
    - enabled: bool
    - reason : 無効時の説明（settings=false, missing, import-fail等）
    - eff_key: 実際に参照する設定キー（alias解決後）
    - mod    : 解決できた set_* モジュール名（あれば）
    """
    eff = _get_settings_target_key(dash_key)
    if eff is None:
        return {"enabled": False, "reason": "tabs.yaml: settings=false-or-missing", "eff_key": None, "mod": ""}
    mod = _resolve_settings_module(eff)
    if mod is None:
        return {"enabled": False, "reason": "settings module not found", "eff_key": eff, "mod": ""}
    return {"enabled": True, "reason": "", "eff_key": eff, "mod": mod}

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

    has_dash_alias = False  # set_dash を使うキー（= target 'dash'）が存在するか

    for k in order:
        t = tabs_def.get(k) or {}
        s = t.get("settings", False)
        # settings: true → set_<k>.py、文字列 → set_<name>.py
        target = k if s is True else (s.strip() if isinstance(s, str) and s.strip() else None)
        if not target:
            continue

        if target == "dash":
            has_dash_alias = True

        has_module = _resolve_settings_module(target) is not None
        if has_module:
            keys.append(k)

    # 初期設定（basic）は “dash（= set_dash）を使うキーが無い時だけ” 末尾に追加
    if not has_dash_alias:
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
        state = _gear_state(target_key)              # 追加：統一判定
        disabled = (not state["enabled"])            # 変更：_gear_stateに基づく
        _audit("dash.gear.state", target=target_key, **state)  # 追加：観測

        clicked = st.button("⚙️", use_container_width=False, key="gear_fallback", disabled=disabled)
        if not clicked:
            return
        if disabled:
            st.toast("このタブには設定がありません", icon="⚠️")
            _audit("settings.open.blocked", target=target_key, **state)  # 追加
            return

        _discard_all_pending()
        st.session_state.pop("__toast", None)
        st.session_state.pop("__settings_error", None)
        st.session_state["set.basic.demo_alert_default"] = _get_header_alert_active()

        st.session_state[_SETTINGS_FLAG] = True
        st.session_state["__settings_open"] = True
        # 毎回メイン設定タブから開始（eff_key は監査用に残すがアクティブには使わない）
        eff_key = state.get("eff_key") or "basic"
        st.session_state[_ACTIVE_KEY] = "main"

        _audit("settings.open", source="gear_fallback", target=target_key,
               eff_key=eff_key, mod=state.get("mod", ""))                 # 追加

        with st.sidebar:
            st.header("設定")
            _render_settings_body()

else:
    @_DLG("設定")
    def _open_settings_dialog():
        # 毎回メイン設定から開始
        st.session_state[_ACTIVE_KEY] = "main"
        _render_settings_body()

# Dialog 環境にのみ定義（_DLG が無い場合は、前段の fallback 定義を温存）
if _DLG is not None:
    def settings_gear():
        # 直前が open で今は閉じている場合の残骸破棄（外側クリック・タブ遷移検知）
        _closed_then_discard_if_needed()

        target_key: str = st.session_state.get("_gear_target") or "dash"
        state = _gear_state(target_key)               # 追加
        disabled = (not state["enabled"])             # 変更
        _audit("dash.gear.state", target=target_key, **state)  # 追加

        clicked = st.button("⚙️", use_container_width=False, key="gear_dialog", disabled=disabled)
        if not clicked:
            return
        if disabled:
            st.toast("このタブには設定がありません", icon="⚠️")
            _audit("settings.open.blocked", target=target_key, **state)  # 追加
            return

        _discard_all_pending()
        st.session_state["set.basic.demo_alert_default"] = _get_header_alert_active()

        st.session_state[_SETTINGS_FLAG] = True
        st.session_state["__settings_open"] = True

        # 毎回メイン設定タブから開始
        eff_key = state.get("eff_key") or "basic"
        st.session_state[_ACTIVE_KEY] = "main"

        _audit("settings.open", source="gear_dialog", target=target_key,
               eff_key=eff_key, mod=state.get("mod", ""))                 # 追加

        _open_settings_dialog()

# ===== 共通本体：タブ＋アクティブ検知（切替＝未保存破棄） =====
def _render_settings_body():
    cfg = dash._load_tabs_cfg()
    tabs_def = cfg.get("tabs") or {}
    keys = _load_settings_keys()

    # 安全フィルタ：set_dash を使うキー（settings: "dash"）が1つでもあれば、basic は除外
    if "basic" in keys:
        for k in list((cfg.get("order") or [])):
            t = (cfg.get("tabs") or {}).get(k) or {}
            s = t.get("settings", False)
            if (isinstance(s, str) and s.strip() == "dash"):
                keys = [x for x in keys if x != "basic"]
                break

    _audit("settings.render.start", keys=keys, prev=st.session_state.get(_ACTIVE_KEY, "basic"))

    # タブラベル作成（title_set / title_dash）
    labels = [_get_label_from_tabs(tabs_def, k) for k in keys]

    # ★空タブ保護：keys が空だと st.tabs([]) で例外化するため早期リターン
    if not keys:
        st.info("設定可能な項目がありません（tabs.yaml / set_* を確認してください）。")
        _audit("settings.render.empty")
        return

    tabs = st.tabs(labels)

    # 直前のアクティブキーを“今回の描画の基準”として固定し、無ければ先頭に合わせる
    prev = st.session_state.get(_ACTIVE_KEY)

    if not prev or prev not in keys:
        prev = keys[0] if keys else "basic"
    # 基準をセッションにも反映（以降の比較はこの基準からの遷移のみを検知）
    st.session_state[_ACTIVE_KEY] = prev

    # 各タブの描画（選択されたタブのみUIが効く仕様。切替検知→他キーの未保存破棄）
    for key, tab in zip(keys, tabs):

        eff_key_scan = _get_settings_target_key(key)
        mod_scan = _resolve_settings_module(eff_key_scan) if eff_key_scan else None
        _audit("settings.tab.scan", key=key, eff_key=eff_key_scan, mod=mod_scan)

        with tab:
            # タブ切替時（=前回と異なるタブへ入ったタイミング）に、前タブの未保存を破棄
            if key != prev and st.session_state.get(_ACTIVE_KEY) == prev:

                _audit("settings.tab.changed", _from=prev, to=key)

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
                    # 呼び出し直前の観測
                    _audit("settings.render.call", key=key, eff_key=eff_key, mod=modname)
                    # ※ 複数機能を束ねる場合のアコーディオンは set_*.py 側で実装（ここではタブのみ）
                    render()
                    # 呼び出し直後の観測
                    _audit("settings.render.done", key=key, eff_key=eff_key)
                else:
                    st.info(f"{modname}.render() が見つかりません。")
                    _audit("settings.render.missing", key=key, eff_key=eff_key, mod=modname, reason="no-render")

            except Exception as e:
                st.error(f"設定モジュールの読み込みに失敗しました: {key}\n{e}")
                _audit("settings.render.error", key=key, eff_key=eff_key, mod=modname, err=repr(e))

    # ---- 適用（保存/デフォルト）：モーダルは閉じない ----
    # 互換: 既存 set_* が置く __settings_dirty も「適用完了」と見なす
    if st.session_state.pop("__settings_dirty", False) or st.session_state.pop("__settings_apply", False):
        _audit("settings.apply", how="save-or-default")
        _discard_all_pending()                         # UI残骸を掃除
        st.session_state["_dash_require_rerun"] = True  # 次のダッシュ描画で反映（ここでは rerun しない）

    # ---- 明示クローズ（閉じるボタン/右上×）のみ rerun ----
    if st.session_state.pop("__settings_close", False):
        _audit("settings.close", how="close-button")
        _discard_all_pending()
        st.session_state[_SETTINGS_FLAG] = False
        st.session_state["__settings_open"] = False
        st.session_state["_dash_force_main"] = True
        st.session_state["_dash_require_rerun"] = True
        st.rerun()

    # ---- 入力変更での rerun は禁止（モーダル即落ちの原因）----
    st.session_state.pop("__settings_changed", None)
