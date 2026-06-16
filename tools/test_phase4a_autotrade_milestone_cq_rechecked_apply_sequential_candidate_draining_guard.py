# path: ./tools/test_phase4a_autotrade_milestone_cq_rechecked_apply_sequential_candidate_draining_guard.py
# desc: Guard rechecked apply drains multiple accepted REQUEST_MODE_CHANGE candidates latest-first, one per run. Rejections mark source_command_id as applied; no command/observer append, runner, or broker.

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

from btcts.autotrade.execution import apply_latest_mode_change_command_once_with_readiness_recheck, default_command_ledger_path, default_mode_state_ledger_path, preview_latest_mode_change_command_apply_with_readiness_recheck, read_command_ledger, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
EXPECTED_APPLY_SEQUENCE = (
    "cmd_cq_latest_live_request",
    "cmd_cq_middle_live_request",
    "cmd_cq_oldest_live_request",
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
            "warnings": ["sequential_candidate_draining_snapshot"],
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


def command_row(command_id: str, requested_at: str, blocker: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": [blocker],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": requested_at,
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "sequential_candidate_draining", command_id],
            "note": readiness_note(command_id),
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_rechecked_apply_sequential_candidate_draining_hot"
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
    observer_count_before = 0
    observer_count_after = 0
    results: list[dict[str, Any]] = []
    skipped_result: dict[str, Any] = {}
    preview_after_drain: dict[str, Any] = {}
    mode_state_rows: list[dict[str, Any]] = []
    mode_state_summary: dict[str, Any] = {}
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
                command_row("cmd_cq_oldest_live_request", now_z(-30), "cq_oldest_candidate_blocker"),
                command_row("cmd_cq_middle_live_request", now_z(-20), "cq_middle_candidate_blocker"),
                command_row("cmd_cq_latest_live_request", now_z(-10), "cq_latest_candidate_blocker"),
            ],
        )
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        for _ in range(3):
            results.append(apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict())
        skipped_result = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        preview_after_drain = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        after_command_count = len(read_command_ledger(command_path))
        mode_state_read = read_mode_state_records(mode_state_path)
        after_mode_count = len(mode_state_read.rows)
        mode_state_rows = [row.to_dict() for row in mode_state_read.rows]
        mode_state_summary = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        observer_count_after = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    actual_apply_sequence = tuple(result.get("command_id") for result in results)
    actual_mode_state_sequence = tuple(row.get("source_command_id") for row in mode_state_rows)
    expected_already_applied_before_each = (
        (),
        ("cmd_cq_latest_live_request",),
        ("cmd_cq_latest_live_request", "cmd_cq_middle_live_request"),
    )
    expected_candidate_counts = (3, 2, 1)
    checks = {
        "apply_selects_latest_unapplied_candidate_each_run": actual_apply_sequence == EXPECTED_APPLY_SEQUENCE and tuple(result.get("candidate_command_count") for result in results) == expected_candidate_counts,
        "apply_tracks_already_applied_ids_before_each_run": tuple(tuple(result.get("already_applied_command_ids") or ()) for result in results) == expected_already_applied_before_each,
        "each_rejection_appends_one_mode_state_record": before_mode_count == 0 and after_mode_count == 3 and all(result.get("record_appended") is True and result.get("rejected_by_readiness") is True and result.get("skip_reason") == "readiness_recheck_not_ready" for result in results),
        "mode_state_source_command_ids_follow_apply_sequence": actual_mode_state_sequence == EXPECTED_APPLY_SEQUENCE,
        "mode_state_records_keep_rejection_metadata": all(row.get("accepted") is False and row.get("mode_changed") is False and row.get("ledger_event") == "autotrade.mode_state_readiness_recheck_rejected" and "readiness_recheck_not_ready" in tuple(row.get("blocked_by") or ()) and row.get("would_send_to_broker") is False for row in mode_state_rows),
        "final_apply_skips_after_all_candidates_drained": skipped_result.get("skipped") is True and skipped_result.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and skipped_result.get("command_id") is None and skipped_result.get("record_appended") is False and tuple(skipped_result.get("already_applied_command_ids") or ()) == tuple(sorted(EXPECTED_APPLY_SEQUENCE)) and skipped_result.get("candidate_command_count") == 0,
        "preview_after_drain_is_read_only_skip": preview_after_drain.get("would_apply") is False and preview_after_drain.get("would_reject_by_readiness") is False and preview_after_drain.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and tuple(preview_after_drain.get("already_applied_command_ids") or ()) == tuple(sorted(EXPECTED_APPLY_SEQUENCE)) and preview_after_drain.get("candidate_command_count") == 0 and preview_after_drain.get("read_only") is True,
        "mode_state_summary_latest_is_oldest_after_drain": mode_state_summary.get("latest_source_command_id") == "cmd_cq_oldest_live_request" and mode_state_summary.get("latest_ledger_event") == "autotrade.mode_state_readiness_recheck_rejected" and (mode_state_summary.get("blocked_by_counts") or {}).get("readiness_recheck_not_ready") == 3,
        "command_and_observer_ledgers_not_appended": before_command_count == 3 and after_command_count == before_command_count and observer_count_after == observer_count_before,
        "apply_source_latest_unapplied_one_shot_no_runner_broker": bool(apply_source) and "candidates[-1]" in apply_source and "row.command_id not in already_applied" in apply_source and not any(token in apply_source for token in APPLY_FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CQ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cq_rechecked_apply_sequential_candidate_draining_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "apply_selects_latest_unapplied_candidate_each_run": checks["apply_selects_latest_unapplied_candidate_each_run"],
            "apply_tracks_already_applied_ids_before_each_run": checks["apply_tracks_already_applied_ids_before_each_run"],
            "each_rejection_appends_one_mode_state_record": checks["each_rejection_appends_one_mode_state_record"],
            "mode_state_source_command_ids_follow_apply_sequence": checks["mode_state_source_command_ids_follow_apply_sequence"],
            "mode_state_records_keep_rejection_metadata": checks["mode_state_records_keep_rejection_metadata"],
            "final_apply_skips_after_all_candidates_drained": checks["final_apply_skips_after_all_candidates_drained"],
            "preview_after_drain_is_read_only_skip": checks["preview_after_drain_is_read_only_skip"],
            "mode_state_summary_latest_is_oldest_after_drain": checks["mode_state_summary_latest_is_oldest_after_drain"],
            "command_and_observer_ledgers_not_appended": checks["command_and_observer_ledgers_not_appended"],
            "apply_source_latest_unapplied_one_shot_no_runner_broker": checks["apply_source_latest_unapplied_one_shot_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "expected_apply_sequence": list(EXPECTED_APPLY_SEQUENCE),
        "actual_apply_sequence": list(actual_apply_sequence),
        "actual_mode_state_sequence": list(actual_mode_state_sequence),
        "results": results,
        "skipped_result": skipped_result,
        "preview_after_drain": preview_after_drain,
        "mode_state_rows": mode_state_rows,
        "mode_state_summary": mode_state_summary,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
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
