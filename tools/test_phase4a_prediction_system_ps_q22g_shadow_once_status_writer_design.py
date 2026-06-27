# path: ./tools/test_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design.py
# desc: Focused guard for PS-Q22G shadow-once status writer design.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design import (  # noqa: E402
    Q22E_STATUS_WRITE_TOKEN,
    SHADOW_ONCE_TOKEN,
    build_shadow_once_status_writer_design,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22G_SHADOW_ONCE_STATUS_WRITER_DESIGN_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design.py"

Q22A_SOURCE = """
build_prediction_warroom_non_ui_scheduled_producer_runner(
    allow_status_artifact_write=True,
    execute_status_artifact_write=True,
)
producer_loop_shadow_once_executed_status_write_only
"""
Q22E_SOURCE = f"""
def run_success_preserving_status_write_once(): pass
{Q22E_STATUS_WRITE_TOKEN}
manual_refresh_exported_status_written
latest_prediction_artifact_written
status_artifact_written
"""
Q22F_READY = {
    "review_state": "q22e_status_only_visibility_review_ready_no_write",
    "review_blockers": [],
    "status_only_write_observed": True,
    "preserves_q21x_success_marker": True,
    "q21x_shadow_preflight_ready_for_one_shot": True,
}


def test_spec_declares_no_write_replacement_design_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22g_shadow_once_status_writer_design=true",
        "read_only_no_write=true",
        "current_q22a_uses_q16b_scaffold_status_writer=true",
        "q22e_success_preserving_status_writer_available=true",
        "q22f_visibility_review_ready=true",
        "future_shadow_once_should_use_q22e_status_writer=true",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_design_ready_when_q22a_scaffold_and_q22e_writer_and_q22f_ready() -> None:
    result = build_shadow_once_status_writer_design(q22a_source=Q22A_SOURCE, q22e_source=Q22E_SOURCE, q22f_packet=Q22F_READY)
    assert result["design_state"] == "shadow_once_status_writer_replacement_design_ready_no_write"
    assert result["design_blockers"] == []
    assert result["current_q22a_uses_q16b_scaffold_status_writer"] is True
    assert result["q22e_success_preserving_status_writer_available"] is True
    assert result["q22f_visibility_review_ready"] is True
    assert result["outer_shadow_once_token_to_keep"] == SHADOW_ONCE_TOKEN
    assert result["inner_status_writer_token_for_future_adapter"] == Q22E_STATUS_WRITE_TOKEN
    assert "call_q22e_success_preserving_status_writer_once_instead_of_q16b_scaffold" in result["future_adapter_sequence_not_executed"]
    assert result["future_contract"]["latest_prediction_artifact_written"] is False
    assert result["future_contract"]["scheduler_enabled"] is False
    assert result["safety"]["status_artifact_written"] is False


def test_design_blocks_when_q22e_or_q22f_missing() -> None:
    result = build_shadow_once_status_writer_design(q22a_source=Q22A_SOURCE, q22e_source="", q22f_packet={"review_state": "blocked"})
    assert result["design_state"] == "shadow_once_status_writer_replacement_design_blocked"
    assert "q22e_success_preserving_status_writer_not_detected" in result["design_blockers"]
    assert "q22f_visibility_review_ready_required" in result["design_blockers"]
    assert "q22f_status_only_observation_required" in result["design_blockers"]


def test_tool_is_read_only() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("write_text(", "open(\"w", "_write_json_atomic", "Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token
    assert "future_adapter_sequence_not_executed" in text


if __name__ == "__main__":
    test_spec_declares_no_write_replacement_design_contract()
    test_design_ready_when_q22a_scaffold_and_q22e_writer_and_q22f_ready()
    test_design_blocks_when_q22e_or_q22f_missing()
    test_tool_is_read_only()
    print(json.dumps({"ok": True}))
