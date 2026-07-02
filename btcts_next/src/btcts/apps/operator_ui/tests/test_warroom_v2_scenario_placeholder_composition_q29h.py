# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_scenario_placeholder_composition_q29h.py
# desc: PS-Q29H guards for WarRoom v2 Japanese scenario placeholder composition.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.scenario_area import (  # noqa: E402
    WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION,
    build_warroom_v2_scenario_area_renderer_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_SCENARIO_PLACEHOLDER_VERSION,
    build_warroom_v2_placeholder_read_models_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
SCENARIO = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/scenario_placeholder.py"
SCENARIO_AREA = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/scenario_area.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29H_WARROOM_V2_SCENARIO_PLACEHOLDER_COMPOSITION_2026-07-02.md"

EXPECTED_HORIZONS = ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]


def _scenario_model() -> dict:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T06:40:00Z")
    for model in packet["read_models"]:
        if model["payload"].get("zone") == "scenario":
            return model
    raise AssertionError("scenario model not found")


def test_q29h_scenario_payload_composes_from_matrix_axes() -> None:
    payload = _scenario_model()["payload"]
    assert payload["scenario_placeholder_version"] == WARROOM_V2_SCENARIO_PLACEHOLDER_VERSION
    assert payload["scenario_area_below_cards"] is True
    assert payload["scenario_source"] == "placeholder_matrix_contract"
    assert payload["row_axis"] == "prediction_item"
    assert payload["column_axis"] == "horizon"
    assert payload["horizon_labels"] == EXPECTED_HORIZONS
    assert payload["matrix_column_count"] == 8
    assert payload["matrix_row_count"] >= 8
    assert "地合い" in payload["prediction_item_titles"]
    assert "方向感" in payload["prediction_item_titles"]
    assert payload["scenario_lines"]
    assert payload["watch_points"]
    assert payload["invalidation_lines"]
    assert payload["runtime_connected"] is False
    assert payload["push_connected"] is False


def test_q29h_scenario_area_renderer_packet_is_display_only() -> None:
    packet = build_warroom_v2_scenario_area_renderer_packet([_scenario_model()])
    assert packet["renderer_version"] == WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION
    assert packet["scenario_area_below_cards"] is True
    assert packet["display_only"] is True
    assert packet["placeholder_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["would_send_to_broker"] is False


def test_q29h_scenario_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in (SCENARIO, SCENARIO_AREA):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 90
        for token in forbidden:
            assert token not in text


def test_q29h_no_route_or_legacy_warroom_change() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in app_text
    assert "scenario_placeholder" not in legacy_text
    assert "prediction_warroom.v2" not in legacy_text


def test_q29h_doc_records_scenario_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "scenario_source=placeholder_matrix_contract" in text
    assert "scenario_area_below_cards=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_invoking_classifier=true" in text
    assert "not_changing_legacy_warroom=true" in text
