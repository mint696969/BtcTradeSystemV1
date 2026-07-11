# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_shell_preview_contract_q29b.py
# desc: PS-Q29B guards for WarRoom v2 shell preview contract. Legacy WarRoom stays detached from v2 runtime/push ownership.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_PLACEHOLDER_READ_MODELS_VERSION,
    WARROOM_V2_SHELL_PREVIEW_VERSION,
    build_warroom_v2_placeholder_read_models_packet,
    build_warroom_v2_shell_preview_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
V2_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29B_WARROOM_V2_SHELL_PREVIEW_CONTRACT_2026-07-02.md"


def test_q29b_placeholder_read_models_cover_layout_widgets() -> None:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T04:40:00Z")
    assert packet["placeholder_read_models_version"] == WARROOM_V2_PLACEHOLDER_READ_MODELS_VERSION
    assert packet["placeholder_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["read_model_count"] == len(packet["read_models"])
    assert "prediction_card_market_regime" in packet["widget_ids"]
    assert "prediction_scenario_ja" in packet["widget_ids"]
    assert "warroom.prediction.scenario_ja" in packet["topics"]


def test_q29b_prediction_cards_have_detail_contract_and_no_runtime_connection() -> None:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T04:40:00Z")
    cards = [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]
    assert len(cards) >= 8
    for card in cards:
        assert card["detail_available"] is True
        assert card["payload"]["placeholder_only"] is True
        assert card["payload"]["runtime_connected"] is False
        assert card["payload"]["push_connected"] is False
        assert card["payload"]["freshness_badge"] == "NO_DATA"
        assert card["safety"]["would_send_to_broker"] is False


def test_q29b_shell_preview_keeps_scenario_below_cards_and_debug_collapsed() -> None:
    packet = build_warroom_v2_shell_preview_packet(generated_at="2026-07-02T04:40:00Z")
    assert packet["shell_preview_version"] == WARROOM_V2_SHELL_PREVIEW_VERSION
    assert packet["warroom_v2_shell_preview_only"] is True
    assert packet["warroom_v2_page_added"] is False
    assert packet["warroom_v2_route_added"] is False
    assert packet["app_navigation_changed"] is False
    assert packet["legacy_warroom_page_changed"] is False
    assert packet["prediction_cards_before_scenario"] is True
    assert packet["debug_default_collapsed"] is True
    assert packet["prediction_card_widget_ids"]
    assert packet["scenario_widget_ids"] == ["prediction_scenario_ja"]
    assert packet["widget_update_unit"] == "topic"
    assert packet["streamlit_required"] is False


def test_q29b_shell_preview_does_not_own_runtime_or_transport() -> None:
    packet = build_warroom_v2_shell_preview_packet(generated_at="2026-07-02T04:40:00Z")
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["page_owns_artifact_scanning"] is False
    assert packet["page_owns_cache_invalidation"] is False
    assert packet["page_owns_classifier_invocation"] is False
    assert packet["page_owns_transport_source"] is False
    assert packet["would_send_to_broker"] is False


def test_q29b_shell_contract_does_not_mount_legacy_warroom_to_v2() -> None:
    # Q29C may mount a separate WarRoom v2 route in app.py. Q29B's durable
    # responsibility guard is that the legacy WarRoom page itself does not own
    # or import v2 contracts, runtime, or shell-preview rendering.
    warroom_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "warroom_v2_page" not in warroom_text
    assert "prediction_warroom.v2.push_widgets" in warroom_text
    assert "ensure_warroom_push_widget_live_observation_runtime" in warroom_text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in warroom_text
    assert "warroom_v2_page" not in warroom_text
    assert "build_warroom_v2_shell_preview_packet" not in warroom_text
    assert "classify_market_regime_feature_bundle(" not in warroom_text
    assert "send_to_broker(" not in warroom_text
    assert "build_warroom_v2_shell_preview_packet" not in warroom_text
    assert "warroom_v2_shell_preview_panel" not in warroom_text


def test_q29b_v2_shell_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "import streamlit",
        "from streamlit",
        "D:" + "\\",
        "E:" + "\\",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
    )
    for path in V2_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"v2 file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29b_doc_records_shell_preview_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "not_mounting_warroom_v2_page=true" in text
    assert "not_adding_sidebar_route=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_touching_autotrade_broker_ledger_mode_parameter=true" in text
