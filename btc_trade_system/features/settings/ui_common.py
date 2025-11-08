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
                            confirm_message: str = "この操作を実行します。よろしいですか？") -> None:
    """
    3ボタン＋確認UIをまとめて描画する。
    - prefix: 'set.basic' / 'set.health' / 'set.collector'
    - key_base: 'set.basic.btn' など（ボタンキーの共通接頭）
    """
    col_close, col_default, col_save = st.columns([1,1,1])

    with col_close:
        if st.button(labels[0], key=f"{key_base}.close"):
            close_section(prefix)

    with col_default:
        if st.button(labels[1], key=f"{key_base}.default"):
            request_confirm(prefix, "default")

    with col_save:
        if st.button(labels[2], type="primary", key=f"{key_base}.save"):
            request_confirm(prefix, "save")

    # 確認UI
    state_key = _kprefix(prefix) + "confirm"
    cf = st.session_state.get(state_key)
    if not isinstance(cf, dict):
        return

    st.warning(confirm_message, icon="⚠️")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("実行", key=f"{key_base}.confirm.yes"):
            try:
                op = (cf.get("op") or "").lower()
                if op == "default" and on_default:
                    on_default()
                elif op == "save" and on_save:
                    on_save()
                mark_dirty()
                st.toast("操作を完了しました", icon="✅")
            finally:
                _pop_confirm(prefix)
                st.rerun()
    with c2:
        if st.button("キャンセル", key=f"{key_base}.confirm.no"):
            _pop_confirm(prefix)
            st.toast("操作をキャンセルしました", icon=None)
