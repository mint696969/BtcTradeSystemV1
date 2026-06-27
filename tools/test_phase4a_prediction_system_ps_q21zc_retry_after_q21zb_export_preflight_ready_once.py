# path: ./tools/test_phase4a_prediction_system_ps_q21zc_retry_after_q21zb_export_preflight_ready_once.py
# desc: Focused guard for PS-Q21ZC exact-token retry wrapper after Q21ZB export-preflight ready.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import REQUIRED_CONFIRMATION  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q21zc_retry_after_q21zb_export_preflight_ready_once import (  # noqa: E402
    RETRY_VERSION,
    run_retry_after_q21zb_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21ZC_RETRY_AFTER_Q21ZB_EXPORT_PREFLIGHT_READY_2026-06-27.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q21zc_retry_after_q21zb_export_preflight_ready_once.py"


def _diag(**overrides: object) -> dict:
    data = {
        "ok": True,
        "payload_usable": True,
        "payload_blockers": [],
        "bridge_ready_for_future_non_ui_export_runner": True,
        "bridge_blocked_reasons": [],
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _q21i(**overrides: object) -> dict:
    data = {
        "ok": True,
        "success": True,
        "latest_prediction_artifact_written": True,
        "status_artifact_written": True,
        "prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T00:00:00Z",
        "generated_at": "2026-06-27T00:00:00Z",
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def test_spec_declares_default_no_write_and_exact_retry_gate() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q21zc_retry_after_q21zb_export_preflight_ready=true",
        "default_execution_is_dry_run_no_write=true",
        "requires_exact_confirmation=WRITE_D_HOT_LATEST_PREDICTION_ONCE",
        "requires_q21zb_payload_usable=true",
        "requires_q21zb_bridge_ready_for_future_non_ui_export_runner=true",
        "recurring_enablement_allowed_now=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_default_blocks_without_invoking_q21i() -> None:
    called = {"value": False}
    def fake(**_: object) -> dict:
        called["value"] = True
        return _q21i()
    result = run_retry_after_q21zb_once(diagnostic_packet=_diag(), q21i_runner=fake, repo_clean=True)
    assert result["retry_state"] == "retry_after_q21zb_blocked_no_write"
    assert result["q21i_runner_invoked"] is False
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert "execute_retry_once_flag_required" in result["blocked_reasons"]
    assert "allow_retry_after_q21zb_export_preflight_ready_flag_required" in result["blocked_reasons"]
    assert "exact_q21i_confirmation_token_required" in result["blocked_reasons"]
    assert called["value"] is False


def test_blocks_when_q21zb_diagnostic_not_ready() -> None:
    result = run_retry_after_q21zb_once(
        operator_acknowledged=True,
        execute_retry_once=True,
        allow_retry_after_q21zb_export_preflight_ready=True,
        confirmation=REQUIRED_CONFIRMATION,
        diagnostic_packet=_diag(payload_usable=False, payload_blockers=["x"], bridge_ready_for_future_non_ui_export_runner=False, bridge_blocked_reasons=["y"]),
        q21i_runner=lambda **_: _q21i(),
        repo_clean=True,
    )
    assert result["q21i_runner_invoked"] is False
    assert "q21zb_payload_usable_required" in result["blocked_reasons"]
    assert "q21zb_payload_blockers_must_be_empty" in result["blocked_reasons"]
    assert "q21zb_bridge_ready_for_future_non_ui_export_runner_required" in result["blocked_reasons"]
    assert "q21zb_bridge_blockers_must_be_empty" in result["blocked_reasons"]


def test_exact_token_and_q21zb_ready_invokes_q21i_once_via_fake_runner() -> None:
    calls = []
    def fake(**kwargs: object) -> dict:
        calls.append(kwargs)
        return _q21i()
    result = run_retry_after_q21zb_once(
        operator_acknowledged=True,
        execute_retry_once=True,
        allow_retry_after_q21zb_export_preflight_ready=True,
        confirmation=REQUIRED_CONFIRMATION,
        diagnostic_packet=_diag(),
        q21i_runner=fake,
        repo_clean=True,
    )
    assert result["retry_version"] == RETRY_VERSION
    assert result["success"] is True
    assert result["q21i_runner_invoked"] is True
    assert len(calls) == 1
    assert calls[0]["execute_one_shot_write"] is True
    assert calls[0]["confirmation"] == REQUIRED_CONFIRMATION
    assert result["producer_loop_enabled"] is False
    assert result["scheduler_enabled"] is False
    assert result["would_send_to_broker"] is False


def test_tool_contains_no_scheduler_or_broker_enablement() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_default_no_write_and_exact_retry_gate()
    test_default_blocks_without_invoking_q21i()
    test_blocks_when_q21zb_diagnostic_not_ready()
    test_exact_token_and_q21zb_ready_invokes_q21i_once_via_fake_runner()
    test_tool_contains_no_scheduler_or_broker_enablement()
    print(json.dumps({"ok": True}))
