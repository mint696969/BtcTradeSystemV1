# path: ./tools/test_phase4a_prediction_system_ps_q19i_warroom_prediction_bilingual_explanation.py
# desc: Focused guard for PS-Q19I WarRoom prediction bilingual explanation layer.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_display_rows,
    latest_prediction_warroom_field_guide_rows,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION_2026-06-25.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"

REQUIRED_MARKERS = (
    "ps_q19i_warroom_prediction_bilingual_explanation=true",
    "warroom_prediction_display_ja_en_switch=true",
    "operator_visible_bilingual_explanation=true",
    "family_label_meaning_visible=true",
    "prediction_label_meaning_visible=true",
    "warning_meaning_visible=true",
    "driver_meaning_visible=true",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _fixture_read_model() -> dict:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "source_artifact_path": "D:/btc_ts_hot/prediction/latest_prediction_system_result.json",
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "generated_at": "2026-06-24T18:57:20Z",
        "age_sec": 60,
        "freshness_state": "fresh",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": 1,
        "selected_horizon_sec": [15],
        "selected_records_by_horizon": {
            "15": [
                {
                    "family": "market_regime",
                    "primary_label": "range_candidate",
                    "confidence": "medium",
                    "score": 0.49,
                    "usable": True,
                    "warnings": ["tier0_source_quality_gate_not_passed"],
                    "drivers": ["range_boundary_visible"],
                }
            ]
        },
        "market_snapshot": {"market_uid": "bitflyer.fx.FX_BTC_JPY", "freshness": "LIVE", "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
        "safety_flags": {"records_all_safe": True},
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_bilingual_explanation_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_ja_rows_include_operator_meanings() -> None:
    rows = latest_prediction_warroom_display_rows(_fixture_read_model(), lang="ja")
    assert rows
    row = rows[0]
    assert row["family_meaning"] == "地合い・レンジ/トレンド判定"
    assert row["label_meaning"] == "レンジ候補"
    assert row["confidence"] == "中"
    assert row["usable"] == "はい"
    assert "重要ソース品質ゲート未達" in row["warning_meaning"]
    assert "レンジ境界が見えている" in row["driver_meaning"]


def test_en_rows_remain_english_and_raw_tokens_visible() -> None:
    rows = latest_prediction_warroom_display_rows(_fixture_read_model(), lang="en")
    row = rows[0]
    assert row["family"] == "market_regime"
    assert row["label"] == "range_candidate"
    assert row["label_meaning"] == "range candidate"
    assert row["warnings"] == "tier0_source_quality_gate_not_passed"
    assert "source-quality gate" in row["warning_meaning"]


def test_packet_localizes_columns_and_preserves_safety() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fixture_read_model(), lang="ja")
    assert packet["ok"] is True
    assert packet["display_language"] == "ja"
    assert packet["freshness_label"] == "新鮮"
    assert packet["operator_visible_bilingual_explanation"] is True
    assert packet["ui_language_switch_consumed"] is True
    assert packet["prediction_rows_display"]
    assert "時間軸" in packet["prediction_rows_display"][0]
    assert "推論項目の意味" in packet["prediction_rows_display"][0]
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_field_guide_exists_in_both_languages() -> None:
    ja = latest_prediction_warroom_field_guide_rows(lang="ja")
    en = latest_prediction_warroom_field_guide_rows(lang="en")
    assert any("何秒先" in row["value"] for row in ja)
    assert any("Time horizon" in row["value"] for row in en)


def test_panel_declares_display_texts_and_ui_lang_usage() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "DISPLAY_TEXTS" in text
    assert "FAMILY_LABELS" in text
    assert "WARNING_LABELS" in text
    assert "DRIVER_LABELS" in text
    assert "st.session_state.get(\"ui_lang\"" in text
    assert "PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION" in text


if __name__ == "__main__":
    test_spec_declares_bilingual_explanation_and_safety_boundaries()
    test_ja_rows_include_operator_meanings()
    test_en_rows_remain_english_and_raw_tokens_visible()
    test_packet_localizes_columns_and_preserves_safety()
    test_field_guide_exists_in_both_languages()
    test_panel_declares_display_texts_and_ui_lang_usage()
    print('{"ok": true}')
