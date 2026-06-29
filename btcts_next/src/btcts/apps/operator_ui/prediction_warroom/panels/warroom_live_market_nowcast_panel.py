# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py
# desc: PS-Q25B display-only WarRoom live market nowcast panel. Reads D-hot collector state for current board/executions/spread/freshness; no writes, scheduler, prediction artifact mutation, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

import streamlit as st

from btcts.apps.operator_ui.components import live_shell

WARROOM_LIVE_MARKET_NOWCAST_PANEL_VERSION = "prediction_warroom.live_market_nowcast_panel.ps_q25b.v1"
WARROOM_LIVE_MARKET_NOWCAST_REFRESH_MODE = "poll_fast"
WARROOM_LIVE_MARKET_NOWCAST_REFRESH_SEC = 3
Q25B_PAGE_ID = "warroom"
Q25B_ZONE_ID = "live_market_nowcast_zone"
Q25B_WIDGET_ID = "warroom_live_market_nowcast_panel"
Q25B_DEFAULT_HOT_ROOT_HINT = r"D:\btc_ts_hot"

STATE_PATHS = {
    "market_state": "state/collector_vnext/unified_market_state_status.json",
    "health": "state/collector_vnext/unified_health.json",
    "daemon": "state/collector_vnext/unified_daemon_status.json",
    "executions": "state/collector_vnext/unified_executions_status.json",
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _parse_utc(value: Any) -> datetime | None:
    text = _clean(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _format_jst(value: Any) -> str:
    parsed = _parse_utc(value)
    if parsed is None:
        return _clean(value) or "-"
    return parsed.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S JST")


def _age_sec(value: Any, *, now: datetime | None = None) -> int | None:
    parsed = _parse_utc(value)
    if parsed is None:
        return None
    reference = now or _utc_now()
    return max(0, int((reference - parsed).total_seconds()))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {"_missing": True, "_path": str(path)}
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_error": str(exc), "_path": str(path)}


def load_warroom_live_market_nowcast_sources(*, hot_root: str | Path = Q25B_DEFAULT_HOT_ROOT_HINT) -> dict[str, dict[str, Any]]:
    root = Path(str(hot_root))
    return {name: _load_json(root / relative) for name, relative in STATE_PATHS.items()}


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _spread_bps(best_bid: Any, best_ask: Any, spread: Any) -> float | None:
    bid = _float(best_bid)
    ask = _float(best_ask)
    spr = _float(spread)
    if bid is None or ask is None or spr is None:
        return None
    mid = (bid + ask) / 2.0
    if mid <= 0:
        return None
    return (spr / mid) * 10000.0


def _spread_state(spread_bps: float | None) -> str:
    if spread_bps is None:
        return "unknown"
    if spread_bps <= 5.0:
        return "tight"
    if spread_bps <= 12.0:
        return "normal"
    return "wide_caution"


def _freshness_state(*, health: Mapping[str, Any], market_state: Mapping[str, Any], executions: Mapping[str, Any], now: datetime) -> str:
    market_age = _age_sec(market_state.get("last_event_ts") or market_state.get("ts"), now=now)
    health_age = _age_sec(health.get("ts"), now=now)
    executions_age = _age_sec(executions.get("ts"), now=now)
    ages = [age for age in (market_age, health_age, executions_age) if age is not None]
    if not ages:
        return "unknown"
    max_age = max(ages)
    if max_age <= 5:
        return "live"
    if max_age <= 15:
        return "slightly_delayed"
    return "stale_caution"


def _live_state_summary(packet: Mapping[str, Any]) -> str:
    ok = packet.get("collector_ok") is True
    lane = _clean(packet.get("market_lane_state")) or "unknown"
    ws_board = _clean(packet.get("ws_state")) or "unknown"
    ws_exec = _clean(packet.get("ws_executions_state")) or "unknown"
    spread_state = _clean(packet.get("spread_state")) or "unknown"
    freshness = _clean(packet.get("nowcast_freshness_state")) or "unknown"
    if ok and lane == "live" and ws_board == "LIVE" and spread_state in {"tight", "normal"} and freshness in {"live", "slightly_delayed"}:
        return "current_market_state_live_observable"
    if freshness == "stale_caution" or spread_state == "wide_caution":
        return "current_market_state_caution"
    if ws_board != "LIVE" or ws_exec not in {"LIVE", "QUIET"}:
        return "current_market_state_stream_attention"
    return "current_market_state_review_required"


def build_warroom_live_market_nowcast_packet(
    *,
    sources: Mapping[str, Any] | None = None,
    hot_root: str | Path = Q25B_DEFAULT_HOT_ROOT_HINT,
    fragment_enabled: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    now_utc = now or _utc_now()
    data = dict(sources or load_warroom_live_market_nowcast_sources(hot_root=hot_root))
    market_state = _as_mapping(data.get("market_state"))
    health = _as_mapping(data.get("health"))
    daemon = _as_mapping(data.get("daemon"))
    executions = _as_mapping(data.get("executions"))
    spread_bps = _spread_bps(market_state.get("last_best_bid"), market_state.get("last_best_ask"), market_state.get("last_spread"))
    packet: dict[str, Any] = {
        "ok": True,
        "nowcast_panel_version": WARROOM_LIVE_MARKET_NOWCAST_PANEL_VERSION,
        "nowcast_role": "current_market_state_not_prediction",
        "source_root_hint": str(hot_root),
        "fragment_enabled": bool(fragment_enabled),
        "refresh_mode": WARROOM_LIVE_MARKET_NOWCAST_REFRESH_MODE,
        "refresh_interval_sec": WARROOM_LIVE_MARKET_NOWCAST_REFRESH_SEC,
        "panel_heartbeat_utc": now_utc.isoformat().replace("+00:00", "Z"),
        "panel_heartbeat_jst": _format_jst(now_utc.isoformat().replace("+00:00", "Z")),
        "market_uid": _clean(market_state.get("last_market_uid")) or "-",
        "symbol": _clean(market_state.get("last_symbol_raw")) or _clean(health.get("symbol")) or "FX_BTC_JPY",
        "market_lane_state": _clean(market_state.get("lane_state")) or "unknown",
        "market_state_ts": _clean(market_state.get("ts")) or "-",
        "market_state_jst": _format_jst(market_state.get("ts")),
        "market_event_ts": _clean(market_state.get("last_event_ts")) or "-",
        "market_event_jst": _format_jst(market_state.get("last_event_ts")),
        "market_event_age_sec": _age_sec(market_state.get("last_event_ts") or market_state.get("ts"), now=now_utc),
        "best_bid": market_state.get("last_best_bid"),
        "best_ask": market_state.get("last_best_ask"),
        "spread": market_state.get("last_spread"),
        "spread_bps": None if spread_bps is None else round(spread_bps, 3),
        "spread_state": _spread_state(spread_bps),
        "source_series_id": _clean(market_state.get("last_source_series_id")) or "-",
        "collector_ok": health.get("ok") is True,
        "collector_status": _clean(health.get("status")) or "unknown",
        "rest_mode": _clean(health.get("rest_mode")) or "unknown",
        "ws_state": _clean(health.get("ws_state")) or "unknown",
        "ws_freshness": _clean(health.get("ws_freshness")) or "unknown",
        "gap_detected": health.get("gap_detected") is True,
        "resync_active": health.get("resync_active") is True,
        "requests_60s": health.get("requests_60s"),
        "utilization": health.get("utilization"),
        "last_429_ts": health.get("last_429_ts"),
        "ws_last_event_ts": _clean(health.get("ws_last_event_ts")) or "-",
        "ws_last_event_age_sec": _age_sec(health.get("ws_last_event_ts"), now=now_utc),
        "ws_executions_state": _clean(health.get("ws_executions_state") or executions.get("ws_state")) or "unknown",
        "ws_executions_freshness": _clean(health.get("ws_executions_freshness")) or "unknown",
        "ws_executions_last_event_ts": _clean(health.get("ws_executions_last_event_ts") or executions.get("ts")) or "-",
        "ws_executions_last_event_age_sec": _age_sec(health.get("ws_executions_last_event_ts") or executions.get("ts"), now=now_utc),
        "ws_executions_trade_count": health.get("ws_executions_trade_count") or executions.get("trade_count"),
        "daemon_mode": _clean(daemon.get("mode")) or "unknown",
        "daemon_cycle_no": daemon.get("cycle_no"),
        "daemon_last_success_ts": _clean(daemon.get("last_success_ts")) or "-",
        "daemon_last_success_age_sec": _age_sec(daemon.get("last_success_ts"), now=now_utc),
        "daemon_stop_requested": daemon.get("stop_requested") is True,
        "daemon_consecutive_failures": daemon.get("consecutive_failures"),
        "daemon_last_error": daemon.get("last_error"),
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
    packet["nowcast_freshness_state"] = _freshness_state(health=health, market_state=market_state, executions=executions, now=now_utc)
    packet["current_state_summary"] = _live_state_summary(packet)
    packet["operator_note"] = "current-state nowcast; not a future prediction and not a trade instruction"
    packet["attention_flags"] = [
        name
        for name, active in (
            ("collector_not_ok", packet.get("collector_ok") is not True),
            ("market_lane_not_live", packet.get("market_lane_state") != "live"),
            ("board_not_live", packet.get("ws_state") != "LIVE"),
            ("spread_wide_caution", packet.get("spread_state") == "wide_caution"),
            ("gap_detected", packet.get("gap_detected") is True),
            ("resync_active", packet.get("resync_active") is True),
            ("daemon_stop_requested", packet.get("daemon_stop_requested") is True),
            ("daemon_failures_present", bool(packet.get("daemon_consecutive_failures"))),
            ("nowcast_stale_caution", packet.get("nowcast_freshness_state") == "stale_caution"),
            ("rate_limit_recent", bool(packet.get("last_429_ts"))),
        )
        if active
    ]
    return packet


def warroom_live_market_nowcast_metric_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"item": "current_state", "value": packet.get("current_state_summary"), "note": "current state, not prediction"},
        {"item": "market_uid", "value": packet.get("market_uid"), "note": packet.get("symbol")},
        {"item": "best_bid", "value": packet.get("best_bid"), "note": "latest market state"},
        {"item": "best_ask", "value": packet.get("best_ask"), "note": "latest market state"},
        {"item": "spread", "value": packet.get("spread"), "note": f"{packet.get('spread_bps')} bps / {packet.get('spread_state')}"},
        {"item": "market_event_age_sec", "value": packet.get("market_event_age_sec"), "note": packet.get("market_event_jst")},
        {"item": "ws_board", "value": packet.get("ws_state"), "note": packet.get("ws_freshness")},
        {"item": "ws_executions", "value": packet.get("ws_executions_state"), "note": packet.get("ws_executions_freshness")},
        {"item": "trade_count", "value": packet.get("ws_executions_trade_count"), "note": "ws executions"},
        {"item": "collector", "value": packet.get("collector_status"), "note": f"rest={packet.get('rest_mode')} util={packet.get('utilization')}"},
        {"item": "gap_resync", "value": f"gap={packet.get('gap_detected')} resync={packet.get('resync_active')}", "note": "must be false/false for clean current state"},
        {"item": "attention_flags", "value": ",".join(str(item) for item in packet.get("attention_flags") or []) or "none", "note": "operator review flags"},
    ]


def render_warroom_live_market_nowcast_panel(*, fragment_enabled: bool = True) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet = build_warroom_live_market_nowcast_packet(fragment_enabled=bool(fragment_enabled))
        packet_holder.update(packet)
        st.caption("PS-Q25B Live Market Nowcast: current board/executions/spread/freshness. This is not a future prediction and not a trade instruction.")
        if packet.get("current_state_summary") == "current_market_state_live_observable":
            st.success(f"🟢 Live current state | {packet.get('market_uid')} | spread={packet.get('spread')} ({packet.get('spread_bps')} bps) | market_age={packet.get('market_event_age_sec')}s")
        elif packet.get("current_state_summary") == "current_market_state_caution":
            st.warning(f"🟡 Current state caution | flags={','.join(packet.get('attention_flags') or []) or 'none'}")
        else:
            st.warning(f"🟠 Current state review required | {packet.get('current_state_summary')} | flags={','.join(packet.get('attention_flags') or []) or 'none'}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("best bid", str(packet.get("best_bid") or "-"))
        c2.metric("best ask", str(packet.get("best_ask") or "-"))
        c3.metric("spread", str(packet.get("spread") or "-"), delta=str(packet.get("spread_state") or "-"))
        c4.metric("market age", "-" if packet.get("market_event_age_sec") is None else f"{packet.get('market_event_age_sec')}s")
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("board WS", str(packet.get("ws_state") or "-"), delta=str(packet.get("ws_freshness") or "-"))
        c6.metric("exec WS", str(packet.get("ws_executions_state") or "-"), delta=str(packet.get("ws_executions_freshness") or "-"))
        c7.metric("trades", str(packet.get("ws_executions_trade_count") or "-"))
        c8.metric("refresh", f"{packet.get('refresh_interval_sec')}s", delta=packet.get("panel_heartbeat_jst"))
        st.dataframe(warroom_live_market_nowcast_metric_rows(packet), width="stretch", hide_index=True)
        st.text(
            "PS_Q25B_LIVE_MARKET_NOWCAST "
            f"current_state_summary={packet.get('current_state_summary')} "
            f"nowcast_freshness_state={packet.get('nowcast_freshness_state')} "
            f"market_event_age_sec={packet.get('market_event_age_sec')} "
            f"spread_bps={packet.get('spread_bps')} "
            f"attention_flags={','.join(packet.get('attention_flags') or []) or 'none'} "
            "read_only=true display_only=true autotrade=false broker=false"
        )

    meta = live_shell.make_slot_meta(
        Q25B_PAGE_ID,
        Q25B_ZONE_ID,
        Q25B_WIDGET_ID,
        label="Live Market Nowcast / current state",
        tone="strong",
        help_text="High-frequency display-only current market state. Not prediction, not trading.",
        refresh_mode=WARROOM_LIVE_MARKET_NOWCAST_REFRESH_MODE,
        priority=10,
        overlay_enabled=False,
        partial_update_enabled=True,
    )
    live_shell.render_fragment_slot(
        meta,
        _render_body,
        enabled=bool(fragment_enabled),
        default_sec=WARROOM_LIVE_MARKET_NOWCAST_REFRESH_SEC,
    )
    return packet_holder or build_warroom_live_market_nowcast_packet(fragment_enabled=bool(fragment_enabled))
