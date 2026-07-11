# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_explanation_adapter.py
# desc: Tests the MR-VS5 read-only MarketRegime explanation adapter before any Streamlit renderer connection.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import market_regime_explanation_adapter as adapter  # noqa: E402


def _write(root: Path, relative_path: str, payload: object) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_complete_fixture(root: Path) -> None:
    _write(
        root,
        adapter.LATEST_CARDS_RELATIVE_PATH,
        {
            "generated_at": "2026-07-11T02:36:47Z",
            "cards": [
                {
                    "horizon_key": "current",
                    "regime_code": "RANGE",
                    "regime_label": "レンジ",
                    "confidence_percent": 65,
                    "freshness_badge": "LIVE",
                    "short_tag_label": "方向感なし",
                    "detail": {"warning_lines": ["forecast_records_stale"]},
                }
            ],
            "safety": {"broker_private_api_allowed": False, "autotrade_trigger_allowed": False},
        },
    )
    _write(
        root,
        adapter.LATEST_READ_MODEL_RELATIVE_PATH,
        {
            "generated_at": "2026-07-11T02:36:47Z",
            "horizons": [
                {
                    "horizon_key": "current",
                    "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
                    "confidence_percent": 65,
                    "conflicts": ["forecast_records_stale", "forecast_records_age_sec:40165"],
                    "diagnostic_record": {
                        "available_signal_count": 34,
                        "display_confidence_replaced": False,
                        "label_selection_reason": "current_l4_candle_window_fallback",
                        "selected_evidence_quality_reason": "current_l4_fallback_uncalibrated_partial",
                        "selected_label_source": "current_l4_candle_window",
                        "selected_signal_strength_percent": None,
                        "shadow_confidence": {
                            "legacy_confidence_percent": 65,
                            "shadow_display_confidence_percent": 0,
                            "currentness_gate_blockers": [],
                            "safety": {"shadow_only": True},
                            "estimator": {
                                "applied_confidence_cap_percent": 99,
                                "blockers": [],
                                "source_rows": [
                                    {
                                        "source_id": "market_regime.source_quality",
                                        "aligned_with_prediction": True,
                                        "direction": "DOWN_TREND",
                                        "freshness_percent": 25,
                                        "quality_percent": 100,
                                        "signal_strength_percent": 25,
                                        "weight_percent": 30,
                                        "quality_score_percent": 25,
                                        "weighted_contribution": 7.5,
                                        "included_in_confidence": True,
                                    },
                                    {
                                        "source_id": "market_regime.price_structure",
                                        "aligned_with_prediction": False,
                                        "direction": "unknown",
                                        "freshness_percent": 100,
                                        "quality_percent": 100,
                                        "signal_strength_percent": 0,
                                        "weight_percent": 20,
                                        "weighted_contribution": 0.0,
                                        "included_in_confidence": True,
                                    },
                                ],
                                "safety": {"prediction_invoked": False, "classifier_invoked": False},
                            },
                        },
                    },
                }
            ],
        },
    )
    _write(
        root,
        adapter.CALIBRATION_READ_MODEL_RELATIVE_PATH,
        {
            "primary_observation_source": "candle_summary",
            "calibration_trust": {
                "current_primary_cohort_started_at": "2026-07-10T15:27:22Z",
                "current_primary_row_count": 56,
                "trusted_legacy_reference_row_count": 8818,
            },
            "primary": {
                "key": "candle_summary",
                "known_total": 8874,
                "calibration_score": 0.1178,
                "counts": {"hit": 664, "partial": 762, "miss": 7448, "unknown": 0, "invalidated": 0},
            },
            "primary_current": {
                "key": "primary_current",
                "known_total": 56,
                "calibration_score": 0.5536,
                "counts": {"hit": 6, "partial": 50, "miss": 0, "unknown": 0, "invalidated": 0},
            },
            "trusted_legacy_reference": {
                "key": "trusted_legacy_reference",
                "known_total": 8818,
                "calibration_score": 0.115,
                "counts": {"hit": 658, "partial": 712, "miss": 7448, "unknown": 0, "invalidated": 0},
            },
            "safety": {"raw_market_data_read": False, "would_send_to_broker": False},
        },
    )
    _write(
        root,
        adapter.SOURCE_SCORECARD_RELATIVE_PATH,
        {
            "minimum_trusted_sample_count": 20,
            "source_progress": [
                {
                    "source_id": "market_regime.source_quality",
                    "ready": True,
                    "trusted_sample_count": 56,
                    "minimum_trusted_sample_count": 20,
                    "remaining_trusted_samples": 0,
                },
                {
                    "source_id": "market_regime.price_structure",
                    "ready": False,
                    "trusted_sample_count": 0,
                    "minimum_trusted_sample_count": 20,
                    "remaining_trusted_samples": 20,
                },
            ],
            "source_scorecards": [
                {
                    "source_id": "market_regime.source_quality",
                    "reliability_percent": 55,
                    "calibration_score": 0.5536,
                    "supporting_count": 56,
                    "contradicting_count": 0,
                    "trusted_sample_count": 56,
                    "minimum_trusted_sample_count": 20,
                }
            ],
            "safety": {"parameter_auto_promotion_allowed": False, "live_parameter_apply_allowed": False},
        },
    )
    _write(
        root,
        adapter.PARAMETER_SET_COMPARISON_RELATIVE_PATH,
        {
            "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
            "comparison_ready": False,
            "comparison_blockers": ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"],
            "calibration_trust": {
                "trusted_parameter_set_count": 1,
                "comparable_parameter_set_count": 1,
            },
            "safety": {"parameter_auto_promotion_allowed": False, "live_parameter_apply_allowed": False},
        },
    )


