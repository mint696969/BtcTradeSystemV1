# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/card_axis_policy.py
# desc: WarRoom v2 card axis policy. Item rows by horizon-axis cards; placeholder-only and display-safe.

from __future__ import annotations

from typing import Any

WARROOM_V2_CARD_AXIS_POLICY_VERSION = "prediction_warroom.v2.card_axis_policy.ps_q29f.v1"
WARROOM_V2_HORIZON_LABELS: tuple[str, ...] = (
    "現在",
    "5分後",
    "15分後",
    "30分後",
    "60分後",
    "6時間後",
    "12時間後",
    "24時間後",
)


def build_warroom_v2_card_axis_policy() -> dict[str, Any]:
    return {
        "ok": True,
        "card_axis_policy_version": WARROOM_V2_CARD_AXIS_POLICY_VERSION,
        "layout_shape": "item_rows_by_horizon_columns",
        "row_axis": "prediction_item",
        "column_axis": "horizon",
        "horizon_labels": list(WARROOM_V2_HORIZON_LABELS),
        "horizon_count": len(WARROOM_V2_HORIZON_LABELS),
        "card_row_layout": "horizontal_time_axis_cards",
        "card_shape": "horizontal_rectangle",
        "wide_window_goal": "show_through_24h_when_space_allows",
        "narrow_window_goal": "show_visible_range_and_scroll_do_not_squeeze",
        "cards_do_not_shrink": True,
        "horizontal_scroll_required": True,
        "card_body_three_lines": True,
        "line_1": "primary_classification_label",
        "line_2": "confidence_or_card_score",
        "line_3": "short_action_or_state_tag",
        "freshness_badge": "top_right_badge_only",
        "freshness_encoded_by_badge_only": True,
        "border_meaning": "evidence_quality",
        "background_tone": "tradability_or_readability_or_risk_temperature",
        "detail_disclosure_mode": "card_overlay",
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "would_send_to_broker": False,
    }
