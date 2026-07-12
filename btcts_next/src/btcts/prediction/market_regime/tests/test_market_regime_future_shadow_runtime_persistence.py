# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_persistence.py
# desc: MR-F5.16 disabled-by-default trace persistence and expiry-gated observation polling tests.
from __future__ import annotations

import json

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_shadow_runtime_persistence import (
    build_future_shadow_trace_persistence_plan,
    persist_future_shadow_traces_once,
    poll_future_shadow_observations,
)
from btcts.prediction.market_regime.future_trace_identity import build_market_regime_future_trace_identity


def _trace(horizon: int = 300):
    forecast = forecast_future_market_regime_baseline(FutureBaselineEvidence(
        origin_timestamp="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        target_horizon_sec=horizon,
        feature_snapshot_ref="snapshot:mr-f5.16",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
        available_feature_families=("price_structure", "volatility", "liquidity", "microprice", "source_quality", "session_context"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    ))
    return build_market_regime_future_trace_identity(forecast)


def test_plan_is_deterministic_and_logical_root_only() -> None:
    plan = build_future_shadow_trace_persistence_plan(traces=(_trace(900), _trace(300)), generated_at="2026-07-12T00:00:00Z")
    assert plan["source_role"] == "hot_data_root"
    assert plan["artifact_relpath"].startswith("prediction/market_regime/future_shadow/runtime_traces/date=2026-07-12/")
    assert plan["trace_ids"] == tuple(sorted(plan["trace_ids"]))
    assert plan["would_write"] is False
    assert all(
        row["contract_version"] == "prediction.market_regime.future_trace_identity.mr_f5_5.v1"
        for row in plan["rows"]
    )
    assert all(row["target_horizon_key"] == f"{row['target_horizon_sec']}s" for row in plan["rows"])


def test_persistence_is_disabled_by_default_and_once_only(tmp_path) -> None:
    plan = build_future_shadow_trace_persistence_plan(traces=(_trace(),), generated_at="2026-07-12T00:00:00Z")
    with pytest.raises(PermissionError, match="disabled_by_default"):
        persist_future_shadow_traces_once(tmp_path, plan=plan)
    with pytest.raises(PermissionError, match="once_ack_required"):
        persist_future_shadow_traces_once(tmp_path, plan=plan, enabled=True)
    first = persist_future_shadow_traces_once(tmp_path, plan=plan, enabled=True, once=True)
    second = persist_future_shadow_traces_once(tmp_path, plan=plan, enabled=True, once=True)
    assert first["written"] is True
    assert second["duplicate"] is True
    payload = json.loads((tmp_path / first["artifact_relpath"]).read_text(encoding="utf-8"))
    assert payload["trace_count"] == 1
    assert payload["canonical_replacement"] is False


def test_persistence_rejects_tampered_plan_and_path_escape(tmp_path) -> None:
    plan = dict(build_future_shadow_trace_persistence_plan(
        traces=(_trace(),), generated_at="2026-07-12T00:00:00Z"
    ))
    escaped = dict(plan)
    escaped["artifact_relpath"] = (
        "prediction/market_regime/future_shadow/runtime_traces/date=2026-07-12/../../escape.json"
    )
    with pytest.raises(ValueError, match="relpath_invalid"):
        persist_future_shadow_traces_once(
            tmp_path, plan=escaped, enabled=True, once=True
        )
    wrong_count = dict(plan)
    wrong_count["trace_count"] = 2
    with pytest.raises(ValueError, match="trace_count_mismatch"):
        persist_future_shadow_traces_once(
            tmp_path, plan=wrong_count, enabled=True, once=True
        )
    wrong_ids = dict(plan)
    wrong_ids["trace_ids"] = ("tampered",)
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        persist_future_shadow_traces_once(
            tmp_path, plan=wrong_ids, enabled=True, once=True
        )


def test_persistence_rejects_tampered_row_contract_and_safety(tmp_path) -> None:
    plan = dict(build_future_shadow_trace_persistence_plan(
        traces=(_trace(),), generated_at="2026-07-12T00:00:00Z"
    ))
    tampered_rows = dict(plan)
    row = dict(plan["rows"][0])
    row["feature_snapshot_ref"] = "tampered:snapshot"
    tampered_rows["rows"] = (row,)
    with pytest.raises(ValueError, match="row_contract"):
        persist_future_shadow_traces_once(
            tmp_path, plan=tampered_rows, enabled=True, once=True
        )
    tampered_safety = dict(plan)
    tampered_safety["scheduler_enabled"] = True
    with pytest.raises(ValueError, match="plan_safety_invalid"):
        persist_future_shadow_traces_once(
            tmp_path, plan=tampered_safety, enabled=True, once=True
        )
    tampered_kind = dict(plan)
    tampered_kind["artifact_kind"] = "canonical_trace_set"
    with pytest.raises(ValueError, match="plan_kind_invalid"):
        persist_future_shadow_traces_once(
            tmp_path, plan=tampered_kind, enabled=True, once=True
        )


def test_polling_rejects_duplicate_or_invalid_trace() -> None:
    trace = _trace()
    with pytest.raises(ValueError, match="poll_trace_duplicate"):
        poll_future_shadow_observations(
            traces=(trace, trace), polled_at=trace.expiry_at,
            observation_reader=lambda item, at: None,
        )
    with pytest.raises(ValueError, match="poll_trace_invalid"):
        poll_future_shadow_observations(
            traces=(object(),), polled_at=trace.expiry_at,
            observation_reader=lambda item, at: None,
        )


def test_polling_skips_unexpired_trace() -> None:
    trace = _trace()
    calls = []
    result = poll_future_shadow_observations(
        traces=(trace,), polled_at="2026-07-12T00:04:59Z",
        observation_reader=lambda item, at: calls.append((item.trace_id, at)),
    )
    assert result == {}
    assert calls == []


def test_polling_reads_only_expired_trace_and_keys_by_trace_id() -> None:
    trace = _trace()
    result = poll_future_shadow_observations(
        traces=(trace,), polled_at=trace.expiry_at,
        observation_reader=lambda item, at: {
            "observation_available": True,
            "observed_at": at,
            "observed_future_state": MarketRegimeCode.BREAKOUT,
            "observation_source_ref": "fixture:closed-candle",
        },
    )
    assert tuple(result) == (trace.trace_id,)
    assert result[trace.trace_id].observed_future_state is MarketRegimeCode.BREAKOUT


def test_plan_rejects_origin_mismatch_and_duplicates() -> None:
    trace = _trace()
    with pytest.raises(ValueError, match="origin_mismatch"):
        build_future_shadow_trace_persistence_plan(traces=(trace,), generated_at="2026-07-12T00:00:01Z")
    with pytest.raises(ValueError, match="trace_duplicate"):
        build_future_shadow_trace_persistence_plan(traces=(trace, trace), generated_at="2026-07-12T00:00:00Z")
