# path: ./tools/test_phase4a_prediction_system_ps_q19d_warroom_realtime_prediction_widget_display_only_guard.py
# desc: Focused guard for PS-Q19D display-only WarRoom realtime prediction panel.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_display_rows,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19D_WARROOM_REALTIME_PREDICTION_WIDGET_DISPLAY_ONLY_2026-06-25.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"

REQUIRED_MARKERS = (
    "ps_q19d_warroom_realtime_prediction_widget_display_only=true",
    "ps_q19c_read_model_consumed=true",
    "warroom_display_panel_mounted=true",
    "streamlit_display_panel_render_allowed=true",
    "fragment_slot_refresh_path_enabled=true",
    "operator_visible_prediction_rows=true",
    "operator_visible_market_snapshot=true",
    "operator_visible_safety_flags=true",
    "PS-Q19E_NON_UI_MANUAL_OR_SCHEDULED_REFRESH_GUARDED",
)

FALSE_BOUNDARIES = (
    "runtime_behavior_changed=false",
    "collector_data_collection_changed=false",
    "prediction_runtime_changed=false",
    "view_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "component_runtime_binding_allowed=false",
    "real_prediction_component_render_invoked=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "ledger_append_allowed=false",
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
        "generated_at": "2026-06-24T16:00:00Z",
        "age_sec": 300,
        "freshness_state": "fresh",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": 2,
        "selected_horizon_sec": [15, 60],
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
            ],
            "60": [
                {
                    "family": "trend_bias",
                    "primary_label": "mild_up_bias",
                    "confidence": "low",
                    "score": 0.31,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["vwap_near_vwap"],
                }
            ],
        },
        "market_snapshot": {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "freshness": "LIVE",
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "best_bid": 100.0,
            "best_ask": 101.0,
            "spread": 1.0,
        },
        "safety_flags": {"records_all_safe": True},
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def test_spec_declares_ps_q19d_display_only_panel_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_display_panel_packet_consumes_q19c_read_model_without_runtime_side_effects() -> None:
    packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fixture_read_model())
    assert packet["ok"] is True
    assert packet["display_panel_version"] == LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION
    assert packet["ps_q19c_read_model_consumed"] is True
    assert packet["warroom_display_panel_mounted"] is True
    assert packet["streamlit_display_panel_render_allowed"] is True
    assert packet["prediction_row_count"] == 2
    assert packet["prediction_rows"][0]["family"] == "market_regime"
    assert packet["market_rows"][0]["value"] == "bitflyer.fx.FX_BTC_JPY"
    for key in (
        "component_runtime_binding_allowed",
        "real_prediction_component_render_invoked",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        assert packet[key] is False, key


def test_display_rows_are_operator_visible_prediction_rows() -> None:
    rows = latest_prediction_warroom_display_rows(_fixture_read_model())
    assert len(rows) == 2
    assert rows[0]["horizon"] == "15s"
    assert rows[1]["label"] == "mild_up_bias"


def test_warroom_page_mounts_display_only_panel_after_q19c() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8")
    assert "render_latest_prediction_warroom_display_panel" in text
    assert "latest_prediction_warroom_read_model_display_panel" in text
    assert "PS-Q19D realtime prediction display" in text
