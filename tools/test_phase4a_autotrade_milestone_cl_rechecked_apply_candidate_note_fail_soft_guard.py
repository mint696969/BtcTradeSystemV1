# path: ./tools/test_phase4a_autotrade_milestone_cl_rechecked_apply_candidate_note_fail_soft_guard.py
# desc: Guard rechecked apply result candidate readiness note parsing is fail-soft. Rejection appends one mode_state; no command/observer append, runner, or broker.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import apply_latest_mode_change_command_once_with_readiness_recheck, default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
CANDIDATE_NOTE_FIELDS = (
    "candidate_readiness_note_present",
    "candidate_readiness_ready",
    "candidate_readiness_current_mode",
    "candidate_readiness_target_mode",
    "candidate_readiness_blocked_by",
    "candidate_readiness_warnings",
    "candidate_readiness_health_state",
    "candidate_readiness_observer_latest_run_id",
    "candidate_readiness_observer_latest_blocked_by",
    "candidate_readiness_observer_latest_would_send_to_broker",
    "candidate_readiness_observer_latest_bounded",
)
FORBIDDEN_APPLY_TOKENS = (
    "append_observer_run_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def command_row(command_id: str, note: str, *, blocked_by: list[str] | None = None) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": blocked_by or [],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-10),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "apply_candidate_note_fail_soft"],
            "note": note,
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_rechecked_apply_candidate_note_fail_soft_hot"
    before_command_count = -1
    after_apply_command_count = -2
    before_mode_count = -1
    after_apply_mode_count = -2
    observer_count_before = 0
    observer_count_after = 0
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
        if command_path.exists():
            command_path.unlink()
        if mode_state_path.exists():
            mode_state_path.unlink()
        if observer_path.exists():
            observer_path.unlink()
        write_jsonl(
            command_path,
            [
                command_row("cmd_cl_candidate_malformed_note", "{not-json", blocked_by=["malformed_note_should_not_crash"]),
                command_row("cmd_cl_candidate_wrong_kind_note", json.dumps({"kind": "not-readiness", "observer_latest_run_id": "should_not_win"}, sort_keys=True), blocked_by=["wrong_kind_note_should_not_drive_context"]),
                command_row("cmd_cl_candidate_array_note", json.dumps(["not", "object"]), blocked_by=["array_note_should_not_drive_context"]),
            ],
        )
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        result = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False)
        after_apply_command_count = len(read_command_ledger(command_path))
        after_apply_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_after = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    result_data = result.to_dict()
    applier_text = APPLIER_FILE.read_text(encoding="utf-8")
    payload_source = function_source(APPLIER_FILE, "_command_readiness_note_payload")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    checks = {
        "candidate_note_payload_helper_is_fail_soft": bool(payload_source) and "except Exception" in payload_source and "return {}" in payload_source and 'payload.get("kind") != "autotrade.mode_change_readiness_snapshot"' in payload_source,
        "apply_result_dataclass_has_candidate_note_fields": all(field in applier_text for field in CANDIDATE_NOTE_FIELDS),
        "apply_ignores_malformed_or_wrong_kind_candidate_note": result_data.get("command_id") == "cmd_cl_candidate_array_note" and result_data.get("candidate_readiness_note_present") is False and result_data.get("candidate_readiness_ready") is None and result_data.get("candidate_readiness_current_mode") is None and result_data.get("candidate_readiness_target_mode") is None and tuple(result_data.get("candidate_readiness_blocked_by") or ()) == () and tuple(result_data.get("candidate_readiness_warnings") or ()) == () and result_data.get("candidate_readiness_health_state") is None and result_data.get("candidate_readiness_observer_latest_run_id") is None and tuple(result_data.get("candidate_readiness_observer_latest_blocked_by") or ()) == (),
        "apply_recheck_still_runs_with_bad_candidate_note": result_data.get("readiness") is not None and result_data.get("rejected_by_readiness") is True and result_data.get("readiness_ready") is False and "readiness_recheck_not_ready" in tuple(result_data.get("blocked_by") or ()),
        "apply_rejection_appended_exactly_one_mode_state": before_mode_count == 0 and after_apply_mode_count == 1 and result_data.get("record_appended") is True and result_data.get("mode_state_record") is not None and (result_data.get("mode_state_record") or {}).get("source_command_id") == "cmd_cl_candidate_array_note",
        "apply_did_not_append_command_or_observer": before_command_count == 3 and after_apply_command_count == before_command_count and observer_count_after == observer_count_before,
        "apply_no_runner_or_broker_or_command_append": bool(apply_source) and not any(token in apply_source for token in FORBIDDEN_APPLY_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CL: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cl_rechecked_apply_candidate_note_fail_soft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "candidate_note_payload_helper_is_fail_soft": checks["candidate_note_payload_helper_is_fail_soft"],
            "apply_result_dataclass_has_candidate_note_fields": checks["apply_result_dataclass_has_candidate_note_fields"],
            "apply_ignores_malformed_or_wrong_kind_candidate_note": checks["apply_ignores_malformed_or_wrong_kind_candidate_note"],
            "apply_recheck_still_runs_with_bad_candidate_note": checks["apply_recheck_still_runs_with_bad_candidate_note"],
            "apply_rejection_appended_exactly_one_mode_state": checks["apply_rejection_appended_exactly_one_mode_state"],
            "apply_did_not_append_command_or_observer": checks["apply_did_not_append_command_or_observer"],
            "apply_no_runner_or_broker_or_command_append": checks["apply_no_runner_or_broker_or_command_append"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "result": result_data,
        "before_command_count": before_command_count,
        "after_apply_command_count": after_apply_command_count,
        "before_mode_count": before_mode_count,
        "after_apply_mode_count": after_apply_mode_count,
        "observer_count_before": observer_count_before,
        "observer_count_after": observer_count_after,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
