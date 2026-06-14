# path: ./tools/test_phase4a_autotrade_milestone_cj_rechecked_apply_cli_candidate_context_guard.py
# desc: Guard rechecked apply CLI JSON output surfaces candidate context and does not duplicate mode_state rejection. No command/observer append, runner, or broker.

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
EXPECTED_CANDIDATE_BLOCKED_BY = ["cj_candidate_command_blocker"]
EXPECTED_NOTE_BLOCKED_BY = ["observer_run_latest_blocked_for_live_target", "mode_off"]
EXPECTED_OBSERVER_BLOCKED_BY = ["mode_off"]
EXPECTED_WARNINGS = ["candidate_note_visible_in_cli_output"]
CANDIDATE_FIELDS = (
    "candidate_command_type",
    "candidate_requested_by",
    "candidate_requested_at",
    "candidate_current_mode",
    "candidate_target_mode",
    "candidate_accepted",
    "candidate_blocked_by",
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


def readiness_note() -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": False,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": EXPECTED_NOTE_BLOCKED_BY,
            "warnings": EXPECTED_WARNINGS,
            "health_state": "warn",
            "observer_latest_run_id": "obs_cj_candidate_note",
            "observer_latest_blocked_by": EXPECTED_OBSERVER_BLOCKED_BY,
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(command_id: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": EXPECTED_CANDIDATE_BLOCKED_BY,
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-10),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "apply_cli_candidate_context"],
            "note": readiness_note(),
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_pythonpath = os.environ.get("PYTHONPATH")
    hot_root = REPO_ROOT / "tmp/btc_ts_rechecked_apply_cli_candidate_context_hot"
    before_command_count = -1
    after_first_command_count = -2
    after_second_command_count = -3
    before_mode_count = -1
    after_first_mode_count = -2
    after_second_mode_count = -3
    observer_count_before = 0
    observer_count_after_first = 0
    observer_count_after_second = 0
    first_data: dict[str, Any] = {}
    second_data: dict[str, Any] = {}
    first_returncode = None
    second_returncode = None
    first_stdout = ""
    second_stdout = ""
    first_stderr = ""
    second_stderr = ""
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
        write_jsonl(command_path, [command_row("cmd_cj_candidate_live_request")])
        env = os.environ.copy()
        env[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        env["PYTHONPATH"] = str(SRC_ROOT) + (os.pathsep + original_pythonpath if original_pythonpath else "")
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        first = run_cli(env)
        first_returncode = first.returncode
        first_stdout = first.stdout
        first_stderr = first.stderr
        try:
            first_data = json.loads(first.stdout)
        except Exception as exc:
            failures.append(f"first CLI stdout was not JSON: {exc}: {first.stdout[:500]}")
        after_first_command_count = len(read_command_ledger(command_path))
        after_first_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_after_first = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        second = run_cli(env)
        second_returncode = second.returncode
        second_stdout = second.stdout
        second_stderr = second.stderr
        try:
            second_data = json.loads(second.stdout)
        except Exception as exc:
            failures.append(f"second CLI stdout was not JSON: {exc}: {second.stdout[:500]}")
        after_second_command_count = len(read_command_ledger(command_path))
        after_second_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_after_second = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
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
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    checks = {
        "cli_first_rejection_exit_code_expected": first_returncode == 2 and first_data.get("rejected_by_readiness") is True and first_data.get("record_appended") is True,
        "cli_first_stdout_has_candidate_context": all(field in first_data for field in CANDIDATE_FIELDS) and first_data.get("candidate_command_type") == "REQUEST_MODE_CHANGE" and first_data.get("candidate_requested_by") == "operator_ui" and first_data.get("candidate_current_mode") == "ARMED_DRY_RUN" and first_data.get("candidate_target_mode") == "LIVE_MIN_SIZE" and first_data.get("candidate_accepted") is True and tuple(first_data.get("candidate_blocked_by") or ()) == tuple(EXPECTED_CANDIDATE_BLOCKED_BY),
        "cli_first_stdout_has_candidate_note_context": first_data.get("candidate_readiness_note_present") is True and first_data.get("candidate_readiness_ready") is False and tuple(first_data.get("candidate_readiness_blocked_by") or ()) == tuple(EXPECTED_NOTE_BLOCKED_BY) and tuple(first_data.get("candidate_readiness_warnings") or ()) == tuple(EXPECTED_WARNINGS) and first_data.get("candidate_readiness_health_state") == "warn",
        "cli_first_stdout_has_candidate_observer_note_details": first_data.get("candidate_readiness_observer_latest_run_id") == "obs_cj_candidate_note" and tuple(first_data.get("candidate_readiness_observer_latest_blocked_by") or ()) == tuple(EXPECTED_OBSERVER_BLOCKED_BY) and first_data.get("candidate_readiness_observer_latest_would_send_to_broker") is False and first_data.get("candidate_readiness_observer_latest_bounded") is True,
        "cli_first_stdout_keeps_recheck_separate": first_data.get("readiness") is not None and first_data.get("readiness_ready") is False and "readiness_recheck_not_ready" in tuple(first_data.get("blocked_by") or ()),
        "cli_first_appended_exactly_one_mode_state_only": before_command_count == 1 and after_first_command_count == before_command_count and before_mode_count == 0 and after_first_mode_count == 1 and observer_count_after_first == observer_count_before,
        "cli_second_does_not_duplicate_mode_state": second_returncode == 2 and second_data.get("skipped") is True and second_data.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and after_second_command_count == before_command_count and after_second_mode_count == after_first_mode_count and observer_count_after_second == observer_count_before,
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
    failures.extend(f"protected lower-layer dirty during milestone CJ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cj_rechecked_apply_cli_candidate_context_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "cli_first_rejection_exit_code_expected": checks["cli_first_rejection_exit_code_expected"],
            "cli_first_stdout_has_candidate_context": checks["cli_first_stdout_has_candidate_context"],
            "cli_first_stdout_has_candidate_note_context": checks["cli_first_stdout_has_candidate_note_context"],
            "cli_first_stdout_has_candidate_observer_note_details": checks["cli_first_stdout_has_candidate_observer_note_details"],
            "cli_first_stdout_keeps_recheck_separate": checks["cli_first_stdout_keeps_recheck_separate"],
            "cli_first_appended_exactly_one_mode_state_only": checks["cli_first_appended_exactly_one_mode_state_only"],
            "cli_second_does_not_duplicate_mode_state": checks["cli_second_does_not_duplicate_mode_state"],
            "cli_uses_result_to_dict": checks["cli_uses_result_to_dict"],
            "cli_and_apply_no_runner_or_broker_or_command_append": checks["cli_and_apply_no_runner_or_broker_or_command_append"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "first_returncode": first_returncode,
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
        "first_stderr": first_stderr,
        "second_stderr": second_stderr,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
