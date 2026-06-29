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
WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_VERSION = "prediction_warroom.live_nowcast_operator_summary.ps_q25c.v1"
WARROOM_LIVE_NOWCAST_SOURCE_LAYERING_VERSION = "prediction_warroom.live_nowcast_source_importance_signal_layering.ps_q25d.v1"
WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION = "prediction_warroom.live_nowcast_composite_score_history_mini_trend.ps_q25e.v1"
WARROOM_LIVE_NOWCAST_HISTORY_SESSION_KEY = "warroom_live_nowcast_composite_score_history_ps_q25e"
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



_ATTENTION_SEVERITY_ORDER = {
    "ok": 0,
    "info": 1,
    "warning": 2,
    "critical": 3,
}

_ATTENTION_DESCRIPTIONS_JA = {
    "collector_not_ok": ("critical", "Collector が healthy ではありません", "現在状態の信頼性が落ちています。取引判断の根拠にしないでください。"),
    "market_lane_not_live": ("critical", "market lane が live ではありません", "板・市場状態の更新が止まっている可能性があります。"),
    "board_not_live": ("critical", "板 WS が LIVE ではありません", "現在価格・spread の信頼性が落ちます。"),
    "spread_wide_caution": ("warning", "spread が広いです", "約定コスト・滑り・薄板に注意してください。"),
    "gap_detected": ("critical", "データ gap を検出しています", "連続性が崩れているため、現在状態の解釈を保留してください。"),
    "resync_active": ("critical", "resync 中です", "再同期完了まで現在状態の判断を弱めてください。"),
    "daemon_stop_requested": ("critical", "daemon stop_requested が true です", "Collector の継続稼働を確認してください。"),
    "daemon_failures_present": ("warning", "daemon failure が存在します", "直近失敗の影響を確認してください。"),
    "nowcast_stale_caution": ("warning", "nowcast が stale です", "現在状態として古くなっています。"),
    "rate_limit_recent": ("warning", "直近 rate limit があります", "REST 制限の影響に注意してください。"),
}

_ATTENTION_DESCRIPTIONS_EN = {
    "collector_not_ok": ("critical", "Collector is not healthy", "Do not use this current state as a decision basis."),
    "market_lane_not_live": ("critical", "Market lane is not live", "Board/current-state updates may be stopped."),
    "board_not_live": ("critical", "Board WS is not LIVE", "Price/spread reliability is reduced."),
    "spread_wide_caution": ("warning", "Spread is wide", "Watch execution cost, slippage, and thin liquidity."),
    "gap_detected": ("critical", "Data gap detected", "Current-state continuity is broken."),
    "resync_active": ("critical", "Resync active", "Wait for resync completion before relying on nowcast."),
    "daemon_stop_requested": ("critical", "Daemon stop requested", "Confirm collector continuity."),
    "daemon_failures_present": ("warning", "Daemon failures present", "Check recent failure impact."),
    "nowcast_stale_caution": ("warning", "Nowcast stale", "Current-state data is old."),
    "rate_limit_recent": ("warning", "Recent rate limit", "REST throttling may affect source coverage."),
}


def classify_warroom_live_nowcast_attention(packet: Mapping[str, Any], *, lang: str = "ja") -> list[dict[str, str]]:
    descriptions = _ATTENTION_DESCRIPTIONS_JA if lang == "ja" else _ATTENTION_DESCRIPTIONS_EN
    rows: list[dict[str, str]] = []
    for code in packet.get("attention_flags") or []:
        severity, label, note = descriptions.get(str(code), ("warning", str(code), "Review this attention flag."))
        rows.append({"code": str(code), "severity": severity, "label": label, "operator_note": note})
    if rows:
        return rows
    if lang == "ja":
        return [{"code": "none", "severity": "ok", "label": "現在状態の重大な注意フラグはありません", "operator_note": "ただしこれは予測ではなく、現在状態の観測です。"}]
    return [{"code": "none", "severity": "ok", "label": "No major current-state attention flags", "operator_note": "This is current-state observation, not prediction."}]


def _max_attention_severity(rows: list[Mapping[str, Any]]) -> str:
    severity = "ok"
    for row in rows:
        candidate = _clean(row.get("severity")) or "ok"
        if _ATTENTION_SEVERITY_ORDER.get(candidate, 0) > _ATTENTION_SEVERITY_ORDER.get(severity, 0):
            severity = candidate
    return severity


