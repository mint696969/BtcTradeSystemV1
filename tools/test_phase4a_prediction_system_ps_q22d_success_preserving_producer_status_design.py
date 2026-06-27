# path: ./tools/test_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design.py
# desc: Focused guard for PS-Q22D success-preserving producer status design.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design import build_success_preserving_status_design  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22D_SUCCESS_PRESERVING_PRODUCER_STATUS_DESIGN_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design.py"


def _status(**overrides: object) -> dict:
    data = {
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": True,
        "last_success_at": "2026-06-27T04:31:32Z",
        "last_success_generated_at": "2026-06-27T04:31:32Z",
        "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T04:31:32Z",
        "last_target_file_size_bytes": 5422419,
        "last_warning_count": 2,
        "warnings": ["orderbook_snapshot_missing_exchange_ts_context_only", "prediction_result_warnings_present:26"],
        "blockers": [],
        "safe_flags": {"producer_enabled_false": True, "scheduler_enabled_false": True, "scheduled_loop_enabled_false": True, "warroom_ui_trigger_false": True, "autotrade_trigger_allowed_false": True, "broker_private_api_allowed_false": True, "would_send_to_broker_false": True},
    }
    data.update(overrides)
    return data


def _q21x(**overrides: object) -> dict:
    data = {"shadow_preflight_ready_for_one_shot": True, "latest_status_success_observed": True, "disabled_boundary_preserved": True}
    data.update(overrides)
    return data


def test_spec_declares_no_write_success_preserving_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22d_success_preserving_producer_status_design=true",
        "read_only_no_write=true",
        "preserves_last_success_generated_at=true",
        "preserves_last_prediction_run_id=true",
        "preserves_q21x_shadow_ready_semantics=true",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_design_preserves_manual_success_fields_without_writing() -> None:
    result = build_success_preserving_status_design(latest_meta={"exists": True, "size_bytes": 5422419}, status_payload=_status(), status_meta={"exists": True}, q21x_packet=_q21x())
    assert result["design_state"] == "success_preserving_producer_status_design_ready_no_write"
    assert result["preserves_last_success_generated_at"] is True
    assert result["preserves_last_prediction_run_id"] is True
    assert result["preserves_last_target_file_size_bytes"] is True
    proposed = result["proposed_status_payload_not_written"]
    assert proposed["producer_state"] == "producer_shadow_status_success_preserved_no_write_design"
    assert proposed["last_success_generated_at"] == "2026-06-27T04:31:32Z"
    assert proposed["last_prediction_run_id"].startswith("prediction_system.ps_g_lite.v1")
    assert proposed["producer_enabled"] is False
    assert proposed["scheduler_enabled"] is False
    assert proposed["blockers"] == []
    assert result["safety"]["status_artifact_written"] is False
    assert result["safety"]["producer_runner_invoked"] is False


def test_design_blocks_without_current_success_status() -> None:
    result = build_success_preserving_status_design(latest_meta={"exists": True, "size_bytes": 1}, status_payload=_status(producer_state="producer_disabled_status_ready", last_success_generated_at=None, last_prediction_run_id=None), status_meta={"exists": True}, q21x_packet=_q21x(latest_status_success_observed=False))
    assert result["design_state"] == "success_preserving_producer_status_design_blocked"
    assert "current_latest_status_success_required" in result["design_blockers"]
    assert "manual_refresh_exported_status_required" in result["design_blockers"]
    assert "last_success_generated_at_required" in result["design_blockers"]
    assert "last_prediction_run_id_required" in result["design_blockers"]


def test_tool_is_read_only_and_has_no_write_or_enablement_tokens() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("write_text(", "open(\"w", "_write_json_atomic", "Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token
    assert "proposed_status_payload_not_written" in text


if __name__ == "__main__":
    test_spec_declares_no_write_success_preserving_contract()
    test_design_preserves_manual_success_fields_without_writing()
    test_design_blocks_without_current_success_status()
    test_tool_is_read_only_and_has_no_write_or_enablement_tokens()
    print(json.dumps({"ok": True}))
