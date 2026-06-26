# path: ./tools/run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py
# desc: PS-Q21V prepares a gated disabled scheduler registration smoke. Default is dry-run/no registration. Temp guard roots may create/readback/remove a mock registration record. Real D-hot/OS scheduler registration is not executed in this preparation slice.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility import DEFAULT_HOT_ROOT  # noqa: E402
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
    REQUIRED_OPERATOR_CONFIRMATION,
    run_preflight,
)

SMOKE_VERSION = "prediction_warroom.disabled_scheduler_registration_smoke.ps_q21v.v1"
MOCK_REGISTRATION_RELATIVE_PATH = Path("scheduler/disabled_non_ui_scheduler_registration.mock.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_d_hot_root(root: Path) -> bool:
    return str(Path(root)).rstrip("\\/").lower().replace("/", "\\") == str(DEFAULT_HOT_ROOT).rstrip("\\/").lower().replace("/", "\\")


def build_disabled_scheduler_registration_payload(*, now_utc: str | None = None) -> dict[str, Any]:
    created_at = now_utc or _utc_now()
    return {
        "registration_schema_version": SMOKE_VERSION,
        "registration_id": f"prediction_warroom.ps_q21v.disabled_scheduler_registration:{created_at}",
        "created_at_utc": created_at,
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "unknown-host",
        "pid": os.getpid(),
        "scheduler_name": "btcts_prediction_warroom_non_ui_disabled_scheduler",
        "scheduler_registered_enabled": False,
        "scheduler_started": False,
        "scheduled_loop_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
    }


def _false_boundaries() -> dict[str, Any]:
    return {
        "os_scheduler_registration_attempted": False,
        "os_scheduler_registered": False,
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
        "d_hot_runtime_artifact_written": False,
        "d_hot_lock_file_created": False,
        "d_hot_lock_file_written": False,
        "lock_acquire_attempted": False,
        "lock_release_attempted": False,
        "producer_enablement_allowed": False,
        "producer_loop_allowed": False,
        "recurring_enablement_allowed_now": False,
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
    }


def run_disabled_scheduler_registration_smoke(
    *,
    target_root: Path = DEFAULT_HOT_ROOT,
    execute_register: bool = False,
    confirmation: str = "",
    allow_guard_test_root: bool = False,
    remove_after_readback: bool = False,
    now_utc: str | None = None,
) -> dict[str, Any]:
    target_root = Path(target_root)
    is_d_hot_target = _is_d_hot_root(target_root)
    confirmation_ok = confirmation == REQUIRED_OPERATOR_CONFIRMATION
    mock_path = target_root / MOCK_REGISTRATION_RELATIVE_PATH
    payload = build_disabled_scheduler_registration_payload(now_utc=now_utc)
    base = {
        "ok": True,
        "smoke_version": SMOKE_VERSION,
        "target_root": str(target_root),
        "mock_registration_path": str(mock_path),
        "is_d_hot_target": is_d_hot_target,
        "execute_register_requested": execute_register,
        "confirmation_ok": confirmation_ok,
        "required_operator_confirmation": REQUIRED_OPERATOR_CONFIRMATION,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        "allow_guard_test_root": allow_guard_test_root,
        "remove_after_readback": remove_after_readback,
        "registration_payload_preview": payload,
        "mock_registration_file_created": False,
        "mock_registration_file_read_back": False,
        "mock_registration_file_removed_after_readback": False,
        "real_d_hot_or_os_scheduler_registration_implemented_in_this_slice": False,
        "blocked_reasons": [],
        **_false_boundaries(),
    }
    if not execute_register:
        return {
            **base,
            "smoke_state": "disabled_scheduler_registration_smoke_dry_run_no_registration",
            "scheduler_registration_allowed_now": False,
            "next_required_action": "separate_exact_operator_confirmation_required_before_any_real_disabled_scheduler_registration_slice",
        }
    blocked: list[str] = []
    if is_d_hot_target:
        blocked.append("real_d_hot_or_os_scheduler_registration_not_implemented_in_ps_q21v_prepare_slice")
    if not is_d_hot_target and not allow_guard_test_root:
        blocked.append("non_d_hot_target_requires_allow_guard_test_root")
    if is_d_hot_target and not confirmation_ok:
        blocked.append("exact_operator_confirmation_required_for_future_real_registration")
    if mock_path.exists():
        blocked.append("mock_registration_already_exists")
    if blocked:
        return {**base, "ok": False, "smoke_state": "disabled_scheduler_registration_smoke_blocked_no_registration", "blocked_reasons": blocked, "scheduler_registration_allowed_now": False}
    mock_path.parent.mkdir(parents=True, exist_ok=True)
    mock_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    read_back = json.loads(mock_path.read_text(encoding="utf-8"))
    readback_ok = read_back == payload
    removed = False
    if remove_after_readback:
        mock_path.unlink()
        removed = not mock_path.exists()
    return {
        **base,
        "ok": bool(readback_ok and (not remove_after_readback or removed)),
        "smoke_state": "disabled_scheduler_registration_mock_created_and_read_back",
        "mock_registration_file_created": True,
        "mock_registration_file_read_back": readback_ok,
        "mock_registration_file_removed_after_readback": removed,
        "scheduler_registration_allowed_now": False,
        "next_required_action": "real_scheduler_registration_still_requires_next_slice_and_exact_operator_confirmation",
    }


def run_default_d_hot_dry_run() -> dict[str, Any]:
    preflight = run_preflight(hot_root=DEFAULT_HOT_ROOT)
    smoke = run_disabled_scheduler_registration_smoke(target_root=DEFAULT_HOT_ROOT, execute_register=False)
    return {
        **smoke,
        "preflight_ok": preflight.get("ok") is True,
        "preflight_ready_for_separate_approval": preflight.get("preflight_ready_for_separate_approval") is True,
        "preflight_state": preflight.get("preflight_state"),
        "preflight_blockers": list(preflight.get("preflight_blockers") or []),
        "visibility_attention_reasons": list(preflight.get("visibility_attention_reasons") or []),
        "latest_prediction_non_stale": preflight.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": preflight.get("latest_status_success_observed") is True,
        "d_hot_lock_artifact_exists": preflight.get("d_hot_lock_artifact_exists") is True,
        "disabled_boundary_preserved": preflight.get("disabled_boundary_preserved") is True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-register", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--target-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--allow-guard-test-root", action="store_true")
    parser.add_argument("--remove-after-readback", action="store_true")
    args = parser.parse_args()
    if args.execute_register:
        result = run_disabled_scheduler_registration_smoke(
            target_root=Path(args.target_root),
            execute_register=True,
            confirmation=args.confirmation,
            allow_guard_test_root=args.allow_guard_test_root,
            remove_after_readback=args.remove_after_readback,
        )
    else:
        result = run_default_d_hot_dry_run()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
