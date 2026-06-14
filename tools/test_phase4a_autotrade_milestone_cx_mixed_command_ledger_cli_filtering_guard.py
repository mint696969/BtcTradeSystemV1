# path: ./tools/test_phase4a_autotrade_milestone_cx_mixed_command_ledger_cli_filtering_guard.py
# desc: Guard preview/apply CLI filter mixed command ledger to accepted REQUEST_MODE_CHANGE only. Rejected mode, accepted non-mode, and malformed rows are ignored/skipped safely.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_mode_state_records, summarize_command_ledger  # noqa: E402
from btcts.autotrade.execution.command_status import read_command_ledger_rows  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

PREVIEW_CLI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_preview_mode_change_rechecked_once.py"
APPLY_CLI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_rechecked_once.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
COMMAND_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
EXPECTED_TARGET = "cmd_cx_oldest_accepted_mode"
CLI_FORBIDDEN_TOKENS = (
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
APPLY_FORBIDDEN_TOKENS = (
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
PREVIEW_FORBIDDEN_TOKENS = (
    "append_mode_state_record(",
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


def readiness_note(command_id: str) -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": False,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": ["observer_run_latest_blocked_for_live_target", f"{command_id}_persisted_blocker"],
            "warnings": ["mixed_command_ledger_cli_filtering_snapshot"],
            "health_state": "warn",
            "observer_latest_run_id": f"obs_{command_id}",
            "observer_latest_blocked_by": [f"{command_id}_observer_blocker"],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(
    *,
    command_id: str,
    command_type: str,
    accepted: bool,
    requested_at: str,
    blocker: str,
    target: str | None = "LIVE_MIN_SIZE",
    current_mode: str = "ARMED_DRY_RUN",
    confirmation: bool = True,
    note: str | None = None,
) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": [blocker] if blocker else [],
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "operator_ui",
            "requested_at": requested_at,
            "current_mode": current_mode,
            "target": target,
            "confirmation": confirmation,
            "reason_codes": ["guard", "mixed_command_ledger_cli_filtering", command_id],
            "note": readiness_note(command_id) if note is None else note,
            "confirmation_required": command_type != "REQUEST_HALT_NEW",
        },
    }


def write_mixed_command_jsonl(path: Path) -> None:
    rows = [
        command_row(
            command_id="cmd_cx_oldest_accepted_mode",
            command_type="REQUEST_MODE_CHANGE",
            accepted=True,
            requested_at=now_z(-40),
            blocker="cx_oldest_mode_candidate_blocker",
        ),
        command_row(
            command_id="cmd_cx_newer_rejected_mode",
            command_type="REQUEST_MODE_CHANGE",
            accepted=False,
            requested_at=now_z(-30),
            blocker="cx_rejected_mode_should_not_be_candidate",
        ),
        command_row(
            command_id="cmd_cx_latest_accepted_non_mode",
            command_type="REQUEST_HALT_NEW",
            accepted=True,
            requested_at=now_z(-20),
            blocker="cx_non_mode_should_not_be_candidate",
            target=None,
            current_mode="OFF",
            confirmation=False,
            note=json.dumps({"kind": "not-readiness", "observer_latest_run_id": "should_not_win"}, sort_keys=True),
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    text += "\n{not-json\n"
    path.write_text(text, encoding="utf-8")


def run_cli(module: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            module,
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_pythonpath = os.environ.get("PYTHONPATH")
    hot_root = REPO_ROOT / "tmp/btc_ts_mixed_command_ledger_cli_filtering_hot"
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
        write_mixed_command_jsonl(command_path)
        env = os.environ.copy()
        env[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        env["PYTHONPATH"] = str(SRC_ROOT) + (os.pathsep + original_pythonpath if original_pythonpath else "")
        before_command_read = read_command_ledger_rows(command_path, max_lines=100)
        before_command_count = len(before_command_read.rows)
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        summary_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        preview_proc_before = run_cli("btcts.apps.autotrade_preview_mode_change_rechecked_once", env)
        preview_before_apply = parse_stdout("preview_before_apply", preview_proc_before.stdout, failures)
        apply_proc = run_cli("btcts.apps.autotrade_apply_mode_change_rechecked_once", env)
        apply_result = parse_stdout("apply", apply_proc.stdout, failures)
        preview_proc_after = run_cli("btcts.apps.autotrade_preview_mode_change_rechecked_once", env)
        preview_after_apply = parse_stdout("preview_after_apply", preview_proc_after.stdout, failures)
        apply_proc_after = run_cli("btcts.apps.autotrade_apply_mode_change_rechecked_once", env)
        apply_after_apply = parse_stdout("apply_after_apply", apply_proc_after.stdout, failures)
        after_apply_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_after = read_mode_state_records(mode_state_path)
        after_apply_mode_count = len(mode_read_after.rows)
        mode_rows_after = [row.to_dict() for row in mode_read_after.rows]
        summary_after = summarize_command_ledger(command_path, max_lines=100).to_dict()
        observer_count_after = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime
        if original_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = original_pythonpath

    preview_cli_source = PREVIEW_CLI_FILE.read_text(encoding="utf-8")
    apply_cli_source = APPLY_CLI_FILE.read_text(encoding="utf-8")
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    command_read_source = function_source(COMMAND_STATUS_FILE, "read_command_ledger_rows")
    checks = {
        "cli_exit_codes_are_preview_rejection_apply_rejection_then_skips": (preview_proc_before.returncode, apply_proc.returncode, preview_proc_after.returncode, apply_proc_after.returncode) == (2, 2, 2, 2),
        "command_reader_skips_malformed_but_keeps_valid_rows": before_command_count == 3 and summary_before.get("skipped_rows") == 1 and summary_before.get("total_rows") == 3 and tuple(summary_before.get("error_samples") or ()) != (),
        "command_summary_sees_latest_non_mode_but_latest_mode_change_note_separately": summary_before.get("latest_command_id") == "cmd_cx_latest_accepted_non_mode" and summary_before.get("latest_command_type") == "REQUEST_HALT_NEW" and summary_before.get("latest_mode_change_readiness_command_id") == "cmd_cx_newer_rejected_mode" and summary_before.get("latest_mode_change_readiness_accepted") is False,
        "preview_cli_filters_to_only_accepted_mode_change_candidate": preview_before_apply.get("command_id") == EXPECTED_TARGET and preview_before_apply.get("candidate_command_count") == 1 and preview_before_apply.get("command_read_skipped_count") == 1 and preview_before_apply.get("candidate_command_type") == "REQUEST_MODE_CHANGE" and preview_before_apply.get("candidate_accepted") is True and tuple(preview_before_apply.get("candidate_blocked_by") or ()) == ("cx_oldest_mode_candidate_blocker",) and preview_before_apply.get("candidate_readiness_note_present") is True,
        "apply_cli_filters_to_only_accepted_mode_change_candidate": apply_result.get("command_id") == EXPECTED_TARGET and apply_result.get("candidate_command_count") == 1 and apply_result.get("command_read_skipped_count") == 1 and apply_result.get("record_appended") is True and apply_result.get("rejected_by_readiness") is True and (apply_result.get("mode_state_record") or {}).get("source_command_id") == EXPECTED_TARGET,
        "preview_cli_after_apply_ignores_rejected_and_non_mode_and_skips": preview_after_apply.get("command_id") is None and preview_after_apply.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and preview_after_apply.get("candidate_command_count") == 0 and preview_after_apply.get("command_read_skipped_count") == 1 and tuple(preview_after_apply.get("already_applied_command_ids") or ()) == (EXPECTED_TARGET,) and preview_after_apply.get("read_only") is True,
        "apply_cli_after_apply_ignores_rejected_and_non_mode_and_skips": apply_after_apply.get("command_id") is None and apply_after_apply.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and apply_after_apply.get("candidate_command_count") == 0 and apply_after_apply.get("command_read_skipped_count") == 1 and tuple(apply_after_apply.get("already_applied_command_ids") or ()) == (EXPECTED_TARGET,) and apply_after_apply.get("record_appended") is False,
        "mode_state_appended_only_for_selected_mode_change": before_mode_count == 0 and after_apply_mode_count == 1 and tuple(row.get("source_command_id") for row in mode_rows_after) == (EXPECTED_TARGET,),
        "command_and_observer_ledgers_not_appended": after_apply_command_count == before_command_count == 3 and observer_count_after == observer_count_before,
        "summary_after_still_mixed_and_read_only": summary_after.get("total_rows") == 3 and summary_after.get("skipped_rows") == 1 and summary_after.get("latest_command_id") == "cmd_cx_latest_accepted_non_mode" and summary_after.get("read_only") is True and summary_after.get("would_send_to_broker") is False,
        "cli_uses_result_to_dict": "result.to_dict()" in preview_cli_source and "json.dumps" in preview_cli_source and "result.to_dict()" in apply_cli_source and "json.dumps" in apply_cli_source,
        "source_filters_accepted_mode_change_and_unapplied": bool(preview_source) and bool(apply_source) and "row.accepted" in preview_source and "row.command.command_type == CommandType.REQUEST_MODE_CHANGE" in preview_source and "row.command_id not in already_applied" in preview_source and "candidates[-1]" in preview_source and "row.accepted" in apply_source and "row.command.command_type == CommandType.REQUEST_MODE_CHANGE" in apply_source and "row.command_id not in already_applied" in apply_source and "candidates[-1]" in apply_source,
        "cli_preview_apply_command_reader_no_runner_broker": bool(command_read_source) and not any(token in preview_cli_source for token in CLI_FORBIDDEN_TOKENS) and not any(token in apply_cli_source for token in CLI_FORBIDDEN_TOKENS) and not any(token in preview_source for token in PREVIEW_FORBIDDEN_TOKENS) and not any(token in apply_source for token in APPLY_FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    stderrs = [preview_proc_before.stderr, apply_proc.stderr, preview_proc_after.stderr, apply_proc_after.stderr]
    failures.extend(f"unexpected stderr in CLI run {index}: {stderr}" for index, stderr in enumerate(stderrs, start=1) if stderr)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CX: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cx_mixed_command_ledger_cli_filtering_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "cli_exit_codes_are_preview_rejection_apply_rejection_then_skips": checks["cli_exit_codes_are_preview_rejection_apply_rejection_then_skips"],
            "command_reader_skips_malformed_but_keeps_valid_rows": checks["command_reader_skips_malformed_but_keeps_valid_rows"],
            "command_summary_sees_latest_non_mode_but_latest_mode_change_note_separately": checks["command_summary_sees_latest_non_mode_but_latest_mode_change_note_separately"],
            "preview_cli_filters_to_only_accepted_mode_change_candidate": checks["preview_cli_filters_to_only_accepted_mode_change_candidate"],
            "apply_cli_filters_to_only_accepted_mode_change_candidate": checks["apply_cli_filters_to_only_accepted_mode_change_candidate"],
            "preview_cli_after_apply_ignores_rejected_and_non_mode_and_skips": checks["preview_cli_after_apply_ignores_rejected_and_non_mode_and_skips"],
            "apply_cli_after_apply_ignores_rejected_and_non_mode_and_skips": checks["apply_cli_after_apply_ignores_rejected_and_non_mode_and_skips"],
            "mode_state_appended_only_for_selected_mode_change": checks["mode_state_appended_only_for_selected_mode_change"],
            "command_and_observer_ledgers_not_appended": checks["command_and_observer_ledgers_not_appended"],
            "summary_after_still_mixed_and_read_only": checks["summary_after_still_mixed_and_read_only"],
            "cli_uses_result_to_dict": checks["cli_uses_result_to_dict"],
            "source_filters_accepted_mode_change_and_unapplied": checks["source_filters_accepted_mode_change_and_unapplied"],
            "cli_preview_apply_command_reader_no_runner_broker": checks["cli_preview_apply_command_reader_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "returncodes": [preview_proc_before.returncode, apply_proc.returncode, preview_proc_after.returncode, apply_proc_after.returncode],
        "summary_before": summary_before,
        "preview_before_apply": preview_before_apply,
        "apply_result": apply_result,
        "preview_after_apply": preview_after_apply,
        "apply_after_apply": apply_after_apply,
        "summary_after": summary_after,
        "mode_rows_after": mode_rows_after,
        "before_command_count": before_command_count,
        "after_apply_command_count": after_apply_command_count,
        "before_mode_count": before_mode_count,
        "after_apply_mode_count": after_apply_mode_count,
        "observer_count_before": observer_count_before,
        "observer_count_after": observer_count_after,
        "stderrs": stderrs,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
