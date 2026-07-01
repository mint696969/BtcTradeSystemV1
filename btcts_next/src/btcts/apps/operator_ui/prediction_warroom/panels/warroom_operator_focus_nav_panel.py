# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py
# desc: PS-Q26N compact WarRoom operator-first focus navigation panel. Layout-only Streamlit presentation; no runtime writes, producer/scheduler, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

import streamlit as st

WARROOM_OPERATOR_FOCUS_NAV_VERSION = "prediction_warroom.operator_focus_nav.ps_q26n.v1"


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
    return {
        "ok": True,
        "focus_nav_version": WARROOM_OPERATOR_FOCUS_NAV_VERSION,
        "operator_first_navigation_visible": True,
        "row_count": len(rows),
        "rows": rows,
        "top_expanded_default": True,
        "reduces_first_screen_ambiguity": True,
        "keeps_existing_panels_available": True,
        "production_ui_code_changed": True,
        "layout_only_change": True,
        "externalized_panel_module": True,
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


def render_warroom_operator_focus_nav() -> None:
    """Render the compact WarRoom operator-first focus navigation block."""
    packet = build_warroom_operator_focus_nav_packet()
    st.session_state["warroom_operator_focus_nav"] = dict(packet)
    st.caption(
        "まずこの順番で見ます。詳細パネルは残していますが、最初は 1→2→3 だけで全体を把握します。"
    )
    st.dataframe(packet["rows"], width="stretch", hide_index=True)
