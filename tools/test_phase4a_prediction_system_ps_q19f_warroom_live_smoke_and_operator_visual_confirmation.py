# path: ./tools/test_phase4a_prediction_system_ps_q19f_warroom_live_smoke_and_operator_visual_confirmation.py
# desc: Focused guard for PS-Q19F WarRoom live smoke and operator visual confirmation helper.

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_phase4a_prediction_system_ps_q19f_warroom_live_smoke import (  # noqa: E402
    PS_Q19F_LIVE_SMOKE_VERSION,
    build_ps_q19f_warroom_live_smoke_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    latest_prediction_artifact_path,
    load_latest_prediction_warroom_read_model,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19F_WARROOM_LIVE_SMOKE_AND_OPERATOR_VISUAL_CONFIRMATION_2026-06-25.md"
SMOKE_TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py"

REQUIRED_MARKERS = (
    "ps_q19f_warroom_live_smoke_and_operator_visual_confirmation=true",
    "ps_q19e_dry_run_no_write_verified=true",
    "ps_q19c_read_model_loaded=true",
    "ps_q19d_display_packet_verified=true",
    "operator_visual_confirmation_flags_supported=true",
    "PS-Q19G_WARROOM_OBSERVATION_CLOSE_AND_REFRESH_POLICY_DECISION",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_smoke=false",
    "status_artifact_write_performed_by_smoke=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "ui_triggered_runner_execution=false",
    "approval_or_authorization_allowed=false",
    "ledger_append_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "would_send_to_broker=false",
)


def _fixture_read_model() -> dict:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "source_artifact_path": "D:/btc_ts_hot/prediction/latest_prediction_system_result.json",
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "generated_at": "2026-06-24T16:00:00Z",
        "age_sec": 300,
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
                    "warnings": [],
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


def test_spec_declares_live_smoke_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_live_smoke_packet_verifies_dry_run_read_model_and_display_packet() -> None:
    packet = build_ps_q19f_warroom_live_smoke_packet(
        hot_latest_root_hint="D:/btc_ts_hot",
        supplied_read_model=_fixture_read_model(),
    )
    assert packet["ok"] is True
    assert packet["ps_q19f_version"] == PS_Q19F_LIVE_SMOKE_VERSION
    assert packet["ps_q19e_dry_run"]["request_state"] == "dry_run_no_write"
    assert packet["ps_q19e_dry_run"]["latest_prediction_artifact_written"] is False
    assert packet["ps_q19e_dry_run"]["status_artifact_written"] is False
    assert packet["read_model"]["version"] == "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1"
    assert packet["display_packet"]["prediction_row_count"] == 1
    assert packet["runtime_artifact_write_performed_by_smoke"] is False
    assert packet["status_artifact_write_performed_by_smoke"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_visual_confirmation_flags_are_recorded_but_do_not_execute_runtime_actions() -> None:
    packet = build_ps_q19f_warroom_live_smoke_packet(
        supplied_read_model=_fixture_read_model(),
        manual_visual_confirmation=True,
        observed_panel_visible=True,
        observed_prediction_rows=True,
        observed_market_snapshot=True,
        observed_safety_flags=True,
    )
    assert packet["ok"] is True
    assert packet["operator_visual_confirmation"]["visual_confirmation_complete"] is True
    assert packet["runtime_artifact_write_performed_by_smoke"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False


def test_smoke_tool_runs_directly_from_repo_root() -> None:
    proc = subprocess.run(
        [sys.executable, str(SMOKE_TOOL), "--root", "D:/btc_ts_hot"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert '"ok": true' in proc.stdout
    assert '"runtime_artifact_write_performed_by_smoke": false' in proc.stdout


def test_read_model_uses_explicit_hot_latest_root_hint_for_live_smoke() -> None:
    target = latest_prediction_artifact_path(hot_latest_root_hint="D:/btc_ts_hot")
    assert str(target).replace("\\", "/").endswith("D:/btc_ts_hot/prediction/latest_prediction_system_result.json")
    model = load_latest_prediction_warroom_read_model(hot_latest_root_hint="D:/btc_ts_hot")
    assert str(model["source_artifact_path"]).replace("\\", "/").endswith("D:/btc_ts_hot/prediction/latest_prediction_system_result.json")


def test_smoke_tool_declares_no_refresh_execution_path() -> None:
    text = SMOKE_TOOL.read_text(encoding="utf-8")
    assert "execute_manual_refresh=False" in text
    assert "runtime_artifact_write_performed_by_smoke" in text
    assert "manual_visual_confirmation" in text
    assert "build_ps_q19e_non_ui_refresh_request_packet" in text


if __name__ == "__main__":
    test_spec_declares_live_smoke_and_safety_boundaries()
    test_live_smoke_packet_verifies_dry_run_read_model_and_display_packet()
    test_visual_confirmation_flags_are_recorded_but_do_not_execute_runtime_actions()
    test_read_model_uses_explicit_hot_latest_root_hint_for_live_smoke()
    test_smoke_tool_runs_directly_from_repo_root()
    test_smoke_tool_declares_no_refresh_execution_path()
    print('{"ok": true}')
