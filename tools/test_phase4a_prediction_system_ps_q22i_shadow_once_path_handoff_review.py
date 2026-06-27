# path: ./tools/test_phase4a_prediction_system_ps_q22i_shadow_once_path_handoff_review.py
# desc: Focused guard for PS-Q22I shadow-once path handoff review.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22i_shadow_once_path_handoff_review import (  # noqa: E402
    SHADOW_TOKEN,
    STATUS_TOKEN,
    Q22E_STATUS_VERSION,
    build_shadow_once_path_handoff_review,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22I_SHADOW_ONCE_PATH_HANDOFF_REVIEW_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22i_shadow_once_path_handoff_review.py"
Q22A_SOURCE = """
build_prediction_warroom_non_ui_scheduled_producer_runner(
    allow_status_artifact_write=True,
    execute_status_artifact_write=True,
)
producer_loop_shadow_once_executed_status_write_only
"""
Q22H_SOURCE = """
def run_shadow_once_q22e_status_writer_adapter(): pass
run_success_preserving_status_write_once
uses_q16b_scaffold_status_writer
uses_q22e_success_preserving_status_writer
SHADOW_ONCE_TOKEN
Q22E_STATUS_WRITE_TOKEN
"""
STATUS_PAYLOAD = {
    "producer_version": Q22E_STATUS_VERSION,
    "producer_state": "manual_refresh_exported_status_written",
    "last_success_generated_at": "2026-06-27T06:06:37Z",
    "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T06:06:37Z",
}
Q21X_READY = {"shadow_preflight_ready_for_one_shot": True, "shadow_preflight_blockers": [], "latest_prediction_non_stale": True, "latest_status_success_observed": True, "disabled_boundary_preserved": True}


def test_spec_declares_handoff_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22i_shadow_once_path_handoff_review=true",
        "read_only_no_write=true",
        "q22a_scaffold_path_detected=true",
        "q22h_adapter_path_detected=true",
        "q22h_exact_execution_observed=true",
        "q22h_should_be_preferred_for_future_shadow_once=true",
        "q22a_scaffold_status_path_should_not_be_used_for_future_shadow_once=true",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_review_ready_when_q22h_status_only_execution_observed() -> None:
    result = build_shadow_once_path_handoff_review(
        q22a_source=Q22A_SOURCE,
        q22h_source=Q22H_SOURCE,
        latest_meta={"exists": True, "mtime_utc": "2026-06-27T06:06:37Z", "size_bytes": 5425754},
        status_meta={"exists": True, "mtime_utc": "2026-06-27T06:55:08Z", "size_bytes": 2310},
        status_payload=STATUS_PAYLOAD,
        q21x_packet=Q21X_READY,
    )
    assert result["review_state"] == "shadow_once_path_handoff_review_ready_no_write"
    assert result["review_blockers"] == []
    assert result["q22a_scaffold_path_detected"] is True
    assert result["q22h_adapter_path_detected"] is True
    assert result["q22h_shadow_token_gate_detected"] is True
    assert result["q22h_status_token_gate_detected"] is True
    assert result["q22h_avoids_q16b_scaffold_call"] is True
    assert result["q22h_exact_execution_observed"] is True
    assert result["q22h_should_be_preferred_for_future_shadow_once"] is True
    assert result["q22a_scaffold_status_path_should_not_be_used_for_future_shadow_once"] is True
    assert result["handoff_recommendation"]["future_exact_execution_should_require_both_tokens"] is True
    assert result["safety"]["latest_prediction_artifact_written"] is False


def test_review_blocks_without_q22h_observation() -> None:
    result = build_shadow_once_path_handoff_review(
        q22a_source=Q22A_SOURCE,
        q22h_source=Q22H_SOURCE,
        latest_meta={"exists": True, "mtime_utc": "2026-06-27T06:55:08Z"},
        status_meta={"exists": True, "mtime_utc": "2026-06-27T06:06:37Z"},
        status_payload={"producer_version": "prediction_warroom_non_ui_scheduled_producer_runner.ps_q16b.v1", "producer_state": "producer_disabled_status_ready"},
        q21x_packet=Q21X_READY,
    )
    assert result["review_state"] == "shadow_once_path_handoff_review_blocked"
    assert "q22h_exact_status_only_execution_observation_required" in result["review_blockers"]
    assert result["q22h_should_be_preferred_for_future_shadow_once"] is False


def test_tool_is_read_only() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("write_text(", "open(\"w", "_write_json_atomic", "Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_handoff_contract()
    test_review_ready_when_q22h_status_only_execution_observed()
    test_review_blocks_without_q22h_observation()
    test_tool_is_read_only()
    print(json.dumps({"ok": True}))
