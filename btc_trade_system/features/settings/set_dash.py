# path: btc_trade_system/features/settings/set_dash.py
# desc: 「初期設定」タブのメインUI（配色・デモアラート・保存/既定/今回のみ適用・監査出力）

from __future__ import annotations
from btc_trade_system.features.settings import settings_svc
from btc_trade_system.features.settings import ui_common as UI

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

def _demo_default_items() -> list[dict]:
    """デモアラート既定リスト（def に items がない場合のフォールバック）。"""
    return [
        {"level": "urgent", "label": "緊急Y"},
        {"level": "crit",   "label": "重大X"},
        {"level": "warn",   "label": "注意A"},
        {"level": "more",   "label": "+1"},
    ]

def _exec_default():
    # 1) 既定値を適用（current を {} に）
    settings_svc.reset_to_default("dash")

    # 2) セッション上書きを解除（保存値をマスクしない）
    st.session_state["_alerts_palette_overrides"] = {}

    # 3) 今回のセクションの作業状態だけクリア（モーダルは閉じない）
    st.session_state.pop("set.basic.pending", None)
    st.session_state.pop("set.basic._last_picks", None)

    # 4) ダッシュへ“即時反映”だけ通知（閉じない）
    st.session_state["_dash_require_rerun"] = True
    st.session_state["__settings_changed"] = True  # Hubは閉じずに再描画
    st.rerun()

def _exec_save():
    # --- 配色（差分保存専用SVCを使用） ---
    pal_save = {
        "urgent": {
            "fg": _norm_hex(st.session_state.get("set.basic.pick.urgent.fg", "#FFFFFF"), "#FFFFFF"),
            "bg": _norm_hex(st.session_state.get("set.basic.pick.urgent.bg", "#FF6B6B"), "#FF6B6B"),
        },
        "crit": {
            "fg": _norm_hex(st.session_state.get("set.basic.pick.crit.fg", "#FFFFFF"), "#FFFFFF"),
            "bg": _norm_hex(st.session_state.get("set.basic.pick.crit.bg", "#F9C8C8"), "#F9C8C8"),
        },
        "warn": {
            "fg": _norm_hex(st.session_state.get("set.basic.pick.warn.fg", "#000000"), "#000000"),
            "bg": _norm_hex(st.session_state.get("set.basic.pick.warn.bg", "#FDE8C8"), "#FDE8C8"),
        },
    }
    ok = bool(getattr(settings_svc, "save_palette")(pal_save))
    if not ok:
        st.error("保存に失敗しました（save_palette が未提供）")
        return

    # --- デモアラート（enabled と items を dash.yaml に保存） ---
    merged_dash = settings_svc.load_yaml("dash")  # def+current 合成（安全）
    merged_dash.setdefault("demo_alerts", {})
    merged_dash["demo_alerts"]["enabled"] = bool(st.session_state.get("set.basic.ui.demo_alerts"))
    # items が def に無い環境でも困らないよう、既存 or 既定の雛形を与える
    if not isinstance(merged_dash["demo_alerts"].get("items"), list):
        merged_dash["demo_alerts"]["items"] = _demo_default_items()

    settings_svc.save_yaml("dash", merged_dash)

    # --- セッション上書き解除＆再描画（閉じない） ---
    st.session_state["_alerts_palette_overrides"] = {}
    st.session_state.pop("set.basic.pending", None)
    st.session_state.pop("set.basic._last_picks", None)
    st.session_state["_dash_require_rerun"] = True
    st.session_state["__settings_changed"] = True
    st.rerun()

def render():
    st.markdown("<div class='settings-tab'>", unsafe_allow_html=True)

    st.subheader("初期設定（dash.yaml）")

    # ---- デモアラート投入（ヘッダーの表示確認用） ----
    st.divider()

    # def+current 合成（保存時と同じ視点）を使って初期チェック状態を整える
    merged_dash = settings_svc.load_yaml("dash")
    if "set.basic.ui.demo_alerts" not in st.session_state:
        initial_enabled = bool((merged_dash.get("demo_alerts") or {}).get("enabled", False))
        st.session_state["set.basic.ui.demo_alerts"] = initial_enabled

    st.checkbox(
        "デモアラートを表示する（保存で有効化/無効化）",
        key="set.basic.ui.demo_alerts",
    )
    st.caption("※ 表示は保存/既定で反映されます。即時反映は行いません。")

    # ---- アラート色（今回のみ適用） ----
    st.subheader("アラート色（保存で適用）")

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
        u_fg = st.color_picker("文字", use["urgent"]["fg"], key="set.basic.pick.urgent.fg", label_visibility="collapsed")
        u_bg = st.color_picker("背景", use["urgent"]["bg"], key="set.basic.pick.urgent.bg", label_visibility="collapsed")
    with c_crit:
        st.caption("重大")
        c_fg = st.color_picker("文字", use["crit"]["fg"], key="set.basic.pick.crit.fg", label_visibility="collapsed")
        c_bg = st.color_picker("背景", use["crit"]["bg"], key="set.basic.pick.crit.bg", label_visibility="collapsed")
    with c_warn:
        st.caption("注意")
        w_fg = st.color_picker("文字", use["warn"]["fg"], key="set.basic.pick.warn.fg", label_visibility="collapsed")
        w_bg = st.color_picker("背景", use["warn"]["bg"], key="set.basic.pick.warn.bg", label_visibility="collapsed")

    # --- 変更検知 → pending へ集約（未編集では pending を立てない） ---
    pal_now = {
        "urgent": {"fg": _norm_hex(st.session_state.get("set.basic.pick.urgent.fg", use["urgent"]["fg"]), use["urgent"]["fg"]),
                   "bg": _norm_hex(st.session_state.get("set.basic.pick.urgent.bg", use["urgent"]["bg"]), use["urgent"]["bg"])},
        "crit":   {"fg": _norm_hex(st.session_state.get("set.basic.pick.crit.fg",   use["crit"]["fg"]),   use["crit"]["fg"]),
                   "bg": _norm_hex(st.session_state.get("set.basic.pick.crit.bg",   use["crit"]["bg"]),   use["crit"]["bg"])},
        "warn":   {"fg": _norm_hex(st.session_state.get("set.basic.pick.warn.fg",   use["warn"]["fg"]),   use["warn"]["fg"]),
                   "bg": _norm_hex(st.session_state.get("set.basic.pick.warn.bg",   use["warn"]["bg"]),   use["warn"]["bg"])},
    }
    last = st.session_state.get("set.basic._last_picks")

    # 初回は“現行有効色”をベースラインとして記憶するだけ（未編集＝pendingなし）
    if last is None:
        st.session_state["set.basic._last_picks"] = pal_now
    else:
        # 前回と差があれば pending を積む
        if pal_now != last:
            st.session_state["set.basic.pending"] = {"palette": pal_now}
            st.session_state["set.basic._last_picks"] = pal_now

    # ボタン操作は上部（ハブ）に集約しました
    st.caption("操作は下部の『デフォルト／保存／閉じる』ボタンをご利用ください。")

    # === セクション専用ボタン（閉じる／デフォルト／保存） ===
    UI.render_section_controls(
        prefix="set.basic",
        on_default=_exec_default,
        on_save=_exec_save,
        key_base="set.basic.btn",
        labels=("閉じる","デフォルト","保存"),
        confirm_message="初期設定を更新します。よろしいですか？"
    )

    st.markdown("</div>", unsafe_allow_html=True)
