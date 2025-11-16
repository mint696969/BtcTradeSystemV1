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

    # 2) セッション上書きを解除（今回のみ適用の上書きなど）
    st.session_state["_alerts_palette_overrides"] = {}

    # 3) セクション作業状態だけクリア（モーダルは閉じない）
    from btc_trade_system.features.settings import ui_common as UI  # 既に上で import 済みなら不要
    UI.discard_prefix("set.dash")
    st.session_state.pop("set.dash.pending", None)
    st.session_state.pop("set.dash._last_picks", None)

    # 4) ダッシュ側へ適用通知（再描画は settings.py 側で一括管理）
    st.session_state["_dash_require_rerun"] = True
    st.session_state.pop("__settings_changed", None)
    st.session_state["__settings_apply"] = True

def _exec_save():
    # --- def+current をベースに 1 回で保存する ---
    merged_dash = settings_svc.load_yaml("dash") or {}

    # ---- アラート色（colors.alert_chip） ----
    colors = merged_dash.setdefault("colors", {})
    pal = colors.setdefault("alert_chip", {})

    pal["urgent"] = {
        "fg": _norm_hex(st.session_state.get("set.dash.pick.urgent.fg", "#FFFFFF"), "#FFFFFF"),
        "bg": _norm_hex(st.session_state.get("set.dash.pick.urgent.bg", "#FF6B6B"), "#FF6B6B"),
    }
    pal["crit"] = {
        "fg": _norm_hex(st.session_state.get("set.dash.pick.crit.fg", "#000000"), "#000000"),
        "bg": _norm_hex(st.session_state.get("set.dash.pick.crit.bg", "#FFCCCC"), "#FFCCCC"),
    }
    pal["warn"] = {
        "fg": _norm_hex(st.session_state.get("set.dash.pick.warn.fg", "#000000"), "#000000"),
        "bg": _norm_hex(st.session_state.get("set.dash.pick.warn.bg", "#FDE8C8"), "#FDE8C8"),
    }

    # ---- デモアラート ON/OFF ----
    merged_dash.setdefault("demo_alerts", {})
    merged_dash["demo_alerts"]["enabled"] = bool(
        st.session_state.get("set.dash.ui.demo_alerts")
    )
    if not isinstance(merged_dash["demo_alerts"].get("items"), list):
        merged_dash["demo_alerts"]["items"] = _demo_default_items()

    # ---- 一括保存（差分計算は settings_svc 側に任せる）----
    # ※ force_save_yaml は def に合わせて未知キーを削除しつつ、今回の merged を丸ごと current として保存する
    ok = settings_svc.force_save_yaml("dash", merged_dash)
    if not ok:
        st.error("dash.yaml の保存に失敗しました。", icon="⚠️")
        return

    # --- セッションのクリーンアップ（モーダルは閉じない） ---
    st.session_state["_alerts_palette_overrides"] = {}
    UI.discard_prefix("set.dash")
    st.session_state.pop("set.dash.pending", None)
    st.session_state.pop("set.dash._last_picks", None)

    # --- ダッシュ側へ適用通知（再描画は settings.py が担当） ---
    st.session_state["_dash_require_rerun"] = True
    st.session_state.pop("__settings_changed", None)
    st.session_state["__settings_apply"] = True

def render():
    st.markdown("<div class='settings-tab'>", unsafe_allow_html=True)

    st.subheader("初期設定（dash.yaml）")

    def_path, act_path = settings_svc.get_paths("dash")
    st.caption(f"適用対象（外部CONFIG）: {act_path.name} ／ 既定: {def_path.name}")

    # ---- デモアラート投入（ヘッダーの表示確認用） ----
    st.divider()

    # def+current 合成（保存時と同じ視点）を使って初期チェック状態を整える
    merged_dash = settings_svc.load_yaml("dash") or {}
    if "set.dash.ui.demo_alerts" not in st.session_state:
        initial_enabled = bool((merged_dash.get("demo_alerts") or {}).get("enabled", False))
        st.session_state["set.dash.ui.demo_alerts"] = initial_enabled

    st.checkbox(
        "デモアラートを表示する（保存で有効化/無効化）",
        key="set.dash.ui.demo_alerts",
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
        u_fg = st.color_picker("文字", use["urgent"]["fg"], key="set.dash.pick.urgent.fg", label_visibility="collapsed")
        u_bg = st.color_picker("背景", use["urgent"]["bg"], key="set.dash.pick.urgent.bg", label_visibility="collapsed")
    with c_crit:
        st.caption("重大")
        c_fg = st.color_picker("文字", use["crit"]["fg"], key="set.dash.pick.crit.fg", label_visibility="collapsed")
        c_bg = st.color_picker("背景", use["crit"]["bg"], key="set.dash.pick.crit.bg", label_visibility="collapsed")
    with c_warn:
        st.caption("注意")
        w_fg = st.color_picker("文字", use["warn"]["fg"], key="set.dash.pick.warn.fg", label_visibility="collapsed")
        w_bg = st.color_picker("背景", use["warn"]["bg"], key="set.dash.pick.warn.bg", label_visibility="collapsed")

    # --- 変更検知 → pending へ集約（未編集では pending を立てない） ---
    pal_now = {
        "urgent": {"fg": _norm_hex(st.session_state.get("set.dash.pick.urgent.fg", use["urgent"]["fg"]), use["urgent"]["fg"]),
                   "bg": _norm_hex(st.session_state.get("set.dash.pick.urgent.bg", use["urgent"]["bg"]), use["urgent"]["bg"])},
        "crit":   {"fg": _norm_hex(st.session_state.get("set.dash.pick.crit.fg",   use["crit"]["fg"]),   use["crit"]["fg"]),
                   "bg": _norm_hex(st.session_state.get("set.dash.pick.crit.bg",   use["crit"]["bg"]),   use["crit"]["bg"])},
        "warn":   {"fg": _norm_hex(st.session_state.get("set.dash.pick.warn.fg",   use["warn"]["fg"]),   use["warn"]["fg"]),
                   "bg": _norm_hex(st.session_state.get("set.dash.pick.warn.bg",   use["warn"]["bg"]),   use["warn"]["bg"])},
    }
    last = st.session_state.get("set.dash._last_picks")

    # 初回は“現行有効色”をベースラインとして記憶するだけ（未編集＝pendingなし）
    if last is None:
        st.session_state["set.dash._last_picks"] = pal_now
    else:
        # 前回と差があれば pending を積む
        if pal_now != last:
            st.session_state["set.dash.pending"] = {"palette": pal_now}
            st.session_state["set.dash._last_picks"] = pal_now

    # ボタン操作は上部（ハブ）に集約しました
    st.caption("操作は下部の『デフォルト／保存／閉じる』ボタンをご利用ください。")

    # === セクション専用ボタン（閉じる／デフォルト／保存） ===
    UI.render_section_controls(
        prefix="set.dash",
        on_default=_exec_default,
        on_save=_exec_save,
        key_base="set.dash.btn",
        labels=("閉じる","デフォルト","保存"),
        confirm_message="初期設定を更新します。よろしいですか？",
        audit_tag=None  # success 監査は settings_svc 側のみ（最小監査）
    )

    st.markdown("</div>", unsafe_allow_html=True)
