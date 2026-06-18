# path: ./tools/test_phase4a_autotrade_milestone_gv_shadow_adapter_guard.py
# desc: Guard S133 Shadow adapter preview remains contract-only, serializable, non-writing, non-publishing, non-executing, and AutoTrade-file-disconnected.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    AutoTradeInferenceSnapshot,
    AutoTradeShadowSignalPreview,
    RealizedOutcome,
    aggregate_ohlcv_from_rows,
    assess_source_quality,
    build_autotrade_shadow_signal_preview,
    build_cross_venue_reference_summary,
    build_forecast_ledger_records_from_bundle,
    build_forecast_outcome_records,
    build_human_technical_summary,
    build_inference_bundle_from_outputs,
    build_missed_opportunity_report,
    build_prediction_calibration_report,
    build_rule_based_v0_outputs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "shadow_adapter.py",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.autotrade",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "requests.get",
    "httpx.get",
    "connect_and_stream",
    "write_canonical(",
    "write_raw(",
    "append_jsonl(",
    "open(",
    ".write(",
    "place_order(",
    "send_order(",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "append_decision_jsonl",
    "would_publish_to_autotrade: bool = True",
    "would_append_shadow_decision: bool = True",
    "would_apply_mode: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _rows() -> list[dict[str, object]]:
    return [
        {"event_ts": "2026-06-18T00:00:05Z", "price": 100.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:00:55Z", "price": 101.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:01:05Z", "price": 101.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:01:55Z", "price": 103.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:02:05Z", "price": 103.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:02:55Z", "price": 104.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:03:05Z", "price": 104.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:03:55Z", "price": 106.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:04:05Z", "price": 106.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:04:30Z", "price": 111.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:04:55Z", "price": 107.0, "size": 1.0},
    ]


def _snapshots() -> list[dict[str, object]]:
    return [
        {"source_id": "bf_fx", "venue": "bitflyer", "symbol": "FX_BTC_JPY", "price": 10050000.0, "market_role": "bitflyer_fx", "event_ts": "2026-06-18T00:00:00Z"},
        {"source_id": "bf_spot", "venue": "bitflyer", "symbol": "BTC_JPY", "price": 10000000.0, "market_role": "bitflyer_spot", "event_ts": "2026-06-18T00:00:00Z"},
        {"source_id": "binance_spot", "venue": "binance", "symbol": "BTC_JPY_REF", "price": 10002000.0, "market_role": "global_spot", "event_ts": "2026-06-18T00:00:00Z"},
    ]


def _bundle_reports(now: datetime):
    candles, _ = aggregate_ohlcv_from_rows(_rows(), timeframes_sec=(60,))
    technical = build_human_technical_summary(candles, timeframe_sec=60)
    quality = {
        "bf_fx": assess_source_quality(source_id="bf_fx", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now, max_age_sec=600),
        "bf_spot": assess_source_quality(source_id="bf_spot", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now, max_age_sec=600),
        "binance_spot": assess_source_quality(source_id="binance_spot", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now, max_age_sec=600),
    }
    cross = build_cross_venue_reference_summary(_snapshots(), source_quality_by_id=quality, now=now)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, cross_venue_summary=cross, horizon_sec=300, now=now)
    bundle = build_inference_bundle_from_outputs(outputs, now=now)
    forecast_batch = build_forecast_ledger_records_from_bundle(bundle, now=now)
    realized = tuple(
        RealizedOutcome(
            outcome_id=f"outcome_{record.family}",
            family=record.family,
            horizon_sec=record.horizon_sec,
            realized_label=record.primary_label if record.family != "volatility_risk" else "elevated_risk",
            realized_direction="risk" if "risk" in record.primary_label or "divergent" in record.primary_label or record.family == "volatility_risk" else "up",
            realized_return=0.012,
            observed_at="2026-06-18T00:10:00Z",
        )
        for record in forecast_batch.records
    )
    outcome_batch = build_forecast_outcome_records(forecast_batch, realized, now=now)
    calibration = build_prediction_calibration_report(outcome_batch, now=now)
    missed = build_missed_opportunity_report(outcome_batch, now=now)
    return bundle, calibration, missed


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            compile(text, str(path), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {path.relative_to(REPO_ROOT)}: {exc}")
        imports = _imports_from(path)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {path.relative_to(REPO_ROOT)}: {prefix}")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")

    now = datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc)
    bundle, calibration, missed = _bundle_reports(now)
    preview = build_autotrade_shadow_signal_preview(bundle, calibration_report=calibration, missed_opportunity_report=missed, now=now)
    missing_preview = build_autotrade_shadow_signal_preview(None, now=now)
    encoded = json.dumps(preview.to_dict(), ensure_ascii=False, sort_keys=True)
    decoded = json.loads(encoded)

    checks = {
        "exports_available": AutoTradeInferenceSnapshot is not None and AutoTradeShadowSignalPreview is not None and build_autotrade_shadow_signal_preview is not None,
        "preview_usable": preview.usable is True,
        "intended_mode_shadow": preview.intended_mode == "SHADOW",
        "preview_only": preview.preview_only is True,
        "snapshot_embedded": preview.inference_snapshot is not None and preview.inference_snapshot.bundle_id == bundle.bundle_id,
        "families_and_horizons_visible": decoded["inference_snapshot"]["families_present"] and decoded["inference_snapshot"]["horizons_present_sec"] == [300],
        "labels_scores_visible": decoded["inference_snapshot"]["labels_by_family"]["trend_bias"] == "long_bias" and decoded["inference_snapshot"]["scores_by_family"]["trend_bias"] == 0.66,
        "reports_visible": decoded["inference_snapshot"]["calibration_average_score"] == 0.8 and decoded["inference_snapshot"]["near_miss_count"] == 1,
        "risk_preview_holds": preview.action_bias == "risk_off" and preview.recommended_action == "HOLD",
        "missing_bundle_blocked": "inference_bundle_missing" in missing_preview.blockers and missing_preview.recommended_action == "HOLD",
        "preview_serializes": decoded["logic_version"] == "prediction_shadow_adapter.s133.v1" and decoded["non_executing"] is True,
        "non_publication_flags_false": decoded["would_publish_to_autotrade"] is False and decoded["would_append_shadow_decision"] is False and decoded["would_apply_mode"] is False and decoded["would_write_runtime_artifact"] is False and decoded["would_send_to_broker"] is False,
        "execution_flags_false": decoded["broker_execution_requested"] is False and decoded["mode_apply_requested"] is False and decoded["command_ledger_append_requested"] is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/" in line]
    failures.extend(f"protected AutoTrade/collector dirty during GV: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gv_shadow_adapter_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_autotrade_and_collector_untouched": not protected_dirty_hits},
        "sample": {
            "preview_id": preview.preview_id,
            "intended_mode": preview.intended_mode,
            "recommended_action": preview.recommended_action,
            "action_bias": preview.action_bias,
            "confidence": preview.confidence,
            "reason_codes": preview.reason_codes,
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_shadow_adapter_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
