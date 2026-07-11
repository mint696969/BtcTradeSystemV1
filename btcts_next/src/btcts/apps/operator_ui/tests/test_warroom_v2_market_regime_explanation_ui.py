# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_explanation_ui.py
# desc: MR-VS5 connected UI tests for read-only MarketRegime explanation rendering.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view as view  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import market_regime_explanation_adapter as adapter  # noqa: E402


class FakeExpander:
    def __enter__(self) -> "FakeExpander":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.tables: list[list[dict[str, object]]] = []
        self.expanders: list[str] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def expander(self, label: object, **_kwargs: object) -> FakeExpander:
        self.expanders.append(str(label))
        return FakeExpander()

    def dataframe(self, rows: list[dict[str, object]], **_kwargs: object) -> None:
        self.tables.append(rows)


def _write(root: Path, relative: str, payload: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fixture(root: Path) -> None:
    _write(root, adapter.LATEST_CARDS_RELATIVE_PATH, {
        "generated_at": "2026-07-11T03:00:00Z",
        "cards": [{"horizon_key": "current", "regime_code": "RANGE", "regime_label": "レンジ", "confidence_percent": 65, "freshness_badge": "LIVE", "short_tag_label": "方向感なし", "detail": {"warning_lines": ["forecast_records_stale"]}}],
    })
    _write(root, adapter.LATEST_READ_MODEL_RELATIVE_PATH, {
        "generated_at": "2026-07-11T03:00:00Z",
        "horizons": [{
            "horizon_key": "current",
            "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
            "diagnostic_record": {
                "display_confidence_replaced": False,
                "available_signal_count": 12,
                "selected_evidence_quality_reason": "partial",
                "selected_label_source": "current_l4_candle_window",
                "label_selection_reason": "current_l4_candle_window_fallback",
                "shadow_confidence": {
                    "legacy_confidence_percent": 65,
                    "shadow_display_confidence_percent": 1,
                    "safety": {"shadow_only": True},
                    "estimator": {"applied_confidence_cap_percent": 99, "blockers": [], "source_rows": [
                        {"source_id": "market_regime.source_quality", "aligned_with_prediction": True, "direction": "DOWN_TREND", "freshness_percent": 25, "quality_percent": 100, "quality_score_percent": 25, "signal_strength_percent": 25, "weight_percent": 30, "weighted_contribution": 7.5, "included_in_confidence": True},
                        {"source_id": "market_regime.price_structure", "aligned_with_prediction": False, "direction": "unknown", "freshness_percent": 100, "quality_percent": 100, "signal_strength_percent": 0, "weight_percent": 20, "weighted_contribution": 0.0, "included_in_confidence": True},
                    ]},
                },
            },
        }],
    })
    _write(root, adapter.CALIBRATION_READ_MODEL_RELATIVE_PATH, {
        "primary_observation_source": "candle_summary",
        "calibration_trust": {"current_primary_cohort_started_at": "2026-07-10T15:27:22Z"},
        "primary": {"key": "candle_summary", "known_total": 8874, "calibration_score": 0.1178, "counts": {"hit": 664, "partial": 762, "miss": 7448}},
        "primary_current": {"key": "primary_current", "known_total": 56, "calibration_score": 0.5536, "counts": {"hit": 6, "partial": 50, "miss": 0}},
        "trusted_legacy_reference": {"key": "trusted_legacy_reference", "known_total": 8818, "calibration_score": 0.115, "counts": {"hit": 658, "partial": 712, "miss": 7448}},
    })
    _write(root, adapter.SOURCE_SCORECARD_RELATIVE_PATH, {
        "minimum_trusted_sample_count": 20,
        "source_progress": [
            {"source_id": "market_regime.source_quality", "ready": True, "trusted_sample_count": 56, "minimum_trusted_sample_count": 20, "remaining_trusted_samples": 0},
            {"source_id": "market_regime.price_structure", "ready": False, "trusted_sample_count": 0, "minimum_trusted_sample_count": 20, "remaining_trusted_samples": 20},
        ],
        "source_scorecards": [{"source_id": "market_regime.source_quality", "reliability_percent": 55, "trusted_sample_count": 56, "minimum_trusted_sample_count": 20}],
    })
    _write(root, adapter.PARAMETER_SET_COMPARISON_RELATIVE_PATH, {
        "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
        "comparison_ready": False,
        "comparison_blockers": ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"],
        "calibration_trust": {"trusted_parameter_set_count": 1, "comparable_parameter_set_count": 1},
        "promotion_candidates": [],
        "recommendations": [],
    })


def test_connected_explanation_ui_uses_current_cohort_and_keeps_shadow_separate(monkeypatch, tmp_path: Path) -> None:
    _fixture(tmp_path)
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": True, "artifact_path": str(tmp_path / adapter.LATEST_CARDS_RELATIVE_PATH), "artifact_read_error": ""})
    fake = FakeStreamlit()

    result = view.render_rt_prediction_cards({"generated_at": "2026-07-11T03:00:00Z", "cards": []}, fake)

    assert result["market_regime_explanation_packet_ok"] is True
    assert result["market_regime_explanation_horizon_count"] == 1
    assert result["market_regime_explanation_safety_violations"] == []
    assert result["market_regime_explanation_prediction_invoked"] is False
    assert result["market_regime_explanation_classifier_invoked"] is False
    assert result["market_regime_explanation_confidence_recalculated"] is False
    assert result["market_regime_calibration_primary_observation_source"] == "primary_current"
    assert result["market_regime_calibration_primary_score"] == 0.5536
    assert result["market_regime_calibration_primary_known_total"] == 56
    assert any("current sample=56" in caption and "not win rate" in caption for caption in fake.captions)
    assert "地合い詳細" in fake.expanders
    assert not any("entry_gate=" in caption or "prediction_invoked=" in caption for caption in fake.captions)
    overview = next(table for table in fake.tables if table and "表示confidence" in table[0])
    assert overview[0]["表示confidence"] == "65%"
    assert overview[0]["shadow"] == "1%"
    sources = next(table for table in fake.tables if table and "source" in table[0])
    price = next(row for row in sources if row["source"] == "market_regime.price_structure")
    assert price["trusted"] == 0
    assert price["minimum"] == 20
    assert price["remaining"] == 20
    assert price["ready"] is False
    quality = next(row for row in sources if row["source"] == "market_regime.source_quality")
    assert quality["quality score"] == "25%"
    assert quality["weighted numerator"] == "7.5"


def test_connected_explanation_ui_fails_closed_when_required_read_model_missing(monkeypatch, tmp_path: Path) -> None:
    _fixture(tmp_path)
    (tmp_path / adapter.LATEST_READ_MODEL_RELATIVE_PATH).unlink()
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": True, "artifact_path": "", "artifact_read_error": ""})
    fake = FakeStreamlit()

    result = view.render_rt_prediction_cards({"cards": []}, fake)

    assert result["market_regime_explanation_packet_ok"] is False
    assert result["market_regime_explanation_prediction_invoked"] is False
    assert result["market_regime_explanation_classifier_invoked"] is False
    assert any("unavailable" in caption and "latest_read_model:artifact_missing" in caption for caption in fake.captions)
    assert "地合い詳細" in fake.expanders


def test_legacy_calibration_schema_remains_compatible_without_current_schema_marker(monkeypatch, tmp_path: Path) -> None:
    _fixture(tmp_path)
    calibration_path = tmp_path / adapter.CALIBRATION_READ_MODEL_RELATIVE_PATH
    payload = json.loads(calibration_path.read_text(encoding="utf-8"))
    payload.pop("primary_current")
    payload.pop("trusted_legacy_reference")
    payload.pop("calibration_trust")
    calibration_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))

    calibration_packet = view._read_market_regime_calibration_read_model_artifact()

    assert calibration_packet["artifact_present"] is True
    assert calibration_packet["artifact_used"] is True
    assert calibration_packet["artifact_read_error"] == ""
    assert calibration_packet["primary_observation_source"] == "candle_summary"
    assert calibration_packet["primary_score"] == 0.1178
    assert calibration_packet["primary_known_total"] == 8874
    assert calibration_packet["schema_mode"] == "legacy_compatibility"


