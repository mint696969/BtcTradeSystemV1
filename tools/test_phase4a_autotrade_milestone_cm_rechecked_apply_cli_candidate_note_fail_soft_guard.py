# path: ./tools/test_phase4a_autotrade_milestone_cm_rechecked_apply_cli_candidate_note_fail_soft_guard.py
# desc: Guard rechecked apply CLI candidate readiness note parsing is fail-soft. Rejection appends one mode_state; no command/observer append, runner, or broker.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CLI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_rechecked_once.py"
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
FORBIDDEN_CLI_TOKENS = (
    "append_mode_state_record",
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


def command_row(command_id: str, note: str, *, blocked_by: list[str]) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-10),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "apply_cli_candidate_note_fail_soft"],
            "note": note,
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def run_cli(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "btcts.apps.autotrade_apply_mode_change_rechecked_once",
            "--max-lines",
            "100",
            "--max-observer-run-age-sec",
            "120",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_stdout(label: str, stdout: str, failures: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except Exception as exc:
        failures.append(f"{label} CLI stdout was not JSON: {exc}: {stdout[:500]}")
        return {}
    if not isinstance(payload, dict):
        failures.append(f"{label} CLI stdout JSON was not object: {type(payload).__name__}")
        return {}
    return payload


def run_case(*, case_name: str, note: str, blocked_by: str, run_twice: bool, failures: list[str]) -> dict[str, Any]:
    hot_root = REPO_ROOT / f"tmp/btc_ts_rechecked_apply_cli_candidate_note_fail_soft_{case_name}_hot"
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
    command_id = f"cmd_cm_candidate_{case_name}_note"
    write_jsonl(command_path, [command_row(command_id, note, blocked_by=[blocked_by])])
    env = os.environ.copy()
    env[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
    env["PYTHONPATH"] = str(SRC_ROOT) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    before_command_count = len(read_command_ledger(command_path))
    before_mode_count = len(read_mode_state_records(mode_state_path).rows)
    observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    first = run_cli(env)
    first_data = parse_stdout(f"{case_name} first", first.stdout, failures)
    after_first_command_count = len(read_command_ledger(command_path))
    after_first_mode_count = len(read_mode_state_records(mode_state_path).rows)
    observer_count_after_first = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    second_data: dict[str, Any] = {}
    second_returncode: int | None = None
    second_stderr = ""
    after_second_command_count = after_first_command_count
    after_second_mode_count = after_first_mode_count
    observer_count_after_second = observer_count_after_first
    if run_twice:
        second = run_cli(env)
        second_returncode = second.returncode
        second_stderr = second.stderr
        second_data = parse_stdout(f"{case_name} second", second.stdout, failures)
        after_second_command_count = len(read_command_ledger(command_path))
        after_second_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_after_second = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    return {
        "case_name": case_name,
        "command_id": command_id,
        "blocked_by": blocked_by,
        "first_returncode": first.returncode,
        "second_returncode": second_returncode,
        "first_result": first_data,
        "second_result": second_data,
        "before_command_count": before_command_count,
        "after_first_command_count": after_first_command_count,
        "after_second_command_count": after_second_command_count,
        "before_mode_count": before_mode_count,
        "after_first_mode_count": after_first_mode_count,
        "after_second_mode_count": after_second_mode_count,
        "observer_count_before": observer_count_before,
        "observer_count_after_first": observer_count_after_first,
        "observer_count_after_second": observer_count_after_second,
        "first_stderr": first.stderr,
        "second_stderr": second_stderr,
    }


def first_result_is_fail_soft(case: dict[str, Any]) -> bool:
    data = case.get("first_result") or {}
    return (
        data.get("command_id") == case.get("command_id")
        and data.get("candidate_readiness_note_present") is False
        and data.get("candidate_readiness_ready") is None
        and data.get("candidate_readiness_current_mode") is None
        and data.get("candidate_readiness_target_mode") is None
        and tuple(data.get("candidate_readiness_blocked_by") or ()) == ()
        and tuple(data.get("candidate_readiness_warnings") or ()) == ()
        and data.get("candidate_readiness_health_state") is None
        and data.get("candidate_readiness_observer_latest_run_id") is None
        and tuple(data.get("candidate_readiness_observer_latest_blocked_by") or ()) == ()
    )


def first_result_rejected_and_appended_once(case: dict[str, Any]) -> bool:
    data = case.get("first_result") or {}
    record = data.get("mode_state_record") or {}
    return (
        case.get("first_returncode") == 2
        and data.get("rejected_by_readiness") is True
        and data.get("record_appended") is True
        and data.get("readiness") is not None
        and data.get("readiness_ready") is False
        and "readiness_recheck_not_ready" in tuple(data.get("blocked_by") or ())
        and record.get("source_command_id") == case.get("command_id")
        and case.get("before_command_count") == 1
        and case.get("after_first_command_count") == 1
        and case.get("before_mode_count") == 0
        and case.get("after_first_mode_count") == 1
        and case.get("observer_count_after_first") == case.get("observer_count_before")
    )


def second_result_does_not_duplicate(case: dict[str, Any]) -> bool:
    data = case.get("second_result") or {}
    return (
        case.get("second_returncode") == 2
        and data.get("skipped") is True
        and data.get("skip_reason") == "no_unapplied_accepted_mode_change_command"
        and case.get("after_second_command_count") == case.get("before_command_count")
        and case.get("after_second_mode_count") == case.get("after_first_mode_count")
        and case.get("observer_count_after_second") == case.get("observer_count_before")
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_pythonpath = os.environ.get("PYTHONPATH")
    try:
        cases = [
            run_case(case_name="malformed", note="{not-json", blocked_by="malformed_note_should_not_crash", run_twice=False, failures=failures),
            run_case(case_name="wrong_kind", note=json.dumps({"kind": "not-readiness", "observer_latest_run_id": "should_not_win"}, sort_keys=True), blocked_by="wrong_kind_note_should_not_drive_context", run_twice=False, failures=failures),
            run_case(case_name="array", note=json.dumps(["not", "object"]), blocked_by="array_note_should_not_drive_context", run_twice=True, failures=failures),
        ]
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime
        if original_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = original_pythonpath

    cli_source = CLI_FILE.read_text(encoding="utf-8")
    payload_source = function_source(APPLIER_FILE, "_command_readiness_note_payload")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    first_results = [case.get("first_result") or {} for case in cases]
    duplicate_case = next(case for case in cases if case.get("case_name") == "array")
    checks = {
        "candidate_note_payload_helper_is_fail_soft": bool(payload_source) and "except Exception" in payload_source and "return {}" in payload_source and 'payload.get("kind") != "autotrade.mode_change_readiness_snapshot"' in payload_source,
        "cli_cases_return_rejection_exit_code_expected": all(case.get("first_returncode") == 2 for case in cases),
        "cli_cases_ignore_malformed_wrong_kind_and_array_notes": all(first_result_is_fail_soft(case) for case in cases),
        "cli_cases_recheck_still_runs_with_bad_candidate_note": all((case.get("first_result") or {}).get("readiness") is not None and "readiness_recheck_not_ready" in tuple((case.get("first_result") or {}).get("blocked_by") or ()) for case in cases),
        "cli_cases_append_exactly_one_mode_state_only": all(first_result_rejected_and_appended_once(case) for case in cases),
        "cli_single_candidate_second_run_does_not_duplicate_mode_state": second_result_does_not_duplicate(duplicate_case),
        "cli_output_keeps_candidate_note_fields_present": all(all(field in data for field in CANDIDATE_NOTE_FIELDS) for data in first_results) and all(field in (duplicate_case.get("second_result") or {}) for field in CANDIDATE_NOTE_FIELDS),
        "cli_uses_result_to_dict": "result.to_dict()" in cli_source and "json.dumps" in cli_source,
        "cli_and_apply_no_runner_or_broker_or_command_append": not any(token in cli_source for token in FORBIDDEN_CLI_TOKENS) and bool(apply_source) and not any(token in apply_source for token in FORBIDDEN_APPLY_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CM: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cm_rechecked_apply_cli_candidate_note_fail_soft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "candidate_note_payload_helper_is_fail_soft": checks["candidate_note_payload_helper_is_fail_soft"],
            "cli_cases_return_rejection_exit_code_expected": checks["cli_cases_return_rejection_exit_code_expected"],
            "cli_cases_ignore_malformed_wrong_kind_and_array_notes": checks["cli_cases_ignore_malformed_wrong_kind_and_array_notes"],
            "cli_cases_recheck_still_runs_with_bad_candidate_note": checks["cli_cases_recheck_still_runs_with_bad_candidate_note"],
            "cli_cases_append_exactly_one_mode_state_only": checks["cli_cases_append_exactly_one_mode_state_only"],
            "cli_single_candidate_second_run_does_not_duplicate_mode_state": checks["cli_single_candidate_second_run_does_not_duplicate_mode_state"],
            "cli_output_keeps_candidate_note_fields_present": checks["cli_output_keeps_candidate_note_fields_present"],
            "cli_uses_result_to_dict": checks["cli_uses_result_to_dict"],
            "cli_and_apply_no_runner_or_broker_or_command_append": checks["cli_and_apply_no_runner_or_broker_or_command_append"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "cases": cases,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
