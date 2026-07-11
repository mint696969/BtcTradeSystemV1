# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_debug_preview_compact_polish_q29n.py
# desc: PS-Q29N guards for WarRoom v2 compact debug preview polish.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.debug_preview import (  # noqa: E402
    WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION,
    build_warroom_v2_debug_preview_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import build_warroom_v2_shell_preview_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DEBUG = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/debug_preview.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29N_WARROOM_V2_DEBUG_PREVIEW_COMPACT_POLISH_2026-07-02.md"


def _packet_and_shell() -> tuple[dict, dict]:
    packet = build_warroom_v2_shell_preview_panel_packet()
    return packet, packet["shell_preview"]


def test_q29n_debug_preview_packet_is_compact_display_only() -> None:
    packet, shell = _packet_and_shell()
    preview = build_warroom_v2_debug_preview_packet(packet, shell)
    assert preview["renderer_version"] == WARROOM_V2_DEBUG_PREVIEW_RENDERER_VERSION
    assert preview["compact_debug_preview"] is True
    assert preview["expanded_by_default"] is False
    assert preview["display_only"] is True
    assert preview["placeholder_only"] is True
    assert preview["runtime_connected"] is False
    assert preview["push_connected"] is False
    assert preview["would_send_to_broker"] is False


def test_q29n_debug_preview_counts_models_by_zone() -> None:
    packet, shell = _packet_and_shell()
    preview = build_warroom_v2_debug_preview_packet(packet, shell)
    models = shell["placeholder_read_models"]["read_models"]
    assert preview["model_count"] == len(models)
    assert preview["zones"]["top"] == 3
    assert preview["zones"]["prediction_cards"] >= 8
    assert preview["zones"]["scenario"] == 1


def test_q29n_debug_preview_renderer_text_is_compact() -> None:
    text = DEBUG.read_text(encoding="utf-8-sig")
    assert "Debug / compact preview" in text
    assert "placeholder-only / display-only" in text
    assert "build_warroom_v2_debug_preview_packet" in text
    assert "placeholder_read_models" in text
    assert "Debug / raw preview packet" not in text
    assert "expanded=False" in text


def test_q29n_debug_preview_is_small_and_side_effect_free() -> None:
    text = DEBUG.read_text(encoding="utf-8-sig")
    assert len(text.splitlines()) <= 120
    for token in ("build_market_regime_source_snapshot(", "classify_market_regime_feature_bundle(", "send_to_broker(", "append_ledger(", "write_runtime_artifact(", "websocket.", "sse."):
        assert token not in text


def test_q29n_no_route_or_legacy_warroom_change() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in app_text
    assert 'LEGACY_PAGE_KEY_REDIRECTS = {' in app_text
    assert '"warroom": "warroom_v2"' in app_text
    assert "debug_preview_renderer.ps_q29n" not in legacy_text
    assert "prediction_warroom.v2.push_widgets" in legacy_text
    assert "ensure_warroom_push_widget_live_observation_runtime" in legacy_text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in legacy_text
    assert "warroom_v2_page" not in legacy_text
    assert "build_warroom_v2_shell_preview_packet" not in legacy_text
    assert "classify_market_regime_feature_bundle(" not in legacy_text
    assert "send_to_broker(" not in legacy_text
    assert "autotrade_trigger_allowed = True" not in legacy_text


def test_q29n_doc_records_debug_preview_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "compact_debug_preview=true" in text
    assert "expanded_by_default=false" in text
    assert "model_count_visible=true" in text
    assert "zone_counts_visible=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
