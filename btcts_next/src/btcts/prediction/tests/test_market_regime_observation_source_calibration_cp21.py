# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_observation_source_calibration_cp21.py
# desc: CP21 tests for preserving observation_source identity in outcomes and calibration summaries. No raw market payload duplication, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_summary import build_market_regime_calibration_summary, build_market_regime_calibration_table  # noqa: E402
from btcts.prediction.market_regime.observation_evaluator import MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION  # noqa: E402
from btcts.prediction.market_regime.outcome_resolver import build_market_regime_outcome_row, validate_market_regime_outcome_row  # noqa: E402
from btcts.prediction.market_regime.tools.resolve_outcomes import _observation_from_current_card  # noqa: E402


def _prediction(run_id: str = "run", horizon_key: str = "300s", regime: str = "RANGE") -> dict:
    return {
        "run_id": run_id,
        "prediction_id": f"{run_id}:{horizon_key}",
        "generated_at": "2026-07-08T12:00:00Z",
        "horizon": "5分後",
        "horizon_sec": 300,
        "horizon_key": horizon_key,
        "regime_code": regime,
        "confidence_percent": 70,
        "parameter_set_id": "ps.v1",
        "detail": {"trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"},
    }


def test_cp21_latest_cards_observation_source_is_preserved_in_outcome_row() -> None:
    observation = _observation_from_current_card(
        payload={"run_id": "latest_run"},
        current_card={"horizon": "現在", "horizon_key": "current", "regime_code": "RANGE", "detail": {"trace_part_jsonl": "trace.jsonl"}},
        resolved_at="2026-07-08T12:05:00Z",
    )
    assert observation["observation_source"] == "latest_cards_current"
    row = build_market_regime_outcome_row(prediction=_prediction(), observation=observation, resolved_at="2026-07-08T12:05:00Z")
    assert row["observation_source"] == "latest_cards_current"
    assert row["observation_summary"]["observation_source"] == "latest_cards_current"
    assert row["observation_evaluator_version"] == ""
    assert validate_market_regime_outcome_row(row)["ok"] is True


def test_cp21_candle_observation_source_and_evaluator_version_are_preserved() -> None:
    observation = {
        "observation_at": "2026-07-08T12:05:00Z",
        "observation_available": True,
        "observed_regime_code": "UP_TREND",
        "observation_source": "candle_summary",
        "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        "source_refs": ["data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/closed.jsonl"],
        "summary": "candle_summary_observation",
    }
    row = build_market_regime_outcome_row(prediction=_prediction(regime="RANGE"), observation=observation, resolved_at="2026-07-08T12:05:00Z")
    assert row["observation_source"] == "candle_summary"
    assert row["observation_evaluator_version"] == MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION
    assert row["observation_summary"]["observation_source"] == "candle_summary"
    assert row["outcome_label"] == "miss"
    assert validate_market_regime_outcome_row(row)["ok"] is True






def test_cp21_single_trusted_parameter_set_does_not_create_promotion_candidate() -> None:
    trusted_rows = []
    for index in range(20):
        row = build_market_regime_outcome_row(
            prediction=_prediction(run_id=f"trusted_hit_{index}", regime="RANGE"),
            observation={
                "observation_at": "2026-07-08T12:05:00Z",
                "observed_regime_code": "RANGE",
                "observation_source": "candle_summary",
                "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
            },
            resolved_at="2026-07-08T12:05:00Z",
        )
        trusted_rows.append(row)

    summary = build_market_regime_calibration_summary(rows=trusted_rows, date="2026-07-08")

    assert summary["trusted_observation_overall"]["known_total"] == 20
    assert summary["trusted_observation_overall"]["calibration_score"] == 1.0
    assert summary["calibration_trust"]["promotion_candidates_require_parameter_set_comparison"] is True
    assert summary["calibration_trust"]["trusted_parameter_set_count"] == 1
    assert summary["calibration_trust"]["current_primary_parameter_set_count"] == 0
    assert summary["promotion_candidates"] == []

