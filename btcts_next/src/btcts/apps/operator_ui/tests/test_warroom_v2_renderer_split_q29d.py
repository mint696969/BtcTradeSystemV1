# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_renderer_split_q29d.py
# desc: PS-Q29D guards for WarRoom v2 renderer responsibility split. Display-only; no runtime or push ownership.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (  # noqa: E402
    WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION,
    WARROOM_V2_MODEL_VIEWS_VERSION,
    WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION,
    WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION,
    WARROOM_V2_TOP_BAR_RENDERER_VERSION,
    warroom_v2_models_by_zone,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import (  # noqa: E402
    build_warroom_v2_shell_preview_panel_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29D_WARROOM_V2_RENDERER_SPLIT_2026-07-02.md"


def test_q29d_renderer_versions_are_exposed() -> None:
    assert WARROOM_V2_MODEL_VIEWS_VERSION.endswith("ps_q29d.v1")
    assert WARROOM_V2_TOP_BAR_RENDERER_VERSION.endswith("ps_q29d.v1")
    # Later visual slices may advance individual renderer versions. Q29D's
    # durable guard is that the split renderer remains exposed, not that every
    # child renderer is permanently pinned to ps_q29d.
    assert "prediction_cards_renderer" in WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION
    assert "scenario_area_renderer" in WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION
    assert WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION.endswith("ps_q29d.v1")


def test_q29d_zone_selection_helper_preserves_shell_layout() -> None:
    packet = build_warroom_v2_shell_preview_panel_packet()
    shell = packet["shell_preview"]
    top = warroom_v2_models_by_zone(shell, "top")
    cards = warroom_v2_models_by_zone(shell, "prediction_cards")
    scenario = warroom_v2_models_by_zone(shell, "scenario")
    assert len(top) == 3
    assert len(cards) >= 8
    assert [model["widget_id"] for model in scenario] == ["prediction_scenario_ja"]
    assert packet["renderer_split"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29d_parent_panel_is_thin_orchestrator() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    assert "render_warroom_v2_top_bar" in text
    assert "render_warroom_v2_prediction_cards" in text
    assert "render_warroom_v2_scenario_area" in text
    assert "render_warroom_v2_debug_preview" in text
    assert "def _render_prediction_cards" not in text
    assert "def _render_scenario" not in text
    assert "def _render_top_widgets" not in text
    assert len(text.splitlines()) <= 80


def test_q29d_renderer_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
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
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29d_route_and_legacy_warroom_are_not_changed_by_split() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in app_text
    assert "prediction_warroom.v2" not in legacy_text
    assert "warroom_v2_shell_preview_panel" not in legacy_text


def test_q29d_doc_records_renderer_split_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "not_changing_app_route=true" in text
    assert "not_changing_legacy_warroom=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_invoking_classifier=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_touching_autotrade_broker_ledger_mode_parameter=true" in text
