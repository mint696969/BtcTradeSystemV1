# path: btc_trade_system/features/settings/ui_common.py
# desc: 設定セクションの共通UI（閉じる/デフォルト/保存＋確認ダイアログ＋dirty＋rerun）

from __future__ import annotations
from typing import Callable, Any, Dict

try:
    import streamlit as st
except Exception:  # pragma: no cover
    import types as _t
    st = _t.SimpleNamespace(
        warning=print, button=lambda *a, **k: False, columns=lambda *a, **k: [None, None, None],
        session_state={}, toast=print, rerun=lambda: None, caption=print
    )

def _kprefix(prefix: str) -> str:
    return prefix if prefix.endswith(".") else prefix + "."

def discard_prefix(prefix: str) -> None:
    p = _kprefix(prefix)
    for k in list(st.session_state.keys()):
        if k.startswith(p):
            st.session_state.pop(k, None)

def mark_dirty() -> None:
    st.session_state["__settings_dirty"] = True

def close_section(prefix: str) -> None:
    st.session_state["__settings_open"] = False
    discard_prefix(prefix)
    st.session_state.pop(_kprefix(prefix) + "pending", None)
    st.rerun()

def request_confirm(prefix: str, op: str, payload: Dict[str, Any] | None = None) -> None:
    st.session_state[_kprefix(prefix) + "confirm"] = {"op": op, "payload": payload or {}}

def _pop_confirm(prefix: str) -> Dict[str, Any] | None:
    key = _kprefix(prefix) + "confirm"
    cf = st.session_state.get(key)
    st.session_state.pop(key, None)
    return cf if isinstance(cf, dict) else None

def render_section_controls(prefix: str,
                            on_default: Callable[[], None] | None,
                            on_save: Callable[[], None] | None,
                            key_base: str,
                            labels: tuple[str, str, str] = ("閉じる","デフォルト","保存"),
                            confirm_message: str = "この操作を実行します。よろしいですか？",
                            active: bool = True) -> None:
    """
    3ボタン＋確認UIをまとめて描画する。
    - active: False の場合は、このセクションが「折りたたみ中」を想定し、
      確認チェックおよび 3 ボタンをすべて無効化（disabled）する。
    """

    # 誤操作防止の確認チェック（これが ON でないと［デフォルト］［保存］は無効）
    # 開閉/タブ移動時は毎回 OFF に初期化する（再オープン時にボタンが誤って有効化されないように）
    confirm_ok_key = f"{key_base}.confirm_ok"
    open_flag = bool(st.session_state.get("__settings_open"))
    prev_flag = st.session_state.get(f"{key_base}.__open_flag")
    if open_flag != prev_flag:
        if open_flag:
            st.session_state[confirm_ok_key] = False
        st.session_state[f"{key_base}.__open_flag"] = open_flag
    last_prefix = st.session_state.get(f"{key_base}.__last_prefix")
    if last_prefix != prefix:
        st.session_state[confirm_ok_key] = False
        st.session_state[f"{key_base}.__last_prefix"] = prefix

    # チェック行（横一列・中央寄せ・折返しなし）
    # 再オープン時：pending が無ければ常に未チェックへ戻す
    if st.session_state.get(_kprefix(prefix) + "pending") is None:
        st.session_state[confirm_ok_key] = False

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.checkbox(
            "変更内容を確認しました",
            key=confirm_ok_key,
            disabled=not active,  # 折りたたみ中はチェック自体も無効
        )
    ok = bool(st.session_state.get(confirm_ok_key)) and active

    col_close, col_default, col_save = st.columns([1,1,1])

    with col_close:
        if st.button(labels[0], key=f"{key_base}.close", disabled=not active):
            close_section(prefix)

    with col_default:
        if st.button(labels[1], key=f"{key_base}.default", disabled=not ok):
            if on_default:
                on_default()
            mark_dirty()
            st.toast("既定値を適用しました", icon="✅")
            st.rerun()

    with col_save:
        if st.button(labels[2], type="primary", key=f"{key_base}.save", disabled=not ok):
            if on_save:
                on_save()
            mark_dirty()
            st.toast("設定を保存しました", icon="✅")
            st.rerun()
