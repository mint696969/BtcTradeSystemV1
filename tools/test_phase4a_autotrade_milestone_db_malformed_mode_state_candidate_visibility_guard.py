# path: ./tools/test_phase4a_autotrade_milestone_db_malformed_mode_state_candidate_visibility_guard.py
# desc: Guard malformed mode_state rows are fail-soft and do not break already-applied candidate filtering for preview/apply.

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

from btcts.autotrade.execution import apply_latest_mode_change_command_once_with_readiness_recheck, default_command_ledger_path, default_mode_state_ledger_path, preview_latest_mode_change_command_apply_with_readiness_recheck, read_command_ledger_rows, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

MODE_STATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
LATEST = "cmd_db_latest_live_request"
MIDDLE = "cmd_db_middle_live_request"
OLDEST = "cmd_db_oldest_live_request"
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
APPLY_FORBIDDEN_TOKENS = tuple(token for token in PREVIEW_FORBIDDEN_TOKENS if token != "append_mode_state_record(")


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
            "warnings": ["malformed_mode_state_candidate_visibility_snapshot"],
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
            "reason_codes": ["guard", "malformed_mode_state_candidate_visibility", command_id],
            "note": readiness_note(command_id),
            "confirmation_required": True,
        },
    }


def mode_state_rejection_row(command_id: str, blocker: str) -> dict[str, Any]:
    return {
        "current_mode": "OFF",
        "previous_mode": "OFF",
        "changed_at": now_z(),
        "source_command_id": command_id,
        "requested_by": "operator_ui",
        "accepted": False,
        "mode_changed": False,
        "reason_codes": ["guard", "malformed_mode_state_candidate_visibility", command_id, "readiness_recheck"],
        "blocked_by": [
            "readiness_recheck_not_ready",
            "mode_transition_not_allowed_or_unconfirmed",
            "runtime_health_blocked",
            "observer_run_missing",
            "observer_run_not_fresh_for_live_target",
            "runtime_health_warnings_present",
            blocker,
        ],
        "ledger_event": "autotrade.mode_state_readiness_recheck_rejected",
        "would_send_to_broker": False,
    }


