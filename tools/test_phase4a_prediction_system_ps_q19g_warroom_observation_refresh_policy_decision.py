# path: ./tools/test_phase4a_prediction_system_ps_q19g_warroom_observation_refresh_policy_decision.py
# desc: Focused guard for PS-Q19G WarRoom observation close and refresh policy decision.

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_phase4a_prediction_system_ps_q19g_warroom_observation_refresh_policy import (  # noqa: E402
    NEXT_OPERATIONAL_STEP,
    PS_Q19G_REFRESH_POLICY_VERSION,
    build_ps_q19g_warroom_observation_refresh_policy_packet,
)
from tools.run_prediction_warroom_bounded_manual_refresh_ps_q19e import PS_Q19E_MANUAL_REFRESH_ACK  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19G_WARROOM_OBSERVATION_CLOSE_AND_REFRESH_POLICY_DECISION_2026-06-25.md"
POLICY_TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q19g_warroom_observation_refresh_policy.py"

REQUIRED_MARKERS = (
    "ps_q19g_warroom_observation_close_and_refresh_policy_decision=true",
    "observation_path_ready=true",
    "read_model_source_is_hot_latest_root=true",
    "manual_refresh_recommended_now=true",
    "refresh_policy_decision=manual_refresh_first_scheduler_deferred",
    "PS-Q19H_OPERATOR_ACK_BOUNDED_MANUAL_REFRESH_AND_WARROOM_VISUAL_RESMOKE",
)

FALSE_BOUNDARIES = (
    "scheduled_loop_enabled=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "runtime_artifact_write_performed_by_policy_helper=false",
    "status_artifact_write_performed_by_policy_helper=false",
    "manual_refresh_executed_by_policy_helper=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "ui_triggered_runner_execution=false",
    "approval_or_authorization_allowed=false",
    "ledger_append_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
)


def _smoke_fixture(*, freshness_state: str = "stale") -> dict:
    return {
        "ok": True,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "read_model": {
            "ok": True,
            "source_artifact_path": "D:/btc_ts_hot/prediction/latest_prediction_system_result.json",
            "freshness_state": freshness_state,
            "generated_at": "2026-06-22T13:34:38Z",
            "age_sec": 189705,
        },
        "display_packet": {
            "ok": True,
            "prediction_row_count": 24,
            "freshness_state": freshness_state,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
        },
    }


def test_spec_declares_observation_close_and_refresh_policy_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_policy_packet_closes_hot_observation_and_recommends_manual_refresh_first() -> None:
    packet = build_ps_q19g_warroom_observation_refresh_policy_packet(
        hot_latest_root_hint="D:/btc_ts_hot",
        supplied_smoke_packet=_smoke_fixture(freshness_state="stale"),
    )
    assert packet["ok"] is True
    assert packet["ps_q19g_version"] == PS_Q19G_REFRESH_POLICY_VERSION
    assert packet["observation_path_ready"] is True
    assert packet["read_model_source_is_hot_latest_root"] is True
    assert packet["prediction_row_count"] == 24
    assert packet["manual_refresh_recommended_now"] is True
    assert packet["refresh_policy_decision"] == "manual_refresh_first_scheduler_deferred"
    assert packet["scheduler_policy_decision"] == "do_not_enable_scheduler_until_after_manual_refresh_visual_confirmation"
    assert packet["manual_refresh_ack"] == PS_Q19E_MANUAL_REFRESH_ACK
    assert packet["next_operational_step"] == NEXT_OPERATIONAL_STEP
    assert packet["scheduled_loop_enabled"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["manual_refresh_executed_by_policy_helper"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_policy_packet_blocks_if_source_is_not_hot_root() -> None:
    smoke = _smoke_fixture()
    smoke["read_model"] = dict(smoke["read_model"], source_artifact_path="E:/btc_ts/prediction/latest_prediction_system_result.json")
    packet = build_ps_q19g_warroom_observation_refresh_policy_packet(
        hot_latest_root_hint="D:/btc_ts_hot",
        supplied_smoke_packet=smoke,
    )
    assert packet["ok"] is False
    assert packet["read_model_source_is_hot_latest_root"] is False
    assert "read_model_source_not_hot_latest_root" in packet["failures"]


def test_policy_tool_runs_directly_from_repo_root() -> None:
    proc = subprocess.run(
        [sys.executable, str(POLICY_TOOL), "--root", "D:/btc_ts_hot"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert '"ok": true' in proc.stdout
    assert '"read_model_source_is_hot_latest_root": true' in proc.stdout
    assert '"manual_refresh_executed_by_policy_helper": false' in proc.stdout


def test_policy_tool_declares_command_but_does_not_execute_refresh() -> None:
    text = POLICY_TOOL.read_text(encoding="utf-8")
    assert "manual_refresh_command" in text
    assert "manual_refresh_executed_by_policy_helper" in text
    assert "manual_refresh_first_scheduler_deferred" in text
    assert "build_ps_q19f_warroom_live_smoke_packet" in text


if __name__ == "__main__":
    test_spec_declares_observation_close_and_refresh_policy_boundaries()
    test_policy_packet_closes_hot_observation_and_recommends_manual_refresh_first()
    test_policy_packet_blocks_if_source_is_not_hot_root()
    test_policy_tool_runs_directly_from_repo_root()
    test_policy_tool_declares_command_but_does_not_execute_refresh()
    print('{"ok": true}')
