# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_parameter_set_comparison_read_model.py
# desc: PS_PARAMETER_SET_COMPARISON_READ_MODEL_V1 tests. Verifies trusted candle_summary parameter-set comparison without auto-promotion, D-hot writes, broker, AutoTrade, or UI inference.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.parameter_set_comparison_read_model import (  # noqa: E402
    TRUSTED_OBSERVATION_SOURCE,
    build_market_regime_parameter_set_comparison_read_model_from_calibration_summary,
    build_market_regime_parameter_set_comparison_read_model_from_outcome_rows,
    validate_market_regime_parameter_set_comparison_read_model,
)


def _row(parameter_set_id: str, label: str, *, source: str = "candle_summary", horizon_key: str = "300s", confidence: int = 70, predicted: str = "RANGE", observed: str = "RANGE") -> dict[str, object]:
    return {
        "outcome_id": f"run:{horizon_key}:{parameter_set_id}:{label}",
        "run_id": "run",
        "generated_at": "2026-07-08T12:00:00Z",
        "resolved_at": "2026-07-08T12:05:00Z",
        "horizon_key": horizon_key,
        "horizon_sec": 300,
        "predicted_regime_code": predicted,
        "observed_regime_code": observed,
        "outcome_label": label,
        "observation_source": source,
        "confidence_percent": confidence,
        "parameter_set_id": parameter_set_id,
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
    }


def test_ps_parameter_set_comparison_audits_legacy_outcome_id_without_grouping_by_it() -> None:
    rows = [
        _row("active.v1", "hit"),
        {**_row("shadow.v2", "hit"), "outcome_id": "run:300s:outcome"},
    ]

    read_model = build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
        rows=rows,
        active_parameter_set_id="active.v1",
        min_trusted_samples=1,
    )

    audit = read_model["outcome_identity_audit"]
    assert audit["identity_source"] == "parameter_set_id_field"
    assert audit["outcome_id_used_for_grouping"] is False
    assert audit["parameter_set_id_field_required"] is True
    assert audit["legacy_outcome_id_without_parameter_set_count"] == 1
    assert audit["legacy_outcome_id_without_parameter_set_present"] is True
    assert read_model["calibration_trust"]["outcome_identity_audit"] == audit
    assert read_model["comparison_ready"] is True
    assert validate_market_regime_parameter_set_comparison_read_model(read_model)["ok"] is True


def test_ps_parameter_set_comparison_uses_trusted_candle_summary_rows_only() -> None:
    rows = [
        _row("active.v1", "hit", confidence=72),
        _row("active.v1", "miss", confidence=72, observed="HIGH_VOL_CHOP"),
        _row("shadow.v2", "hit", confidence=72),
        _row("shadow.v2", "partial", confidence=68, observed="LOW_VOL_COMPRESSION"),
        _row("active.v1", "hit", source="latest_cards_current", confidence=99),
        _row("shadow.v2", "miss", source="latest_cards_current", confidence=99, observed="DOWN_TREND"),
    ]

    read_model = build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
        rows=rows,
        active_parameter_set_id="active.v1",
        min_trusted_samples=2,
    )

    assert read_model["artifact_kind"] == "parameter_set_comparison_read_model"
    assert read_model["comparison_ready"] is True
    assert read_model["comparison_scope"] == "trusted_candle_summary_outcomes_only"
    assert read_model["calibration_trust"]["trusted_observation_source"] == TRUSTED_OBSERVATION_SOURCE
    assert read_model["calibration_trust"]["trusted_row_count"] == 4
    assert read_model["calibration_trust"]["reference_only_row_count"] == 2
    assert read_model["calibration_trust"]["latest_cards_current_is_reference_only"] is True
    assert read_model["outcome_identity_audit"]["identity_source"] == "parameter_set_id_field"
    assert read_model["outcome_identity_audit"]["outcome_id_used_for_grouping"] is False
    assert read_model["promotion_candidates"] == []

    by_id = {item["parameter_set_id"]: item for item in read_model["parameter_sets"]}
    assert by_id["active.v1"]["known_total"] == 2
    assert by_id["active.v1"]["calibration_score"] == 0.5
    assert by_id["shadow.v2"]["known_total"] == 2
    assert by_id["shadow.v2"]["calibration_score"] == 0.75
    assert all(item["auto_apply_allowed"] is False and item["human_gate_required"] is True for item in read_model["recommendations"])

    validation = validate_market_regime_parameter_set_comparison_read_model(read_model)
    assert validation["ok"] is True


def test_ps_parameter_set_comparison_reports_insufficient_sample_without_autopromotion() -> None:
    read_model = build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
        rows=[_row("active.v1", "hit")],
        active_parameter_set_id="active.v1",
        min_trusted_samples=2,
    )

    assert read_model["comparison_ready"] is False
    assert read_model["comparison_blockers"] == ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"]
    assert read_model["parameter_sets"][0]["insufficient_sample"] is True
    assert read_model["recommendations"][0]["recommendation"] == "insufficient_sample"
    assert read_model["safety"]["parameter_auto_promotion_allowed"] is False
    assert read_model["safety"]["live_parameter_apply_allowed"] is False
    assert read_model["safety"]["writes_dhot"] is False


def test_ps_parameter_set_comparison_summary_input_is_conservative_until_trusted_dimension_exists() -> None:
    daily_summary = {
        "date": "2026-07-08",
        "calibration_trust": {
            "trusted_observation_source": "candle_summary",
            "reference_only_observation_source": "latest_cards_current",
            "latest_cards_current_is_reference_only": True,
            "trusted_row_count": 568,
            "reference_only_row_count": 804,
            "trusted_parameter_set_count": 1,
        },
    }
    table = {"month": "2026-07", "rows": [{"key": "active.v1|300s", "known_total": 568, "calibration_score": 0.66}]}

    read_model = build_market_regime_parameter_set_comparison_read_model_from_calibration_summary(
        daily_summary=daily_summary,
        calibration_table=table,
    )

    assert read_model["comparison_ready"] is False
    assert read_model["comparison_scope"] == "calibration_summary_aggregate_safety_view"
    assert read_model["comparison_blockers"] == ["parameter_set_by_observation_source_rows_not_available_in_summary"]
    assert read_model["calibration_trust"]["comparison_blockers"] == ["aggregate_summary_cannot_filter_parameter_sets_to_trusted_source"]
    assert read_model["outcome_identity_audit"]["identity_source"] == "parameter_set_id_field"
    assert read_model["outcome_identity_audit"]["outcome_id_used_for_grouping"] is False
    assert read_model["promotion_candidates"] == []
    assert validate_market_regime_parameter_set_comparison_read_model(read_model)["ok"] is True


def test_ps_parameter_set_comparison_source_has_no_execution_or_raw_payload_tokens() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/parameter_set_comparison_read_model.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "build_market_regime_parameter_set_comparison_read_model_from_outcome_rows",
        "trusted_candle_summary_outcomes_only",
        "latest_cards_current_is_reference_only",
        "recommendation_shape_only",
        "human_gate_required_for_parameter_change",
        "outcome_identity_audit",
        "parameter_set_id_field",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_text(",
        "open(\"a",
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