def build_warroom_live_nowcast_operator_summary_packet(packet: Mapping[str, Any], *, lang: str = "ja") -> dict[str, Any]:
    attention_rows = classify_warroom_live_nowcast_attention(packet, lang=lang)
    max_severity = _max_attention_severity(attention_rows)
    freshness = _clean(packet.get("nowcast_freshness_state")) or "unknown"
    state = _clean(packet.get("current_state_summary")) or "unknown"
    spread_state = _clean(packet.get("spread_state")) or "unknown"
    if max_severity == "critical" or freshness == "stale_caution" or state in {"current_market_state_stream_attention", "current_market_state_review_required"}:
        grade = "not_usable_for_current_decision"
        tone = "critical"
    elif max_severity == "warning" or spread_state == "wide_caution":
        grade = "usable_with_caution"
        tone = "warning"
    elif state == "current_market_state_live_observable" and freshness in {"live", "slightly_delayed"}:
        grade = "live_observable"
        tone = "ok"
    else:
        grade = "review_required"
        tone = "info"
    if lang == "ja":
        summary_map = {
            "live_observable": "現在状態は観測可能です。板・collector・主要WSは利用可能で、重大な注意フラグはありません。",
            "usable_with_caution": "現在状態は利用できますが注意が必要です。注意フラグを確認してください。",
            "not_usable_for_current_decision": "現在状態は判断材料として弱いです。stale/gap/resync/stream 状態を確認してください。",
            "review_required": "現在状態は追加確認が必要です。表示値と attention を確認してください。",
        }
        instruction_map = {
            "live_observable": "予測を見る前の土台として利用できます。ただしこれは予測ではなく現在状態の観測であり、売買指示ではありません。",
            "usable_with_caution": "予測や判断を弱め、spread・freshness・WS状態を優先確認してください。",
            "not_usable_for_current_decision": "予測評価や売買判断より先にデータ状態を確認してください。",
            "review_required": "人間が状態を確認してから予測を読んでください。",
        }
    else:
        summary_map = {
            "live_observable": "Current market state is observable; major live sources are usable with no major attention flags.",
            "usable_with_caution": "Current market state is usable with caution; review attention flags.",
            "not_usable_for_current_decision": "Current market state is weak for decision support; check stale/gap/resync/stream state.",
            "review_required": "Current market state needs additional operator review.",
        }
        instruction_map = {
            "live_observable": "Usable as the foundation before reading predictions. Not a trade instruction.",
            "usable_with_caution": "De-weight predictions and inspect spread/freshness/WS state first.",
            "not_usable_for_current_decision": "Confirm data state before prediction review or trading decisions.",
            "review_required": "Review current state before reading predictions.",
        }
    return {
        "ok": True,
        "operator_summary_version": WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_VERSION,
        "nowcast_role": "current_market_state_not_prediction",
        "operator_state_grade": grade,
        "operator_attention_severity": tone,
        "operator_summary_text": summary_map[grade],
        "operator_instruction_text": instruction_map[grade],
        "attention_rows": attention_rows,
        "attention_flag_count": len([row for row in attention_rows if row.get("code") != "none"]),
        "current_state_summary": packet.get("current_state_summary"),
        "nowcast_freshness_state": packet.get("nowcast_freshness_state"),
        "spread_state": packet.get("spread_state"),
        "spread_bps": packet.get("spread_bps"),
        "market_event_age_sec": packet.get("market_event_age_sec"),
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "current_state_not_prediction": True,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def warroom_live_nowcast_operator_summary_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"item": "operator_state_grade", "value": summary.get("operator_state_grade"), "note": summary.get("operator_summary_text")},
        {"item": "attention_severity", "value": summary.get("operator_attention_severity"), "note": f"flags={summary.get('attention_flag_count')}"},
        {"item": "operator_instruction", "value": summary.get("operator_instruction_text"), "note": "current-state guidance only"},
        {"item": "freshness", "value": summary.get("nowcast_freshness_state"), "note": f"market_age={summary.get('market_event_age_sec')}s"},
        {"item": "spread", "value": summary.get("spread_state"), "note": f"{summary.get('spread_bps')} bps"},
    ]