def test_cp21_promotion_candidates_ignore_latest_cards_current_reference_rows() -> None:
    reference_rows = []
    for index in range(20):
        row = dict(_prediction(run_id=f"reference_{index}", regime="RANGE"))
        row.update(
            {
                "outcome_id": f"reference_{index}:300s:outcome",
                "resolved_at": "2026-07-08T12:05:00Z",
                "predicted_regime_code": "RANGE",
                "observed_regime_code": "RANGE",
                "outcome_label": "hit",
                "observation_source": "latest_cards_current",
            }
        )
        reference_rows.append(row)
    trusted_miss = build_market_regime_outcome_row(
        prediction=_prediction(run_id="trusted_miss", regime="RANGE"),
        observation={
            "observation_at": "2026-07-08T12:05:00Z",
            "observed_regime_code": "UP_TREND",
            "observation_source": "candle_summary",
            "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        },
        resolved_at="2026-07-08T12:05:00Z",
    )

    summary = build_market_regime_calibration_summary(rows=[*reference_rows, trusted_miss], date="2026-07-08")

    assert summary["overall"]["calibration_score"] > 0.9
    assert summary["primary_observation_source"] == "candle_summary"
    assert summary["primary_observation_overall"]["counts"]["miss"] == 1
    assert summary["trusted_observation_overall"]["key"] == "candle_summary"
    assert summary["calibration_trust"]["latest_cards_current_is_reference_only"] is True
    assert summary["calibration_trust"]["promotion_candidates_use_observation_source"] == "candle_summary"
    assert summary["promotion_candidates"] == []

def test_cp21_calibration_groups_by_observation_source_and_defaults_legacy_rows() -> None:
    legacy = {
        "outcome_id": "legacy:300s:outcome",
        "run_id": "legacy",
        "generated_at": "2026-07-08T12:00:00Z",
        "resolved_at": "2026-07-08T12:05:00Z",
        "horizon_key": "300s",
        "horizon_sec": 300,
        "predicted_regime_code": "RANGE",
        "observed_regime_code": "RANGE",
        "outcome_label": "hit",
        "confidence_percent": 60,
        "parameter_set_id": "ps.v1",
    }
    candle = build_market_regime_outcome_row(
        prediction=_prediction(run_id="candle", regime="RANGE"),
        observation={
            "observation_at": "2026-07-08T12:05:00Z",
            "observed_regime_code": "UP_TREND",
            "observation_source": "candle_summary",
            "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        },
        resolved_at="2026-07-08T12:05:00Z",
    )
    summary = build_market_regime_calibration_summary(rows=[legacy, candle], date="2026-07-08")
    by_source = {row["key"]: row for row in summary["by_observation_source"]}
    assert by_source["latest_cards_current"]["counts"]["hit"] == 1
    assert by_source["candle_summary"]["counts"]["miss"] == 1
    by_source_horizon = {row["key"]: row for row in summary["by_observation_source_horizon"]}
    assert by_source_horizon["latest_cards_current|300s"]["total"] == 1
    assert by_source_horizon["candle_summary|300s"]["total"] == 1
    table = build_market_regime_calibration_table(daily_summaries=[summary], month="2026-07")
    assert table["observation_source_row_count"] == 2
    assert {row["key"] for row in table["observation_source_rows"]} == {"latest_cards_current|300s", "candle_summary|300s"}
    assert summary["safety"]["parameter_auto_promotion_allowed"] is False
    assert "raw_candles" not in json.dumps(summary, ensure_ascii=False)


def test_cp21_calibration_separates_current_and_legacy_trusted_cohorts() -> None:
    legacy = build_market_regime_outcome_row(
        prediction=_prediction(run_id="legacy_current_split", regime="RANGE"),
        observation={
            "observation_at": "2026-07-08T12:05:00Z",
            "observed_regime_code": "UP_TREND",
            "observation_source": "candle_summary",
            "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        },
        resolved_at="2026-07-08T12:05:00Z",
    )
    current_prediction = _prediction(run_id="current_current_split", regime="RANGE")
    current_prediction["generated_at"] = "2026-07-10T15:27:22Z"
    current = build_market_regime_outcome_row(
        prediction=current_prediction,
        observation={
            "observation_at": "2026-07-10T15:32:22Z",
            "observed_regime_code": "RANGE",
            "observation_source": "candle_summary",
            "observation_evaluator_version": MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
        },
        resolved_at="2026-07-10T15:32:22Z",
    )
    reference = dict(_prediction(run_id="compat_reference", regime="RANGE"))
    reference.update({
        "outcome_id": "compat_reference:300s:outcome",
        "resolved_at": "2026-07-08T12:05:00Z",
        "predicted_regime_code": "RANGE",
        "observed_regime_code": "RANGE",
        "outcome_label": "hit",
        "observation_source": "latest_cards_current",
    })

    summary = build_market_regime_calibration_summary(rows=[legacy, current, reference], date="2026-07-10")

    assert summary["primary_current"]["total"] == 1
    assert summary["primary_current"]["counts"]["hit"] == 1
    assert summary["trusted_legacy_reference"]["total"] == 1
    assert summary["trusted_legacy_reference"]["counts"]["miss"] == 1
    assert summary["compatibility_reference"]["total"] == 1
    assert summary["compatibility_overall"]["total"] == 3
    assert summary["calibration_trust"]["trusted_parameter_set_count"] == 1
    assert summary["calibration_trust"]["current_primary_parameter_set_count"] == 1
    assert summary["calibration_trust"]["current_primary_row_count"] == 1
    assert summary["calibration_trust"]["trusted_legacy_reference_row_count"] == 1
    assert summary["calibration_trust"]["compatibility_reference_row_count"] == 1
    assert summary["calibration_trust"]["promotion_candidates_use_current_primary_cohort_only"] is True
