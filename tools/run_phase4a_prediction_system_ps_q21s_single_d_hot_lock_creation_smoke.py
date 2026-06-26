# path: ./tools/run_phase4a_prediction_system_ps_q21s_single_d_hot_lock_creation_smoke.py
# desc: PS-Q21S gated single D-hot lock creation smoke tool. Default is dry-run/no creation. Actual D-hot creation requires exact confirmation and remains no acquire/release, no scheduler registration, no producer loop, no runner invocation, no artifact writes beyond the single lock file, no AutoTrade/broker.

from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    LOCK_RELATIVE_PATH,
)
from tools.verify_phase4a_prediction_system_ps_q21r_d_hot_lock_creation_approval_preflight import (  # noqa: E402
    REQUIRED_OPERATOR_CONFIRMATION,
    run_preflight,
)

SMOKE_VERSION = "prediction_warroom.single_d_hot_lock_creation_smoke.ps_q21s.v1"
LOCK_TTL_SEC = 900


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _parse_utc(value: str | None) -> datetime:
    if not value:
        return _utc_now()
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_d_hot_root(root: Path) -> bool:
    return str(Path(root)).rstrip("\\/").lower().replace("/", "\\") == str(DEFAULT_HOT_ROOT).rstrip("\\/").lower().replace("/", "\\")


def build_lock_payload(*, run_id: str, now_utc: str | None = None, reason: str = "ps_q21s_single_d_hot_lock_creation_smoke") -> dict[str, Any]:
    now = _parse_utc(now_utc)
    return {
        "lock_schema_version": SMOKE_VERSION,
        "run_id": run_id,
        "pid": os.getpid(),
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "unknown-host",
        "started_at_utc": _iso(now),
        "expires_at_utc": _iso(now + timedelta(seconds=LOCK_TTL_SEC)),
        "reason": reason,
        "single_d_hot_lock_creation_smoke": True,
        "scheduler_registration_allowed": False,
        "producer_loop_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
    }


def _false_runtime_boundaries() -> dict[str, Any]:
    return {
        "lock_acquire_attempted": False,
        "lock_acquired": False,
        "lock_release_attempted": False,
        "lock_released": False,
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
        "scheduler_registration_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "producer_loop_allowed": False,
        "recurring_enablement_allowed_now": False,
        "runtime_artifact_write_allowed_except_single_lock_file": False,
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


def run_single_lock_file_creation_smoke(
    *,
    target_root: Path = DEFAULT_HOT_ROOT,
    execute_create: bool = False,
    confirmation: str = "",
    allow_guard_test_root: bool = False,
    remove_after_readback: bool = False,
    now_utc: str | None = None,
) -> dict[str, Any]:
    target_root = Path(target_root)
    lock_path = target_root / LOCK_RELATIVE_PATH
    is_d_hot_target = _is_d_hot_root(target_root)
    confirmation_ok = confirmation == REQUIRED_OPERATOR_CONFIRMATION
    run_id = f"prediction_warroom.ps_q21s.lock_smoke:{_iso(_parse_utc(now_utc))}"
    payload = build_lock_payload(run_id=run_id, now_utc=now_utc)

    base = {
        "ok": True,
        "smoke_version": SMOKE_VERSION,
        "target_root": str(target_root),
        "lock_artifact_path": str(lock_path),
        "is_d_hot_target": is_d_hot_target,
        "execute_create_requested": execute_create,
        "confirmation_ok": confirmation_ok,
        "required_operator_confirmation": REQUIRED_OPERATOR_CONFIRMATION,
        "allow_guard_test_root": allow_guard_test_root,
        "remove_after_readback": remove_after_readback,
        "lock_payload_preview": payload,
        "d_hot_lock_file_created": False,
        "d_hot_lock_file_written": False,
        "lock_file_created": False,
        "lock_file_read_back": False,
        "lock_file_removed_after_readback": False,
        "blocked_reasons": [],
        **_false_runtime_boundaries(),
    }

    if not execute_create:
        return {
            **base,
            "smoke_state": "single_d_hot_lock_creation_smoke_dry_run_no_creation",
            "next_required_action": "rerun_with_execute_create_and_exact_confirmation_only_when_operator_approves",
            "d_hot_lock_file_creation_allowed_now": False,
            "single_lock_file_write_allowed_now": False,
        }

    blocked: list[str] = []
    if is_d_hot_target and not confirmation_ok:
        blocked.append("exact_operator_confirmation_required_for_d_hot_lock_creation")
    if not is_d_hot_target and not allow_guard_test_root:
        blocked.append("non_d_hot_target_requires_allow_guard_test_root")
    if lock_path.exists():
        blocked.append("lock_artifact_already_exists")
    if blocked:
        return {
            **base,
            "ok": False,
            "smoke_state": "single_lock_creation_smoke_blocked_no_creation",
            "blocked_reasons": blocked,
            "d_hot_lock_file_creation_allowed_now": False,
            "single_lock_file_write_allowed_now": False,
        }

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    read_back = json.loads(lock_path.read_text(encoding="utf-8"))
    read_back_ok = read_back == payload
    removed = False
    if remove_after_readback:
        lock_path.unlink()
        removed = not lock_path.exists()
    return {
        **base,
        "smoke_state": "single_lock_file_creation_smoke_created_and_read_back" if read_back_ok else "single_lock_file_creation_smoke_readback_failed",
        "ok": bool(read_back_ok and (not remove_after_readback or removed)),
        "lock_file_created": True,
        "lock_file_read_back": read_back_ok,
        "lock_file_removed_after_readback": removed,
        "d_hot_lock_file_created": bool(is_d_hot_target),
        "d_hot_lock_file_written": bool(is_d_hot_target),
        "d_hot_lock_file_creation_allowed_now": bool(is_d_hot_target and confirmation_ok),
        "single_lock_file_write_allowed_now": True,
        "next_required_action": "run_visibility_recheck_and_keep_scheduler_producer_disabled",
    }


def run_default_d_hot_dry_run() -> dict[str, Any]:
    preflight = run_preflight(hot_root=DEFAULT_HOT_ROOT)
    smoke = run_single_lock_file_creation_smoke(target_root=DEFAULT_HOT_ROOT, execute_create=False)
    return {
        **smoke,
        "preflight_ok": preflight.get("ok") is True,
        "preflight_ready_for_separate_approval": preflight.get("preflight_ready_for_separate_approval") is True,
        "preflight_state": preflight.get("preflight_state"),
        "latest_prediction_non_stale": preflight.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": preflight.get("latest_status_success_observed") is True,
        "disabled_boundary_preserved": preflight.get("disabled_boundary_preserved") is True,
        "d_hot_lock_artifact_exists_before": preflight.get("d_hot_lock_artifact_exists") is True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-create", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--target-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--allow-guard-test-root", action="store_true")
    parser.add_argument("--remove-after-readback", action="store_true")
    args = parser.parse_args()
    if args.execute_create:
        result = run_single_lock_file_creation_smoke(
            target_root=Path(args.target_root),
            execute_create=True,
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