def _render_warroom_live_nowcast_operator_summary(packet: Mapping[str, Any], *, lang: str = "ja") -> Mapping[str, Any]:
    summary = build_warroom_live_nowcast_operator_summary_packet(packet, lang=lang)
    tone = summary.get("operator_attention_severity")
    message = f"{summary.get('operator_summary_text')} {summary.get('operator_instruction_text')}"
    if tone == "critical":
        st.error(message)
    elif tone == "warning":
        st.warning(message)
    elif tone == "ok":
        st.success(message)
    else:
        st.info(message)
    st.dataframe(warroom_live_nowcast_operator_summary_rows(summary), width="stretch", hide_index=True)
    st.dataframe(summary.get("attention_rows") or [], width="stretch", hide_index=True)
    return summary



_SOURCE_IMPORTANCE_PROFILES = {
    "current_nowcast": {
        "board_spread": 1.00,
        "collector_freshness": 0.95,
        "ws_board_state": 0.95,
        "gap_resync": 0.95,
        "executions_flow": 0.75,
        "rate_limit_pressure": 0.55,
        "daemon_continuity": 0.70,
    },
    "tactical_5m": {
        "executions_flow": 0.95,
        "board_spread": 0.90,
        "collector_freshness": 0.90,
        "gap_resync": 0.85,
        "rate_limit_pressure": 0.55,
        "daemon_continuity": 0.60,
    },
    "tactical_15m": {
        "executions_flow": 0.90,
        "board_spread": 0.75,
        "collector_freshness": 0.85,
        "gap_resync": 0.80,
        "rate_limit_pressure": 0.50,
        "daemon_continuity": 0.55,
    },
    "scenario_30m_1h": {
        "collector_freshness": 0.85,
        "gap_resync": 0.80,
        "executions_flow": 0.70,
        "board_spread": 0.60,
        "rate_limit_pressure": 0.50,
        "daemon_continuity": 0.55,
    },
}

_SIGNAL_LAYER_DESCRIPTIONS_JA = {
    "foundation_integrity": "まずデータ連続性・freshness・gap/resync を確認する土台レイヤー。",
    "microstructure_now": "板、best bid/ask、spread、WS board を見る現在状態レイヤー。",
    "trade_flow_now": "約定WS、trade count、executions freshness を見る短期フローレイヤー。",
    "operational_pressure": "REST利用率、rate limit、daemon状態を見る運用圧力レイヤー。",
    "prediction_input_gate": "この現在状態を予測入力の前提として使えるかを判断するゲート。",
}


