# path: ./tools/test_phase4a_autotrade_milestone_dl_accepted_mode_change_recheck_malformed_decision_ledgers_guard.py
# desc: Guard accepted REQUEST_MODE_CHANGE is rechecked against malformed decision-ledger health and appends only a mode_state rejection when not ready.

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
    preview_latest_mode_change_command_apply_with_readiness_recheck,
    read_command_ledger_rows,
    read_mode_state_records,
    summarize_command_ledger,
    summarize_mode_state,
)
from btcts.autotrade.health import build_autotrade_runtime_health_snapshot  # noqa: E402
from btcts.autotrade.ledger.decision_status import default_shadow_decision_status_path, summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_outcome_status import summarize_forecast_outcome_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_resolution import default_forecast_outcome_ledger_path  # noqa: E402
from btcts.autotrade.ledger.observer_run_status import default_observer_run_ledger_path, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
HEALTH_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/health.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
COMMAND_ID = "cmd_dl_accepted_live_request"
STATE_SOURCE = "cmd_dl_state_armed_dry_run"
FORBIDDEN_PREVIEW_TOKENS = (
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
FORBIDDEN_APPLY_TOKENS = tuple(token for token in FORBIDDEN_PREVIEW_TOKENS if token != "append_mode_state_record(")


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def readiness_note_ready(command_id: str) -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": True,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": [],
            "warnings": [],
            "health_state": "ok",
            "observer_run_fresh": True,
            "observer_latest_run_id": f"obs_{command_id}_preflight_ready",
            "observer_latest_blocked_by": [],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "mode_changed": False,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row() -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": COMMAND_ID,
        "accepted": True,
        "blocked_by": [],
        "command": {
            "command_id": COMMAND_ID,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-15),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "accepted_mode_change_recheck_malformed_decision_ledgers", COMMAND_ID],
            "note": readiness_note_ready(COMMAND_ID),
            "confirmation_required": True,
        },
    }


def mode_state_armed_row() -> dict[str, Any]:
    return {
        "current_mode": "ARMED_DRY_RUN",
        "previous_mode": "PAPER_OR_REPLAY",
        "changed_at": now_z(-20),
        "source_command_id": STATE_SOURCE,
        "requested_by": "operator_ui",
        "accepted": True,
        "mode_changed": True,
        "reason_codes": ["guard", "accepted_mode_change_recheck_malformed_decision_ledgers", STATE_SOURCE],
        "blocked_by": [],
        "ledger_event": "autotrade.mode_state_recorded",
        "would_send_to_broker": False,
    }


def observer_row(run_id: str, offset_seconds: int, blocker: str = "") -> dict[str, Any]:
    return {
        "run_id": run_id,
        "started_at": now_z(offset_seconds - 1),
        "finished_at": now_z(offset_seconds),
        "requested_cycles": 1,
        "completed_cycles": 1,
        "appended_shadow_decision_count": 1,
        "appended_forecast_outcome_count": 1,
        "duplicate_snapshot_skipped_count": 0,
        "skip_duplicate_snapshot": True,
        "blocked_by": [blocker] if blocker else [],
        "would_send_to_broker": False,
        "bounded": True,
        "source": "autotrade.observer_cycle_bounded",
    }


def shadow_row(decision_id: str, action: str, blocker: str = "") -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": f"fcst_{decision_id}", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": action},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": action,
        "reason_codes": ["guard", "accepted_mode_change_recheck_malformed_decision_ledgers", decision_id],
        "blocked_by": [blocker] if blocker else [],
        "would_order": None,
    }


def outcome_row(forecast_id: str, result: str, confidence: str = "medium") -> dict[str, Any]:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": f"snap_{forecast_id}",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": f"actual_{forecast_id}",
        "forecast_direction": "down",
        "forecast_confidence": confidence,
        "expected_change": "strengthen_sell",
        "drivers": ["sell_pressure_or_ground"],
        "blocked_by": [],
        "result": result,
        "direction_hit": result == "hit",
        "change_type_hit": result == "hit",
        "divergence_reasons": [] if result == "hit" else ["direction_mismatch"],
    }


