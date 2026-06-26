# path: ./tools/test_phase4a_prediction_system_ps_q21d_warroom_prediction_refresh_live_badge.py
# desc: Focused guard for PS-Q21D WarRoom prediction refresh live badge.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    Q19D_REFRESH_SEC,
    WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_refresh_live_badge_packet,
)

PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21D_WARROOM_PREDICTION_REFRESH_LIVE_BADGE_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21d_warroom_prediction_refresh_live_badge=true",
    "operator_visible_refresh_live_badge=true",
    "refresh_live_badge_version=prediction_warroom.warroom_prediction_refresh_live_badge.ps_q21d.v1",
    "refresh_live_badge_state=prediction_refresh_live",
    "refresh_live_badge_message_visible=true",
    "refresh_target=latest_prediction_warroom_read_model_display_panel",
    "refresh_interval_sec=5",
    "broad_page_reload_disabled=true",
)

FALSE_BOUNDARIES = (
    "runtime_enablement_allowed=false",
    "loader_binding_runtime_allowed=false",
    "component_runtime_binding_allowed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
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
        "generated_at": "2026-06-26T02:53:39Z",
        "age_sec": 5,
        "freshness_state": "fresh",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": 1,
        "selected_horizon_sec": [15],
        "selected_records_by_horizon": {"15": [{"family": "market_regime", "primary_label": "range_candidate", "confidence": "medium", "score": 0.52, "usable": True, "warnings": [], "drivers": []}]},
        "market_snapshot": {"market_uid": "bitflyer.fx.FX_BTC_JPY", "freshness": "LIVE", "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use", "best_bid": 9631209.0, "best_ask": 9632797.0, "spread": 1588.0},
        "safety_flags": {"records_all_safe": True},
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_live_badge_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_packet_exposes_live_badge_fields_without_runtime_side_effects() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=True,
        lang="ja",
    )
    assert packet["ok"] is True
    assert packet["refresh_live_badge_version"] == WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION
    assert packet["operator_visible_refresh_live_badge"] is True
    assert packet["refresh_live_badge_rendered"] is True
    assert packet["refresh_interval_sec"] == Q19D_REFRESH_SEC == 5
    assert packet["refresh_target"] == "latest_prediction_warroom_read_model_display_panel"
    assert packet["broad_page_reload_disabled"] is True
    assert packet["view_artifact_write_allowed"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_live_badge_packet_is_visible_active_and_localized() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=True,
        lang="ja",
    )
    badge = latest_prediction_warroom_refresh_live_badge_packet(packet, lang="ja")
    assert badge["refresh_live_badge_version"] == WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION
    assert badge["refresh_live_badge_active"] is True
    assert badge["refresh_live_badge_state"] == "prediction_refresh_live"
    assert badge["operator_visible_refresh_live_badge"] is True
    assert badge["refresh_live_badge_auto_refresh_enabled"] is True
    assert badge["refresh_live_badge_broad_reload_disabled"] is True
    assert badge["refresh_live_badge_interval_sec"] == "5"
    assert badge["refresh_live_badge_heartbeat_utc"].endswith("Z")
    message = str(badge["refresh_live_badge_message"])
    assert "予測パネル更新中" in message
    assert "heartbeat UTC=" in message
    assert "更新間隔=5s" in message
    assert "全体再読込なし" in message
    assert badge["runtime_enablement_allowed"] is False
    assert badge["view_artifact_write_allowed"] is False
    assert badge["autotrade_trigger_allowed"] is False
    assert badge["broker_private_api_allowed"] is False
    assert badge["would_send_to_broker"] is False


def test_panel_renders_live_badge_above_status_strip_and_preserves_footer() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION" in text
    assert "def latest_prediction_warroom_refresh_live_badge_packet" in text
    assert "def _render_refresh_live_badge" in text
    assert "_render_refresh_live_badge(packet, lang=lang)" in text
    assert "st.success" in text
    assert "st.warning" in text
    assert "columns = st.columns(5)" in text
    assert "column.metric" in text
    assert "auto_refresh={packet.get('warroom_prediction_display_auto_refresh_enabled')}" in text
    assert "refresh_heartbeat_utc={packet.get('refresh_heartbeat_utc')}" in text
    assert text.index("_render_refresh_live_badge(packet, lang=lang)") < text.index("columns = st.columns(5)")


def test_panel_has_no_runtime_execution_or_artifact_write_enablement() -> None:
    text = PANEL.read_text(encoding="utf-8")
    forbidden = (
        "runtime_artifact_write_allowed: bool = True",
        "status_artifact_write_allowed: bool = True",
        "prediction_artifact_write_allowed: bool = True",
        "view_artifact_write_allowed: bool = True",
        "scheduler_enabled: bool = True",
        "producer_enabled: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "broker_private_api_allowed: bool = True",
        "would_send_to_broker: bool = True",
        "send_order(",
        "place_order(",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_live_badge_and_safety_boundaries()
    test_packet_exposes_live_badge_fields_without_runtime_side_effects()
    test_live_badge_packet_is_visible_active_and_localized()
    test_panel_renders_live_badge_above_status_strip_and_preserves_footer()
    test_panel_has_no_runtime_execution_or_artifact_write_enablement()
    print('{"ok": true}')
