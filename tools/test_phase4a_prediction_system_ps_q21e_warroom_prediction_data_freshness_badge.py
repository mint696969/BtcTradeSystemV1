# path: ./tools/test_phase4a_prediction_system_ps_q21e_warroom_prediction_data_freshness_badge.py
# desc: Focused guard for PS-Q21E WarRoom prediction data freshness badge.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_data_freshness_badge_packet,
)

PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21E_WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21e_warroom_prediction_data_freshness_badge=true",
    "operator_visible_data_freshness_badge=true",
    "data_freshness_badge_version=prediction_warroom.warroom_prediction_data_freshness_badge.ps_q21e.v1",
    "panel_liveness_and_data_freshness_separated=true",
    "freshness_state_visible=true",
    "prediction_age_visible=true",
    "prediction_row_count_visible=true",
    "prediction_generated_at_visible=true",
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


def _fixture_read_model(*, freshness_state: str = "fresh", age_sec: int = 5, record_count: int = 1) -> dict:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "generated_at": "2026-06-26T02:53:39Z",
        "age_sec": age_sec,
        "freshness_state": freshness_state,
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": record_count,
        "selected_horizon_sec": [15] if record_count else [],
        "selected_records_by_horizon": {"15": [{"family": "market_regime", "primary_label": "range_candidate", "confidence": "medium", "score": 0.52, "usable": True, "warnings": [], "drivers": []}]} if record_count else {},
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


def test_spec_declares_data_freshness_badge_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_packet_exposes_data_freshness_badge_fields_without_runtime_side_effects() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=True,
        lang="ja",
    )
    assert packet["ok"] is True
    assert packet["data_freshness_badge_version"] == WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION
    assert packet["operator_visible_data_freshness_badge"] is True
    assert packet["data_freshness_badge_rendered"] is True
    assert packet["view_artifact_write_allowed"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_data_freshness_badge_is_fresh_when_prediction_data_is_fresh() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(freshness_state="fresh", age_sec=5, record_count=1),
        fragment_enabled=True,
        lang="ja",
    )
    badge = latest_prediction_warroom_data_freshness_badge_packet(packet, lang="ja")
    assert badge["data_freshness_badge_version"] == WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION
    assert badge["operator_visible_data_freshness_badge"] is True
    assert badge["data_freshness_badge_state"] == "prediction_data_fresh"
    assert badge["data_freshness_badge_fresh"] is True
    assert badge["data_freshness_badge_attention"] is False
    assert badge["data_freshness_badge_age_sec"] == "5"
    assert badge["data_freshness_badge_prediction_row_count"] == "1"
    assert badge["data_freshness_badge_generated_at"] == "2026-06-26T02:53:39Z"
    message = str(badge["data_freshness_badge_message"])
    assert "予測データ fresh" in message
    assert "age=5s" in message
    assert "rows=1" in message
    assert "generated_at=2026-06-26T02:53:39Z" in message
    assert badge["runtime_enablement_allowed"] is False
    assert badge["view_artifact_write_allowed"] is False
    assert badge["autotrade_trigger_allowed"] is False
    assert badge["broker_private_api_allowed"] is False
    assert badge["would_send_to_broker"] is False


def test_data_freshness_badge_warns_when_prediction_data_is_stale_even_if_panel_refresh_is_live() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(freshness_state="stale", age_sec=120, record_count=1),
        fragment_enabled=True,
        lang="ja",
    )
    badge = latest_prediction_warroom_data_freshness_badge_packet(packet, lang="ja")
    assert packet["warroom_prediction_display_auto_refresh_enabled"] is True
    assert badge["data_freshness_badge_state"] == "prediction_data_attention"
    assert badge["data_freshness_badge_attention"] is True
    assert badge["data_freshness_badge_freshness_state"] == "stale"
    assert badge["data_freshness_badge_age_sec"] == "120"
    assert "freshness注意" in str(badge["data_freshness_badge_message"])
    assert "パネル更新中でも" in str(badge["data_freshness_badge_note"])


def test_panel_renders_data_freshness_badge_after_refresh_status_and_before_reading_guide() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION" in text
    assert "def latest_prediction_warroom_data_freshness_badge_packet" in text
    assert "def _render_prediction_data_freshness_badge" in text
    assert "_render_prediction_data_freshness_badge(packet, lang=lang)" in text
    assert "data_freshness_badge_message" in text
    assert "予測データ fresh" in text
    assert "freshness注意" in text
    assert text.index("_render_refresh_status_strip(packet, lang=lang)") < text.index("_render_prediction_data_freshness_badge(packet, lang=lang)")
    assert text.index("_render_prediction_data_freshness_badge(packet, lang=lang)") < text.index("with st.expander(_t(lang, \"reading_title\"), expanded=True):")


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
    test_spec_declares_data_freshness_badge_and_safety_boundaries()
    test_packet_exposes_data_freshness_badge_fields_without_runtime_side_effects()
    test_data_freshness_badge_is_fresh_when_prediction_data_is_fresh()
    test_data_freshness_badge_warns_when_prediction_data_is_stale_even_if_panel_refresh_is_live()
    test_panel_renders_data_freshness_badge_after_refresh_status_and_before_reading_guide()
    test_panel_has_no_runtime_execution_or_artifact_write_enablement()
    print('{"ok": true}')
