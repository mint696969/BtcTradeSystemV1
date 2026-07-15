# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_shadow_pair_once.py
# desc: MR-F8.6 tests for the explicit-input read-only paired shadow forecast once tool.

from __future__ import annotations

import json

import pytest

from btcts.prediction.market_regime.tools.shadow_pair_once import build_shadow_pair_once_report, main


def bundle(bundle_id: str = "bundle:1") -> dict:
    return {
        "artifact_kind": "future_origin_evidence_bundle",
        "bundle_id": bundle_id,
        "prediction_origin": "2026-07-15T00:00:00Z",
        "feature_snapshot_ref": "snapshot:mr-f8.6",
        "target_horizon_sec": 900,
        "origin_current_state": "RANGE",
        "candidate_probability_by_state": {"BREAKOUT": 0.44, "RANGE": 0.34, "UP_TREND": 0.22},
        "feature_snapshot": {
            "origin_current_state": "RANGE",
            "available_feature_families": ["price_structure", "volatility", "liquidity", "source_quality", "microprice"],
            "source_timestamp_epoch_sec": 100.0,
            "origin_timestamp_epoch_sec": 100.0,
        },
    }


def test_builds_pair_from_single_bundle_without_write_surface() -> None:
    report = build_shadow_pair_once_report(input_payload=bundle())
    assert report["pair_count"] == 1
    assert report["pairs"][0]["candidate_count"] == 2
    assert report["safety"]["writes_hot_data"] is False
    assert report["safety"]["parameter_auto_promotion_allowed"] is False


def test_builds_pairs_from_batch() -> None:
    payload = {"artifact_kind": "future_origin_evidence_batch", "rows": [bundle("a"), bundle("b")]}
    report = build_shadow_pair_once_report(input_payload=payload)
    assert report["pair_count"] == 2


def test_duplicate_bundle_id_fails_closed() -> None:
    payload = {"artifact_kind": "future_origin_evidence_batch", "rows": [bundle(), bundle()]}
    with pytest.raises(ValueError, match="duplicate_bundle_id"):
        build_shadow_pair_once_report(input_payload=payload)


def test_cli_requires_preflight(tmp_path) -> None:
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(bundle()), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        main(["--input-json", str(path)])
    assert exc.value.code == 2
    assert main(["--input-json", str(path), "--preflight"]) == 0