def test_top_calibration_reader_does_not_fallback_to_compatibility_primary(monkeypatch, tmp_path: Path) -> None:
    _fixture(tmp_path)
    calibration_path = tmp_path / adapter.CALIBRATION_READ_MODEL_RELATIVE_PATH
    payload = json.loads(calibration_path.read_text(encoding="utf-8"))
    payload.pop("primary_current")
    calibration_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", lambda **kwargs: {"cards": kwargs.get("cards") or [], "card_count": len(kwargs.get("cards") or []), "artifact_cards_used": True, "artifact_path": "", "artifact_read_error": ""})
    fake = FakeStreamlit()

    calibration_packet = view._read_market_regime_calibration_read_model_artifact()
    result = view.render_rt_prediction_cards({"cards": []}, fake)

    assert calibration_packet["artifact_present"] is True
    assert calibration_packet["artifact_used"] is False
    assert calibration_packet["artifact_read_error"] == "calibration_read_model_has_no_primary_current"
    assert calibration_packet["primary_observation_source"] == ""
    assert calibration_packet["primary_score"] is None
    assert calibration_packet["primary_known_total"] == 0

    assert result["market_regime_calibration_read_model_used"] is False
    assert result["market_regime_calibration_primary_observation_source"] == ""
    assert result["market_regime_calibration_primary_score"] is None
    assert result["market_regime_calibration_primary_known_total"] == 0
    assert result["market_regime_explanation_packet_ok"] is True
    assert any("calibration_read_model_has_no_primary_current" in caption for caption in fake.captions)
    assert not any("score=0.1178" in caption or "known=8874" in caption for caption in fake.captions)


def test_prediction_cards_view_has_no_explanation_inference_or_write_path() -> None:
    text = Path(view.__file__).read_text(encoding="utf-8")
    required = ["build_market_regime_explanation_packet", "_render_market_regime_explanation", "not win rate", "market_regime_explanation_packet_ok"]
    forbidden = ["classify_market_regime_feature_bundle(", "build_market_regime_source_snapshot(", "write_market_regime_latest_artifacts_once", "subprocess.Popen", "requests.post"]
    assert [token for token in required if token not in text] == []
    assert [token for token in forbidden if token in text] == []
