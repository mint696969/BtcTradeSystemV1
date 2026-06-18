# path: ./tools/test_phase4a_autotrade_milestone_go_human_technical_indicators_guard.py
# desc: Guard S126 human technical indicators remain deterministic, serializable, non-collecting, and non-executing.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    CandleWickBodySummary,
    HumanTechnicalSummary,
    MovingAverageSlopeSummary,
    RangeBoundarySummary,
    SupportResistanceZone,
    VolatilityTechnicalSummary,
    VwapRelationSummary,
    aggregate_ohlcv_from_rows,
    build_human_technical_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "technical.py",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
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
    "would_collect_public_source: bool = True",
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
    # five 1m candles after aggregation: rising close, latest candle has upper-wick rejection.
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

    candles, diag = aggregate_ohlcv_from_rows(_rows(), timeframes_sec=(60,))
    summary = build_human_technical_summary(candles, timeframe_sec=60)
    missing = build_human_technical_summary([], timeframe_sec=60)
    data = summary.to_dict()
    decoded = json.loads(json.dumps(data, ensure_ascii=False, sort_keys=True))

    checks = {
        "exports_available": all(item is not None for item in (
            CandleWickBodySummary,
            HumanTechnicalSummary,
            MovingAverageSlopeSummary,
            RangeBoundarySummary,
            SupportResistanceZone,
            VolatilityTechnicalSummary,
            VwapRelationSummary,
            build_human_technical_summary,
        )),
        "sample_ohlcv_usable": diag.usable is True and len(candles) == 5,
        "summary_usable": summary.usable is True and summary.candle_count == 5,
        "support_and_resistance_visible": bool(summary.support_zones) and bool(summary.resistance_zones),
        "range_boundary_visible": summary.range_boundary.range_low == 100.0 and summary.range_boundary.range_high == 111.0,
        "ma_slope_visible": summary.moving_average.slope_label == "rising" and summary.moving_average.cross_state == "short_above_long",
        "vwap_relation_visible": summary.vwap_relation.relation in ("above_vwap", "below_vwap", "near_vwap"),
        "volatility_visible": summary.volatility.atr is not None and summary.volatility.range_width == 11.0,
        "wick_body_visible": summary.wick_body.wick_signal == "upper_wick_rejection",
        "missing_candles_blocked": missing.usable is False and "ohlcv_candles_missing" in missing.blockers,
        "summary_serializes": decoded["logic_version"] == "prediction_human_technical.s126.v1" and decoded["usable"] is True,
        "non_executing_flags_false": decoded["would_collect_public_source"] is False and decoded["would_write_runtime_artifact"] is False and decoded["would_send_to_broker"] is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/execution/" in line]
    failures.extend(f"protected execution/collector dirty during GO: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_go_human_technical_indicators_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_execution_and_collector_untouched": not protected_dirty_hits},
        "sample": {
            "candle_count": summary.candle_count,
            "range": summary.range_boundary.to_dict(),
            "ma": summary.moving_average.to_dict(),
            "wick_signal": summary.wick_body.wick_signal,
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_human_technical_indicators_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
