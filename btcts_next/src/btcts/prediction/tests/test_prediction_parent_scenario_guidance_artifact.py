# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_parent_scenario_guidance_artifact.py
# desc: PS_PARENT_SCENARIO_GUIDANCE_ARTIFACT_V1 tests. Verifies common parent scenario-guidance latest read-model artifact is pure, grouped by horizon, and non-executing.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.scenario_guidance import (  # noqa: E402
    PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH,
    PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION,
    build_parent_scenario_guidance_latest_read_model_artifact,
    parent_scenario_guidance_latest_read_model_relpath,
    validate_parent_scenario_guidance_latest_read_model_artifact,
)
from btcts.prediction.scenario_parts import build_prediction_family_scenario_part  # noqa: E402


def _part(family: str, horizon_key: str, state: str, role: str, confidence: int, *, blockers: list[str] | None = None) -> dict[str, object]:
    return build_prediction_family_scenario_part(
        prediction_family_id=family,
        horizon_key=horizon_key,
        horizon_group="nowcast" if horizon_key == "current" else "short_horizon",
        scenario_state=state,
        scenario_label=f"{family}:{state}",
        scenario_summary=f"{family} contributes {state}",
        confidence_percent=confidence,
        estimated_signal_strength_percent=confidence,
        part_role=role,
        blockers=blockers or [],
        warnings=[],
        evidence_refs=[{"artifact_ref": f"prediction/{family}/latest_read_model.json"}],
        parameter_set_id=f"{family}.pset.v1",
        generated_at="2026-07-10T00:00:00Z",
    )


def test_parent_scenario_guidance_artifact_groups_parts_by_horizon() -> None:
    artifact = build_parent_scenario_guidance_latest_read_model_artifact(
        [
            _part("market_regime", "current", "bullish", "primary_context", 65),
            _part("volatility_risk", "current", "risk_off", "risk_cap", 55),
            _part("market_regime", "300s", "bullish", "primary_context", 65),
        ],
        generated_at="2026-07-10T00:00:00Z",
        source_run_id="parent_guidance_test",
    )

    assert artifact["contract_version"] == PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_VERSION
    assert artifact["artifact_kind"] == "parent_scenario_guidance_latest_read_model"
    assert artifact["relpath"] == PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH
    assert parent_scenario_guidance_latest_read_model_relpath() == PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH
    assert artifact["horizon_count"] == 2
    assert artifact["family_part_count"] == 3
    assert artifact["prediction_family_ids"] == ["market_regime", "volatility_risk"]
    assert artifact["horizons"][0]["horizon_key"] == "current"
    assert artifact["horizons"][0]["family_part_count"] == 2
    assert artifact["horizons"][0]["dominant_family_id"] == "market_regime"
    assert artifact["horizons"][1]["horizon_key"] == "300s"
    assert artifact["safety"]["writes_dhot"] is False
    assert artifact["safety"]["ui_render_invokes_classifier"] is False
    assert artifact["safety"]["broker_private_api_allowed"] is False
    assert artifact["safety"]["autotrade_trigger_allowed"] is False
    assert validate_parent_scenario_guidance_latest_read_model_artifact(artifact)["ok"] is True


def test_parent_scenario_guidance_artifact_rejects_invalid_parts_without_execution() -> None:
    valid = _part("market_regime", "current", "bullish", "primary_context", 65)
    invalid = dict(valid)
    invalid["scenario_state"] = "moonshot"

    artifact = build_parent_scenario_guidance_latest_read_model_artifact([valid, invalid], generated_at="2026-07-10T00:00:00Z")

    assert artifact["horizon_count"] == 1
    assert artifact["family_part_count"] == 1
    assert artifact["rejected_part_count"] == 1
    assert artifact["rejected_parts"][0]["prediction_family_id"] == "market_regime"
    assert "scenario_state_not_allowed" in artifact["rejected_parts"][0]["failures"]
    assert artifact["safety"]["prediction_invoked"] is False
    assert artifact["safety"]["classifier_invoked"] is False
    assert validate_parent_scenario_guidance_latest_read_model_artifact(artifact)["ok"] is True


def test_parent_scenario_guidance_artifact_validator_rejects_raw_payload_and_mutation_flags() -> None:
    artifact = build_parent_scenario_guidance_latest_read_model_artifact([
        _part("market_regime", "current", "bullish", "primary_context", 65)
    ])
    artifact["horizons"][0]["raw_candles"] = []
    artifact["safety"]["live_parameter_apply_allowed"] = True

    validation = validate_parent_scenario_guidance_latest_read_model_artifact(artifact)

    assert validation["ok"] is False
    assert "forbidden_raw_payload_key_present" in validation["failures"]
    assert "safety_live_parameter_apply_allowed_not_false" in validation["failures"]


def test_parent_scenario_guidance_source_has_no_writer_or_runtime_paths() -> None:
    text = (Path(__file__).resolve().parents[1] / "scenario_guidance.py").read_text(encoding="utf-8")
    required = [
        "build_parent_scenario_guidance_latest_read_model_artifact",
        "validate_parent_scenario_guidance_latest_read_model_artifact",
        "parent_scenario_guidance_latest_read_model_relpath",
        "parent_guidance_artifact_only",
        "ui_render_invokes_classifier",
        "live_parameter_apply_allowed",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_text(",
        "subprocess.Popen",
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
