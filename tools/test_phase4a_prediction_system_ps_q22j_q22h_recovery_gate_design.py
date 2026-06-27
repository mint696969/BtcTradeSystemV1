# path: ./tools/test_phase4a_prediction_system_ps_q22j_q22h_recovery_gate_design.py
# desc: Focused guard for PS-Q22J Q22H recovery gate design.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22j_q22h_recovery_gate_design import (  # noqa: E402
    Q22E_STATUS_VERSION,
    SHADOW_TOKEN,
    STATUS_TOKEN,
    build_q22h_recovery_gate_design,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22J_Q22H_RECOVERY_GATE_DESIGN_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22j_q22h_recovery_gate_design.py"
Q22F_SOURCE = f"q22e_status_version_required {Q22E_STATUS_VERSION} status_only_write_observed"
Q22G_SOURCE = "q22f_status_only_observation_required q22f_visibility_review_ready_required"
Q22H_SOURCE = "q22g_shadow_once_status_writer_design_ready_required q22g_design_blockers_must_be_empty q22f_visibility_review_ready_required"
Q22E_SOURCE = f"run_success_preserving_status_write_once {STATUS_TOKEN} manual_refresh_exported_status_written latest_prediction_artifact_written"
Q21X_READY = {"shadow_preflight_ready_for_one_shot": True, "shadow_preflight_blockers": []}
STATUS_Q21ZC = {
    "producer_version": "prediction_warroom_bounded_manual_refresh_runner.ps_q16d.v1",
    "producer_state": "manual_refresh_exported_status_written",
    "last_success_generated_at": "2026-06-27T07:10:30Z",
    "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T07:10:30Z",
    "producer_enabled": False,
    "scheduler_enabled": False,
    "blockers": [],
}


def test_spec_declares_cycle_break_design_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22j_q22h_recovery_gate_design=true",
        "read_only_no_write=true",
        "current_q22h_requires_q22g_ready=true",
        "q22g_requires_q22f_status_only_observation=true",
        "q21zc_refresh_can_remove_q22e_status_marker=true",
        "cycle_break_design_required=true",
        "future_q22h_recovery_mode_should_allow_q22e_status_writer_when_q21x_ready=true",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_design_ready_for_q21zc_refreshed_success_status() -> None:
    result = build_q22h_recovery_gate_design(
        q22f_source=Q22F_SOURCE,
        q22g_source=Q22G_SOURCE,
        q22h_source=Q22H_SOURCE,
        q22e_source=Q22E_SOURCE,
        latest_meta={"exists": True, "mtime_utc": "2026-06-27T07:10:30Z"},
        status_meta={"exists": True, "mtime_utc": "2026-06-27T07:10:30Z"},
        status_payload=STATUS_Q21ZC,
        q21x_packet=Q21X_READY,
    )
    assert result["design_state"] == "q22h_recovery_gate_design_ready_no_write"
    assert result["design_blockers"] == []
    assert result["current_q22h_requires_q22g_ready"] is True
    assert result["q22g_requires_q22f_status_only_observation"] is True
    assert result["q22f_requires_q22e_status_marker"] is True
    assert result["q21zc_refresh_can_remove_q22e_status_marker"] is True
    assert result["future_recovery_gate_not_executed"]["may_bypass_q22g_ready"] is True
    assert result["future_recovery_gate_not_executed"]["writes_latest_prediction_artifact"] is False
    assert result["normal_path_contract"]["keep_q22g_ready_required_for_non_recovery_shadow_once"] is True
    assert result["safety"]["status_artifact_written"] is False


def test_design_blocks_without_success_status_or_q22e_writer() -> None:
    result = build_q22h_recovery_gate_design(
        q22f_source=Q22F_SOURCE,
        q22g_source=Q22G_SOURCE,
        q22h_source=Q22H_SOURCE,
        q22e_source="",
        latest_meta={"exists": True},
        status_meta={"exists": True},
        status_payload={"producer_state": "producer_disabled_status_ready"},
        q21x_packet=Q21X_READY,
    )
    assert result["design_state"] == "q22h_recovery_gate_design_blocked"
    assert "q22e_success_preserving_status_writer_not_detected" in result["design_blockers"]
    assert "manual_refresh_success_status_required_for_recovery_design" in result["design_blockers"]


def test_tool_is_read_only() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("write_text(", "open(\"w", "_write_json_atomic", "Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_cycle_break_design_contract()
    test_design_ready_for_q21zc_refreshed_success_status()
    test_design_blocks_without_success_status_or_q22e_writer()
    test_tool_is_read_only()
    print(json.dumps({"ok": True}))
