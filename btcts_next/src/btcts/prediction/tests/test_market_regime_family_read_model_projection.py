# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_family_read_model_projection.py
# desc: MR-VS6.2 pure projection guards from MarketRegime packets into the common family read-model contract.

from __future__ import annotations

import ast
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.family_read_model import validate_prediction_family_read_model  # noqa: E402
from btcts.prediction.market_regime import (  # noqa: E402
    EvidenceQuality,
    FreshnessState,
    MarketRegimeCode,
    MarketRegimePrediction,
    MarketRegimePredictionPacket,
    TacticalHint,
)
from btcts.prediction.market_regime.artifact_projection import (  # noqa: E402
    build_market_regime_family_read_model,
)


def _packet() -> MarketRegimePredictionPacket:
    horizons = (
        ("現在", 0),
        ("5分後", 300),
        ("15分後", 900),
        ("30分後", 1800),
        ("60分後", 3600),
        ("6時間後", 21600),
        ("12時間後", 43200),
        ("24時間後", 86400),
    )
    predictions = tuple(
        MarketRegimePrediction(
            horizon_label=label,
            horizon_sec=seconds,
            regime_code=MarketRegimeCode.UNKNOWN if seconds == 86400 else MarketRegimeCode.RANGE,
            confidence_percent=15 if seconds == 86400 else 63,
            evidence_quality=EvidenceQuality.MISSING if seconds == 86400 else EvidenceQuality.PARTIAL,
            freshness_state=FreshnessState.MISSING if seconds == 86400 else FreshnessState.LIVE,
            tactical_hint=TacticalHint.UNKNOWN_HOLD if seconds == 86400 else TacticalHint.RANGE_TACTIC,
            drivers=("price_in_range",),
            warnings=("comparison_not_ready",),
            missing_sources=("cross_venue",) if seconds == 86400 else (),
            invalidation_hints=("range_break",),
            parameter_set_id="market_regime.pset.test.v1",
            source_priority_policy_id="market_regime.source_policy.test.v1",
            feature_bundle_hash=f"bundle-{seconds}",
        )
        for label, seconds in horizons
    )
    return MarketRegimePredictionPacket(
        generated_at="2026-07-12T00:00:00Z",
        predictions=predictions,
        parameter_set_id="market_regime.pset.test.v1",
        logic_version="market_regime.logic.test.v1",
    )


def _model() -> dict:
    return build_market_regime_family_read_model(
        packet=_packet(),
        run_id="market-regime-run-1",
        prediction_id="market-regime-prediction-1",
        model_id="market-regime-model-1",
        feature_set_version="market-regime-features-1",
        target_definition_version="market-regime-targets-1",
        evaluation_window_ref="eval-window-1",
        source_refs=[{"artifact_kind": "latest_prediction", "relpath": "prediction/latest.json"}],
        trace_refs=[{"artifact_kind": "trace", "trace_id": "trace-1"}],
    )


def test_projection_is_exported_from_market_regime_package() -> None:
    from btcts.prediction.market_regime import build_market_regime_family_read_model as exported

    assert exported is build_market_regime_family_read_model


def test_projection_preserves_identity_and_all_eight_horizons() -> None:
    model = _model()
    assert validate_prediction_family_read_model(model)["ok"] is True
    assert model["prediction_family_id"] == "market_regime"
    assert model["run_id"] == "market-regime-run-1"
    assert model["prediction_id"] == "market-regime-prediction-1"
    assert model["model_id"] == "market-regime-model-1"
    assert model["logic_version"] == "market_regime.logic.test.v1"
    assert model["parameter_set_id"] == "market_regime.pset.test.v1"
    assert model["feature_set_version"] == "market-regime-features-1"
    assert model["target_definition_version"] == "market-regime-targets-1"
    assert model["horizon_count"] == 8
    assert [row["horizon_sec"] for row in model["horizon_rows"]] == [0, 300, 900, 1800, 3600, 21600, 43200, 86400]
    assert [row["horizon_group"] for row in model["horizon_rows"]] == [
        "current", "short_horizon", "short_horizon", "short_horizon",
        "short_horizon", "long_horizon", "long_horizon", "long_horizon",
    ]


def test_projection_preserves_unknown_15_percent_and_regime_payload() -> None:
    row = _model()["horizon_rows"][-1]
    assert row["primary_label"] == "UNKNOWN"
    assert row["primary_label_display"] == "不明"
    assert row["confidence_percent"] == 15
    assert row["blockers"] == ["cross_venue"]
    assert row["family_payload"] == {
        "regime_code": "UNKNOWN",
        "regime_label": "不明",
        "tactical_hint": "UNKNOWN_HOLD",
        "source_priority_policy_id": "market_regime.source_policy.test.v1",
        "signal_summary_ref": "bundle-86400",
    }


def test_projection_carries_only_bounded_refs_and_no_raw_diagnostic_payload() -> None:
    row = _model()["horizon_rows"][0]
    assert row["source_refs"] == [{"artifact_kind": "latest_prediction", "relpath": "prediction/latest.json"}]
    assert row["trace_refs"] == [{"artifact_kind": "trace", "trace_id": "trace-1"}]
    assert "diagnostic_record" not in row
    assert "raw_candles" not in repr(row)
    assert "raw_orderbook" not in repr(row)
    assert _model()["safety"]["broker_private_api_allowed"] is False
    assert _model()["safety"]["autotrade_trigger_allowed"] is False
    assert _model()["safety"]["order_intent_submitted"] is False


def test_projection_module_remains_pure_and_has_no_ui_or_execution_dependencies() -> None:
    module_path = Path(__file__).resolve().parents[1] / "market_regime" / "artifact_projection.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    imported_modules: set[str] = set()
    called_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)

    forbidden_import_prefixes = ("streamlit", "requests", "btcts.apps.operator_ui")
    forbidden_calls = {"write_text", "write_bytes", "run", "Popen", "post", "submit_order", "send_order"}
    assert [name for name in imported_modules if name.startswith(forbidden_import_prefixes)] == []
    assert sorted(called_names & forbidden_calls) == []
