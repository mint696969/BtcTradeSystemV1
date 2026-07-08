# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_parameter_set_registry_cp8.py
# desc: CP8 tests for market-regime parameter-set registry MVP and writer artifact metadata. Tmp fixtures only; no scheduler, broker, AutoTrade, or live parameter apply.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.parameter_set import build_default_market_regime_parameter_set  # noqa: E402
from btcts.prediction.market_regime.parameter_set_registry import (  # noqa: E402
    MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
    MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION,
    build_default_market_regime_parameter_set_registry,
    validate_market_regime_parameter_set_registry,
)
from btcts.prediction.market_regime.tools.write_latest import build_market_regime_latest_artifact_set  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/103000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T10:30:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/103000/forecast_records.jsonl"},
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


def test_cp8_default_registry_has_single_active_and_safe_flags() -> None:
    registry = build_default_market_regime_parameter_set_registry()
    active = registry.active_parameter_set()
    assert active.parameter_set_id == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    assert registry.active_entry().registry_state == "active"
    assert registry.rollback_parameter_set_id == active.parameter_set_id
    result = validate_market_regime_parameter_set_registry(registry)
    assert result["ok"] is True
    assert result["active_parameter_set_id"] == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    data = registry.to_dict()
    assert data["safety"]["live_parameter_apply_allowed"] is False
    assert data["safety"]["candidate_auto_promotion_allowed"] is False
    assert data["safety"]["human_gate_required_for_active_change"] is True
    assert data["safety"]["broker_private_api_allowed"] is False
    assert data["safety"]["autotrade_trigger_allowed"] is False


def test_cp8_registry_accepts_candidate_without_changing_active() -> None:
    registry = build_default_market_regime_parameter_set_registry()
    candidate = build_default_market_regime_parameter_set().with_status("candidate", change_reason="test_candidate")
    candidate = candidate.__class__(
        parameter_set_id="market_regime_engine_parameter_set.candidate.test",
        version="0.1.1",
        status=candidate.status,
        created_by=candidate.created_by,
        change_reason=candidate.change_reason,
        supported_horizons_sec=candidate.supported_horizons_sec,
        required_feature_groups=candidate.required_feature_groups,
        thresholds=dict(candidate.thresholds),
        weights=dict(candidate.weights),
    )
    updated = registry.with_candidate(candidate, change_reason="shadow_eval_request", evidence_ref="replay:test")
    assert registry.active_parameter_set_id == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    assert updated.active_parameter_set_id == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    assert len(updated.entries_by_state("candidate")) == 1
    assert updated.entries_by_state("candidate")[0].parent_parameter_set_id == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    assert validate_market_regime_parameter_set_registry(updated)["ok"] is True


def test_cp8_writer_includes_parameter_set_registry_metadata(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T10:31:00Z",
        run_id="market_regime_cp8_test",
    )
    latest_cards = artifacts["latest_cards"]
    read_model = artifacts["latest_read_model"]
    compact = latest_cards["compact_summary"]
    source_summary = read_model["source_contribution_summary"]
    assert compact["parameter_set_registry_version"] == MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION
    assert compact["active_parameter_set_id"] == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    assert compact["parameter_set_registry_ok"] is True
    assert source_summary["parameter_set_registry"]["registry_version"] == MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION
    assert source_summary["active_parameter_set"]["parameter_set_id"] == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    for horizon in read_model["horizons"]:
        assert horizon["active_parameter_set_id"] == MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
        assert horizon["parameter_set_registry_version"] == MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION
