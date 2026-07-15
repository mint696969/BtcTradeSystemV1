# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_shadow_pair_write_once.py
# desc: MR-F8.6 tests for the guarded dry-run/default and explicit-once shadow pair writer CLI boundary.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_pair_trace_plan import build_future_shadow_pair_trace_plan
from btcts.prediction.market_regime.tools.shadow_pair_write_once import (
    classify_output_root,
    execute_shadow_pair_write_once,
)


def report() -> dict:
    evidence = FutureBaselineEvidence(
        origin_timestamp="2026-07-15T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:writer-cli",
        regime_scores={
            MarketRegimeCode.BREAKOUT: 0.44,
            MarketRegimeCode.RANGE: 0.34,
            MarketRegimeCode.UP_TREND: 0.22,
        },
        available_feature_families=(
            "price_structure",
            "volatility",
            "liquidity",
            "source_quality",
            "microprice",
        ),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )
    pair = dict(build_future_shadow_candidate_pair(evidence=evidence))
    pair["trace_plan"] = build_future_shadow_pair_trace_plan(pair=pair)
    return {
        "schema_version": "market_regime_shadow_pair_once_report.mr_f8_6.v1",
        "ok": True,
        "pairs": [pair],
    }


def test_repo_tmp_root_is_allowed_and_other_root_is_rejected(tmp_path) -> None:
    repo = tmp_path / "repo"
    allowed = repo / "tmp" / "mr_f8"
    assert classify_output_root(allowed, repository_root=repo, hot_root=tmp_path / "hot") == "repo_tmp"
    with pytest.raises(ValueError, match="output_root_not_allowed"):
        classify_output_root(repo / "outside", repository_root=repo, hot_root=tmp_path / "hot")


def test_dry_run_is_default_and_does_not_write(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "evidence"
    result = execute_shadow_pair_write_once(
        preflight_report=report(),
        pair_index=0,
        output_root=output,
        repository_root=repo,
        hot_root=tmp_path / "hot",
    )
    assert result["dry_run"] is True
    assert result["written"] is False
    assert not output.exists()


def test_tmp_write_is_explicit_and_idempotent(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "evidence"
    kwargs = {
        "preflight_report": report(),
        "pair_index": 0,
        "output_root": output,
        "write": True,
        "once": True,
        "explicit_write_ack": True,
        "repository_root": repo,
        "hot_root": tmp_path / "hot",
    }
    first = execute_shadow_pair_write_once(**kwargs)
    assert first["written"] is True
    assert first["verified"] is True
    second = execute_shadow_pair_write_once(**kwargs)
    assert second["written"] is False
    assert second["duplicate"] is True


def test_dhot_requires_additional_ack(tmp_path) -> None:
    repo = tmp_path / "repo"
    hot = tmp_path / "hot"
    with pytest.raises(PermissionError, match="dhot_ack_required"):
        execute_shadow_pair_write_once(
            preflight_report=report(),
            pair_index=0,
            output_root=hot,
            repository_root=repo,
            hot_root=hot,
        )
    result = execute_shadow_pair_write_once(
        preflight_report=report(),
        pair_index=0,
        output_root=hot,
        allow_dhot_write=True,
        repository_root=repo,
        hot_root=hot,
    )
    assert result["dry_run"] is True
    assert result["output_root_kind"] == "d_hot"
    assert not hot.exists()


def test_write_still_requires_once_and_explicit_ack(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "evidence"
    with pytest.raises(PermissionError, match="once_ack_required"):
        execute_shadow_pair_write_once(
            preflight_report=report(),
            pair_index=0,
            output_root=output,
            write=True,
            repository_root=repo,
            hot_root=tmp_path / "hot",
        )
