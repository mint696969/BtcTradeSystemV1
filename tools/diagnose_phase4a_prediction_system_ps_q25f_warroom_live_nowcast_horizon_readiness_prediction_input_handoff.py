# path: ./tools/diagnose_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff.py
# desc: Read-only diagnostic for PS-Q25F WarRoom Live Nowcast horizon readiness and prediction-input handoff.

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
    WARROOM_LIVE_NOWCAST_HORIZON_READINESS_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_operator_summary_packet,
    build_warroom_live_nowcast_source_importance_packet,
    build_warroom_live_nowcast_composite_score_packet,
    build_warroom_live_nowcast_history_mini_trend_packet,
    build_warroom_live_nowcast_horizon_readiness_packet,
    warroom_live_nowcast_horizon_readiness_summary_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25F_WARROOM_LIVE_NOWCAST_HORIZON_READINESS_PREDICTION_INPUT_HANDOFF_2026-06-30.md"


def _fake_sources(*, warning: bool = False, critical: bool = False) -> dict[str, dict[str, Any]]:
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
        "health": {
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
        },
        "daemon": {"ts": "2026-06-29T18:11:32Z", "mode": "RUNNING", "cycle_no": 54641, "last_success_ts": "2026-06-29T18:11:32Z", "stop_requested": False, "consecutive_failures": 0, "last_error": None},
        "executions": {"ts": "2026-06-29T18:11:18Z", "ws_state": "LIVE", "lane_state": "live", "trade_count": 24173},
    }


def _readiness(*, warning: bool = False, critical: bool = False) -> dict[str, Any]:
    packet = build_warroom_live_market_nowcast_packet(
        sources=_fake_sources(warning=warning, critical=critical),
        fragment_enabled=True,
        now=datetime(2026, 6, 29, 18, 11, 32, tzinfo=timezone.utc),
    )
    summary = build_warroom_live_nowcast_operator_summary_packet(packet, lang="ja")
    layering = build_warroom_live_nowcast_source_importance_packet(packet, summary, lang="ja")
    composite = build_warroom_live_nowcast_composite_score_packet(packet, summary, layering)
    mini = build_warroom_live_nowcast_history_mini_trend_packet([composite])
    return build_warroom_live_nowcast_horizon_readiness_packet(packet, summary, layering, composite, mini)


def run_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_diagnostic() -> dict[str, Any]:
    normal = _readiness()
    warning = _readiness(warning=True)
    critical = _readiness(critical=True)
    rows = normal.get("horizon_readiness_rows") or []
    summary_rows = warroom_live_nowcast_horizon_readiness_summary_rows(normal)
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if normal.get("horizon_readiness_version") != WARROOM_LIVE_NOWCAST_HORIZON_READINESS_VERSION:
        blockers.append("horizon_readiness_version_required")
    if normal.get("nowcast_role") != "current_market_state_not_prediction":
        blockers.append("current_state_not_prediction_required")
    if normal.get("overall_horizon_readiness") != "all_horizons_ready":
        blockers.append("normal_all_horizons_ready_required")
    if warning.get("overall_horizon_readiness") not in {"horizons_read_with_caution", "longer_horizons_context_only", "horizons_not_ready"}:
        blockers.append("warning_readiness_degraded_required")
    if critical.get("overall_horizon_readiness") != "horizons_not_ready":
        blockers.append("critical_horizons_not_ready_required")
    if len(rows) != 4:
        blockers.append("four_horizon_rows_required")
    row_text = json.dumps(rows, ensure_ascii=False)
    for marker in ("5m", "15m", "30m", "1h", "ready", "prediction_input_gate"):
        if marker not in row_text:
            blockers.append(f"horizon_row_marker_required:{marker}")
    summary_text = json.dumps(summary_rows, ensure_ascii=False)
    for marker in ("horizon_readiness_version", "overall_horizon_readiness", "current_state_score", "prediction_input_gate"):
        if marker not in summary_text:
            blockers.append(f"summary_row_required:{marker}")
    for marker in ("WARROOM_LIVE_NOWCAST_HORIZON_READINESS_VERSION", "build_warroom_live_nowcast_horizon_readiness_packet", "_render_warroom_live_nowcast_horizon_readiness", "overall_horizon_readiness"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in ("horizon_readiness_rows_visible=true", "overall_horizon_readiness_visible=true", "horizon_5m_supported=true", "producer_cadence_changed=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "display_only", "non_executing", "current_state_not_prediction"):
        if normal.get(key) is not True:
            blockers.append(f"readiness_true_required:{key}")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if normal.get(key) is not False:
            blockers.append(f"readiness_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "normal_readiness": normal,
        "warning_readiness": warning,
        "critical_readiness": critical,
        "safety": {
            "read_only_diagnostic": True,
            "warroom_display_only": True,
            "current_state_not_prediction": True,
            "producer_cadence_changed": False,
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
    result = run_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
