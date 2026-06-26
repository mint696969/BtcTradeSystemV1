# path: ./tools/smoke_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only.py
# desc: PS-Q21P disabled lock smoke using temp/mock path only. Writes/removes only a temp lock file; never creates D-hot lock file, never registers scheduler, never invokes producer/export runners, no runtime/status/prediction writes, no AutoTrade/broker.

from __future__ import annotations

from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.design_phase4a_prediction_system_ps_q21o_single_run_lock_contract import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    LOCK_RELATIVE_PATH,
    LOCK_STALE_AFTER_SEC_DEFAULT,
    run_contract,
)

SMOKE_VERSION = "prediction_warroom.disabled_lock_smoke_temp_path_only.ps_q21p.v1"
TEMP_LOCK_FILE_NAME = "non_ui_scheduler_producer.lock.mock.json"


def _utc_now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _is_d_hot_lock_path(path: Path) -> bool:
    normalized = str(path).rstrip("\\/").lower().replace("/", "\\")
    target = str(DEFAULT_HOT_ROOT / LOCK_RELATIVE_PATH).rstrip("\\/").lower().replace("/", "\\")
    return normalized == target


def _build_lock_payload(*, run_id: str, now: datetime, owner: str = "ps_q21p_disabled_lock_smoke") -> dict[str, Any]:
    return {
        "lock_schema_version": SMOKE_VERSION,
        "run_id": run_id,
        "pid": os.getpid(),
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "unknown-host",
        "started_at_utc": _iso(now),
        "expires_at_utc": _iso(now + timedelta(seconds=LOCK_STALE_AFTER_SEC_DEFAULT)),
        "reason": owner,
        "temp_mock_lock_only": True,
        "d_hot_lock_file_allowed": False,
    }


def perform_temp_lock_smoke(*, temp_root: Path, run_id: str = "ps_q21p-disabled-lock-smoke", now_utc: str | None = None) -> dict[str, Any]:
    temp_root = Path(temp_root)
    lock_path = temp_root / TEMP_LOCK_FILE_NAME
    d_hot_lock_target = DEFAULT_HOT_ROOT / LOCK_RELATIVE_PATH
    if _is_d_hot_lock_path(lock_path):
        return {
            "ok": False,
            "smoke_state": "blocked_temp_lock_path_resolves_to_d_hot_lock_path",
            "blocked_reasons": ["temp_lock_path_must_not_equal_d_hot_runtime_lock_path"],
            "temp_lock_path": str(lock_path),
            "d_hot_lock_artifact_path": str(d_hot_lock_target),
            "d_hot_lock_file_created": False,
            "temp_lock_file_created": False,
            "temp_lock_file_removed": False,
            "read_only_contract_verified_before_smoke": False,
            **_safety_false_fields(),
        }
    now = datetime.fromisoformat(now_utc.replace("Z", "+00:00")) if now_utc else _utc_now_dt()
    now = now.astimezone(timezone.utc).replace(microsecond=0)
    payload = _build_lock_payload(run_id=run_id, now=now)
    before_exists = lock_path.exists()
    if before_exists:
        return {
            "ok": False,
            "smoke_state": "blocked_temp_lock_path_already_exists",
            "blocked_reasons": ["temp_lock_path_already_exists"],
            "temp_lock_path": str(lock_path),
            "d_hot_lock_artifact_path": str(d_hot_lock_target),
            "d_hot_lock_file_created": False,
            "temp_lock_file_created": False,
            "temp_lock_file_removed": False,
            "read_only_contract_verified_before_smoke": False,
            **_safety_false_fields(),
        }
    temp_root.mkdir(parents=True, exist_ok=True)
    temp_lock_file_created = False
    temp_lock_file_read_back = False
    temp_lock_file_removed = False
    try:
        lock_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp_lock_file_created = lock_path.exists()
        read_back = json.loads(lock_path.read_text(encoding="utf-8"))
        temp_lock_file_read_back = read_back == payload
    finally:
        if lock_path.exists():
            lock_path.unlink()
        temp_lock_file_removed = not lock_path.exists()
    return {
        "ok": bool(temp_lock_file_created and temp_lock_file_read_back and temp_lock_file_removed),
        "smoke_state": "disabled_temp_lock_smoke_passed_no_d_hot_lock_creation" if temp_lock_file_created and temp_lock_file_read_back and temp_lock_file_removed else "disabled_temp_lock_smoke_failed",
        "blocked_reasons": [],
        "temp_lock_path": str(lock_path),
        "temp_lock_root": str(temp_root),
        "temp_lock_file_existed_before": before_exists,
        "temp_lock_file_created": temp_lock_file_created,
        "temp_lock_file_read_back": temp_lock_file_read_back,
        "temp_lock_file_removed": temp_lock_file_removed,
        "temp_lock_payload_run_id": payload["run_id"],
        "temp_lock_payload_started_at_utc": payload["started_at_utc"],
        "temp_lock_payload_expires_at_utc": payload["expires_at_utc"],
        "d_hot_lock_artifact_path": str(d_hot_lock_target),
        "d_hot_lock_file_created": False,
        "d_hot_lock_file_written": False,
        "d_hot_lock_acquire_attempted": False,
        "d_hot_lock_release_attempted": False,
        **_safety_false_fields(),
    }


