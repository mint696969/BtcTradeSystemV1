# path: ./tools/diagnose_phase4a_prediction_system_ps_q25e_warroom_live_nowcast_composite_score_history_mini_trend.py
# desc: Read-only diagnostic for PS-Q25E WarRoom Live Nowcast composite score and session mini-trend.

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
    WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_operator_summary_packet,
    build_warroom_live_nowcast_source_importance_packet,
    build_warroom_live_nowcast_composite_score_packet,
    build_warroom_live_nowcast_history_mini_trend_packet,
    warroom_live_nowcast_composite_score_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25e_warroom_live_nowcast_composite_score_history_mini_trend.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25E_WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_HISTORY_MINI_TREND_2026-06-30.md"


def _fake_sources(*, warning: bool = False, critical: bool = False) -> dict[str, dict[str, Any]]:
    health = {
        "ts": "2026-06-29T18:11:28Z",
        "ok": True,
        "status": "healthy",
        "rest_mode": "NORMAL",
        "ws_state": "LIVE",
        "ws_freshness": "LIVE",
        "gap_detected": bool(critical),
        "resync_active": False,
        "requests_60s": 95,
        "utilization": 0.95,
        "last_429_ts": None,
        "ws_last_event_ts": "2026-06-29T18:11:28Z",
        "ws_executions_state": "LIVE",
        "ws_executions_freshness": "QUIET",
        "ws_executions_last_event_ts": "2026-06-29T18:11:18Z",
        "ws_executions_trade_count": 24173,
    }
    return {
        "market_state": {
            "ts": "2026-06-29T18:11:24Z",
            "lane_state": "live",
            "last_event_ts": "2026-06-29T18:11:24Z",
            "last_market_uid": "bitflyer.fx.FX_BTC_JPY",
            "last_symbol_raw": "FX_BTC_JPY",
            "last_best_bid": 9779378.0,
            "last_best_ask": 9782310.0,
            "last_spread": 24000.0 if warning else 2932.0,
            "last_source_series_id": "collector_main-stream-bitflyer-unified_board_ws-test",
        },
        "health": health,
        "daemon": {"ts": "2026-06-29T18:11:32Z", "mode": "RUNNING", "cycle_no": 54641, "last_success_ts": "2026-06-29T18:11:32Z", "stop_requested": False, "consecutive_failures": 0, "last_error": None},
        "executions": {"ts": "2026-06-29T18:11:18Z", "ws_state": "LIVE", "lane_state": "live", "trade_count": 24173},
    }


def _composite(*, warning: bool = False, critical: bool = False) -> dict[str, Any]:
    packet = build_warroom_live_market_nowcast_packet(
        sources=_fake_sources(warning=warning, critical=critical),
        fragment_enabled=True,
        now=datetime(2026, 6, 29, 18, 11, 32, tzinfo=timezone.utc),
    )
    summary = build_warroom_live_nowcast_operator_summary_packet(packet, lang="ja")
    layering = build_warroom_live_nowcast_source_importance_packet(packet, summary, lang="ja")
    return build_warroom_live_nowcast_composite_score_packet(packet, summary, layering)


def run_warroom_live_nowcast_composite_score_history_mini_trend_diagnostic() -> dict[str, Any]:
    normal = _composite()
    warning = _composite(warning=True)
    critical = _composite(critical=True)
    mini_trend = build_warroom_live_nowcast_history_mini_trend_packet([warning, normal])
    rows = warroom_live_nowcast_composite_score_rows(normal, mini_trend)
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if normal.get("composite_score_version") != WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION:
        blockers.append("composite_score_version_required")
    if normal.get("nowcast_role") != "current_market_state_not_prediction":
        blockers.append("current_state_not_prediction_required")
    if not isinstance(normal.get("current_state_score"), int) or not (0 <= normal.get("current_state_score") <= 100):
        blockers.append("normal_score_0_to_100_required")
    if not isinstance(warning.get("current_state_score"), int) or warning.get("current_state_score") >= normal.get("current_state_score"):
        blockers.append("warning_score_must_be_lower_than_normal")
    if not isinstance(critical.get("current_state_score"), int) or critical.get("current_state_score") >= warning.get("current_state_score"):
        blockers.append("critical_score_must_be_lower_than_warning")
    if mini_trend.get("current_state_score_trend") not in {"improving", "stable", "deteriorating", "insufficient_history"}:
        blockers.append("mini_trend_state_required")
    if mini_trend.get("history_sample_count") != 2:
        blockers.append("mini_trend_two_samples_required")
    row_text = json.dumps(rows, ensure_ascii=False)
    for marker in ("current_state_score", "score_note", "mini_trend", "prediction_input_gate", "penalty_reasons"):
        if marker not in row_text:
            blockers.append(f"score_row_required:{marker}")
    for marker in ("WARROOM_LIVE_NOWCAST_COMPOSITE_SCORE_VERSION", "build_warroom_live_nowcast_composite_score_packet", "build_warroom_live_nowcast_history_mini_trend_packet", "_render_warroom_live_nowcast_composite_score", "current_state_score_trend"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in ("current_state_score_visible=true", "mini_trend_visible=true", "session_state_history_only=true", "persistent_history_artifact_written=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "display_only", "non_executing", "current_state_not_prediction"):
        if normal.get(key) is not True or mini_trend.get(key) is not True:
            blockers.append(f"score_true_required:{key}")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if normal.get(key) is not False or mini_trend.get(key) is not False:
            blockers.append(f"score_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "normal_composite": normal,
        "warning_composite": warning,
        "critical_composite": critical,
        "mini_trend": mini_trend,
        "safety": {
            "read_only_diagnostic": True,
            "warroom_display_only": True,
            "session_state_history_only": True,
            "persistent_history_artifact_written": False,
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
    result = run_warroom_live_nowcast_composite_score_history_mini_trend_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
