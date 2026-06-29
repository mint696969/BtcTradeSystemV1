# path: ./tools/diagnose_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility.py
# desc: Read-only diagnostic for PS-Q25B WarRoom Live Market Nowcast high-frequency visibility.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_MARKET_NOWCAST_PANEL_VERSION,
    WARROOM_LIVE_MARKET_NOWCAST_REFRESH_MODE,
    WARROOM_LIVE_MARKET_NOWCAST_REFRESH_SEC,
    build_warroom_live_market_nowcast_packet,
    warroom_live_market_nowcast_metric_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25b_warroom_live_market_nowcast_high_frequency_visibility.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25B_WARROOM_LIVE_MARKET_NOWCAST_HIGH_FREQUENCY_VISIBILITY_2026-06-30.md"


def _fake_sources() -> dict[str, dict[str, Any]]:
    return {
        "market_state": {
            "ts": "2026-06-29T18:11:24Z",
            "lane_state": "live",
            "last_event_ts": "2026-06-29T18:11:24Z",
            "last_market_uid": "bitflyer.fx.FX_BTC_JPY",
            "last_symbol_raw": "FX_BTC_JPY",
            "last_best_bid": 9779378.0,
            "last_best_ask": 9782310.0,
            "last_spread": 2932.0,
            "last_source_series_id": "collector_main-stream-bitflyer-unified_board_ws-test",
        },
        "health": {
            "ts": "2026-06-29T18:11:28Z",
            "ok": True,
            "status": "healthy",
            "rest_mode": "NORMAL",
            "ws_state": "LIVE",
            "ws_freshness": "LIVE",
            "gap_detected": False,
            "resync_active": False,
            "requests_60s": 95,
            "utilization": 0.95,
            "last_429_ts": None,
            "ws_last_event_ts": "2026-06-29T18:11:28Z",
            "ws_executions_state": "LIVE",
            "ws_executions_freshness": "QUIET",
            "ws_executions_last_event_ts": "2026-06-29T18:11:18Z",
            "ws_executions_trade_count": 24173,
        },
        "daemon": {
            "ts": "2026-06-29T18:11:32Z",
            "mode": "RUNNING",
            "cycle_no": 54641,
            "last_success_ts": "2026-06-29T18:11:32Z",
            "stop_requested": False,
            "consecutive_failures": 0,
            "last_error": None,
        },
        "executions": {
            "ts": "2026-06-29T18:11:18Z",
            "ws_state": "LIVE",
            "lane_state": "live",
            "trade_count": 24173,
        },
    }


def run_warroom_live_market_nowcast_high_frequency_visibility_diagnostic() -> dict[str, Any]:
    now = datetime(2026, 6, 29, 18, 11, 32, tzinfo=timezone.utc)
    packet = build_warroom_live_market_nowcast_packet(sources=_fake_sources(), fragment_enabled=True, now=now)
    rows = warroom_live_market_nowcast_metric_rows(packet)
    panel_text = PANEL.read_text(encoding="utf-8")
    warroom_text = WARROOM_PAGE.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if packet.get("nowcast_panel_version") != WARROOM_LIVE_MARKET_NOWCAST_PANEL_VERSION:
        blockers.append("nowcast_panel_version_required")
    if packet.get("nowcast_role") != "current_market_state_not_prediction":
        blockers.append("current_state_not_prediction_required")
    if packet.get("refresh_mode") != WARROOM_LIVE_MARKET_NOWCAST_REFRESH_MODE:
        blockers.append("poll_fast_refresh_mode_required")
    if packet.get("refresh_interval_sec") != WARROOM_LIVE_MARKET_NOWCAST_REFRESH_SEC:
        blockers.append("refresh_interval_3s_required")
    for key in ("best_bid", "best_ask", "spread", "spread_bps", "market_event_age_sec", "ws_state", "ws_executions_state", "collector_status", "gap_detected", "resync_active", "attention_flags"):
        if key not in packet:
            blockers.append(f"packet_key_required:{key}")
    if packet.get("current_state_summary") != "current_market_state_live_observable":
        blockers.append("live_observable_summary_required")
    if packet.get("nowcast_freshness_state") not in {"live", "slightly_delayed"}:
        blockers.append("nowcast_freshness_live_or_slightly_delayed_required")
    if packet.get("read_only") is not True or packet.get("display_only") is not True or packet.get("non_executing") is not True:
        blockers.append("display_only_read_only_non_executing_required")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"safety_false_required:{key}")
    row_text = json.dumps(rows, ensure_ascii=False)
    for marker in ("current_state", "best_bid", "best_ask", "spread", "market_event_age_sec", "ws_board", "ws_executions", "collector", "gap_resync", "attention_flags"):
        if marker not in row_text:
            blockers.append(f"metric_row_required:{marker}")
    if "render_warroom_live_market_nowcast_panel" not in warroom_text:
        blockers.append("warroom_page_mount_required")
    if "PS-Q25B Live Market Nowcast" not in warroom_text:
        blockers.append("warroom_page_section_required")
    if "Q25B_DEFAULT_HOT_ROOT_HINT = r\"D:\\btc_ts_hot\"" not in panel_text:
        blockers.append("d_hot_root_hint_required")
    if "live_shell.render_fragment_slot" not in panel_text or "poll_fast" not in panel_text:
        blockers.append("fragment_poll_fast_render_required")
    for marker in ("current_state_not_prediction=true", "high_frequency_fragment_refresh_sec=3", "best_bid_visible=true", "attention_flags_visible=true"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": {
            "nowcast_panel_version": packet.get("nowcast_panel_version"),
            "nowcast_role": packet.get("nowcast_role"),
            "refresh_mode": packet.get("refresh_mode"),
            "refresh_interval_sec": packet.get("refresh_interval_sec"),
            "current_state_summary": packet.get("current_state_summary"),
            "nowcast_freshness_state": packet.get("nowcast_freshness_state"),
            "best_bid": packet.get("best_bid"),
            "best_ask": packet.get("best_ask"),
            "spread": packet.get("spread"),
            "spread_bps": packet.get("spread_bps"),
            "market_event_age_sec": packet.get("market_event_age_sec"),
            "ws_state": packet.get("ws_state"),
            "ws_executions_state": packet.get("ws_executions_state"),
            "attention_flags": packet.get("attention_flags"),
        },
        "safety": {
            "read_only_diagnostic": True,
            "warroom_display_only": True,
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
        },
    }


def main() -> int:
    result = run_warroom_live_market_nowcast_high_frequency_visibility_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
