# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py
# desc: WarRoom operator-first focus navigation panel. Visual-only Streamlit presentation; no runtime writes, producer/scheduler, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

import streamlit as st

WARROOM_OPERATOR_FOCUS_NAV_VERSION = "prediction_warroom.operator_focus_nav.ps_q26n.v1"
WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_VERSION = "prediction_warroom.operator_focus_visual_tune.ps_q26s.v1"
WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION = "prediction_warroom.operator_focus_command_cards.ps_q26t.v1"


def warroom_operator_focus_card_rows() -> list[dict]:
    """Return first-glance command cards for the WarRoom entry."""
    return [
        {
            "card_id": "current_state",
            "順": "①",
            "見出し": "現在状態",
            "主確認": "live / board / freshness",
            "合図": "古い・注意なら予測を弱めに読む",
            "tone": "primary",
        },
        {
            "card_id": "prediction_read",
            "順": "②",
            "見出し": "予測表示",
            "主確認": "generated_at / horizon",
            "合図": "時刻が変わった時だけ予測更新",
            "tone": "accent",
        },
        {
            "card_id": "operator_alert",
            "順": "③",
            "見出し": "alert / operator",
            "主確認": "注意・要約・安全境界",
            "合図": "最後に全体注意を確認",
            "tone": "safe",
        },
    ]


def warroom_operator_focus_route_rows() -> list[dict]:
    """Return a compact visual route for the first screen.

    This is intentionally short and visual. It does not replace the existing
    detailed navigation rows; it gives the operator a quick reading rhythm.
    """
    return [
        {
            "順": "①",
            "見る": "現在状態",
            "意味": "live / board / freshness",
            "初期": "開く",
        },
        {
            "順": "②",
            "見る": "予測表示",
            "意味": "generated_at / horizon",
            "初期": "開く",
        },
        {
            "順": "③",
            "見る": "alert / operator",
            "意味": "注意・要約・安全境界",
            "初期": "開く",
        },
        {
            "順": "④⑤",
            "見る": "理由と履歴",
            "意味": "graph / evidence / timeline",
            "初期": "必要時だけ開く",
        },
    ]


def warroom_operator_focus_visual_route_text() -> str:
    return "読む順: ① 現在状態 → ② 予測表示 → ③ alert/operator → ④⑤ 理由確認"


def warroom_operator_focus_nav_rows() -> list[dict]:
    """Return compact operator-first WarRoom navigation rows.

    The rows reduce first-screen ambiguity by telling the operator where to look
    first. This is display-only and does not load/refresh/write runtime artifacts
    or touch producer, scheduler, AutoTrade, broker, ledger, mode, or parameters.
    """
    return [
        {
            "優先": "1",
            "見る場所": "現在状態 nowcast / board・freshness",
            "何を見るか": "live状態・板/約定freshness・spread・attention flags",
            "判断": "ここが古い/注意なら、下の予測は弱めに読む",
        },
        {
            "優先": "2",
            "見る場所": "リアルタイム予測表示 / read model",
            "何を見るか": "generated_at・予測データ鮮度・15s/60s・horizon期限",
            "判断": "generated_atが変わった時だけ予測そのものが更新",
        },
        {
            "優先": "3",
            "見る場所": "ヘッダー / alert / AI operator",
            "何を見るか": "全体注意・operator向け要約・安全境界",
            "判断": "現在状態と予測を読んだ後の補助として見る",
        },
        {
            "優先": "4",
            "見る場所": "市場証拠 / graph / active event",
            "何を見るか": "liquidity・trade flow・regime・graph context",
            "判断": "詳しく理由を確認したい時だけ開く",
        },
        {
            "優先": "5",
            "見る場所": "operator support / timeline / evidence",
            "何を見るか": "履歴・watch・decision log・evidence presentation",
            "判断": "最後に背景確認。入口ではなく補助として見る",
        },
    ]


def build_warroom_operator_focus_nav_packet() -> dict:
    rows = warroom_operator_focus_nav_rows()
    route_rows = warroom_operator_focus_route_rows()
    card_rows = warroom_operator_focus_card_rows()
    return {
        "ok": True,
        "focus_nav_version": WARROOM_OPERATOR_FOCUS_NAV_VERSION,
        "focus_visual_tune_version": WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_VERSION,
        "focus_command_cards_version": WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION,
        "operator_first_navigation_visible": True,
        "visual_route_strip_visible": True,
        "command_cards_visible": True,
        "visual_route_text": warroom_operator_focus_visual_route_text(),
        "card_row_count": len(card_rows),
        "card_rows": card_rows,
        "route_row_count": len(route_rows),
        "route_rows": route_rows,
        "row_count": len(rows),
        "rows": rows,
        "top_expanded_default": True,
        "reduces_first_screen_ambiguity": True,
        "improves_first_screen_scanability": True,
        "improves_first_screen_glanceability": True,
        "visual_only_change": True,
        "keeps_existing_panels_available": True,
        "production_ui_code_changed": True,
        "layout_only_change": True,
        "externalized_panel_module": True,
        "warroom_page_changed": False,
        "warroom_page_slimming_main_goal": False,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def _render_focus_card(card: dict) -> None:
    st.markdown(f"**{card['順']} {card['見出し']}**")
    st.caption(str(card["主確認"]))
    st.write(str(card["合図"]))


def render_warroom_operator_focus_nav() -> None:
    """Render the compact WarRoom operator-first focus navigation block."""
    packet = build_warroom_operator_focus_nav_packet()
    st.session_state["warroom_operator_focus_nav"] = dict(packet)
    st.caption(
        "まずこの順番で見ます。詳細パネルは残していますが、最初は 1→2→3 だけで全体を把握します。"
    )
    card_columns = st.columns(len(packet["card_rows"]))
    for column, card in zip(card_columns, packet["card_rows"]):
        with column:
            _render_focus_card(card)
    st.markdown(f"**{packet['visual_route_text']}**")
    st.dataframe(packet["route_rows"], width="stretch", hide_index=True)
    st.caption("④⑤ は理由確認・背景確認用です。必要な時だけ開きます。")
    st.dataframe(packet["rows"], width="stretch", hide_index=True)
