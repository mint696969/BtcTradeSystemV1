# path: ./tools/test_phase4a_autotrade_milestone_dk_rejected_mode_change_not_apply_candidate_guard.py
# desc: Guard rejected REQUEST_MODE_CHANGE rows are never apply candidates, even with malformed command/mode_state rows.

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

from btcts.autotrade.execution import (  # noqa: E402
    apply_latest_mode_change_command_once_with_readiness_recheck,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    preview_latest_mode_change_command_apply,
    preview_latest_mode_change_command_apply_with_readiness_recheck,
    read_command_ledger_rows,
    read_mode_state_records,
    summarize_command_ledger,
    summarize_mode_state,
)
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
COMMAND_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
APPLIED = "cmd_dk_accepted_already_applied"
REJECTED = "cmd_dk_rejected_latest_mode_change"
FORBIDDEN_READ_ONLY_PREVIEW_TOKENS = (
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
FORBIDDEN_APPLY_TOKENS = tuple(token for token in FORBIDDEN_READ_ONLY_PREVIEW_TOKENS if token != "append_mode_state_record(")


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def readiness_note(command_id: str, *, ready: bool) -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": ready,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": [] if ready else ["runtime_health_warnings_present", f"{command_id}_rejected_blocker"],
            "warnings": [] if ready else ["rejected_mode_change_not_apply_candidate_snapshot"],
            "health_state": "ok" if ready else "warn",
            "observer_run_fresh": True,
            "observer_latest_run_id": f"obs_{command_id}",
            "observer_latest_blocked_by": [] if ready else [f"{command_id}_observer_blocker"],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "mode_changed": False,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(command_id: str, *, accepted: bool, requested_at: str, blocker: str = "") -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": [] if accepted else ["readiness_preflight_not_ready", blocker],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": requested_at,
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "rejected_mode_change_not_apply_candidate", command_id],
            "note": readiness_note(command_id, ready=accepted),
            "confirmation_required": True,
        },
    }


def mode_state_row(source_command_id: str) -> dict[str, Any]:
    return {
        "current_mode": "OFF",
        "previous_mode": "OFF",
        "changed_at": now_z(-10),
        "source_command_id": source_command_id,
        "requested_by": "operator_ui",
        "accepted": False,
        "mode_changed": False,
        "reason_codes": ["guard", "rejected_mode_change_not_apply_candidate", source_command_id, "already_applied"],
        "blocked_by": ["readiness_recheck_not_ready"],
        "ledger_event": "autotrade.mode_state_readiness_recheck_rejected",
        "would_send_to_broker": False,
    }