def build_warroom_live_nowcast_source_importance_packet(packet: Mapping[str, Any], summary: Mapping[str, Any] | None = None, *, lang: str = "ja") -> dict[str, Any]:
    summary_map = summary if isinstance(summary, Mapping) else {}
    attention = {str(item) for item in packet.get("attention_flags") or []}
    spread_state = _clean(packet.get("spread_state")) or "unknown"
    freshness = _clean(packet.get("nowcast_freshness_state")) or "unknown"
    operator_grade = _clean(summary_map.get("operator_state_grade")) or "unknown"
    rows: list[dict[str, Any]] = []

    def add(layer: str, source: str, role: str, importance: float, status: str, reason: str) -> None:
        rows.append({
            "layer": layer,
            "source": source,
            "role": role,
            "importance": round(float(importance), 2),
            "status": status,
            "reason": reason,
        })

    foundation_status = "usable" if freshness in {"live", "slightly_delayed"} and not ({"gap_detected", "resync_active"} & attention) else "blocked"
    add("foundation_integrity", "collector_freshness", "current-state trust gate", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["collector_freshness"], foundation_status, f"freshness={freshness}")
    add("foundation_integrity", "gap_resync", "continuity gate", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["gap_resync"], "blocked" if {"gap_detected", "resync_active"} & attention else "usable", "gap/resync must stay false before reading prediction")
    add("microstructure_now", "board_spread", "best bid/ask and cost state", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["board_spread"], "caution" if spread_state == "wide_caution" else "usable", f"spread_state={spread_state} spread_bps={packet.get('spread_bps')}")
    add("microstructure_now", "ws_board_state", "board stream liveness", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["ws_board_state"], "usable" if packet.get("ws_state") == "LIVE" else "blocked", f"ws_state={packet.get('ws_state')}")
    add("trade_flow_now", "executions_flow", "recent trade-flow liveness", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["executions_flow"], "usable" if packet.get("ws_executions_state") == "LIVE" else "caution", f"exec_state={packet.get('ws_executions_state')} exec_freshness={packet.get('ws_executions_freshness')}")
    add("operational_pressure", "rate_limit_pressure", "REST/API pressure context", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["rate_limit_pressure"], "caution" if "rate_limit_recent" in attention else "usable", f"utilization={packet.get('utilization')} last_429={packet.get('last_429_ts')}")
    add("operational_pressure", "daemon_continuity", "collector daemon continuity", _SOURCE_IMPORTANCE_PROFILES["current_nowcast"]["daemon_continuity"], "blocked" if packet.get("daemon_stop_requested") is True else "usable", f"daemon_mode={packet.get('daemon_mode')} failures={packet.get('daemon_consecutive_failures')}")

    top_read_order = ["foundation_integrity", "microstructure_now", "trade_flow_now", "operational_pressure", "prediction_input_gate"]
    if operator_grade == "live_observable" and foundation_status == "usable":
        input_gate = "prediction_input_foundation_usable"
    elif operator_grade == "usable_with_caution":
        input_gate = "prediction_input_foundation_caution"
    else:
        input_gate = "prediction_input_foundation_weak"
    if lang == "ja":
        instruction = "予測を見る前に foundation_integrity → microstructure_now → trade_flow_now の順で確認してください。これは現在状態の信号レイヤーであり、売買指示ではありません。"
    else:
        instruction = "Before reading predictions, check foundation_integrity → microstructure_now → trade_flow_now. This is current-state signal layering, not a trade instruction."
    return {
        "ok": True,
        "source_layering_version": WARROOM_LIVE_NOWCAST_SOURCE_LAYERING_VERSION,
        "nowcast_role": "current_market_state_not_prediction",
        "source_importance_rows": rows,
        "source_importance_row_count": len(rows),
        "read_order": top_read_order,
        "prediction_input_gate": input_gate,
        "operator_instruction_text": instruction,
        "profiles": _SOURCE_IMPORTANCE_PROFILES,
        "layer_descriptions": _SIGNAL_LAYER_DESCRIPTIONS_JA if lang == "ja" else {},
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "current_state_not_prediction": True,
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


def warroom_live_nowcast_source_layer_summary_rows(layering: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"item": "source_layering_version", "value": layering.get("source_layering_version"), "note": "display-only current-state layer"},
        {"item": "prediction_input_gate", "value": layering.get("prediction_input_gate"), "note": "whether current state is a usable foundation before prediction"},
        {"item": "read_order", "value": " → ".join(str(item) for item in layering.get("read_order") or []), "note": "operator read order"},
        {"item": "operator_instruction", "value": layering.get("operator_instruction_text"), "note": "not a trade instruction"},
    ]


def _render_warroom_live_nowcast_source_layering(packet: Mapping[str, Any], summary: Mapping[str, Any]) -> Mapping[str, Any]:
    layering = build_warroom_live_nowcast_source_importance_packet(packet, summary, lang="ja")
    st.caption("PS-Q25D source importance / signal layering: read current-state sources before predictions. Display-only; no execution.")
    st.dataframe(warroom_live_nowcast_source_layer_summary_rows(layering), width="stretch", hide_index=True)
    st.dataframe(layering.get("source_importance_rows") or [], width="stretch", hide_index=True)
    return layering




def _score_penalty_from_source_row(row: Mapping[str, Any]) -> float:
    importance = _float(row.get("importance")) or 0.0
    status = _clean(row.get("status"))
    if status == "blocked":
        return 28.0 * importance
    if status == "caution":
        return 10.0 * importance
    if status not in {"usable", ""}:
        return 6.0 * importance
    return 0.0


def _bounded_score(value: float) -> int:
    return int(round(max(0.0, min(100.0, value))))


