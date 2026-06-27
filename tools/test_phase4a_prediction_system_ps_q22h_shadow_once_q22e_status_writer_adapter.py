# path: ./tools/test_phase4a_prediction_system_ps_q22h_shadow_once_q22e_status_writer_adapter.py
# desc: Focused guard for PS-Q22H shadow-once adapter using Q22E status writer.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q22h_shadow_once_q22e_status_writer_adapter import (  # noqa: E402
    ADAPTER_VERSION,
    Q22E_STATUS_WRITE_TOKEN,
    SHADOW_ONCE_TOKEN,
    run_shadow_once_q22e_status_writer_adapter,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22H_SHADOW_ONCE_Q22E_STATUS_WRITER_ADAPTER_2026-06-27.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22h_shadow_once_q22e_status_writer_adapter.py"


def _q21x(**overrides: object) -> dict:
    data = {
        "ok": True,
        "shadow_preflight_ready_for_one_shot": True,
        "shadow_preflight_blockers": [],
        "latest_prediction_non_stale": True,
        "latest_status_success_observed": True,
        "disabled_boundary_preserved": True,
    }
    data.update(overrides)
    return data


def _q22g(**overrides: object) -> dict:
    data = {
        "design_state": "shadow_once_status_writer_replacement_design_ready_no_write",
        "design_blockers": [],
        "q22e_success_preserving_status_writer_available": True,
        "q22f_visibility_review_ready": True,
    }
    data.update(overrides)
    return data


def test_spec_declares_exact_tokens_and_no_scheduler_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22h_shadow_once_q22e_status_writer_adapter=true",
        "default_execution_is_dry_run_no_write=true",
        "requires_outer_shadow_once_confirmation=ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN",
        "requires_inner_status_writer_confirmation=WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE",
        "uses_q22e_success_preserving_status_writer=true",
        "uses_q16b_scaffold_status_writer=false",
        "writes_latest_prediction_artifact=false",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_default_blocks_without_invoking_status_writer() -> None:
    called = {"value": False}
    def fake(**kwargs: object) -> dict:
        called["value"] = True
        return {}
    result = run_shadow_once_q22e_status_writer_adapter(q21x_packet=_q21x(), q22g_design_packet=_q22g(), status_writer_runner=fake, repo_clean=True)
    assert result["adapter_state"] == "shadow_once_q22e_status_writer_blocked_no_write"
    assert result["status_writer_invoked"] is False
    assert result["status_artifact_written"] is False
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert "execute_shadow_once_flag_required" in result["blocked_reasons"]
    assert "exact_shadow_once_confirmation_token_required" in result["blocked_reasons"]
    assert "exact_status_write_confirmation_token_required" in result["blocked_reasons"]
    assert called["value"] is False


def test_blocks_when_q21x_or_q22g_not_ready() -> None:
    result = run_shadow_once_q22e_status_writer_adapter(
        operator_acknowledged=True,
        execute_shadow_once=True,
        shadow_once_confirmation=SHADOW_ONCE_TOKEN,
        status_write_confirmation=Q22E_STATUS_WRITE_TOKEN,
        q21x_packet=_q21x(shadow_preflight_ready_for_one_shot=False, shadow_preflight_blockers=["x"]),
        q22g_design_packet=_q22g(design_state="blocked", design_blockers=["y"]),
        status_writer_runner=lambda **kwargs: {"status_artifact_written": True},
        repo_clean=True,
    )
    assert result["status_writer_invoked"] is False
    assert "q21x_shadow_preflight_ready_required" in result["blocked_reasons"]
    assert "q21x_shadow_preflight_blockers_must_be_empty" in result["blocked_reasons"]
    assert "q22g_shadow_once_status_writer_design_ready_required" in result["blocked_reasons"]
    assert "q22g_design_blockers_must_be_empty" in result["blocked_reasons"]


def test_exact_tokens_invokes_q22e_status_writer_once_and_verifies_after_q21x() -> None:
    calls = []
    def fake(**kwargs: object) -> dict:
        calls.append(kwargs)
        return {
            "success": True,
            "status_artifact_written": True,
            "status_artifact_path": r"D:\btc_ts_hot\prediction\status\non_ui_scheduled_producer_status.json",
            "latest_prediction_artifact_written": False,
            "producer_loop_enabled": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "would_send_to_broker": False,
        }
    result = run_shadow_once_q22e_status_writer_adapter(
        operator_acknowledged=True,
        execute_shadow_once=True,
        shadow_once_confirmation=SHADOW_ONCE_TOKEN,
        status_write_confirmation=Q22E_STATUS_WRITE_TOKEN,
        q21x_packet=_q21x(),
        q21x_after_packet=_q21x(),
        q22g_design_packet=_q22g(),
        status_writer_runner=fake,
        repo_clean=True,
    )
    assert result["adapter_version"] == ADAPTER_VERSION
    assert result["adapter_state"] == "shadow_once_q22e_status_writer_executed_status_write_only"
    assert result["success"] is True
    assert result["status_writer_invoked"] is True
    assert result["status_artifact_written"] is True
    assert result["latest_prediction_artifact_written"] is False
    assert result["producer_loop_enabled"] is False
    assert result["scheduler_enabled"] is False
    assert result["trigger_added"] is False
    assert result["would_send_to_broker"] is False
    assert result["uses_q16b_scaffold_status_writer"] is False
    assert result["uses_q22e_success_preserving_status_writer"] is True
    assert len(calls) == 1
    assert calls[0]["operator_acknowledged"] is True
    assert calls[0]["execute_status_write_once"] is True
    assert calls[0]["confirmation"] == Q22E_STATUS_WRITE_TOKEN


def test_tool_contains_no_scheduler_broker_or_scaffold_runner_call() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "run_success_preserving_status_write_once" in text
    assert "build_prediction_warroom_non_ui_scheduled_producer_runner" not in text
    for token in ("Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_exact_tokens_and_no_scheduler_boundary()
    test_default_blocks_without_invoking_status_writer()
    test_blocks_when_q21x_or_q22g_not_ready()
    test_exact_tokens_invokes_q22e_status_writer_once_and_verifies_after_q21x()
    test_tool_contains_no_scheduler_broker_or_scaffold_runner_call()
    print(json.dumps({"ok": True}))
