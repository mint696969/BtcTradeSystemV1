# path: ./tools/test_phase4a_autotrade_milestone_ci_rechecked_apply_result_candidate_context_guard.py
# desc: Guard rechecked apply result surfaces candidate command metadata and persisted readiness note context. Rejection appends one mode_state; no command/observer append, runner, or broker.

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
CANDIDATE_METADATA_FIELDS = (
    "candidate_command_type",
    "candidate_requested_by",
    "candidate_requested_at",
    "candidate_current_mode",
    "candidate_target_mode",
    "candidate_accepted",
    "candidate_blocked_by",
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
EXPECTED_CANDIDATE_BLOCKED_BY = ["ci_candidate_command_blocker"]
EXPECTED_NOTE_BLOCKED_BY = ["observer_run_latest_blocked_for_live_target", "mode_off"]
EXPECTED_OBSERVER_BLOCKED_BY = ["mode_off"]
EXPECTED_WARNINGS = ["candidate_note_persisted_before_apply"]
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
            "observer_latest_run_id": "obs_ci_candidate_note",
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
            "reason_codes": ["guard", "apply_result_candidate_context"],
            "note": readiness_note(),
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_rechecked_apply_result_candidate_context_hot"
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
        write_jsonl(command_path, [command_row("cmd_ci_candidate_live_request")])
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
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    checks = {
        "apply_result_dataclass_has_candidate_metadata_fields": all(field in applier_text for field in CANDIDATE_METADATA_FIELDS),
        "apply_result_dataclass_has_candidate_note_fields": all(field in applier_text for field in CANDIDATE_NOTE_FIELDS),
        "apply_result_surfaces_candidate_command_metadata": result_data.get("command_id") == "cmd_ci_candidate_live_request" and result_data.get("candidate_command_type") == "REQUEST_MODE_CHANGE" and result_data.get("candidate_requested_by") == "operator_ui" and isinstance(result_data.get("candidate_requested_at"), str) and result_data.get("candidate_current_mode") == "ARMED_DRY_RUN" and result_data.get("candidate_target_mode") == "LIVE_MIN_SIZE" and result_data.get("candidate_accepted") is True and tuple(result_data.get("candidate_blocked_by") or ()) == tuple(EXPECTED_CANDIDATE_BLOCKED_BY),
        "apply_result_surfaces_candidate_readiness_note_context": result_data.get("candidate_readiness_note_present") is True and result_data.get("candidate_readiness_ready") is False and result_data.get("candidate_readiness_current_mode") == "ARMED_DRY_RUN" and result_data.get("candidate_readiness_target_mode") == "LIVE_MIN_SIZE" and tuple(result_data.get("candidate_readiness_blocked_by") or ()) == tuple(EXPECTED_NOTE_BLOCKED_BY) and tuple(result_data.get("candidate_readiness_warnings") or ()) == tuple(EXPECTED_WARNINGS) and result_data.get("candidate_readiness_health_state") == "warn",
        "apply_result_surfaces_candidate_observer_note_details": result_data.get("candidate_readiness_observer_latest_run_id") == "obs_ci_candidate_note" and tuple(result_data.get("candidate_readiness_observer_latest_blocked_by") or ()) == tuple(EXPECTED_OBSERVER_BLOCKED_BY) and result_data.get("candidate_readiness_observer_latest_would_send_to_broker") is False and result_data.get("candidate_readiness_observer_latest_bounded") is True,
        "apply_recheck_result_still_separate": result_data.get("readiness") is not None and result_data.get("rejected_by_readiness") is True and result_data.get("readiness_ready") is False and "readiness_recheck_not_ready" in tuple(result_data.get("blocked_by") or ()),
        "apply_rejection_appended_exactly_one_mode_state": before_mode_count == 0 and after_apply_mode_count == 1 and result_data.get("record_appended") is True and result_data.get("mode_state_record") is not None,
        "apply_did_not_append_command_or_observer": before_command_count == 1 and after_apply_command_count == before_command_count and observer_count_after == observer_count_before,
        "apply_no_runner_or_broker_or_command_append": bool(apply_source) and not any(token in apply_source for token in FORBIDDEN_APPLY_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CI: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ci_rechecked_apply_result_candidate_context_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "apply_result_dataclass_has_candidate_metadata_fields": checks["apply_result_dataclass_has_candidate_metadata_fields"],
            "apply_result_dataclass_has_candidate_note_fields": checks["apply_result_dataclass_has_candidate_note_fields"],
            "apply_result_surfaces_candidate_command_metadata": checks["apply_result_surfaces_candidate_command_metadata"],
            "apply_result_surfaces_candidate_readiness_note_context": checks["apply_result_surfaces_candidate_readiness_note_context"],
            "apply_result_surfaces_candidate_observer_note_details": checks["apply_result_surfaces_candidate_observer_note_details"],
            "apply_recheck_result_still_separate": checks["apply_recheck_result_still_separate"],
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
