# path: ./tools/test_phase4a_prediction_system_ps_q19j_warroom_prediction_text_catalog_split.py
# desc: Focused guard for PS-Q19J WarRoom prediction text catalog split.

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
)
from btcts.apps.operator_ui.prediction_warroom.texts.latest_prediction_display_texts import (  # noqa: E402
    DISPLAY_TEXTS,
    DRIVER_LABELS,
    FAMILY_LABELS,
    VALUE_LABELS,
    WARNING_LABELS,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19J_WARROOM_PREDICTION_TEXT_CATALOG_SPLIT_2026-06-25.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
TEXT_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py"
GLOBAL_UI_TEXT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/ui_text.py"
COMMON_TEXTS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/texts/common.py"

REQUIRED_MARKERS = (
    "ps_q19j_warroom_prediction_text_catalog_split=true",
    "prediction_warroom_text_catalog_directory_added=true",
    "latest_prediction_display_text_catalog_added=true",
    "panel_imports_split_text_catalog=true",
    "global_ui_text_not_expanded=true",
    "common_texts_not_expanded=true",
    "bilingual_behavior_preserved=true",
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
        "market_snapshot": {"market_uid": "bitflyer.fx.FX_BTC_JPY", "freshness": "LIVE"},
        "safety_flags": {"records_all_safe": True},
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_split_catalog_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_catalog_module_contains_bilingual_prediction_texts() -> None:
    assert DISPLAY_TEXTS["ja"]["reading_title"] == "この推論エリアの読み方"
    assert DISPLAY_TEXTS["en"]["reading_title"] == "How to read this prediction area"
    assert FAMILY_LABELS["ja"]["market_regime"] == "地合い・レンジ/トレンド判定"
    assert VALUE_LABELS["ja"]["range_candidate"] == "レンジ候補"
    assert "重要ソース品質" in WARNING_LABELS["ja"]["tier0_source_quality_gate_not_passed"]
    assert DRIVER_LABELS["ja"]["range_boundary_visible"] == "レンジ境界が見えている"


def test_panel_imports_catalog_and_does_not_define_large_catalogs_inline() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "prediction_warroom.texts.latest_prediction_display_texts import" in text
    assert "DISPLAY_TEXTS = {" not in text
    assert "FAMILY_LABELS = {" not in text
    assert "WARNING_LABELS = {" not in text
    assert "DRIVER_LABELS = {" not in text


def test_global_language_files_not_used_for_prediction_catalog() -> None:
    assert "PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION" not in GLOBAL_UI_TEXT.read_text(encoding="utf-8")
    assert "PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION" not in COMMON_TEXTS.read_text(encoding="utf-8")
    assert "PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION" in TEXT_MODULE.read_text(encoding="utf-8")


def test_bilingual_behavior_is_preserved_after_split() -> None:
    rows = latest_prediction_warroom_display_rows(_fixture_read_model(), lang="ja")
    assert rows[0]["family_meaning"] == "地合い・レンジ/トレンド判定"
    assert rows[0]["label_meaning"] == "レンジ候補"
    packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fixture_read_model(), lang="ja")
    assert packet["ok"] is True
    assert packet["display_language"] == "ja"
    assert packet["operator_visible_bilingual_explanation"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_catalog_module_is_text_only_no_streamlit_or_runtime_io() -> None:
    text = TEXT_MODULE.read_text(encoding="utf-8")
    assert "import streamlit" not in text
    assert "write_text" not in text
    assert "open(" not in text
    assert "build_prediction" not in text
    assert "broker" in text  # only safety comments/doc text are allowed


if __name__ == "__main__":
    test_spec_declares_split_catalog_and_safety_boundaries()
    test_catalog_module_contains_bilingual_prediction_texts()
    test_panel_imports_catalog_and_does_not_define_large_catalogs_inline()
    test_global_language_files_not_used_for_prediction_catalog()
    test_bilingual_behavior_is_preserved_after_split()
    test_catalog_module_is_text_only_no_streamlit_or_runtime_io()
    print('{"ok": true}')
