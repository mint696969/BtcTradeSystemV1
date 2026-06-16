# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor_logic.py
# desc: Market Monitor の表示用判定ロジックを分離した logic 層。

from __future__ import annotations


def _pick_status_value(
    key: str,
    *,
    board: dict,
    state: dict | None,
    summary: dict | None,
):
    # UI must prefer L4/shared summary or market state over lower-level board payload.
    # Board is only a fallback surfacing source.
    return (
        (summary.get(key) if summary else None)
        or (state.get(key) if state else None)
        or board.get(key)
    )


def monitor_status_values(
    board: dict,
    state: dict | None,
    summary: dict | None = None,
) -> dict:
    return {
        "trust_state": _pick_status_value(
            "trust_state",
            board=board,
            state=state,
            summary=summary,
        ),
        "continuity_state": _pick_status_value(
            "continuity_state",
            board=board,
            state=state,
            summary=summary,
        ),
        "interpretation_bucket": _pick_status_value(
            "interpretation_bucket",
            board=board,
            state=state,
            summary=summary,
        ),
        "interpretation_reason": _pick_status_value(
            "interpretation_reason",
            board=board,
            state=state,
            summary=summary,
        ),
    }