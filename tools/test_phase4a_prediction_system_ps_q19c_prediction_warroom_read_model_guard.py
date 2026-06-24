# path: ./tools/test_phase4a_prediction_system_ps_q19c_prediction_warroom_read_model_guard.py
# desc: Focused guard for PS-Q19C read-only Prediction WarRoom read model.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    build_latest_prediction_warroom_read_model,
    load_latest_prediction_payload,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19C_PREDICTION_WARROOM_READ_MODEL_2026-06-25.md"

REQUIRED_MARKERS = (
    "ps_q19c_prediction_warroom_read_model=true",
    "latest_prediction_warroom_read_model_added=true",
    "health_log_gate_prerequisite_closed=true",
    "read_model_source_prediction_artifact=prediction/latest_prediction_system_result.json",
    "read_model_declared_view_artifact=prediction/status/latest_prediction_warroom_view.json",
    "PS-Q19D_WARROOM_REALTIME_PREDICTION_WIDGET_DISPLAY_ONLY",
)

FALSE_BOUNDARIES = (
    "view_artifact_write_allowed=false",
    "runtime_behavior_changed=false",
    "collector_data_collection_changed=false",
    "ui_code_changed=false",
    "prediction_runtime_changed=false",
    "ui_mount_allowed=false",
    "real_prediction_widget_rendering_allowed=false",
    "real_prediction_widget_render_invoked=false",
    "streamlit_real_widget_render_invoked=false",
    "component_runtime_binding_allowed=false",
    "refresh_invocation_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
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


def _fixture_payload() -> dict:
    return {
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-24T16:00:00Z",
            "read_only": True,
            "non_executing": True,
            "family_count": 2,
            "horizon_count": 2,
            "record_count": 4,
            "records": [
                {
                    "family": "market_regime",
                    "horizon_sec": 15,
                    "horizon_key": "15s",
                    "primary_label": "range_candidate",
                    "confidence": "medium",
                    "score": 0.49,
                    "usable": True,
                    "warnings": ["tier0_source_quality_gate_not_passed"],
                    "drivers": ["range_boundary_visible"],
                    "values_snapshot": {"estimated_signal_strength_percent": 49},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                },
                {
                    "family": "trend_bias",
                    "horizon_sec": 60,
                    "horizon_key": "60s",
                    "primary_label": "mild_up_bias",
                    "confidence": "low",
                    "score": 0.31,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["vwap_near_vwap"],
                    "values_snapshot": {"estimated_reference_hit_rate_percent": 31},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                },
            ],
        },
    }


def test_spec_declares_ps_q19c_read_model_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_build_latest_prediction_warroom_read_model_is_display_only_and_safe() -> None:
    model = build_latest_prediction_warroom_read_model(
        payload=_fixture_payload(),
        market_state={
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "collector_ts": "2026-06-24T16:00:05Z",
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "best_bid": 100.0,
            "best_ask": 101.0,
            "spread": 1.0,
        },
        market_diag={"preferred_row_freshness": "LIVE", "preferred_row_age_sec": 2.0},
        now_utc="2026-06-24T16:05:00Z",
    )
    assert model["ok"] is True
    assert model["read_model_version"] == LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION
    assert model["freshness_state"] == "fresh"
    assert model["age_sec"] == 300
    assert model["record_count"] == 4
    assert model["selected_records_by_horizon"]["15"][0]["family"] == "market_regime"
    assert model["selected_records_by_horizon"]["60"][0]["primary_label"] == "mild_up_bias"
    assert model["market_snapshot"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert model["safety_flags"]["records_all_safe"] is True
    assert model["read_only"] is True
    assert model["non_executing"] is True
    assert model["display_only"] is True
    for key in (
        "ui_mount_allowed",
        "real_prediction_widget_rendering_allowed",
        "real_prediction_widget_render_invoked",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "view_artifact_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        assert model[key] is False, key


def test_stale_prediction_is_visible_but_not_execution_ready() -> None:
    model = build_latest_prediction_warroom_read_model(
        payload=_fixture_payload(),
        market_state={},
        market_diag={},
        now_utc="2026-06-24T18:00:01Z",
    )
    assert model["freshness_state"] == "stale"
    assert "source_generated_at_stale" in model["warning_reason_codes"]
    assert model["autotrade_trigger_allowed"] is False
    assert model["broker_private_api_allowed"] is False


def test_load_latest_prediction_payload_is_bounded_and_read_only(tmp_path: Path) -> None:
    path = tmp_path / "latest_prediction_system_result.json"
    path.write_text(json.dumps(_fixture_payload()), encoding="utf-8")
    payload = load_latest_prediction_payload(path=path, max_bytes=100_000)
    assert payload["forecast_batch"]["record_count"] == 4
    assert path.exists()

    too_small = load_latest_prediction_payload(path=path, max_bytes=8)
    assert too_small == {}
