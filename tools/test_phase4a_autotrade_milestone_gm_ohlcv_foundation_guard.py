# path: ./tools/test_phase4a_autotrade_milestone_gm_ohlcv_foundation_guard.py
# desc: Guard S124 OHLCV foundation remains deterministic, serializable, non-collecting, and non-executing.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    OHLCVAggregationDiagnostics,
    OHLCVCandle,
    Timeframe,
    aggregate_ohlcv_from_rows,
    build_default_timeframes,
    timeframe_by_seconds,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "ohlcv.py",
)
EXPECTED_TIMEFRAMES = (60, 300, 900, 1800, 3600, 14400, 86400)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
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
    "place_order(",
    "send_order(",
    "would_send_to_broker: bool = True",
    "would_collect_public_source: bool = True",
    "would_write_runtime_artifact: bool = True",
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
        {"event_ts": "2026-06-18T00:00:05Z", "price": 100.0, "size": 0.5},
        {"event_ts": "2026-06-18T00:00:35Z", "price": 102.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:01:10Z", "price": 101.0, "size": 0.25},
        {"event_ts": "2026-06-18T00:01:40Z", "price": 103.0, "size": 0.75},
        {"event_ts": "2026-06-18T00:04:20Z", "price": 104.0, "size": 1.0},
        {"event_ts": "2026-06-18T00:04:50Z", "price": 99.0, "size": 0.5},
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

    timeframes = build_default_timeframes()
    candles, diag = aggregate_ohlcv_from_rows(
        _rows(),
        timeframes_sec=(60, 300, 900),
        now=datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc),
        max_latest_age_sec=600,
        source_family="synthetic_unit_rows",
        source_symbol="BTC_JPY",
        source_venue="unit",
    )
    candle_data = [candle.to_dict() for candle in candles]
    encoded = json.dumps({"candles": candle_data, "diagnostics": diag.to_dict()}, ensure_ascii=False, sort_keys=True)
    decoded = json.loads(encoded)
    one_minute = [c for c in candle_data if c["timeframe"]["timeframe_sec"] == 60 and c["start_ts"] == "2026-06-18T00:00:00Z"][0]
    five_minute = [c for c in candle_data if c["timeframe"]["timeframe_sec"] == 300][0]

    empty_candles, empty_diag = aggregate_ohlcv_from_rows([], timeframes_sec=(60,))
    stale_candles, stale_diag = aggregate_ohlcv_from_rows(
        _rows(),
        timeframes_sec=(60,),
        now=datetime(2026, 6, 18, 1, 0, 0, tzinfo=timezone.utc),
        max_latest_age_sec=60,
    )

    checks = {
        "exports_available": all(item is not None for item in (Timeframe, OHLCVCandle, OHLCVAggregationDiagnostics, aggregate_ohlcv_from_rows)),
        "expected_timeframes_present": tuple(tf.timeframe_sec for tf in timeframes) == EXPECTED_TIMEFRAMES,
        "timeframe_lookup_ok": timeframe_by_seconds(300).label == "5m",
        "aggregation_returns_candles": len(candles) >= 3,
        "one_minute_ohlc_correct": one_minute["open"] == 100.0 and one_minute["high"] == 102.0 and one_minute["low"] == 100.0 and one_minute["close"] == 102.0,
        "five_minute_ohlc_correct": five_minute["open"] == 100.0 and five_minute["high"] == 104.0 and five_minute["low"] == 99.0 and five_minute["close"] == 99.0,
        "volume_and_vwap_visible": five_minute["volume"] == 4.0 and five_minute["vwap"] is not None,
        "diagnostics_serializes": decoded["diagnostics"]["logic_version"] == "prediction_ohlcv.s124.v1" and decoded["diagnostics"]["usable"] is True,
        "non_executing_flags_false": decoded["diagnostics"]["would_collect_public_source"] is False and decoded["diagnostics"]["would_write_runtime_artifact"] is False and decoded["diagnostics"]["would_send_to_broker"] is False,
        "empty_rows_blocked": empty_candles == tuple() and "ohlcv_rows_missing_or_unusable" in empty_diag.blocked_by,
        "stale_warning_visible": bool(stale_candles) and "latest_row_stale_for_ohlcv" in stale_diag.warnings,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/execution/" in line]
    failures.extend(f"protected execution/collector dirty during GM: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gm_ohlcv_foundation_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_execution_and_collector_untouched": not protected_dirty_hits},
        "sample": {
            "candle_count": len(candles),
            "requested_timeframes": diag.requested_timeframes_sec,
            "usable": diag.usable,
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ohlcv_foundation_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
