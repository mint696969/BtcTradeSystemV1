# path: ./tools/diagnose_phase4a_prediction_system_ps_q25d_warroom_live_nowcast_source_importance_signal_layering.py
# desc: Read-only diagnostic for PS-Q25D WarRoom Live Nowcast source importance and signal layering.

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
    WARROOM_LIVE_NOWCAST_SOURCE_LAYERING_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_operator_summary_packet,
    build_warroom_live_nowcast_source_importance_packet,
    warroom_live_nowcast_source_layer_summary_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25d_warroom_live_nowcast_source_importance_signal_layering.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25D_WARROOM_LIVE_NOWCAST_SOURCE_IMPORTANCE_SIGNAL_LAYERING_2026-06-30.md"


def _fake_sources(*, warning: bool = False) -> dict[str, dict[str, Any]]:
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
        "daemon": {"ts": "2026-06-29T18:11:32Z", "mode": "RUNNING", "cycle_no": 54641, "last_success_ts": "2026-06-29T18:11:32Z", "stop_requested": False, "consecutive_failures": 0, "last_error": None},
        "executions": {"ts": "2026-06-29T18:11:18Z", "ws_state": "LIVE", "lane_state": "live", "trade_count": 24173},
    }


def _packet(*, warning: bool = False) -> dict[str, Any]:
    return build_warroom_live_market_nowcast_packet(
        sources=_fake_sources(warning=warning),
        fragment_enabled=True,
        now=datetime(2026, 6, 29, 18, 11, 32, tzinfo=timezone.utc),
    )


def run_warroom_live_nowcast_source_importance_signal_layering_diagnostic() -> dict[str, Any]:
    normal_packet = _packet()
    normal_summary = build_warroom_live_nowcast_operator_summary_packet(normal_packet, lang="ja")
    normal_layering = build_warroom_live_nowcast_source_importance_packet(normal_packet, normal_summary, lang="ja")
    warning_packet = _packet(warning=True)
    warning_summary = build_warroom_live_nowcast_operator_summary_packet(warning_packet, lang="ja")
    warning_layering = build_warroom_live_nowcast_source_importance_packet(warning_packet, warning_summary, lang="ja")
    summary_rows = warroom_live_nowcast_source_layer_summary_rows(normal_layering)
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if normal_layering.get("source_layering_version") != WARROOM_LIVE_NOWCAST_SOURCE_LAYERING_VERSION:
        blockers.append("source_layering_version_required")
    if normal_layering.get("nowcast_role") != "current_market_state_not_prediction":
        blockers.append("current_state_not_prediction_required")
    if normal_layering.get("prediction_input_gate") != "prediction_input_foundation_usable":
        blockers.append("usable_prediction_input_gate_required")
    if warning_layering.get("prediction_input_gate") != "prediction_input_foundation_caution":
        blockers.append("caution_prediction_input_gate_required")
    if normal_layering.get("source_importance_row_count", 0) < 7:
        blockers.append("source_importance_rows_required")
    layer_text = json.dumps(normal_layering, ensure_ascii=False)
    for marker in ("foundation_integrity", "microstructure_now", "trade_flow_now", "operational_pressure", "prediction_input_gate", "current_nowcast", "tactical_5m", "tactical_15m", "scenario_30m_1h"):
        if marker not in layer_text:
            blockers.append(f"layer_or_profile_required:{marker}")
    row_text = json.dumps(summary_rows, ensure_ascii=False)
    for marker in ("source_layering_version", "prediction_input_gate", "read_order", "operator_instruction"):
        if marker not in row_text:
            blockers.append(f"summary_row_required:{marker}")
    for marker in ("WARROOM_LIVE_NOWCAST_SOURCE_LAYERING_VERSION", "build_warroom_live_nowcast_source_importance_packet", "_render_warroom_live_nowcast_source_layering", "prediction_input_gate"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in ("source_importance_rows_visible=true", "prediction_input_gate_visible=true", "foundation_integrity_layer_supported=true", "tactical_5m_profile_supported=true"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "display_only", "non_executing", "current_state_not_prediction"):
        if normal_layering.get(key) is not True:
            blockers.append(f"layering_true_required:{key}")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if normal_layering.get(key) is not False:
            blockers.append(f"layering_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "normal_layering": normal_layering,
        "warning_layering": warning_layering,
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
    result = run_warroom_live_nowcast_source_importance_signal_layering_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
