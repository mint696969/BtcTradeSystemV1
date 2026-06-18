# path: ./tools/test_phase4a_autotrade_milestone_gs_forecast_ledger_guard.py
# desc: Guard S130 forecast ledger contracts remain in-memory, serializable, non-writing, non-collecting, non-executing, and AutoTrade-disconnected.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    ForecastLedgerBatch,
    ForecastLedgerRecord,
    aggregate_ohlcv_from_rows,
    assess_source_quality,
    build_cross_venue_reference_summary,
    build_forecast_ledger_records_from_bundle,
    build_human_technical_summary,
    build_inference_bundle_from_outputs,
    build_rule_based_v0_outputs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "forecast_ledger.py",
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
    "would_append_ledger: bool = True",
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
    batch = build_forecast_ledger_records_from_bundle(bundle, now=now)
    empty_bundle = build_inference_bundle_from_outputs(tuple(), now=now)
    empty_batch = build_forecast_ledger_records_from_bundle(empty_bundle, now=now)
    missing_batch = build_forecast_ledger_records_from_bundle(None, now=now)
    encoded = json.dumps(batch.to_dict(), ensure_ascii=False, sort_keys=True)
    decoded = json.loads(encoded)

    checks = {
        "exports_available": ForecastLedgerBatch is not None and ForecastLedgerRecord is not None and build_forecast_ledger_records_from_bundle is not None,
        "batch_usable": batch.usable is True,
        "record_count_matches_outputs": batch.record_count == len(outputs) == 5,
        "family_count_present": batch.family_count == 5,
        "horizon_count_present": batch.horizon_count == 1,
        "records_have_family_and_horizon": all(record.family and record.horizon_sec == 300 and record.horizon_key == "300s" for record in batch.records),
        "records_have_prediction_snapshots": all(record.prediction_id and record.primary_label and record.parameter_set_id for record in batch.records),
        "records_are_in_memory_only": decoded["would_append_ledger"] is False and decoded["would_write_runtime_artifact"] is False and decoded["would_send_to_broker"] is False,
        "record_flags_false": all(item["would_append_ledger"] is False and item["would_write_runtime_artifact"] is False and item["would_send_to_broker"] is False and item["broker_execution_requested"] is False and item["mode_apply_requested"] is False and item["command_ledger_append_requested"] is False for item in decoded["records"]),
        "batch_serializes": decoded["logic_version"] == "prediction_forecast_ledger.s130.v1" and decoded["non_executing"] is True,
        "empty_bundle_blocked": "forecast_outputs_missing" in empty_batch.blockers,
        "missing_bundle_blocked": "inference_bundle_missing" in missing_batch.blockers,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/" in line]
    failures.extend(f"protected AutoTrade/collector dirty during GS: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gs_forecast_ledger_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_autotrade_and_collector_untouched": not protected_dirty_hits},
        "sample": {
            "batch_id": batch.batch_id,
            "record_count": batch.record_count,
            "family_count": batch.family_count,
            "horizon_count": batch.horizon_count,
            "families": [record.family for record in batch.records],
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_forecast_ledger_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
