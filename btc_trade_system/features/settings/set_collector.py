# path: btc_trade_system/features/settings/set_collector.py
# desc: コレクタ設定タブ。def+current 合成の編集（enabled_exchanges / poll_interval_s）を提供し、
#       保存/デフォルトは settings_svc 経由・モーダルは閉じず即反映。

from __future__ import annotations
from typing import Any, Dict, List
import streamlit as st

from btc_trade_system.features.settings import settings_svc
from btc_trade_system.features.settings import ui_common as UI

PREFIX = "set.collector"   # 本セクションの session_state 接頭辞
AREA   = "collector"       # 保存先ファイル名 collector.yaml

# ----------------------------
# helpers
# ----------------------------
def _deep_merge(dst: dict, src: dict) -> dict:
    """dict を再帰マージ（src 優先）。"""
    from collections.abc import Mapping
    for k, v in (src or {}).items():
        if isinstance(v, Mapping) and isinstance(dst.get(k), Mapping):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def _mark_changed() -> None:
    st.session_state["__settings_changed"] = True

# ----------------------------
# actions
# ----------------------------
def _exec_default() -> None:
    """current を空差分（= 既定へ）に戻し、閉じずに即反映。"""
    settings_svc.reset_to_default(AREA)              # atomic+fsync+監査は SVC 側
    UI.discard_prefix(PREFIX)                        # セクション内の未保存キーだけ破棄
    st.session_state["_dash_require_rerun"] = True   # 1回だけ再描画
    st.session_state["__settings_changed"] = True
    st.rerun()

def _exec_save() -> None:
    """pending を current へ差分保存し、閉じずに即反映。"""
    pending = st.session_state.get(f"{PREFIX}.pending", {}) or {}
    current = settings_svc.load_yaml(AREA) or {}
    merged  = _deep_merge(current, pending)

    settings_svc.save_yaml(AREA, merged)             # atomic+fsync+監査は SVC 側
    UI.discard_prefix(PREFIX)                        # 次回オープンをクリーンに
    st.session_state["_dash_require_rerun"] = True
    st.session_state["__settings_changed"] = True
    st.rerun()

# ----------------------------
# UI (minimal)
# ----------------------------
def render() -> None:
    st.markdown("<div class='settings-tab'>", unsafe_allow_html=True)
    st.subheader("コレクタ設定（collector.yaml）")

    # def+current 合成（SVC が def→current の順で解決）
    merged: Dict[str, Any] = settings_svc.load_yaml(AREA)

    gen = (merged.get("general") or {})
    enabled: List[str] = list(gen.get("enabled_exchanges") or [])
    poll_interval_s: int = int(gen.get("poll_interval_s", 1))

    st.markdown("### 有効な取引所")
    txt = st.text_input(
        "カンマ区切り（例: bitflyer,binance,bybit,okx）",
        value=",".join(enabled) if enabled else "",
        key=f"{PREFIX}.enabled_text",
        on_change=_mark_changed,
        placeholder="bitflyer,binance,bybit,okx",
    )
    new_enabled = [x.strip() for x in txt.split(",") if x.strip()]

    st.markdown("### ポーリング間隔（秒）")
    new_interval = st.number_input(
        "poll_interval_s",
        min_value=1, max_value=60,
        value=poll_interval_s if poll_interval_s > 0 else 1,
        key=f"{PREFIX}.poll_interval_s",
        on_change=_mark_changed,
    )

    # pending をこのセクションに集約（タブ切替時の未保存破棄に備える）
    pending = {
        "general": {
            "enabled_exchanges": new_enabled,
            "poll_interval_s": int(new_interval),
        }
    }
    _old = st.session_state.get(f"{PREFIX}.pending", {})
    st.session_state[f"{PREFIX}.pending"] = _deep_merge(_old or {}, pending)

    # 共通フッター：閉じる／デフォルト／保存（確認＋閉じず反映）
    UI.render_section_controls(
        prefix=PREFIX,
        on_default=_exec_default,
        on_save=_exec_save,
        key_base=f"{PREFIX}.btn",
        labels=("閉じる", "デフォルト", "保存"),
        confirm_message="コレクタ設定を更新します。よろしいですか？",
        active=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
