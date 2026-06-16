# path: ./tools/test_phase4a_autotrade_milestone_cs_rechecked_preview_sequential_candidate_visibility_guard.py
# desc: Guard rechecked preview selects latest unapplied accepted REQUEST_MODE_CHANGE as mode_state source_command_id advances. Preview is read-only; no command/mode/observer append, runner, or broker.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, preview_latest_mode_change_command_apply_with_readiness_recheck, read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
EXPECTED_PREVIEW_SEQUENCE = (
    "cmd_cs_latest_live_request",
    "cmd_cs_middle_live_request",
    "cmd_cs_oldest_live_request",
    None,
)
CANDIDATE_CONTEXT_FIELDS = (
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
            "warnings": ["preview_sequential_candidate_visibility_snapshot"],
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
            "reason_codes": ["guard", "preview_sequential_candidate_visibility", command_id],
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
        "reason_codes": ["guard", "preview_sequential_candidate_visibility", command_id, "readiness_recheck"],
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def run_preview_snapshot(*, mode_state_path: Path, applied_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], int, int]:
    if applied_rows:
        write_jsonl(mode_state_path, applied_rows)
    elif mode_state_path.exists():
        mode_state_path.unlink()
    before_count = len(read_mode_state_records(mode_state_path).rows)
    preview = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
    after_count = len(read_mode_state_records(mode_state_path).rows)
    return preview, before_count, after_count


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_rechecked_preview_sequential_candidate_visibility_hot"
    before_command_count = -1
    after_command_count = -2
    mode_count_before_each: list[int] = []
    mode_count_after_each: list[int] = []
    observer_count_before = 0
    observer_count_after = 0
    previews: list[dict[str, Any]] = []
    final_mode_state_rows: list[dict[str, Any]] = []
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
                command_row("cmd_cs_oldest_live_request", now_z(-30), "cs_oldest_candidate_blocker"),
                command_row("cmd_cs_middle_live_request", now_z(-20), "cs_middle_candidate_blocker"),
                command_row("cmd_cs_latest_live_request", now_z(-10), "cs_latest_candidate_blocker"),
            ],
        )
        applied_latest = mode_state_rejection_row("cmd_cs_latest_live_request", "cs_latest_candidate_blocker")
        applied_middle = mode_state_rejection_row("cmd_cs_middle_live_request", "cs_middle_candidate_blocker")
        applied_oldest = mode_state_rejection_row("cmd_cs_oldest_live_request", "cs_oldest_candidate_blocker")
        scenarios = [
            [],
            [applied_latest],
            [applied_latest, applied_middle],
            [applied_latest, applied_middle, applied_oldest],
        ]
        before_command_count = len(read_command_ledger(command_path))
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        for rows in scenarios:
            preview, before_mode_count_for_preview, after_mode_count_for_preview = run_preview_snapshot(mode_state_path=mode_state_path, applied_rows=rows)
            mode_count_before_each.append(before_mode_count_for_preview)
            previews.append(preview)
            mode_count_after_each.append(after_mode_count_for_preview)
        after_command_count = len(read_command_ledger(command_path))
        final_mode_state_rows = [row.to_dict() for row in read_mode_state_records(mode_state_path).rows]
        observer_count_after = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    actual_preview_sequence = tuple(preview.get("command_id") for preview in previews)
    expected_candidate_counts = (3, 2, 1, 0)
    expected_already_applied = (
        (),
        ("cmd_cs_latest_live_request",),
        ("cmd_cs_latest_live_request", "cmd_cs_middle_live_request"),
        tuple(sorted(("cmd_cs_latest_live_request", "cmd_cs_middle_live_request", "cmd_cs_oldest_live_request"))),
    )
    active_previews = previews[:3]
    drained_preview = previews[3] if len(previews) >= 4 else {}
    checks = {
        "preview_selects_latest_unapplied_candidate_as_applied_ids_advance": actual_preview_sequence == EXPECTED_PREVIEW_SEQUENCE and tuple(preview.get("candidate_command_count") for preview in previews) == expected_candidate_counts,
        "preview_tracks_already_applied_ids": tuple(tuple(preview.get("already_applied_command_ids") or ()) for preview in previews) == expected_already_applied,
        "active_previews_recheck_and_surface_candidate_context": all(preview.get("would_apply") is False and preview.get("would_reject_by_readiness") is True and preview.get("skip_reason") == "readiness_recheck_not_ready" and preview.get("candidate_command_type") == "REQUEST_MODE_CHANGE" and preview.get("candidate_readiness_note_present") is True and all(field in preview for field in CANDIDATE_CONTEXT_FIELDS) for preview in active_previews),
        "drained_preview_is_no_unapplied_read_only_default_context": drained_preview.get("would_apply") is False and drained_preview.get("would_reject_by_readiness") is False and drained_preview.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and drained_preview.get("command_id") is None and drained_preview.get("candidate_command_count") == 0 and drained_preview.get("readiness") is None and drained_preview.get("candidate_readiness_note_present") is False and tuple(drained_preview.get("candidate_blocked_by") or ()) == () and drained_preview.get("read_only") is True,
        "preview_does_not_append_command_mode_or_observer": before_command_count == 3 and after_command_count == before_command_count and mode_count_before_each == mode_count_after_each and observer_count_after == observer_count_before,
        "final_mode_state_rows_preserved": tuple(row.get("source_command_id") for row in final_mode_state_rows) == ("cmd_cs_latest_live_request", "cmd_cs_middle_live_request", "cmd_cs_oldest_live_request"),
        "preview_source_latest_unapplied_read_only_no_runner_broker": bool(preview_source) and "candidates[-1]" in preview_source and "row.command_id not in already_applied" in preview_source and not any(token in preview_source for token in PREVIEW_FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CS: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cs_rechecked_preview_sequential_candidate_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "preview_selects_latest_unapplied_candidate_as_applied_ids_advance": checks["preview_selects_latest_unapplied_candidate_as_applied_ids_advance"],
            "preview_tracks_already_applied_ids": checks["preview_tracks_already_applied_ids"],
            "active_previews_recheck_and_surface_candidate_context": checks["active_previews_recheck_and_surface_candidate_context"],
            "drained_preview_is_no_unapplied_read_only_default_context": checks["drained_preview_is_no_unapplied_read_only_default_context"],
            "preview_does_not_append_command_mode_or_observer": checks["preview_does_not_append_command_mode_or_observer"],
            "final_mode_state_rows_preserved": checks["final_mode_state_rows_preserved"],
            "preview_source_latest_unapplied_read_only_no_runner_broker": checks["preview_source_latest_unapplied_read_only_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "expected_preview_sequence": list(EXPECTED_PREVIEW_SEQUENCE),
        "actual_preview_sequence": list(actual_preview_sequence),
        "previews": previews,
        "mode_count_before_each": mode_count_before_each,
        "mode_count_after_each": mode_count_after_each,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
        "observer_count_before": observer_count_before,
        "observer_count_after": observer_count_after,
        "final_mode_state_rows": final_mode_state_rows,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
