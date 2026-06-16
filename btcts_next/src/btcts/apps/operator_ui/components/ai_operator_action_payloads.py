# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_action_payloads.py
# desc: AI Operator の support context を research / watch 用 payload に落とす境界。

from __future__ import annotations


def _build_tactic_review_carry(support_context: dict) -> dict:
    return {
        "tactic_summary_lines": tuple(
            support_context.get("tactic_summary_lines") or ()
        ),
        "tactic_interpretation_lines": tuple(
            support_context.get("tactic_interpretation_lines") or ()
        ),
        "primary_tactic_interpretation_line": str(
            support_context.get("primary_tactic_interpretation_line") or ""
        ),
        "tactic_primary_summary_line": str(
            support_context.get("tactic_primary_summary_line") or ""
        ),
    }


def build_research_context_base(
    *,
    session_name: str,
    start_ts: str = "",
    end_ts: str = "",
    jump_ts: str = "",
    kind_filter: str = "all",
    event_filter: str = "",
    filtered_rows: int = 1,
) -> dict:
    return {
        "session_name": session_name,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "jump_ts": jump_ts,
        "kind_filter": kind_filter,
        "event_filter": event_filter,
        "filtered_rows": int(filtered_rows),
    }


def build_research_replay_context(support_context: dict) -> dict:
    return {
        **build_research_context_base(
            session_name="warroom_ai_operator",
            start_ts="",
            end_ts="",
            jump_ts=support_context.get("event_ts") or "",
            kind_filter="all",
            event_filter=support_context.get("pressure_bias") or "",
            filtered_rows=1,
        ),
        **_build_tactic_review_carry(support_context),
    }


def build_tactic_review_carry(item: dict) -> dict:
    return _build_tactic_review_carry(item)


def normalize_watch_item_payload(item: dict) -> dict:
    return {
        "ts": item.get("ts"),
        "regime": item.get("regime"),
        "action": item.get("action"),
        "risk": item.get("risk"),
        "tactic_summary_lines": tuple(item.get("tactic_summary_lines") or ()),
        "tactic_interpretation_lines": tuple(
            item.get("tactic_interpretation_lines") or ()
        ),
        "primary_tactic_interpretation_line": str(
            item.get("primary_tactic_interpretation_line") or ""
        ),
        "tactic_primary_summary_line": str(
            item.get("tactic_primary_summary_line") or ""
        ),
    }


def build_watch_item(support_context: dict) -> dict:
    return normalize_watch_item_payload(
        {
            "ts": support_context.get("event_ts"),
            "regime": support_context.get("regime"),
            "action": support_context.get("advisory_action"),
            "risk": support_context.get("advisory_risk"),
            **_build_tactic_review_carry(support_context),
        }
    )