def build_warroom_live_nowcast_composite_score_packet(
    packet: Mapping[str, Any],
    operator_summary: Mapping[str, Any],
    source_layering: Mapping[str, Any],
) -> dict[str, Any]:
    score = 100.0
    penalty_reasons: list[str] = []
    for row in source_layering.get("source_importance_rows") or []:
        if not isinstance(row, Mapping):
            continue
        penalty = _score_penalty_from_source_row(row)
        if penalty:
            score -= penalty
            penalty_reasons.append(f"{row.get('source')}:{row.get('status')}:-{round(penalty, 1)}")
    severity = _clean(operator_summary.get("operator_attention_severity")) or "ok"
    if severity == "critical":
        score -= 35.0
        penalty_reasons.append("operator_attention=critical:-35")
    elif severity == "warning":
        score -= 12.0
        penalty_reasons.append("operator_attention=warning:-12")
    elif severity == "info":
        score -= 5.0
        penalty_reasons.append("operator_attention=info:-5")
    freshness = _clean(packet.get("nowcast_freshness_state")) or "unknown"
    if freshness == "stale_caution":
        score -= 24.0
        penalty_reasons.append("freshness=stale_caution:-24")
    elif freshness == "unknown":
        score -= 12.0
        penalty_reasons.append("freshness=unknown:-12")
    elif freshness == "slightly_delayed":
        score -= 3.0
        penalty_reasons.append("freshness=slightly_delayed:-3")
    spread_state = _clean(packet.get("spread_state")) or "unknown"
    if spread_state == "wide_caution":
        score -= 12.0
        penalty_reasons.append("spread=wide_caution:-12")
    elif spread_state == "unknown":
        score -= 5.0
        penalty_reasons.append("spread=unknown:-5")
    market_age = _float(packet.get("market_event_age_sec"))
    if market_age is None:
        score -= 8.0
        penalty_reasons.append("market_age=unknown:-8")
    elif market_age > 30:
        score -= 16.0
        penalty_reasons.append("market_age>30s:-16")
    elif market_age > 15:
        score -= 8.0
        penalty_reasons.append("market_age>15s:-8")
    composite_score = _bounded_score(score)
    if composite_score >= 85:
        grade = "high_quality_current_state"
        note = "現在状態の土台はかなり良好です。"
    elif composite_score >= 70:
        grade = "usable_current_state"
        note = "現在状態は利用可能です。軽い遅延や注意点は確認してください。"
    elif composite_score >= 50:
        grade = "caution_current_state"
        note = "現在状態は注意付きです。予測や判断を弱めてください。"
    else:
        grade = "weak_current_state"
        note = "現在状態の信頼性が弱いです。予測を見る前にデータ状態を確認してください。"
    return {
        "ok": True,
        "composite_score_version": WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION,
        "nowcast_role": "current_market_state_not_prediction",
        "current_state_score": composite_score,
        "current_state_score_grade": grade,
        "current_state_score_note": note,
        "penalty_reasons": penalty_reasons,
        "penalty_count": len(penalty_reasons),
        "prediction_input_gate": source_layering.get("prediction_input_gate"),
        "operator_attention_severity": operator_summary.get("operator_attention_severity"),
        "operator_state_grade": operator_summary.get("operator_state_grade"),
        "freshness_state": packet.get("nowcast_freshness_state"),
        "spread_state": packet.get("spread_state"),
        "spread_bps": packet.get("spread_bps"),
        "market_event_age_sec": packet.get("market_event_age_sec"),
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "current_state_not_prediction": True,
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


def build_warroom_live_nowcast_history_mini_trend_packet(history: list[Mapping[str, Any]]) -> dict[str, Any]:
    samples = [item for item in history if isinstance(item, Mapping)]
    if not samples:
        trend = "insufficient_history"
        delta = 0
    else:
        first = int(_float(samples[0].get("current_state_score")) or 0)
        last = int(_float(samples[-1].get("current_state_score")) or 0)
        delta = last - first
        if len(samples) < 2:
            trend = "insufficient_history"
        elif delta >= 5:
            trend = "improving"
        elif delta <= -5:
            trend = "deteriorating"
        else:
            trend = "stable"
    return {
        "ok": True,
        "mini_trend_version": WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION,
        "history_sample_count": len(samples),
        "current_state_score_trend": trend,
        "current_state_score_delta": delta,
        "latest_score": samples[-1].get("current_state_score") if samples else None,
        "latest_grade": samples[-1].get("current_state_score_grade") if samples else None,
        "history_scores": [item.get("current_state_score") for item in samples],
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "current_state_not_prediction": True,
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


def warroom_live_nowcast_composite_score_rows(composite: Mapping[str, Any], mini_trend: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    trend = mini_trend if isinstance(mini_trend, Mapping) else {}
    return [
        {"item": "current_state_score", "value": composite.get("current_state_score"), "note": composite.get("current_state_score_grade")},
        {"item": "score_note", "value": composite.get("current_state_score_note"), "note": "current-state only"},
        {"item": "mini_trend", "value": trend.get("current_state_score_trend"), "note": f"delta={trend.get('current_state_score_delta')} samples={trend.get('history_sample_count')}"},
        {"item": "prediction_input_gate", "value": composite.get("prediction_input_gate"), "note": "foundation before prediction"},
        {"item": "penalty_reasons", "value": ",".join(str(item) for item in composite.get("penalty_reasons") or []) or "none", "note": "score deductions"},
    ]


def _append_warroom_live_nowcast_session_history(composite: Mapping[str, Any], packet: Mapping[str, Any], *, max_samples: int = 12) -> list[dict[str, Any]]:
    existing = st.session_state.get(WARROOM_LIVE_NOWCAST_HISTORY_SESSION_KEY)
    history = list(existing) if isinstance(existing, list) else []
    sample = {
        "ts": packet.get("panel_heartbeat_utc"),
        "market_event_age_sec": packet.get("market_event_age_sec"),
        "spread_bps": packet.get("spread_bps"),
        "current_state_score": composite.get("current_state_score"),
        "current_state_score_grade": composite.get("current_state_score_grade"),
        "prediction_input_gate": composite.get("prediction_input_gate"),
    }
    if not history or history[-1] != sample:
        history.append(sample)
    history = history[-int(max_samples):]
    st.session_state[WARROOM_LIVE_NOWCAST_HISTORY_SESSION_KEY] = history
    return history


def _render_warroom_live_nowcast_composite_score(packet: Mapping[str, Any], operator_summary: Mapping[str, Any], source_layering: Mapping[str, Any]) -> Mapping[str, Any]:
    composite = build_warroom_live_nowcast_composite_score_packet(packet, operator_summary, source_layering)
    history = _append_warroom_live_nowcast_session_history(composite, packet)
    mini_trend = build_warroom_live_nowcast_history_mini_trend_packet(history)
    st.caption("PS-Q25E current-state composite score / mini trend: display-only session history, not persisted, not prediction.")
    st.metric("current-state score", str(composite.get("current_state_score")), delta=str(mini_trend.get("current_state_score_trend")))
    st.dataframe(warroom_live_nowcast_composite_score_rows(composite, mini_trend), width="stretch", hide_index=True)
    return {"composite": composite, "mini_trend": mini_trend}


def render_warroom_live_market_nowcast_panel(*, fragment_enabled: bool = True) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet = build_warroom_live_market_nowcast_packet(fragment_enabled=bool(fragment_enabled))
        packet_holder.update(packet)
        st.caption("PS-Q25B/Q25C Live Market Nowcast: current board/executions/spread/freshness plus operator classification. This is not a future prediction and not a trade instruction.")
        operator_summary = _render_warroom_live_nowcast_operator_summary(packet, lang="ja")
        source_layering = _render_warroom_live_nowcast_source_layering(packet, operator_summary)
        score_packet = _render_warroom_live_nowcast_composite_score(packet, operator_summary, source_layering)
        composite_score = score_packet.get("composite", {}) if isinstance(score_packet, Mapping) else {}
        mini_trend = score_packet.get("mini_trend", {}) if isinstance(score_packet, Mapping) else {}
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
            f"operator_state_grade={operator_summary.get('operator_state_grade')} "
            f"operator_attention_severity={operator_summary.get('operator_attention_severity')} "
            f"prediction_input_gate={source_layering.get('prediction_input_gate')} "
            f"current_state_score={composite_score.get('current_state_score')} "
            f"current_state_score_trend={mini_trend.get('current_state_score_trend')} "
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
