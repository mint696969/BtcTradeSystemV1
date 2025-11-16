# path: ./btc_trade_system/features/settings/set_main.py
# desc: メイン設定セクション（当面はタイトルのみ。保存/既定はSVCへ委譲、モーダルは閉じない）。

from __future__ import annotations
import streamlit as st
from btc_trade_system.features.settings import settings_svc as S
from btc_trade_system.features.settings import ui_common as UI

def _exec_default():
    """current を既定値へ戻し、モーダルは閉じずにダッシュへ反映指示。"""
    S.reset_to_default("main")
    UI.discard_prefix("set.main")

    # ダッシュ側への適用通知（再描画は settings.py 側で一括管理）
    st.session_state["_dash_require_rerun"] = True
    st.session_state.pop("__settings_changed", None)
    st.session_state["__settings_apply"] = True

def _exec_save():
    """タイトルを保存し、モーダルは閉じずにダッシュへ反映指示。"""
    base = S.load_yaml("main") or {}
    title = st.session_state.get("set.main.title") or base.get("title") or "メイン"

    merged = dict(base)
    merged["title"] = str(title).strip() or "メイン"

    # v4 方針：force_save_yaml を優先し、無ければ save_yaml へフォールバック
    force = getattr(S, "force_save_yaml", None)
    if callable(force):
        force("main", merged)
    else:
        S.save_yaml("main", merged)

    UI.discard_prefix("set.main")

    # ダッシュ側への適用通知（再描画は settings.py 側で一括管理）
    st.session_state["_dash_require_rerun"] = True
    st.session_state.pop("__settings_changed", None)
    st.session_state["__settings_apply"] = True

def render() -> None:
    st.subheader("設定（メイン）")
    cur = S.load_yaml("main") or {}
    title = cur.get("title") or "メイン"
    st.text_input("タイトル", value=title, key="set.main.title")

    UI.render_section_controls(
        prefix="set.main",
        on_default=_exec_default,
        on_save=_exec_save,
        key_base="set.main.btn",
        labels=("閉じる","デフォルト","保存"),
        confirm_message="メイン設定を更新します。よろしいですか？",
        audit_tag=None  # success監査はSVC側のみ
    )
