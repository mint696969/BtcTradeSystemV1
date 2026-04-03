# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor_presenter.py
# desc: Market Monitor の caption / source 表示を分離した presenter 層。

from __future__ import annotations

from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def source_label_map(lang: str) -> dict:
    return {
        "unknown": get_text(lang, "market_monitor_source_unknown"),
        "live_canonical": get_text(lang, "market_monitor_source_live_canonical"),
        "market_state_live": get_text(lang, "market_monitor_source_market_state_live"),
        "replay_board_fallback": get_text(lang, "market_monitor_source_replay_board_fallback"),
        "market_state_preferred": get_text(lang, "market_monitor_source_market_state_preferred"),
    }


def best_bid_ask_ts_caption(lang: str, board: dict) -> str:
    return get_text(lang, "market_monitor_best_bid_ask_ts_line").format(
        best_bid=board.get("best_bid"),
        best_ask=board.get("best_ask"),
        ts=format_ui_ts(board.get("event_ts"), lang),
    )


def source_caption(
    *,
    lang: str,
    source_label: str,
    has_state: bool,
    preferred_freshness,
) -> str:
    mapping = source_label_map(lang)
    return get_text(lang, "market_monitor_source_line").format(
        board_source=mapping.get(source_label, source_label),
        state_source=mapping.get(
            "market_state_preferred" if has_state else "-",
            "-" if not has_state else "market_state_preferred",
        ),
        preferred_state_freshness=preferred_freshness,
    )


def interpretation_caption(
    *,
    lang: str,
    continuity_state,
    interpretation_bucket,
    interpretation_reason,
) -> str:
    return get_text(lang, "market_monitor_interpretation_line").format(
        continuity_state=continuity_state or "-",
        interpretation_bucket=interpretation_bucket or "-",
        interpretation_reason=interpretation_reason or "-",
    )
