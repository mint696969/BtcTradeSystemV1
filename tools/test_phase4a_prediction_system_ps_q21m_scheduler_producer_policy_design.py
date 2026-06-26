# path: ./tools/test_phase4a_prediction_system_ps_q21m_scheduler_producer_policy_design.py
# desc: Focused guard for PS-Q21M read-only scheduler/producer policy design.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.design_phase4a_prediction_system_ps_q21m_scheduler_producer_policy import (  # noqa: E402
    DESIGN_VERSION,
    REQUIRED_APPROVAL_GATES,
    build_scheduler_producer_policy_design,
)

TOOL = REPO_ROOT / "tools/design_phase4a_prediction_system_ps_q21m_scheduler_producer_policy.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21M_SCHEDULER_PRODUCER_POLICY_DESIGN_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21m_scheduler_producer_policy_design=true",
    "read_only_policy_design_only=true",
    "ready_for_disabled_dry_run_design_slice=observed_result",
    "recurring_enablement_allowed_now=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
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
        "last_success_at": "2026-06-26T07:34:29Z",
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


def test_spec_declares_policy_design_and_no_enablement() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_fresh_one_shot_allows_disabled_dry_run_design_not_enablement() -> None:
    result = build_scheduler_producer_policy_design(
        latest_payload=_latest(),
        status_payload=_status(),
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        now_utc="2026-06-26T07:35:00Z",
    )
    assert result["ok"] is True
    assert result["design_version"] == DESIGN_VERSION
    assert result["policy_design_state"] == "ready_for_disabled_dry_run_design_not_enablement"
    assert result["one_shot_manual_write_success_observed"] is True
    assert result["latest_prediction_non_stale"] is True
    assert result["disabled_boundary_preserved"] is True
    assert result["ready_for_disabled_dry_run_design_slice"] is True
    assert result["recurring_enablement_allowed_now"] is False
    assert result["ready_for_scheduler_enablement"] is False
    assert result["ready_for_producer_enablement"] is False
    assert set(REQUIRED_APPROVAL_GATES).issubset(set(result["required_approval_gates_before_any_enablement"]))
    assert result["policy_design"]["run_lock_policy"]["single_non_overlapping_runner_lock_required"] is True
    assert result["policy_design"]["failure_backoff_policy"]["fail_closed_on_blockers"] is True
    assert result["policy_design"]["visibility_policy"]["show_scheduler_and_producer_disabled_state"] is True
    assert result["scheduler_enablement_allowed"] is False
    assert result["producer_enablement_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_stale_or_boundary_breaks_disabled_dry_run_readiness() -> None:
    status = dict(_status())
    status["producer_enabled"] = True
    result = build_scheduler_producer_policy_design(
        latest_payload=_latest(),
        status_payload=status,
        latest_meta=_meta(5256095),
        status_meta=_meta(2018),
        now_utc="2026-06-26T09:00:00Z",
    )
    assert result["policy_design_state"] == "policy_design_attention_stale_or_boundary"
    assert result["latest_prediction_non_stale"] is False
    assert result["disabled_boundary_preserved"] is False
    assert result["ready_for_disabled_dry_run_design_slice"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_is_read_only_design_only_no_enablement_or_writes() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "request_warroom_ui_trigger=True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "policy_design" in text
    assert "recurring_enablement_allowed_now" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_policy_design_and_no_enablement()
    test_fresh_one_shot_allows_disabled_dry_run_design_not_enablement()
    test_stale_or_boundary_breaks_disabled_dry_run_readiness()
    test_tool_is_read_only_design_only_no_enablement_or_writes()
    print('{"ok": true}')
