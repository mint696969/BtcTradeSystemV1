# path: ./tools/diagnose_phase4a_prediction_system_ps_q25c_warroom_live_nowcast_operator_summary_attention_classification.py
# desc: Read-only diagnostic for PS-Q25C WarRoom Live Nowcast operator summary and attention classification.

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
    WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_operator_summary_packet,
    classify_warroom_live_nowcast_attention,
    warroom_live_nowcast_operator_summary_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25c_warroom_live_nowcast_operator_summary_attention_classification.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25C_WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_ATTENTION_CLASSIFICATION_2026-06-30.md"


def _fake_sources(*, with_warning: bool = False, with_critical: bool = False) -> dict[str, dict[str, Any]]:
    health = {
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
    }
    market = {
        "ts": "2026-06-29T18:11:24Z",
        "lane_state": "live",
        "last_event_ts": "2026-06-29T18:11:24Z",
        "last_market_uid": "bitflyer.fx.FX_BTC_JPY",
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9779378.0,
        "last_best_ask": 9782310.0,
        "last_spread": 2932.0,
        "last_source_series_id": "collector_main-stream-bitflyer-unified_board_ws-test",
    }
    if with_warning:
        market["last_spread"] = 24000.0
    if with_critical:
        health["gap_detected"] = True
    return {
        "market_state": market,
        "health": health,
        "daemon": {"ts": "2026-06-29T18:11:32Z", "mode": "RUNNING", "cycle_no": 54641, "last_success_ts": "2026-06-29T18:11:32Z", "stop_requested": False, "consecutive_failures": 0, "last_error": None},
        "executions": {"ts": "2026-06-29T18:11:18Z", "ws_state": "LIVE", "lane_state": "live", "trade_count": 24173},
    }


def _packet(*, with_warning: bool = False, with_critical: bool = False) -> dict[str, Any]:
    return build_warroom_live_market_nowcast_packet(
        sources=_fake_sources(with_warning=with_warning, with_critical=with_critical),
        fragment_enabled=True,
        now=datetime(2026, 6, 29, 18, 11, 32, tzinfo=timezone.utc),
    )


def run_warroom_live_nowcast_operator_summary_attention_classification_diagnostic() -> dict[str, Any]:
    normal = _packet()
    warning = _packet(with_warning=True)
    critical = _packet(with_critical=True)
    normal_summary = build_warroom_live_nowcast_operator_summary_packet(normal, lang="ja")
    warning_summary = build_warroom_live_nowcast_operator_summary_packet(warning, lang="ja")
    critical_summary = build_warroom_live_nowcast_operator_summary_packet(critical, lang="ja")
    normal_rows = warroom_live_nowcast_operator_summary_rows(normal_summary)
    attention_rows = classify_warroom_live_nowcast_attention(warning, lang="ja")
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if normal_summary.get("operator_summary_version") != WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_VERSION:
        blockers.append("operator_summary_version_required")
    if normal_summary.get("nowcast_role") != "current_market_state_not_prediction":
        blockers.append("current_state_not_prediction_required")
    if normal_summary.get("operator_state_grade") != "live_observable":
        blockers.append("live_observable_grade_required")
    if normal_summary.get("operator_attention_severity") != "ok":
        blockers.append("ok_attention_severity_required")
    if warning_summary.get("operator_state_grade") != "usable_with_caution":
        blockers.append("warning_grade_required")
    if warning_summary.get("operator_attention_severity") != "warning":
        blockers.append("warning_attention_severity_required")
    if critical_summary.get("operator_state_grade") != "not_usable_for_current_decision":
        blockers.append("critical_grade_required")
    if critical_summary.get("operator_attention_severity") != "critical":
        blockers.append("critical_attention_severity_required")
    if "予測ではなく" not in str(normal_summary.get("operator_instruction_text") or ""):
        blockers.append("ja_instruction_not_prediction_required")
    row_text = json.dumps(normal_rows, ensure_ascii=False)
    for marker in ("operator_state_grade", "attention_severity", "operator_instruction", "freshness", "spread"):
        if marker not in row_text:
            blockers.append(f"summary_row_required:{marker}")
    attention_text = json.dumps(attention_rows, ensure_ascii=False)
    if "spread_wide_caution" not in attention_text:
        blockers.append("attention_row_spread_warning_required")
    for marker in ("WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_VERSION", "_render_warroom_live_nowcast_operator_summary", "operator_state_grade", "operator_attention_severity"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in ("operator_state_grade_visible=true", "attention_rows_visible=true", "current_state_not_prediction=true"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "display_only", "non_executing", "current_state_not_prediction"):
        if normal_summary.get(key) is not True:
            blockers.append(f"summary_true_required:{key}")
    for key in ("autotrade_trigger_allowed", "broker_private_api_allowed", "would_send_to_broker"):
        if normal_summary.get(key) is not False:
            blockers.append(f"summary_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "normal_summary": normal_summary,
        "warning_summary": warning_summary,
        "critical_summary": critical_summary,
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
    result = run_warroom_live_nowcast_operator_summary_attention_classification_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