def write_command_ledger(path: Path) -> None:
    rows = [
        command_row(APPLIED, accepted=True, requested_at=now_z(-30)),
        command_row(REJECTED, accepted=False, requested_at=now_z(-5), blocker="dk_rejected_latest_blocker"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_mode_state_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(mode_state_row(APPLIED), ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_rejected_mode_change_not_apply_candidate_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
        for path in (command_path, mode_state_path, observer_path):
            if path.exists():
                path.unlink()
        write_command_ledger(command_path)
        write_mode_state_ledger(mode_state_path)
        before_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines()),
        }
        command_read_before = read_command_ledger_rows(command_path, max_lines=100).to_dict()
        command_summary_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        mode_read_before = read_mode_state_records(mode_state_path, max_lines=100).to_dict()
        mode_summary_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        legacy_preview = preview_latest_mode_change_command_apply(command_path=command_path, mode_state_path=mode_state_path, max_lines=100).to_dict()
        readiness_preview = preview_latest_mode_change_command_apply_with_readiness_recheck(command_path=command_path, mode_state_path=mode_state_path, max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        readiness_apply = apply_latest_mode_change_command_once_with_readiness_recheck(command_path=command_path, mode_state_path=mode_state_path, max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        command_read_after = read_command_ledger_rows(command_path, max_lines=100).to_dict()
        command_summary_after = summarize_command_ledger(command_path, max_lines=100).to_dict()
        mode_read_after = read_mode_state_records(mode_state_path, max_lines=100).to_dict()
        mode_summary_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        after_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines()),
        }
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    rejected_row = (command_read_before.get("rows") or [])[-1]
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    legacy_preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    command_read_source = function_source(COMMAND_STATUS_FILE, "read_command_ledger_rows")
    checks = {
        "fixture_has_accepted_applied_and_rejected_latest_with_malformed_rows": command_summary_before.get("total_rows") == 2 and command_summary_before.get("skipped_rows") == 1 and command_summary_before.get("latest_command_id") == REJECTED and command_summary_before.get("latest_accepted") is False and mode_summary_before.get("total_rows") == 1 and mode_summary_before.get("skipped_rows") == 1 and tuple(mode_read_before.get("rows") or [{}])[0].get("source_command_id") == APPLIED,
        "legacy_preview_ignores_rejected_latest_and_has_no_candidate": legacy_preview.get("would_apply") is False and legacy_preview.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and legacy_preview.get("command_id") is None and legacy_preview.get("candidate_command_count") == 0 and tuple(legacy_preview.get("already_applied_command_ids") or ()) == (APPLIED,) and legacy_preview.get("command_read_skipped_count") == 1 and legacy_preview.get("mode_state_read_skipped_count") == 1,
        "readiness_preview_ignores_rejected_latest_and_has_no_candidate": readiness_preview.get("would_apply") is False and readiness_preview.get("would_reject_by_readiness") is False and readiness_preview.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and readiness_preview.get("command_id") is None and readiness_preview.get("candidate_command_count") == 0 and tuple(readiness_preview.get("already_applied_command_ids") or ()) == (APPLIED,) and readiness_preview.get("command_read_skipped_count") == 1 and readiness_preview.get("mode_state_read_skipped_count") == 1 and readiness_preview.get("readiness") is None,
        "readiness_apply_ignores_rejected_latest_and_appends_nothing": readiness_apply.get("applied") is False and readiness_apply.get("skipped") is True and readiness_apply.get("rejected_by_readiness") is False and readiness_apply.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and readiness_apply.get("command_id") is None and readiness_apply.get("candidate_command_count") == 0 and readiness_apply.get("record_appended") is False and readiness_apply.get("mode_state_record") is None,
        "ledgers_unchanged_after_apply_skip": after_line_counts == before_line_counts == {"command": 3, "mode_state": 2, "observer": 0} and command_read_after == command_read_before and command_summary_after == command_summary_before and mode_read_after == mode_read_before and mode_summary_after == mode_summary_before,
        "rejected_row_readiness_note_is_visible_but_not_candidate": rejected_row.get("accepted") is False and (rejected_row.get("command") or {}).get("command_type") == "REQUEST_MODE_CHANGE" and command_summary_before.get("latest_mode_change_readiness_command_id") == REJECTED and command_summary_before.get("latest_mode_change_readiness_accepted") is False and command_summary_before.get("latest_mode_change_readiness_ready") is False,
        "candidate_filters_require_accepted_request_mode_change_and_not_applied": all(bool(source) and "if row.accepted" in source and "row.command.command_type == CommandType.REQUEST_MODE_CHANGE" in source and "row.command_id not in already_applied" in source for source in (legacy_preview_source, preview_source, apply_source)),
        "preview_sources_are_readonly_no_append_runner_broker": bool(legacy_preview_source) and bool(preview_source) and not any(token in legacy_preview_source for token in FORBIDDEN_READ_ONLY_PREVIEW_TOKENS) and not any(token in preview_source for token in FORBIDDEN_READ_ONLY_PREVIEW_TOKENS),
        "apply_source_no_command_observer_broker_and_no_candidate_path_skips": bool(apply_source) and "skip_reason=\"no_unapplied_accepted_mode_change_command\"" in apply_source and "record_appended=False" in apply_source and not any(token in apply_source for token in FORBIDDEN_APPLY_TOKENS),
        "command_reader_failsoft_surfaces_skipped_rows": bool(command_read_source) and "skipped += 1" in command_read_source and "error_samples" in command_read_source,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DK: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dk_rejected_mode_change_not_apply_candidate_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "fixture_has_accepted_applied_and_rejected_latest_with_malformed_rows": checks["fixture_has_accepted_applied_and_rejected_latest_with_malformed_rows"],
            "legacy_preview_ignores_rejected_latest_and_has_no_candidate": checks["legacy_preview_ignores_rejected_latest_and_has_no_candidate"],
            "readiness_preview_ignores_rejected_latest_and_has_no_candidate": checks["readiness_preview_ignores_rejected_latest_and_has_no_candidate"],
            "readiness_apply_ignores_rejected_latest_and_appends_nothing": checks["readiness_apply_ignores_rejected_latest_and_appends_nothing"],
            "ledgers_unchanged_after_apply_skip": checks["ledgers_unchanged_after_apply_skip"],
            "rejected_row_readiness_note_is_visible_but_not_candidate": checks["rejected_row_readiness_note_is_visible_but_not_candidate"],
            "candidate_filters_require_accepted_request_mode_change_and_not_applied": checks["candidate_filters_require_accepted_request_mode_change_and_not_applied"],
            "preview_sources_are_readonly_no_append_runner_broker": checks["preview_sources_are_readonly_no_append_runner_broker"],
            "apply_source_no_command_observer_broker_and_no_candidate_path_skips": checks["apply_source_no_command_observer_broker_and_no_candidate_path_skips"],
            "command_reader_failsoft_surfaces_skipped_rows": checks["command_reader_failsoft_surfaces_skipped_rows"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "command_read_before": command_read_before,
        "command_summary_before": command_summary_before,
        "mode_read_before": mode_read_before,
        "mode_summary_before": mode_summary_before,
        "legacy_preview": legacy_preview,
        "readiness_preview": readiness_preview,
        "readiness_apply": readiness_apply,
        "command_read_after": command_read_after,
        "command_summary_after": command_summary_after,
        "mode_read_after": mode_read_after,
        "mode_summary_after": mode_summary_after,
        "before_line_counts": before_line_counts,
        "after_line_counts": after_line_counts,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
