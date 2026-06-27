# path: ./tools/test_phase4a_prediction_system_ps_q22b_post_shadow_status_semantics.py
# desc: Focused guard for PS-Q22B post-shadow status semantics diagnostic.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22b_post_shadow_status_semantics import build_post_shadow_status_semantics_report  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22B_POST_SHADOW_STATUS_SEMANTICS_REVIEW_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22b_post_shadow_status_semantics.py"


def _status(**overrides: object) -> dict:
    data = {
        "producer_state": "producer_disabled_status_ready",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": False,
        "last_success_generated_at": None,
        "last_prediction_run_id": None,
        "warnings": [
            "latest_prediction_source_adapter_not_supplied_for_design_context",
            "producer_status_artifact_not_supplied_yet_expected_before_warroom_status_display",
        ],
        "blockers": [],
    }
    data.update(overrides)
    return data


def _q21x(**overrides: object) -> dict:
    data = {
        "latest_prediction_non_stale": True,
        "latest_status_success_observed": False,
        "disabled_boundary_preserved": False,
        "shadow_preflight_ready_for_one_shot": False,
        "shadow_preflight_blockers": ["latest_status_success_required_before_shadow_once", "disabled_boundary_preserved_required"],
    }
    data.update(overrides)
    return data


def test_spec_declares_no_write_semantics_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22b_post_shadow_status_semantics_review=true",
        "read_only_no_write=true",
        "q16b_status_scaffold_overwrote_manual_success_status=true",
        "q21x_blocked_after_shadow_expected=true",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_detects_q16b_scaffold_status_and_q21x_block() -> None:
    result = build_post_shadow_status_semantics_report(status_payload=_status(), q21x_packet=_q21x(), latest_meta={"exists": True}, status_meta={"exists": True})
    assert result["ok"] is True
    assert result["read_only_no_write"] is True
    assert result["q16b_status_scaffold_detected"] is True
    assert result["q21x_blocked_by_q16b_scaffold_status"] is True
    assert result["q21x_latest_prediction_non_stale"] is True
    assert result["q21x_latest_status_success_observed"] is False
    assert result["safety"]["status_artifact_written"] is False
    assert result["safety"]["producer_runner_invoked"] is False
    assert "WRITE_D_HOT_LATEST_PREDICTION_ONCE" in result["prepared_restore_command_not_executed"]


def test_does_not_misclassify_manual_success_status() -> None:
    result = build_post_shadow_status_semantics_report(
        status_payload=_status(producer_state="manual_refresh_exported_status_written", last_success_generated_at="2026-06-27T04:09:31Z", last_prediction_run_id="run"),
        q21x_packet=_q21x(latest_status_success_observed=True, disabled_boundary_preserved=True, shadow_preflight_ready_for_one_shot=True, shadow_preflight_blockers=[]),
        latest_meta={"exists": True},
        status_meta={"exists": True},
    )
    assert result["q16b_status_scaffold_detected"] is False
    assert result["q21x_blocked_by_q16b_scaffold_status"] is False


def test_tool_is_read_only_and_does_not_execute_restore() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "run_retry_after_q21zb_once(",
        "run_one_shot_write(",
        "build_prediction_warroom_non_ui_scheduled_producer_runner(",
        "write_text(",
        "open(\"w",
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "Start-ScheduledTask",
        "send_order(",
        "place_order(",
    )
    for token in forbidden:
        assert token not in text, token
    assert "prepared_restore_command_not_executed" in text


if __name__ == "__main__":
    test_spec_declares_no_write_semantics_boundary()
    test_detects_q16b_scaffold_status_and_q21x_block()
    test_does_not_misclassify_manual_success_status()
    test_tool_is_read_only_and_does_not_execute_restore()
    print(json.dumps({"ok": True}))