def write_command_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "{not-json\n"
    text += json.dumps(command_row(), ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_mode_state_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "{not-json\n"
    text += json.dumps(mode_state_armed_row(), ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_jsonl_with_malformed(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_accepted_mode_change_recheck_malformed_decision_ledgers_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = default_observer_run_ledger_path(ensure=True)
        shadow_path = default_shadow_decision_status_path(ensure=True)
        outcome_path = default_forecast_outcome_ledger_path(ensure=True)
        for path in (command_path, mode_state_path, observer_path, shadow_path, outcome_path):
            if path.exists():
                path.unlink()
        write_command_ledger(command_path)
        write_mode_state_ledger(mode_state_path)
        write_jsonl_with_malformed(observer_path, [observer_row("obs_dl_old", -20), observer_row("obs_dl_latest", -5, "dl_latest_observer_blocker")])
        write_jsonl_with_malformed(shadow_path, [shadow_row("dl_old", "WAIT", "dl_old_shadow_blocker"), shadow_row("dl_latest", "WAIT", "dl_latest_shadow_blocker")])
        write_jsonl_with_malformed(outcome_path, [outcome_row("fcst_dl_old", "hit", "medium"), outcome_row("fcst_dl_latest", "miss", "high")])
        before_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": len(observer_path.read_text(encoding="utf-8").splitlines()),
            "shadow": len(shadow_path.read_text(encoding="utf-8").splitlines()),
            "outcome": len(outcome_path.read_text(encoding="utf-8").splitlines()),
        }
        command_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        mode_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        observer_before = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_before = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_before = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        health_before = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=120, max_lines=100).to_dict()
        preview_before = preview_latest_mode_change_command_apply_with_readiness_recheck(command_path=command_path, mode_state_path=mode_state_path, max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        apply_result = apply_latest_mode_change_command_once_with_readiness_recheck(command_path=command_path, mode_state_path=mode_state_path, max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        preview_after = preview_latest_mode_change_command_apply_with_readiness_recheck(command_path=command_path, mode_state_path=mode_state_path, max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        command_after = summarize_command_ledger(command_path, max_lines=100).to_dict()
        command_read_after = read_command_ledger_rows(command_path, max_lines=100).to_dict()
        mode_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        mode_read_after = read_mode_state_records(mode_state_path, max_lines=100).to_dict()
        observer_after = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_after = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_after = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        after_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": len(observer_path.read_text(encoding="utf-8").splitlines()),
            "shadow": len(shadow_path.read_text(encoding="utf-8").splitlines()),
            "outcome": len(outcome_path.read_text(encoding="utf-8").splitlines()),
        }
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    health_warnings = tuple(health_before.get("warnings") or ())
    apply_blocked = tuple(apply_result.get("blocked_by") or ())
    record = apply_result.get("mode_state_record") if isinstance(apply_result.get("mode_state_record"), dict) else {}
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    rejected_record_source = function_source(APPLIER_FILE, "_readiness_rejected_mode_state_record")
    health_source = function_source(HEALTH_FILE, "build_autotrade_runtime_health_snapshot")
    checks = {
        "fixture_has_accepted_candidate_armed_state_and_malformed_health_ledgers": command_before.get("total_rows") == 1 and command_before.get("skipped_rows") == 1 and command_before.get("latest_command_id") == COMMAND_ID and command_before.get("latest_accepted") is True and mode_before.get("current_mode") == "ARMED_DRY_RUN" and mode_before.get("skipped_rows") == 1 and observer_before.get("skipped_rows") == 1 and shadow_before.get("skipped_rows") == 1 and outcome_before.get("total_rows") == 2,
        "runtime_health_warns_from_malformed_decision_ledgers_and_latest_observer_blocker": health_before.get("observer_runs", {}).get("latest_run_id") == "obs_dl_latest" and tuple(health_before.get("observer_runs", {}).get("latest_blocked_by") or ()) == ("dl_latest_observer_blocker",) and "observer_run_ledger_has_skipped_rows" in health_warnings and "shadow_decision_ledger_has_skipped_rows" in health_warnings and health_before.get("would_send_to_broker") is False and health_before.get("read_only") is True,
        "preview_selects_accepted_candidate_but_rejects_by_recheck_health": preview_before.get("command_id") == COMMAND_ID and preview_before.get("candidate_command_count") == 1 and preview_before.get("candidate_accepted") is True and preview_before.get("candidate_readiness_note_present") is True and preview_before.get("candidate_readiness_ready") is True and preview_before.get("would_apply") is False and preview_before.get("would_reject_by_readiness") is True and preview_before.get("skip_reason") == "readiness_recheck_not_ready" and "dl_latest_observer_blocker" in tuple(preview_before.get("blocked_by") or ()) and preview_before.get("command_read_skipped_count") == 1 and preview_before.get("mode_state_read_skipped_count") == 1,
        "apply_appends_one_mode_state_rejection_only": apply_result.get("applied") is False and apply_result.get("skipped") is False and apply_result.get("rejected_by_readiness") is True and apply_result.get("record_appended") is True and apply_result.get("command_id") == COMMAND_ID and apply_result.get("candidate_readiness_ready") is True and apply_result.get("readiness_ready") is False and "readiness_recheck_not_ready" in apply_blocked and "dl_latest_observer_blocker" in apply_blocked and record.get("source_command_id") == COMMAND_ID and record.get("accepted") is False and record.get("mode_changed") is False and record.get("ledger_event") == "autotrade.mode_state_readiness_recheck_rejected" and record.get("would_send_to_broker") is False,
        "only_mode_state_line_count_increased_by_one": after_line_counts == {"command": before_line_counts["command"], "mode_state": before_line_counts["mode_state"] + 1, "observer": before_line_counts["observer"], "shadow": before_line_counts["shadow"], "outcome": before_line_counts["outcome"]},
        "command_and_decision_summaries_unchanged_after_apply": command_after == command_before and command_read_after.get("skipped_count") == 1 and observer_after == observer_before and shadow_after == shadow_before and outcome_after == outcome_before,
        "mode_state_after_apply_marks_command_applied_and_preserves_skip": mode_after.get("total_rows") == 2 and mode_after.get("skipped_rows") == 1 and mode_after.get("latest_source_command_id") == COMMAND_ID and mode_after.get("latest_accepted") is False and mode_after.get("current_mode") == "ARMED_DRY_RUN" and mode_read_after.get("skipped_count") == 1,
        "preview_after_apply_is_drained_because_rejection_marks_source_command_id": preview_after.get("would_apply") is False and preview_after.get("would_reject_by_readiness") is False and preview_after.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and preview_after.get("command_id") is None and preview_after.get("candidate_command_count") == 0 and COMMAND_ID in tuple(preview_after.get("already_applied_command_ids") or ()) and preview_after.get("command_read_skipped_count") == 1 and preview_after.get("mode_state_read_skipped_count") == 1,
        "preview_source_readonly_no_append_runner_broker": bool(preview_source) and "evaluate_autotrade_live_readiness" in preview_source and not any(token in preview_source for token in FORBIDDEN_PREVIEW_TOKENS),
        "apply_source_rechecks_appends_mode_state_only_no_broker": bool(apply_source) and "evaluate_autotrade_live_readiness" in apply_source and "_readiness_rejected_mode_state_record" in apply_source and "append_mode_state_record" in apply_source and not any(token in apply_source for token in FORBIDDEN_APPLY_TOKENS),
        "rejection_record_and_health_sources_are_readonly_no_broker": bool(rejected_record_source) and "would_send_to_broker=False" in rejected_record_source and bool(health_source) and "observer_run_ledger_has_skipped_rows" in health_source and "shadow_decision_ledger_has_skipped_rows" in health_source and "would_send_to_broker=False" in health_source,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DL: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dl_accepted_mode_change_recheck_malformed_decision_ledgers_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "fixture_has_accepted_candidate_armed_state_and_malformed_health_ledgers": checks["fixture_has_accepted_candidate_armed_state_and_malformed_health_ledgers"],
            "runtime_health_warns_from_malformed_decision_ledgers_and_latest_observer_blocker": checks["runtime_health_warns_from_malformed_decision_ledgers_and_latest_observer_blocker"],
            "preview_selects_accepted_candidate_but_rejects_by_recheck_health": checks["preview_selects_accepted_candidate_but_rejects_by_recheck_health"],
            "apply_appends_one_mode_state_rejection_only": checks["apply_appends_one_mode_state_rejection_only"],
            "only_mode_state_line_count_increased_by_one": checks["only_mode_state_line_count_increased_by_one"],
            "command_and_decision_summaries_unchanged_after_apply": checks["command_and_decision_summaries_unchanged_after_apply"],
            "mode_state_after_apply_marks_command_applied_and_preserves_skip": checks["mode_state_after_apply_marks_command_applied_and_preserves_skip"],
            "preview_after_apply_is_drained_because_rejection_marks_source_command_id": checks["preview_after_apply_is_drained_because_rejection_marks_source_command_id"],
            "preview_source_readonly_no_append_runner_broker": checks["preview_source_readonly_no_append_runner_broker"],
            "apply_source_rechecks_appends_mode_state_only_no_broker": checks["apply_source_rechecks_appends_mode_state_only_no_broker"],
            "rejection_record_and_health_sources_are_readonly_no_broker": checks["rejection_record_and_health_sources_are_readonly_no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "command_before": command_before,
        "mode_before": mode_before,
        "observer_before": observer_before,
        "shadow_before": shadow_before,
        "outcome_before": outcome_before,
        "health_before": health_before,
        "preview_before": preview_before,
        "apply_result": apply_result,
        "preview_after": preview_after,
        "command_after": command_after,
        "mode_after": mode_after,
        "mode_read_after": mode_read_after,
        "observer_after": observer_after,
        "shadow_after": shadow_after,
        "outcome_after": outcome_after,
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
