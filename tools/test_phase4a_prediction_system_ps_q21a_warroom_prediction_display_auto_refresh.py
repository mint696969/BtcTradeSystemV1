# path: ./tools/test_phase4a_prediction_system_ps_q21a_warroom_prediction_display_auto_refresh.py
# desc: Focused guard for PS-Q21A WarRoom prediction display auto-refresh.

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
    WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
)

PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21A_WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21a_warroom_prediction_display_auto_refresh=true",
    "warroom_prediction_display_auto_refresh_enabled=true",
    "operator_visible_refresh_heartbeat=true",
    "refresh_target=latest_prediction_warroom_read_model_display_panel",
    "broad_page_reload_disabled=true",
    "runtime_enablement_allowed=false",
    "loader_binding_runtime_allowed=false",
)

FALSE_BOUNDARIES = (
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
        "generated_at": "2026-06-26T01:18:12Z",
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


def test_spec_declares_auto_refresh_target_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_display_panel_packet_exposes_auto_refresh_and_heartbeat() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=True,
        lang="ja",
    )
    assert packet["ok"] is True
    assert packet["auto_refresh_version"] == WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION
    assert packet["warroom_prediction_display_auto_refresh_enabled"] is True
    assert packet["operator_visible_refresh_heartbeat"] is True
    assert packet["refresh_target"] == "latest_prediction_warroom_read_model_display_panel"
    assert packet["refresh_interval_sec"] == Q19D_REFRESH_SEC == 5
    assert packet["refresh_heartbeat_utc"].endswith("Z")
    assert packet["broad_page_reload_disabled"] is True
    assert packet["view_artifact_write_allowed"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_display_panel_packet_can_be_disabled_by_fragment_flag_without_runtime_side_effects() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=False,
    )
    assert packet["warroom_prediction_display_auto_refresh_enabled"] is False
    assert packet["operator_visible_refresh_heartbeat"] is False
    assert packet["fragment_slot_refresh_path_enabled"] is False
    assert packet["broad_page_reload_disabled"] is True
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_warroom_page_keeps_prediction_auto_refresh_default_on_independent_of_global_page_refresh() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert "def _prediction_warroom_display_fragment_enabled" in text
    assert "warroom_prediction_auto_refresh_enabled" in text
    assert "prediction_fragment_enabled = _prediction_warroom_display_fragment_enabled(page_fragment_enabled=fragment_enabled)" in text
    assert "render_latest_prediction_warroom_display_panel(fragment_enabled=prediction_fragment_enabled)" in text
    assert "_render_prediction_warroom_latest_prediction_observation_cleanup_summary_section(fragment_enabled=prediction_fragment_enabled)" in text


def test_module_has_no_runtime_execution_or_artifact_write_enablement() -> None:
    panel_text = PANEL.read_text(encoding="utf-8")
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    forbidden_panel = (
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
    for token in forbidden_panel:
        assert token not in panel_text, token
    forbidden_page = (
        "send_order(",
        "place_order(",
        "view_artifact_write_allowed=True",
        "scheduler_enabled=True",
        "producer_enabled=True",
        "autotrade_trigger_allowed=True",
        "broker_private_api_allowed=True",
    )
    for token in forbidden_page:
        assert token not in page_text, token


if __name__ == "__main__":
    test_spec_declares_auto_refresh_target_and_safety_boundaries()
    test_display_panel_packet_exposes_auto_refresh_and_heartbeat()
    test_display_panel_packet_can_be_disabled_by_fragment_flag_without_runtime_side_effects()
    test_warroom_page_keeps_prediction_auto_refresh_default_on_independent_of_global_page_refresh()
    test_module_has_no_runtime_execution_or_artifact_write_enablement()
    print('{"ok": true}')
