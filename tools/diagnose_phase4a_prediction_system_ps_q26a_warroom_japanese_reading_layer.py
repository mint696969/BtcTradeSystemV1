# path: ./tools/diagnose_phase4a_prediction_system_ps_q26a_warroom_japanese_reading_layer.py
# desc: Read-only diagnostic for PS-Q26A WarRoom Japanese reading layer.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_JAPANESE_READING_LAYER_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_japanese_reading_layer_packet,
    build_warroom_live_nowcast_operator_summary_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION,
    build_latest_prediction_warroom_japanese_reading_layer_packet,
    latest_prediction_warroom_display_rows,
    latest_prediction_warroom_horizon_expiry_packet,
    latest_prediction_warroom_operator_action_guidance_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26a_warroom_japanese_reading_layer.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26A_WARROOM_JAPANESE_READING_LAYER_2026-06-30.md"
NOWCAST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
PRED = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_japanese_reading_layer_q26a.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_japanese_reading_layer_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    nowcast_src = _read(NOWCAST)
    pred_src = _read(PRED)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26a_warroom_japanese_reading_layer=true",
        "nowcast_japanese_reading_layer_added=true",
        "prediction_japanese_reading_layer_added=true",
        "operator_visible_japanese_rows=true",
        "trade_guidance_added=false",
        "broker_private_api_allowed=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_LIVE_NOWCAST_JAPANESE_READING_LAYER_VERSION",
        "warroom_live_nowcast_japanese_reading_rows",
        "build_warroom_live_nowcast_japanese_reading_layer_packet",
        "PS-Q26A 日本語読み方",
    ):
        if marker not in nowcast_src:
            blockers.append(f"nowcast_src_marker_required:{marker}")
    for marker in (
        "WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION",
        "latest_prediction_warroom_japanese_reading_rows",
        "build_latest_prediction_warroom_japanese_reading_layer_packet",
        "PS-Q26A 日本語読み方",
    ):
        if marker not in pred_src:
            blockers.append(f"prediction_src_marker_required:{marker}")
    for marker in (
        "test_q26a_nowcast_japanese_reading_layer_is_display_only",
        "test_q26a_prediction_japanese_reading_layer_is_display_only",
    ):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")

    nowcast_packet = build_warroom_live_market_nowcast_packet(
        sources={
            "market_state": {"lane_state": "live", "last_best_bid": 100.0, "last_best_ask": 101.0, "last_spread": 1.0, "last_event_ts": "2026-06-30T00:00:00Z", "ts": "2026-06-30T00:00:00Z"},
            "health": {"ok": True, "status": "healthy", "ws_state": "LIVE", "ws_freshness": "LIVE", "gap_detected": False, "resync_active": False, "ts": "2026-06-30T00:00:00Z"},
            "daemon": {"mode": "RUNNING"},
            "executions": {"ts": "2026-06-30T00:00:00Z"},
        }
    )
    summary = build_warroom_live_nowcast_operator_summary_packet(nowcast_packet, lang="ja")
    nowcast_layer = build_warroom_live_nowcast_japanese_reading_layer_packet(nowcast_packet, summary)
    read_model = {"ok": True, "generated_at": "2026-06-30T00:00:00Z", "age_sec": 20, "freshness_state": "fresh", "selected_horizon_sec": [15, 60, 300, 900], "selected_records_by_horizon": {"15": [{"family": "trend_bias", "primary_label": "short_bias", "confidence": "medium", "score": 0.66}], "60": [{"family": "cross_venue_confirmation", "primary_label": "confirmed", "confidence": "high", "score": 0.7}], "300": [{"family": "market_regime", "primary_label": "range_candidate", "confidence": "medium", "score": 0.52}], "900": [{"family": "volatility_risk", "primary_label": "compression_watch", "confidence": "medium", "score": 0.58}]}}
    prediction_rows = latest_prediction_warroom_display_rows(read_model, lang="ja")
    expiry = latest_prediction_warroom_horizon_expiry_packet(read_model, lang="ja")
    guidance = latest_prediction_warroom_operator_action_guidance_packet({"horizon_expiry_packet": expiry, "freshness_state": "fresh", "age_sec": 20}, lang="ja")
    prediction_layer = build_latest_prediction_warroom_japanese_reading_layer_packet(read_model, prediction_rows=prediction_rows, horizon_expiry_packet=expiry, operator_action_guidance_packet=guidance)
    for name, packet in (("nowcast", nowcast_layer), ("prediction", prediction_layer)):
        if packet.get("row_count", 0) < 5:
            blockers.append(f"{name}_row_count_too_small")
        for key in ("read_only", "display_only", "non_executing"):
            if packet.get(key) is not True:
                blockers.append(f"{name}_true_required:{key}")
        for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
            if packet.get(key) is not False:
                blockers.append(f"{name}_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "nowcast_layer_version": WARROOM_LIVE_NOWCAST_JAPANESE_READING_LAYER_VERSION,
        "prediction_layer_version": WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION,
        "nowcast_layer": nowcast_layer,
        "prediction_layer": prediction_layer,
        "safety": {
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "trade_guidance_added": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_warroom_japanese_reading_layer_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
