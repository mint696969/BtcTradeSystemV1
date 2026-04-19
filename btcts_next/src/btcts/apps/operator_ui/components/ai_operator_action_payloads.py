# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_action_payloads.py
# desc: AI Operator の support context を research / watch 用 payload に落とす境界。

from __future__ import annotations


def build_research_replay_context(support_context: dict) -> dict:
    return {
        "session_name": "warroom_ai_operator",
        "start_ts": "",
        "end_ts": "",
        "jump_ts": support_context.get("event_ts") or "",
        "kind_filter": "all",
        "event_filter": support_context.get("pressure_bias") or "",
        "filtered_rows": 1,
    }


def build_watch_item(support_context: dict) -> dict:
    return {
        "ts": support_context.get("event_ts"),
        "regime": support_context.get("regime"),
        "action": support_context.get("advisory_action"),
        "risk": support_context.get("advisory_risk"),
    }