def test_complete_adapter_packet_separates_display_shadow_and_source_semantics(tmp_path: Path) -> None:
    _write_complete_fixture(tmp_path)

    packet = adapter.build_market_regime_explanation_packet(tmp_path)

    assert packet["ok"] is True
    assert packet["horizon_count"] == 1
    horizon = packet["horizons"][0]
    assert horizon["card"]["display_confidence_percent"] == 65
    assert horizon["confidence"]["shadow_confidence_percent"] == 0
    assert horizon["confidence"]["shadow_only"] is True
    assert horizon["confidence"]["display_replaced"] is False
    assert horizon["confidence"]["explanation"].endswith("not win rate")
    assert horizon["warnings"] == ["forecast_records_stale", "forecast_records_age_sec:40165"]
    assert horizon["fallbacks"] == ["current_l4_candle_window_fallback"]

    sources = {row["source_id"]: row for row in horizon["sources"]}
    quality = sources["market_regime.source_quality"]
    assert quality["direction"] == "supporting"
    assert quality["configured_weight_percent"] == 30
    assert quality["current_quality_score_percent"] == 25
    assert quality["current_weighted_numerator"] == 7.5
    assert quality["historical_reliability_percent"] == 55
    assert quality["trusted_sample_count"] == 56
    assert quality["ready"] is True

    price_structure = sources["market_regime.price_structure"]
    assert price_structure["direction"] == "not_ready"
    assert price_structure["trusted_sample_count"] == 0
    assert price_structure["minimum_trusted_sample_count"] == 20
    assert price_structure["remaining_trusted_samples"] == 20
    assert price_structure["ready"] is False
    assert price_structure["not_ready_reason"] == "minimum_trusted_samples_not_met"

    assert horizon["calibration"]["available"] is True
    assert horizon["calibration"]["cohort"] == "primary_current"
    assert horizon["calibration"]["cohort_started_at"] == "2026-07-10T15:27:22Z"
    assert horizon["calibration"]["score"] == 0.5536
    assert horizon["calibration"]["sample_count"] == 56
    assert horizon["calibration"]["counts"] == {
        "hit": 6,
        "partial": 50,
        "miss": 0,
        "unknown": 0,
        "invalidated": 0,
    }
    assert horizon["calibration"]["interpretation"] == "not_win_rate"
    assert horizon["calibration"]["selection_reason"] == "primary_current_is_canonical_for_current_logic"
    assert horizon["calibration"]["fallback_used"] is False
    assert horizon["calibration"]["compatibility_reference"]["score"] == 0.1178
    assert horizon["calibration"]["compatibility_reference"]["sample_count"] == 8874
    assert horizon["calibration"]["trusted_legacy_reference"]["score"] == 0.115
    assert horizon["calibration"]["trusted_legacy_reference"]["sample_count"] == 8818
    assert horizon["parameter_set"]["comparison_ready"] is False
    assert horizon["parameter_set"]["trusted_parameter_set_count"] == 1
    assert horizon["parameter_set"]["best_parameter_set_claim_allowed"] is False
    assert horizon["parameter_set"]["auto_promotion_allowed"] is False
    assert packet["safety_violations"] == []


