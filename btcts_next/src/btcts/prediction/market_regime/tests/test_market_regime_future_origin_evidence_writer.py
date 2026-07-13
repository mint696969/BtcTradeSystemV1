# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_writer.py
# desc: MR-F6.6 fixture-root tests for the disabled append-only prediction-origin evidence writer.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_origin_evidence import MarketRegimeOriginEvidence, build_market_regime_origin_evidence_bundle
from btcts.prediction.market_regime.future_origin_evidence_writer import build_origin_evidence_approval, build_origin_evidence_write_plan, preflight_origin_evidence_write, write_origin_evidence_once


def _bundle(trace: str = "trace:1"):
    return build_market_regime_origin_evidence_bundle(MarketRegimeOriginEvidence(
        prediction_origin="2026-07-14T00:00:00Z", prediction_origin_epoch_sec=1000.0,
        source_timestamp="2026-07-13T23:59:59Z", source_timestamp_epoch_sec=999.0,
        target_horizon_sec=300, trace_id=trace, model_id="model.v1", logic_version="logic.v1",
        parameter_set_id="params.v1", target_definition_version="market_regime_target.300s.v1",
        feature_snapshot_ref=f"snapshot:{trace}", current_state=MarketRegimeCode.RANGE,
        previous_state=MarketRegimeCode.RANGE, regime_scores={MarketRegimeCode.RANGE: 1.0},
        recent_return=0.0, fast_ma=100.0, slow_ma=100.0, realized_volatility=0.02,
        low_volatility_threshold=0.01, high_volatility_threshold=0.03,
        current_forecast_label_selection=MarketRegimeCode.RANGE,
    ))


def _plan(bundles=None):
    return build_origin_evidence_write_plan(generated_at="2026-07-14T00:00:00Z", writer_id="mr-f6-origin-writer", writer_contract_version="writer.v1", bundles=bundles or (_bundle(),))


def _approval():
    return build_origin_evidence_approval(approval_id="approval:test", operator_ids=("operator:test",), requested_at="2026-07-14T00:00:00Z", expires_at="2026-07-15T00:00:00Z", approved_writer_id="mr-f6-origin-writer", approved_writer_contract_version="writer.v1")


def test_preflight_does_not_write(tmp_path: Path) -> None:
    result = preflight_origin_evidence_write(plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z")
    assert result["write_allowed"] is True
    assert result["would_write"] is False
    assert not list(tmp_path.rglob("*"))


def test_writer_disabled_and_once_ack_required(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="disabled_by_default"):
        write_origin_evidence_once(tmp_path, plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z")
    with pytest.raises(PermissionError, match="once_ack_required"):
        write_origin_evidence_once(tmp_path, plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z", enabled=True)


def test_writer_creates_isolated_append_only_batch(tmp_path: Path) -> None:
    result = write_origin_evidence_once(tmp_path, plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z", enabled=True, once=True)
    path = tmp_path / result["artifact_relpath"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert result["written"] is True
    assert payload["append_only"] is True
    assert payload["canonical_isolated"] is True
    assert payload["historical_backfill_allowed"] is False
    assert "latest" not in result["artifact_relpath"]


def test_same_batch_is_idempotent_and_conflict_fails(tmp_path: Path) -> None:
    first = write_origin_evidence_once(tmp_path, plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z", enabled=True, once=True)
    second = write_origin_evidence_once(tmp_path, plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z", enabled=True, once=True)
    assert first["written"] is True and second["duplicate"] is True
    path = tmp_path / first["artifact_relpath"]
    path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="existing_artifact_conflict"):
        write_origin_evidence_once(tmp_path, plan=_plan(), approval=_approval(), bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z", enabled=True, once=True)


def test_tamper_and_approval_scope_fail_closed() -> None:
    tampered = dict(_bundle()); tampered["parameter_set_id"] = "tampered"
    with pytest.raises(ValueError, match="bundle_hash_mismatch"):
        preflight_origin_evidence_write(plan=_plan(), approval=_approval(), bundles=(tampered,), executed_at="2026-07-14T01:00:00Z")
    bad = dict(_approval()); bad["approved_writer_id"] = "other"
    with pytest.raises(PermissionError, match="approval_scope_mismatch"):
        preflight_origin_evidence_write(plan=_plan(), approval=bad, bundles=(_bundle(),), executed_at="2026-07-14T01:00:00Z")


def test_plan_and_runtime_bundle_sets_must_match_exactly() -> None:
    plan = _plan((_bundle("trace:1"),))
    with pytest.raises(ValueError, match="bundle_set_mismatch"):
        preflight_origin_evidence_write(
            plan=plan,
            approval=_approval(),
            bundles=(_bundle("trace:1"), _bundle("trace:extra")),
            executed_at="2026-07-14T01:00:00Z",
        )
    bad_count = dict(plan)
    bad_count["row_count"] = 2
    with pytest.raises(ValueError, match="plan_row_count_mismatch"):
        preflight_origin_evidence_write(
            plan=bad_count,
            approval=_approval(),
            bundles=(_bundle("trace:1"),),
            executed_at="2026-07-14T01:00:00Z",
        )
    bad_hashes = dict(plan)
    bad_hashes["bundle_hashes"] = ()
    with pytest.raises(ValueError, match="plan_bundle_identity_invalid"):
        preflight_origin_evidence_write(
            plan=bad_hashes,
            approval=_approval(),
            bundles=(_bundle("trace:1"),),
            executed_at="2026-07-14T01:00:00Z",
        )


def test_nested_immutable_bundle_values_are_serialized_canonically(tmp_path: Path) -> None:
    bundle = _bundle()
    plan = _plan((bundle,))
    result = write_origin_evidence_once(
        tmp_path,
        plan=plan,
        approval=_approval(),
        bundles=(bundle,),
        executed_at="2026-07-14T01:00:00Z",
        enabled=True,
        once=True,
    )
    payload = json.loads((tmp_path / result["artifact_relpath"]).read_text(encoding="utf-8"))
    row = payload["rows"][0]
    assert isinstance(row["feature_snapshot"], dict)
    assert isinstance(row["candidate_probability_by_state"], dict)
    assert row["candidate_probability_by_state"] == {"RANGE": 1.0}


def test_no_cli_or_scheduler_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_writer as module
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
