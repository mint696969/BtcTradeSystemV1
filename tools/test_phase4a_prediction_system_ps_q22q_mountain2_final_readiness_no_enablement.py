# path: ./tools/test_phase4a_prediction_system_ps_q22q_mountain2_final_readiness_no_enablement.py
# desc: Focused guard for PS-Q22Q final Mountain2 no-enable readiness packet.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22q_mountain2_final_readiness_no_enablement import (  # noqa: E402
    READINESS_VERSION,
    build_final_readiness_packet,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22Q_MOUNTAIN2_FINAL_READINESS_NO_ENABLEMENT_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22q_mountain2_final_readiness_no_enablement.py"


def _packet(**overrides: object) -> dict:
    data = {
        "scheduler_enabled": False,
        "trigger_added": False,
        "recurring_enablement_allowed_now": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def test_spec_declares_final_no_enablement_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22q_mountain2_final_readiness_no_enablement=true",
        "final_pre_danger_boundary_packet=true",
        "read_only_review_only=true",
        "no_scheduler_action_replacement=true",
        "no_scheduler_enablement=true",
        "no_trigger_addition=true",
        "no_recurring_or_periodic_execution=true",
        "no_latest_prediction_artifact_write=true",
        "scheduler_action_replacement_executed=false",
        "scheduler_enabled=false",
        "trigger_added=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_ready_packet_still_requires_stop_before_actual_mountain2() -> None:
    result = build_final_readiness_packet(
        repo_status_short="",
        q22m_packet=_packet(prep_state="ready", prep_ready_for_future_enablement_design=True, prep_blockers=[]),
        q22n_packet=_packet(contract_state="ready", contract_ready_for_future_no_enable_runner_skeleton=True, contract_blockers=[]),
        q22o_packet=_packet(runner_state="ready", runner_ready_for_future_danger_boundary_review=True, blocked_reasons=[]),
        q22p_packet=_packet(contract_state="ready", contract_ready_for_future_enablement_review=True, contract_blockers=[]),
    )
    assert result["readiness_version"] == READINESS_VERSION
    assert result["readiness_state"] == "mountain2_final_pre_danger_boundary_ready_no_enablement"
    assert result["ready_to_execute_mountain2_now"] is False
    assert result["must_stop_before_actual_mountain2"] is True
    assert result["operator_confirmation_required_before_actual_mountain2"] is True
    assert result["future_enablement_token_used"] is False
    assert result["dangerous_operations_not_executed"]["scheduler_enablement"] is False
    assert result["scheduler_action_replacement_executed"] is False
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["lock_acquire_attempted"] is False
    assert result["would_send_to_broker"] is False


def test_blocks_if_any_prior_packet_crossed_boundary() -> None:
    result = build_final_readiness_packet(
        repo_status_short="",
        q22m_packet=_packet(scheduler_enabled=True),
        q22n_packet=_packet(trigger_added=True),
        q22o_packet=_packet(latest_prediction_artifact_written=True),
        q22p_packet=_packet(would_send_to_broker=True),
    )
    assert result["safe_to_stop_before_danger_boundary"] is False
    assert "q22m_must_preserve_no_scheduler_no_trigger" in result["readiness_blockers"]
    assert "q22n_must_preserve_no_scheduler_no_trigger" in result["readiness_blockers"]
    assert "q22o_must_preserve_no_runtime_writes" in result["readiness_blockers"]
    assert "q22p_must_preserve_no_broker_send" in result["readiness_blockers"]


def test_tool_contains_no_scheduler_runtime_write_or_broker_execution() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in (
        "run_one_shot_write",
        "run_bounded_manual_freshness_recovery_once",
        "execute_one_shot_write=True",
        "allow_runtime_artifact_write=True",
        "execute_status_write_once=True",
        "_write_json_atomic",
        ".write_text(",
        "Path.replace(",
        "os.replace(",
        "send_order(",
        "place_order(",
    ):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_final_no_enablement_boundary()
    test_ready_packet_still_requires_stop_before_actual_mountain2()
    test_blocks_if_any_prior_packet_crossed_boundary()
    test_tool_contains_no_scheduler_runtime_write_or_broker_execution()
    print(json.dumps({"ok": True}))
