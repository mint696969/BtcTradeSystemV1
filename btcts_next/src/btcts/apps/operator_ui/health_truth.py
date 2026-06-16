# path: ./btcts_next/src/btcts/apps/operator_ui/health_truth.py
# desc: Health タブ向けの current truth 判定 helper。

from __future__ import annotations

from datetime import datetime, timezone


def parse_ts(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def age_seconds_from_ts(value: str | None) -> float | None:
    dt = parse_ts(value)
    if dt is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds())


def api_current_truth(state: dict) -> tuple[str, str]:
    health_payload = state.get("health") or {}
    rate_payload = state.get("rate") or {}
    rate_items = rate_payload.get("items") or {}
    bitflyer_rate = rate_items.get("bitflyer") or {}

    mode = str(bitflyer_rate.get("mode") or bitflyer_rate.get("summary_state") or "").upper()
    engaged = bool(bitflyer_rate.get("engaged"))
    last_429_ts = bitflyer_rate.get("last_429_ts")
    ok = health_payload.get("ok")

    if ok is False:
        return "red", "health_continuity_reason_health_not_ok"
    if mode == "CRIT":
        return "orange", "health_continuity_reason_warn_error"
    if last_429_ts or engaged or mode in {"WARN", "RECOVERY"}:
        return "yellow", "health_continuity_reason_warn_error"
    if mode == "NORMAL" or ok is True:
        return "green", "health_continuity_reason_steady"
    return "gray", "health_continuity_reason_no_data"


def ws_current_truth(
    *,
    lane_payload: dict,
    fallback_payload: dict,
) -> tuple[str, str]:
    ws_state = str(
        lane_payload.get("ws_state")
        or lane_payload.get("state")
        or fallback_payload.get("ws_state")
        or fallback_payload.get("lane_state")
        or ""
    ).upper()

    freshness = str(
        lane_payload.get("ws_freshness")
        or fallback_payload.get("ws_freshness")
        or ""
    ).upper()

    last_event_ts = (
        lane_payload.get("last_event_ts")
        or lane_payload.get("connected_ts")
        or fallback_payload.get("last_event_ts")
        or fallback_payload.get("connected_ts")
        or fallback_payload.get("ts")
    )
    age_sec = age_seconds_from_ts(last_event_ts)

    if not ws_state and age_sec is None:
        return "gray", "health_continuity_reason_no_data"
    if ws_state in {"BROKEN", "STOPPED", "FAILED", "ERROR"} or freshness == "BROKEN":
        return "red", "health_continuity_reason_warn_error"
    if freshness == "STALE":
        return "orange", "health_continuity_reason_warn_error"
    if ws_state in {"SYNCING", "CONNECTING"}:
        return "yellow", "health_continuity_reason_warn_error"
    if ws_state == "LIVE":
        # A live websocket can be quiet, especially executions/trades.  Do not
        # turn a live lane orange only because no trade/message event was
        # observed for 30 seconds; rely on explicit freshness/state when present.
        if freshness in {"", "LIVE", "QUIET"}:
            return "green", "health_continuity_reason_steady"
        return "yellow", "health_continuity_reason_warn_error"
    if ws_state == "QUIET":
        return "green", "health_continuity_reason_steady"
    if age_sec is not None and age_sec > 300:
        return "red", "health_continuity_reason_warn_error"
    if age_sec is not None and age_sec > 30:
        return "orange", "health_continuity_reason_warn_error"
    return "gray", "health_continuity_reason_no_data"
