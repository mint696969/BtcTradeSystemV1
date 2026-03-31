# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor_logic.py
# desc: Market Monitor の表示用判定ロジックを分離した logic 層。

from __future__ import annotations


def monitor_status_values(board: dict, state: dict | None) -> dict:
    trust_state = board.get("trust_state") or (state.get("trust_state") if state else None)
    continuity_state = board.get("continuity_state") or (state.get("continuity_state") if state else None)
    interpretation_bucket = board.get("interpretation_bucket") or (state.get("interpretation_bucket") if state else None)
    interpretation_reason = board.get("interpretation_reason") or (state.get("interpretation_reason") if state else None)

    return {
        "trust_state": trust_state,
        "continuity_state": continuity_state,
        "interpretation_bucket": interpretation_bucket,
        "interpretation_reason": interpretation_reason,
    }