# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_trace_ledger_cp9.py
# desc: CP9 tests for market-regime trace ledger MVP. Tmp fixtures only; appends prediction trace JSONL, no raw market duplication, scheduler, broker, AutoTrade, or trade ledger behavior.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.trace_ledger import (  # noqa: E402
    MARKET_REGIME_TRACE_LEDGER_VERSION,
    append_market_regime_trace_row_once,
    trace_ledger_meta_relpath,
    trace_ledger_part_relpath,
    validate_market_regime_trace_row,
)
from btcts.prediction.market_regime.tools.write_latest import (  # noqa: E402
    build_market_regime_latest_artifact_set,
    write_market_regime_latest_artifacts_once,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/110000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T11:00:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/110000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "score": 0.80, "values_snapshot": {"estimated_signal_strength_percent": 70, "estimated_reference_hit_rate_percent": 65, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 900, "primary_label": "trend_candidate", "score": 0.88, "values_snapshot": {"estimated_signal_strength_percent": 82, "estimated_reference_hit_rate_percent": 74, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9730264.0,
        "last_spread": 1200.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def _contains_forbidden_key(value: object) -> bool:
    forbidden = {"raw_candles", "raw_orderbook", "raw_trades", "raw_executions", "raw_market_payload", "raw_source_payload", "bids", "asks", "trades", "executions"}
    if isinstance(value, dict):
        return any(str(key) in forbidden or _contains_forbidden_key(nested) for key, nested in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def test_cp9_trace_partition_relpaths_are_stable() -> None:
    assert trace_ledger_part_relpath("2026-07-08T11:22:33Z") == "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl"
    assert trace_ledger_meta_relpath("2026-07-08T11:22:33Z") == "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.meta.json"


def test_cp9_build_artifact_set_contains_valid_trace_row_without_filesystem_write(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T11:01:00Z",
        run_id="market_regime_cp9_test",
    )
    trace_row = artifacts["trace_row"]
    assert trace_row["trace_ledger_version"] == MARKET_REGIME_TRACE_LEDGER_VERSION
    assert trace_row["trace_part_jsonl"] == "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl"
    assert validate_market_regime_trace_row(trace_row)["ok"] is True
    assert trace_row["safety"]["trace_ledger_append_only"] is True
    assert trace_row["safety"]["broker_private_api_allowed"] is False
    assert trace_row["safety"]["autotrade_trigger_allowed"] is False
    assert _contains_forbidden_key(trace_row) is False
    assert not (tmp_path / trace_row["trace_part_jsonl"]).exists()
    assert artifacts["manifest"]["refs"]["trace_part_jsonl"] == trace_row["trace_part_jsonl"]


def test_cp9_append_market_regime_trace_row_once_writes_jsonl_and_meta(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T11:02:00Z",
        run_id="market_regime_cp9_append_test",
    )
    result = append_market_regime_trace_row_once(tmp_path, artifacts["trace_row"])
    assert result["ok"] is True
    assert result["row_count"] == 1
    part = tmp_path / result["trace_part_jsonl"]
    meta = tmp_path / result["trace_part_meta_json"]
    assert part.exists()
    assert meta.exists()
    rows = [json.loads(line) for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1
    assert rows[0]["run_id"] == "market_regime_cp9_append_test"
    assert _contains_forbidden_key(rows[0]) is False
    meta_payload = json.loads(meta.read_text(encoding="utf-8"))
    assert meta_payload["row_count"] == 1
    assert meta_payload["raw_market_data_duplicated"] is False


def test_cp9_write_latest_once_appends_trace_and_updates_status_manifest(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    result = write_market_regime_latest_artifacts_once(
        hot_root=tmp_path,
        generated_at="2026-07-08T11:03:00Z",
        run_id="market_regime_cp9_write_test",
    )
    assert result["ok"] is True
    assert result["trace_ledger_append"]["ok"] is True
    assert result["prediction_trace_append_allowed"] is True
    assert result["trade_ledger_append_allowed"] is False
    trace_part = tmp_path / "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl"
    assert trace_part.exists()
    status = json.loads((tmp_path / "prediction/market_regime/status.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "prediction/market_regime/runs/market_regime_cp9_write_test/manifest.json").read_text(encoding="utf-8"))
    assert status["trace_ledger_available"] is True
    assert status["outcome_resolver_available"] is True
    assert manifest["refs"]["trace_part_jsonl"] == "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl"

def test_mr_vs4_trace_row_contains_compact_source_attribution_for_future_scorecards(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T11:04:00Z",
        run_id="market_regime_mr_vs4_attribution_test",
    )
    trace_row = artifacts["trace_row"]
    attribution = trace_row["source_attribution_by_horizon"]
    assert set(attribution) == {"current", "300s", "900s", "1800s", "3600s", "21600s", "43200s", "86400s"}
    sample = attribution["300s"]
    assert sample["horizon_key"] == "300s"
    assert sample["predicted_regime"]
    assert sample["parameter_set_id"] == artifacts["active_parameter_set_id"]
    assert sample["source_signals"]
    for signal in sample["source_signals"].values():
        assert set(signal) == {
            "direction",
            "signal_strength_percent",
            "freshness_percent",
            "quality_percent",
            "blocked",
        }
    encoded = json.dumps(trace_row, ensure_ascii=False, sort_keys=True).encode("utf-8")
    assert len(encoded) < 128 * 1024
    assert _contains_forbidden_key(trace_row) is False