def test_missing_optional_artifacts_are_explicit_and_fail_closed_without_losing_cards(tmp_path: Path) -> None:
    _write_complete_fixture(tmp_path)
    (tmp_path / adapter.SOURCE_SCORECARD_RELATIVE_PATH).unlink()
    (tmp_path / adapter.CALIBRATION_READ_MODEL_RELATIVE_PATH).unlink()

    packet = adapter.build_market_regime_explanation_packet(tmp_path)

    assert packet["ok"] is True
    assert packet["artifact_status"]["source_scorecard"]["used"] is False
    assert packet["artifact_status"]["source_scorecard"]["error"] == "artifact_missing"
    assert packet["artifact_status"]["calibration"]["error"] == "artifact_missing"
    horizon = packet["horizons"][0]
    assert horizon["calibration"]["available"] is False
    assert horizon["calibration"]["cohort"] == "primary_current"
    assert horizon["calibration"]["fallback_used"] is False
    assert horizon["calibration"]["unavailable_reason"] == "primary_current_missing"
    price_structure = {row["source_id"]: row for row in horizon["sources"]}["market_regime.price_structure"]
    assert price_structure["ready"] is False
    assert price_structure["trusted_sample_count"] == 0


def test_required_read_model_missing_makes_packet_not_ok(tmp_path: Path) -> None:
    _write_complete_fixture(tmp_path)
    (tmp_path / adapter.LATEST_READ_MODEL_RELATIVE_PATH).unlink()

    packet = adapter.build_market_regime_explanation_packet(tmp_path)

    assert packet["ok"] is False
    assert packet["artifact_status"]["latest_read_model"]["error"] == "artifact_missing"
    assert packet["safety"]["prediction_invoked"] is False
    assert packet["safety"]["classifier_invoked"] is False
    assert packet["safety"]["writes_dhot"] is False


def test_malformed_and_oversized_artifacts_are_bounded(tmp_path: Path, monkeypatch) -> None:
    _write_complete_fixture(tmp_path)
    malformed = tmp_path / adapter.CALIBRATION_READ_MODEL_RELATIVE_PATH
    malformed.write_text("{broken", encoding="utf-8")
    monkeypatch.setitem(adapter.ARTIFACT_MAX_BYTES, adapter.SOURCE_SCORECARD_RELATIVE_PATH, 8)

    packet = adapter.build_market_regime_explanation_packet(tmp_path)

    assert packet["artifact_status"]["calibration"]["error"].startswith("artifact_json_invalid:")
    assert packet["artifact_status"]["source_scorecard"]["error"].startswith("artifact_too_large:")
    assert packet["horizons"][0]["calibration"]["available"] is False


def test_true_execution_safety_flag_is_surfaced_and_packet_rejected(tmp_path: Path) -> None:
    _write_complete_fixture(tmp_path)
    cards_path = tmp_path / adapter.LATEST_CARDS_RELATIVE_PATH
    payload = json.loads(cards_path.read_text(encoding="utf-8"))
    payload["safety"]["broker_private_api_allowed"] = True
    cards_path.write_text(json.dumps(payload), encoding="utf-8")

    packet = adapter.build_market_regime_explanation_packet(tmp_path)

    assert packet["ok"] is False
    assert any("broker_private_api_allowed" in item for item in packet["safety_violations"])
    assert packet["safety"]["broker_private_api_allowed"] is False
    assert packet["safety"]["would_send_to_broker"] is False


def test_adapter_source_has_no_inference_write_subprocess_or_broker_path() -> None:
    text = Path(adapter.__file__).read_text(encoding="utf-8")
    required = [
        "build_market_regime_explanation_packet",
        "SOURCE_SCORECARD_RELATIVE_PATH",
        "shadow_confidence_percent",
        "historical_reliability_percent",
        "confidence_recalculated",
        "not_win_rate",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "write_market_regime_latest_artifacts_once",
        "write_market_regime_source_scorecard",
        "subprocess.Popen",
        "requests.post",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
