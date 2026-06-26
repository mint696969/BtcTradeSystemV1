# path: ./tools/test_phase4a_prediction_system_ps_q21n_disabled_non_ui_scheduler_producer_dry_run_design.py
# desc: Focused guard for PS-Q21N disabled non-UI scheduler/producer dry-run design.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.design_phase4a_prediction_system_ps_q21n_disabled_non_ui_scheduler_producer_dry_run import (  # noqa: E402
    DRY_RUN_DESIGN_VERSION,
    build_disabled_non_ui_scheduler_producer_dry_run_design,
)

TOOL = REPO_ROOT / "tools/design_phase4a_prediction_system_ps_q21n_disabled_non_ui_scheduler_producer_dry_run.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21N_DISABLED_NON_UI_SCHEDULER_PRODUCER_DRY_RUN_DESIGN_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21n_disabled_non_ui_scheduler_producer_dry_run_design=true",
    "read_only_dry_run_design_only=true",
    "dry_run_design_ready=observed_result",
    "scheduler_registration_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "producer_loop_allowed=false",
    "recurring_enablement_allowed_now=false",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def _latest() -> dict:
    return {
        "run_identity": {"generated_at": "2026-06-26T07:34:29Z"},
        "forecast_batch": {"generated_at": "2026-06-26T07:34:29Z", "records": [{"x": 1}, {"x": 2}]},
    }


def _status() -> dict:
    return {
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": True,
        "freshness_max_age_sec": 3600,
        "recommended_cadence_sec": 300,
        "last_success_generated_at": "2026-06-26T07:34:29Z",
        "last_failure_at": None,
        "blockers": [],
        "warnings": ["prediction_result_warnings_present:19"],
        "safe_flags": {
            "producer_enabled_false": True,
            "scheduler_enabled_false": True,
            "scheduled_loop_enabled_false": True,
            "warroom_ui_trigger_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
        },
    }


def _meta(size: int) -> dict:
    return {"exists": True, "size_bytes": size, "mtime_utc": "2026-06-26T07:34:29Z"}


def test_spec_declares_disabled_dry_run_design_and_no_enablement() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_disabled_dry_run_design_ready_without_invocation_or_registration() -> None:
    result = build_disabled_non_ui_scheduler_producer_dry_run_design(
        latest_payload=_latest(),
        status_payload=_status(),
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        now_utc="2026-06-26T07:35:00Z",
    )
    assert result["ok"] is True
    assert result["dry_run_design_version"] == DRY_RUN_DESIGN_VERSION
    assert result["dry_run_design_state"] == "disabled_non_ui_scheduler_producer_dry_run_design_ready_no_registration"
    assert result["dry_run_design_ready"] is True
    assert result["latest_prediction_non_stale"] is True
    assert result["latest_status_success_observed"] is True
    assert result["disabled_boundary_preserved"] is True
    assert result["disabled_dry_run_plan"]["tick_source"] == "manual_cli_or_test_only_no_scheduler_registration"
    execution = result["dry_run_execution_result"]
    assert execution["scheduler_registered"] is False
    assert execution["scheduler_started"] is False
    assert execution["scheduled_loop_enabled"] is False
    assert execution["producer_loop_enabled"] is False
    assert execution["producer_runner_invoked"] is False
    assert execution["bounded_manual_refresh_invoked"] is False
    assert execution["actual_export_runner_invoked"] is False
    assert execution["latest_prediction_artifact_written"] is False
    assert execution["status_artifact_written"] is False
    assert result["scheduler_registration_allowed"] is False
    assert result["scheduler_enablement_allowed"] is False
    assert result["producer_enablement_allowed"] is False
    assert result["producer_loop_allowed"] is False
    assert result["recurring_enablement_allowed_now"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_stale_or_boundary_breaks_dry_run_design_ready() -> None:
    status = dict(_status())
    status["scheduler_enabled"] = True
    result = build_disabled_non_ui_scheduler_producer_dry_run_design(
        latest_payload=_latest(),
        status_payload=status,
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        now_utc="2026-06-26T09:00:00Z",
    )
    assert result["dry_run_design_state"] == "disabled_non_ui_scheduler_producer_dry_run_design_blocked"
    assert result["dry_run_design_ready"] is False
    assert "latest_prediction_non_stale_required_before_disabled_dry_run_design" in result["dry_run_design_blockers"]
    assert "disabled_boundary_required_before_disabled_dry_run_design" in result["dry_run_design_blockers"]
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_is_read_only_design_only_no_registration_enablement_writes() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "request_warroom_ui_trigger=True",
        "scheduler_registered\": True",
        "producer_runner_invoked\": True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "scheduler_registered" in text
    assert "producer_runner_invoked" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_disabled_dry_run_design_and_no_enablement()
    test_disabled_dry_run_design_ready_without_invocation_or_registration()
    test_stale_or_boundary_breaks_dry_run_design_ready()
    test_tool_is_read_only_design_only_no_registration_enablement_writes()
    print('{"ok": true}')
