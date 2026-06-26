# path: ./tools/verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight.py
# desc: PS-Q21U read-only scheduler/producer registration preflight contract after PS-Q21T. No scheduler registration, no producer loop, no lock creation/acquire/release, no runner invocation, no artifact writes, no AutoTrade/broker.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    LOCK_RELATIVE_PATH,
    run_visibility,
)

PREFLIGHT_VERSION = "prediction_warroom.scheduler_producer_registration_preflight.ps_q21u.v1"
REQUIRED_OPERATOR_CONFIRMATION = "REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN"
REQUIRED_NEXT_PRODUCER_CONFIRMATION = "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _false_boundary_fields() -> dict[str, Any]:
    return {
        "scheduler_registration_allowed_now": False,
        "scheduler_enablement_allowed_now": False,
        "producer_enablement_allowed_now": False,
        "producer_loop_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "d_hot_lock_file_creation_allowed_now": False,
        "d_hot_lock_file_write_allowed_now": False,
        "lock_acquire_allowed_now": False,
        "lock_release_allowed_now": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
        "scheduler_registered": False,
        "scheduler_started": False,
        "scheduled_loop_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "warroom_ui_trigger_invoked": False,
    }


def build_scheduler_producer_registration_preflight(*, visibility_packet: Mapping[str, Any]) -> dict[str, Any]:
    visibility = _as_mapping(visibility_packet)
    blockers: list[str] = []
    if visibility.get("ok") is not True:
        blockers.append("visibility_packet_ok_required")
    if visibility.get("visibility_state") != "lock_scheduler_status_visible_non_stale_disabled_no_lock":
        blockers.append("visibility_non_stale_disabled_no_lock_required")
    if visibility.get("latest_prediction_non_stale") is not True:
        blockers.append("latest_prediction_non_stale_required")
    if visibility.get("latest_status_success_observed") is not True:
        blockers.append("latest_status_success_required")
    if visibility.get("disabled_boundary_preserved") is not True:
        blockers.append("disabled_boundary_preserved_required")
    if visibility.get("d_hot_lock_artifact_exists") is not False:
        blockers.append("d_hot_lock_absent_required_before_scheduler_registration_preflight")
    if visibility.get("scheduler_enabled") is not False:
        blockers.append("scheduler_disabled_required")
    if visibility.get("producer_enabled") is not False:
        blockers.append("producer_disabled_required")
    preflight_ready = not blockers
    return {
        "ok": True,
        "preflight_version": PREFLIGHT_VERSION,
        "preflight_state": "scheduler_producer_registration_preflight_ready_for_separate_approval_no_registration" if preflight_ready else "scheduler_producer_registration_preflight_blocked_no_registration",
        "preflight_ready_for_separate_approval": preflight_ready,
        "preflight_blockers": blockers,
        "separate_operator_approval_required": True,
        "required_operator_confirmation": REQUIRED_OPERATOR_CONFIRMATION,
        "producer_loop_separate_operator_approval_required": True,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "rollback_plan_required": True,
        "hot_root": str(DEFAULT_HOT_ROOT),
        "d_hot_lock_artifact_path": str(DEFAULT_HOT_ROOT / LOCK_RELATIVE_PATH),
        "visibility_state": str(visibility.get("visibility_state") or ""),
        "visibility_attention_reasons": list(visibility.get("visibility_attention_reasons") or []),
        "generated_at": str(visibility.get("generated_at") or ""),
        "age_sec": visibility.get("age_sec"),
        "latest_prediction_non_stale": visibility.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": visibility.get("latest_status_success_observed") is True,
        "disabled_boundary_preserved": visibility.get("disabled_boundary_preserved") is True,
        "d_hot_lock_artifact_exists": visibility.get("d_hot_lock_artifact_exists") is True,
        "producer_state": str(visibility.get("producer_state") or ""),
        "producer_enabled": visibility.get("producer_enabled") is True,
        "scheduler_enabled": visibility.get("scheduler_enabled") is True,
        "output_count": int(visibility.get("output_count") or 0),
        "status_warnings": list(visibility.get("status_warnings") or []),
        "registration_preflight_contract": {
            "clean_worktree_required": True,
            "ps_q21q_visibility_non_stale_disabled_no_lock_required": True,
            "d_hot_lock_absent_required_before_registration": True,
            "scheduler_registration_default_disabled": True,
            "register_disabled_scheduler_only": True,
            "producer_loop_must_remain_disabled": True,
            "runner_invocation_must_remain_disabled": True,
            "status_artifact_write_must_remain_disabled": True,
            "post_registration_visibility_recheck_required": True,
            "rollback_plan_required": True,
            "rollback_unregister_scheduler_only": True,
            "producer_loop_enablement_still_separate_approval": True,
            "broker_and_autotrade_never_allowed": True,
        },
        "rollback_plan": {
            "rollback_trigger_examples": [
                "scheduler_registration_unexpected_state",
                "post_registration_visibility_recheck_unexpected",
                "operator_abort_before_producer_loop_enablement",
            ],
            "rollback_scope": "unregister_only_the_disabled_non_ui_scheduler_registered_by_the_approved_slice",
            "rollback_must_not_delete_prediction_or_status_artifacts": True,
            "rollback_must_not_delete_d_hot_lock_artifacts_except_explicit_smoke_lock_rollback": True,
            "rollback_must_not_enable_producer_loop": True,
            "rollback_must_not_touch_broker_or_autotrade": True,
        },
        "next_allowed_slice_after_explicit_approval": "register_disabled_non_ui_scheduler_once_no_producer_loop_no_runner",
        "read_only_registration_preflight_only": True,
        **_false_boundary_fields(),
    }


def run_preflight(*, hot_root: Path | None = None) -> dict[str, Any]:
    visibility = run_visibility(hot_root=hot_root or DEFAULT_HOT_ROOT)
    return build_scheduler_producer_registration_preflight(visibility_packet=visibility)


def main() -> int:
    result = run_preflight()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