def write_command_jsonl(path: Path) -> None:
    rows = [
        command_row(OLDEST, now_z(-30), "db_oldest_candidate_blocker"),
        command_row(MIDDLE, now_z(-20), "db_middle_candidate_blocker"),
        command_row(LATEST, now_z(-10), "db_latest_candidate_blocker"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def write_mode_state_with_malformed(path: Path) -> None:
    rows = [
        mode_state_rejection_row(LATEST, "db_latest_candidate_blocker"),
        mode_state_rejection_row(MIDDLE, "db_middle_candidate_blocker"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_malformed_mode_state_candidate_visibility_hot"
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
        write_command_jsonl(command_path)
        write_mode_state_with_malformed(mode_state_path)
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_before = read_mode_state_records(mode_state_path, max_lines=100)
        before_mode_count = len(mode_read_before.rows)
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        mode_summary_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        preview_before_apply = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        apply_result = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        preview_after_apply = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        after_apply_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_after = read_mode_state_records(mode_state_path, max_lines=100)
        after_apply_mode_count = len(mode_read_after.rows)
        mode_summary_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        mode_rows_after = [row.to_dict() for row in mode_read_after.rows]
        observer_count_after = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    read_mode_source = function_source(MODE_STATE_FILE, "read_mode_state_records")
    summarize_mode_source = function_source(MODE_STATE_FILE, "summarize_mode_state")
    applied_ids_source = function_source(APPLIER_FILE, "_applied_command_ids")
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    checks = {
        "mode_state_reader_skips_malformed_but_keeps_valid_rows": before_mode_count == 2 and mode_read_before.skipped_count == 1 and tuple(mode_read_before.error_samples) != (),
        "mode_state_summary_surfaces_skipped_error_and_latest_valid_row": mode_summary_before.get("total_rows") == 2 and mode_summary_before.get("skipped_rows") == 1 and tuple(mode_summary_before.get("error_samples") or ()) != () and mode_summary_before.get("latest_source_command_id") == MIDDLE and mode_summary_before.get("read_only") is True,
        "preview_ignores_malformed_mode_state_and_selects_oldest_unapplied": preview_before_apply.get("command_id") == OLDEST and preview_before_apply.get("candidate_command_count") == 1 and tuple(preview_before_apply.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE))) and preview_before_apply.get("mode_state_read_skipped_count") == 1 and preview_before_apply.get("would_reject_by_readiness") is True,
        "apply_ignores_malformed_mode_state_and_appends_only_oldest_rejection": apply_result.get("command_id") == OLDEST and apply_result.get("candidate_command_count") == 1 and tuple(apply_result.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE))) and apply_result.get("mode_state_read_skipped_count") == 1 and apply_result.get("record_appended") is True and (apply_result.get("mode_state_record") or {}).get("source_command_id") == OLDEST,
        "preview_after_apply_is_drained_despite_malformed_mode_state": preview_after_apply.get("command_id") is None and preview_after_apply.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and preview_after_apply.get("candidate_command_count") == 0 and tuple(preview_after_apply.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE, OLDEST))) and preview_after_apply.get("mode_state_read_skipped_count") == 1,
        "mode_state_after_apply_preserves_skipped_and_appends_one_valid_row": after_apply_mode_count == before_mode_count + 1 == 3 and mode_read_after.skipped_count == 1 and tuple(row.get("source_command_id") for row in mode_rows_after) == (LATEST, MIDDLE, OLDEST) and mode_summary_after.get("latest_source_command_id") == OLDEST and mode_summary_after.get("skipped_rows") == 1,
        "command_and_observer_ledgers_not_appended": after_apply_command_count == before_command_count == 3 and observer_count_after == observer_count_before,
        "mode_state_reader_source_failsoft_and_read_only": bool(read_mode_source) and "try:" in read_mode_source and "skipped += 1" in read_mode_source and "error_samples" in read_mode_source and "append_mode_state_record" not in read_mode_source,
        "mode_state_summary_source_uses_reader_and_read_only": bool(summarize_mode_source) and "read_mode_state_records" in summarize_mode_source and "skipped_rows=read.skipped_count" in summarize_mode_source and "read_only=True" in summarize_mode_source,
        "applier_applied_ids_uses_mode_state_reader_skipped_count": bool(applied_ids_source) and "read_mode_state_records" in applied_ids_source and "read.skipped_count" in applied_ids_source,
        "preview_apply_source_surfaces_mode_state_skipped_counts_no_runner_broker": bool(preview_source) and bool(apply_source) and "mode_state_read_skipped_count=state_skipped" in preview_source and "mode_state_read_skipped_count=state_skipped" in apply_source and not any(token in preview_source for token in PREVIEW_FORBIDDEN_TOKENS) and not any(token in apply_source for token in APPLY_FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DB: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_db_malformed_mode_state_candidate_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_state_reader_skips_malformed_but_keeps_valid_rows": checks["mode_state_reader_skips_malformed_but_keeps_valid_rows"],
            "mode_state_summary_surfaces_skipped_error_and_latest_valid_row": checks["mode_state_summary_surfaces_skipped_error_and_latest_valid_row"],
            "preview_ignores_malformed_mode_state_and_selects_oldest_unapplied": checks["preview_ignores_malformed_mode_state_and_selects_oldest_unapplied"],
            "apply_ignores_malformed_mode_state_and_appends_only_oldest_rejection": checks["apply_ignores_malformed_mode_state_and_appends_only_oldest_rejection"],
            "preview_after_apply_is_drained_despite_malformed_mode_state": checks["preview_after_apply_is_drained_despite_malformed_mode_state"],
            "mode_state_after_apply_preserves_skipped_and_appends_one_valid_row": checks["mode_state_after_apply_preserves_skipped_and_appends_one_valid_row"],
            "command_and_observer_ledgers_not_appended": checks["command_and_observer_ledgers_not_appended"],
            "mode_state_reader_source_failsoft_and_read_only": checks["mode_state_reader_source_failsoft_and_read_only"],
            "mode_state_summary_source_uses_reader_and_read_only": checks["mode_state_summary_source_uses_reader_and_read_only"],
            "applier_applied_ids_uses_mode_state_reader_skipped_count": checks["applier_applied_ids_uses_mode_state_reader_skipped_count"],
            "preview_apply_source_surfaces_mode_state_skipped_counts_no_runner_broker": checks["preview_apply_source_surfaces_mode_state_skipped_counts_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "mode_read_before": mode_read_before.to_dict(),
        "mode_summary_before": mode_summary_before,
        "preview_before_apply": preview_before_apply,
        "apply_result": apply_result,
        "preview_after_apply": preview_after_apply,
        "mode_read_after": mode_read_after.to_dict(),
        "mode_summary_after": mode_summary_after,
        "mode_rows_after": mode_rows_after,
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