def _safety_false_fields() -> dict[str, Any]:
    return {
        "read_only_contract_verified_before_smoke": False,
        "scheduler_registration_allowed": False,
        "scheduler_enablement_allowed": False,
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


def run_disabled_lock_smoke() -> dict[str, Any]:
    contract = run_contract(hot_root=DEFAULT_HOT_ROOT)
    contract_ok = bool(contract.get("ok") is True and contract.get("lock_contract_ready") is True)
    with tempfile.TemporaryDirectory(prefix="ps_q21p_disabled_lock_smoke_") as tmp:
        smoke = perform_temp_lock_smoke(temp_root=Path(tmp)) if contract_ok else {
            "ok": False,
            "smoke_state": "blocked_lock_contract_not_ready",
            "blocked_reasons": ["ps_q21o_lock_contract_must_be_ready_before_temp_lock_smoke"],
            "temp_lock_file_created": False,
            "temp_lock_file_removed": False,
            "d_hot_lock_file_created": False,
            **_safety_false_fields(),
        }
    result = {
        "ok": bool(contract_ok and smoke.get("ok") is True),
        "smoke_version": SMOKE_VERSION,
        "smoke_state": smoke.get("smoke_state"),
        "contract_ok": contract.get("ok") is True,
        "lock_contract_ready": contract.get("lock_contract_ready") is True,
        "lock_contract_state": str(contract.get("lock_contract_state") or ""),
        "generated_at": str(contract.get("generated_at") or ""),
        "age_sec": contract.get("age_sec"),
        "latest_prediction_non_stale": contract.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": contract.get("latest_status_success_observed") is True,
        "disabled_boundary_preserved": contract.get("disabled_boundary_preserved") is True,
        "hot_root": str(DEFAULT_HOT_ROOT),
        "d_hot_lock_artifact_path": str(DEFAULT_HOT_ROOT / LOCK_RELATIVE_PATH),
        "temp_lock_path": str(smoke.get("temp_lock_path") or ""),
        "temp_lock_file_created": smoke.get("temp_lock_file_created") is True,
        "temp_lock_file_read_back": smoke.get("temp_lock_file_read_back") is True,
        "temp_lock_file_removed": smoke.get("temp_lock_file_removed") is True,
        "d_hot_lock_file_created": False,
        "d_hot_lock_file_written": False,
        "d_hot_lock_acquire_attempted": False,
        "d_hot_lock_release_attempted": False,
        "blocked_reasons": list(smoke.get("blocked_reasons") or []),
        "read_only_contract_verified_before_smoke": contract_ok,
        "temp_mock_lock_smoke_only": True,
        **{k: v for k, v in _safety_false_fields().items() if k != "read_only_contract_verified_before_smoke"},
    }
    return result


def main() -> int:
    result = run_disabled_lock_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
