# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_parent_scenario_guidance_artifacts_writer.py
# desc: PS_PARENT_SCENARIO_GUIDANCE_WRITER_V1 tests. Verifies parent scenario-guidance writer writes only the parent guidance read-model artifact and remains non-executing.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.scenario_guidance import (  # noqa: E402
    PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH,
    validate_parent_scenario_guidance_latest_read_model_artifact,
)
from btcts.prediction.scenario_guidance_artifacts import (  # noqa: E402
    PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_WRITER_VERSION,
    build_parent_scenario_guidance_artifact_write_plan,
    preflight_parent_scenario_guidance_latest_read_model,
    write_parent_scenario_guidance_latest_read_model,
)
from btcts.prediction.scenario_parts import build_prediction_family_scenario_part  # noqa: E402


def _part(family: str = "market_regime", horizon_key: str = "current", state: str = "bullish", role: str = "primary_context", confidence: int = 65) -> dict[str, object]:
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
        evidence_refs=[{"artifact_ref": f"prediction/{family}/latest_read_model.json"}],
        parameter_set_id=f"{family}.pset.v1",
        generated_at="2026-07-10T00:00:00Z",
    )


def test_parent_scenario_guidance_preflight_builds_plan_without_writing(tmp_path: Path) -> None:
    plan = build_parent_scenario_guidance_artifact_write_plan(
        tmp_path,
        family_scenario_parts=[
            _part("market_regime", "current", "bullish", "primary_context", 65),
            _part("market_regime", "300s", "bullish", "primary_context", 65),
        ],
        generated_at="2026-07-10T00:00:00Z",
        source_run_id="parent_guidance_writer_test",
    )

    assert plan["ok"] is True
    assert plan["preflight_only"] is True
    assert plan["would_write"] is False
    assert plan["parent_scenario_guidance_artifact_writer_version"] == PREDICTION_PARENT_SCENARIO_GUIDANCE_ARTIFACT_WRITER_VERSION
    assert plan["parent_scenario_guidance_read_model_json"] == PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH
    assert plan["horizon_count"] == 2
    assert plan["family_part_count"] == 2
    assert plan["rejected_part_count"] == 0
    assert plan["prediction_family_ids"] == ["market_regime"]
    assert plan["scenario_states"] == ["bullish"]
    assert plan["safety"]["writes_parent_scenario_guidance_read_model_only"] is True
    assert plan["safety"]["broker_private_api_allowed"] is False
    assert plan["safety"]["autotrade_trigger_allowed"] is False
    assert plan["safety"]["live_parameter_apply_allowed"] is False
    assert validate_parent_scenario_guidance_latest_read_model_artifact(plan["read_model"])["ok"] is True
    assert not (tmp_path / PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH).exists()

    public = preflight_parent_scenario_guidance_latest_read_model(
        tmp_path,
        family_scenario_parts=[_part()],
        generated_at="2026-07-10T00:00:00Z",
    )
    assert "read_model" not in public
    assert public["would_write"] is False
    assert not (tmp_path / PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH).exists()


def test_parent_scenario_guidance_writer_writes_only_read_model_artifact(tmp_path: Path) -> None:
    result = write_parent_scenario_guidance_latest_read_model(
        tmp_path,
        family_scenario_parts=[
            _part("market_regime", "current", "bullish", "primary_context", 65),
            _part("volatility_risk", "current", "risk_off", "risk_cap", 55),
        ],
        generated_at="2026-07-10T00:00:00Z",
        source_run_id="parent_guidance_writer_test",
    )

    assert result["ok"] is True
    assert result["would_write"] is True
    assert result["parent_scenario_guidance_read_model_json"] == PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH
    assert result["horizon_count"] == 1
    assert result["family_part_count"] == 2
    assert result["prediction_family_ids"] == ["market_regime", "volatility_risk"]
    assert result["safety"]["writes_parent_scenario_guidance_read_model_only"] is True
    assert result["safety"]["prediction_invoked"] is False
    assert result["safety"]["classifier_invoked"] is False
    assert result["safety"]["parameter_auto_promotion_allowed"] is False

    written = tmp_path / PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH
    assert written.exists()
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "parent_scenario_guidance_latest_read_model"
    assert payload["horizon_count"] == 1
    assert payload["family_part_count"] == 2
    assert validate_parent_scenario_guidance_latest_read_model_artifact(payload)["ok"] is True
    assert not (tmp_path / "prediction/market_regime/latest_read_model.json").exists()
    assert not (tmp_path / "prediction/market_regime/status.json").exists()
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()


def test_parent_scenario_guidance_writer_keeps_invalid_parts_as_rejected(tmp_path: Path) -> None:
    valid = _part("market_regime", "current", "bullish", "primary_context", 65)
    invalid = dict(valid)
    invalid["scenario_state"] = "moonshot"

    result = write_parent_scenario_guidance_latest_read_model(
        tmp_path,
        family_scenario_parts=[valid, invalid],
        generated_at="2026-07-10T00:00:00Z",
    )

    assert result["ok"] is True
    assert result["horizon_count"] == 1
    assert result["family_part_count"] == 1
    assert result["rejected_part_count"] == 1
    payload = json.loads((tmp_path / PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH).read_text(encoding="utf-8"))
    assert payload["rejected_part_count"] == 1
    assert "scenario_state_not_allowed" in payload["rejected_parts"][0]["failures"]


def test_parent_scenario_guidance_writer_source_has_no_runtime_or_inference_paths() -> None:
    text = (Path(__file__).resolve().parents[1] / "scenario_guidance_artifacts.py").read_text(encoding="utf-8")
    required = [
        "write_parent_scenario_guidance_latest_read_model",
        "preflight_parent_scenario_guidance_latest_read_model",
        "build_parent_scenario_guidance_artifact_write_plan",
        "writes_parent_scenario_guidance_read_model_only",
        "parameter_auto_promotion_allowed",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "append_market_regime_trace_row_once(",
        "append_market_regime_outcome_row_once(",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
