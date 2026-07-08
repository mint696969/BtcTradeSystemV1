# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_outcome_resolver_cp12.py
# desc: CP12 tests for market-regime outcome resolver MVP. Tmp fixtures only; no raw duplication, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.outcome_resolver import (  # noqa: E402
    MARKET_REGIME_OUTCOME_RESOLVER_VERSION,
    append_market_regime_outcome_row_once,
    build_market_regime_outcome_row,
    outcome_meta_relpath,
    outcome_part_relpath,
    resolve_market_regime_outcome_label,
    validate_market_regime_outcome_row,
)


def _prediction(**overrides):
    base = {
        "run_id": "market_regime_cp12_run",
        "prediction_id": "market_regime_cp12_run:latest",
        "generated_at": "2026-07-08T12:00:00Z",
        "horizon": "15分後",
        "horizon_sec": 900,
        "horizon_key": "900s",
        "regime_code": "RANGE",
        "confidence_percent": 70,
        "evidence_quality": "PARTIAL",
        "freshness_badge": "LIVE",
        "parameter_set_id": "market_regime_engine_parameter_set.v1",
        "detail": {"trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"},
    }
    base.update(overrides)
    return base


def test_cp12_outcome_partition_relpaths_are_stable() -> None:
    assert outcome_part_relpath("2026-07-08T12:34:56Z") == "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    assert outcome_meta_relpath("2026-07-08T12:34:56Z") == "prediction/market_regime/outcomes/date=2026-07-08/part-00001.meta.json"


def test_cp12_resolve_hit_partial_miss_invalidated_unknown() -> None:
    assert resolve_market_regime_outcome_label(predicted_regime_code="RANGE", observation={"observation_at": "2026-07-08T12:15:00Z", "observed_regime_code": "RANGE"}, expiry_at="2026-07-08T12:15:00Z")[0] == "hit"
    assert resolve_market_regime_outcome_label(predicted_regime_code="RANGE", observation={"observation_at": "2026-07-08T12:15:00Z", "observed_regime_code": "REVERSAL_WATCH"}, expiry_at="2026-07-08T12:15:00Z")[0] == "partial"
    assert resolve_market_regime_outcome_label(predicted_regime_code="RANGE", observation={"observation_at": "2026-07-08T12:15:00Z", "observed_regime_code": "UP_TREND"}, expiry_at="2026-07-08T12:15:00Z")[0] == "miss"
    assert resolve_market_regime_outcome_label(predicted_regime_code="RANGE", observation={"observation_at": "2026-07-08T12:15:00Z", "observed_regime_code": "UP_TREND", "invalidated": True}, expiry_at="2026-07-08T12:15:00Z")[0] == "invalidated"
    assert resolve_market_regime_outcome_label(predicted_regime_code="RANGE", observation={"observation_at": "2026-07-08T12:14:00Z", "observed_regime_code": "RANGE"}, expiry_at="2026-07-08T12:15:00Z")[0] == "unknown"


def test_cp12_build_outcome_row_is_valid_and_compact() -> None:
    row = build_market_regime_outcome_row(
        prediction=_prediction(),
        observation={
            "observation_at": "2026-07-08T12:15:00Z",
            "observed_regime_code": "RANGE",
            "source_refs": ["prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"],
            "summary": "range remained valid until horizon expiry",
        },
        resolved_at="2026-07-08T12:16:00Z",
    )
    assert row["outcome_resolver_version"] == MARKET_REGIME_OUTCOME_RESOLVER_VERSION
    assert row["outcome_label"] == "hit"
    assert row["expiry_at"] == "2026-07-08T12:15:00Z"
    assert row["trace_part_jsonl"]
    assert row["safety"]["raw_market_data_duplicated"] is False
    assert row["safety"]["parameter_auto_promotion_allowed"] is False
    assert validate_market_regime_outcome_row(row)["ok"] is True


def test_cp12_append_outcome_row_writes_jsonl_and_meta(tmp_path: Path) -> None:
    row = build_market_regime_outcome_row(
        prediction=_prediction(),
        observation={"observation_at": "2026-07-08T12:15:00Z", "observed_regime_code": "UP_TREND"},
        resolved_at="2026-07-08T12:16:00Z",
    )
    result = append_market_regime_outcome_row_once(tmp_path, row)
    assert result["ok"] is True
    assert result["row_count"] == 1
    part = tmp_path / result["outcome_part_jsonl"]
    meta = tmp_path / result["outcome_part_meta_json"]
    assert part.exists()
    assert meta.exists()
    rows = [json.loads(line) for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1
    assert rows[0]["outcome_label"] == "miss"
    meta_payload = json.loads(meta.read_text(encoding="utf-8"))
    assert meta_payload["row_count"] == 1
    assert meta_payload["raw_market_data_duplicated"] is False


def test_cp12_outcome_validation_rejects_raw_payload_and_unsafe_flags() -> None:
    row = build_market_regime_outcome_row(
        prediction=_prediction(),
        observation={"observation_at": "2026-07-08T12:15:00Z", "observed_regime_code": "RANGE"},
        resolved_at="2026-07-08T12:16:00Z",
    )
    bad = dict(row)
    bad["observation_summary"] = dict(bad["observation_summary"])
    bad["observation_summary"]["raw_candles"] = [{"close": 1}]
    bad["safety"] = dict(bad["safety"])
    bad["safety"]["broker_private_api_allowed"] = True
    result = validate_market_regime_outcome_row(bad)
    assert result["ok"] is False
    assert "forbidden_raw_payload_key_present" in result["failures"]
    assert "safety_broker_private_api_allowed_not_false" in result["failures"]
