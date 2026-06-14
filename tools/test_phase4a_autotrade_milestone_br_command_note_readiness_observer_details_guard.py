# path: ./tools/test_phase4a_autotrade_milestone_br_command_note_readiness_observer_details_guard.py
# desc: Guard mode-change command ledger note carries readiness observer latest blocked details. Existing command append only; no mode/observer append, no runner/broker.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    build_mode_change_command_request_record,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    read_command_ledger,
    read_mode_state_records,
    submit_mode_change_command_request,
)
from btcts.autotrade.ledger import ObserverRunRecord, append_observer_run_record, default_observer_run_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

TARGET_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_change_request.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
NOTE_FIELDS = (
    "observer_latest_run_id",
    "observer_latest_blocked_by",
    "observer_latest_would_send_to_broker",
    "observer_latest_bounded",
)
FORBIDDEN_TOKENS = (
    "append_mode_state_record",
    "append_observer_run_record",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
    "streamlit",
    "btcts.apps.operator_ui",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)
EXPECTED_BLOCKED_BY = (
    "mode_off",
    "mode_runtime_gate_blocked_shadow_decision_append",
    "mode_runtime_gate_blocked_forecast_outcome_resolution",
)


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def parse_note(record: Any) -> dict[str, Any]:
    return json.loads(record.command.note)


def seed_observer(path: Path) -> None:
    if path.exists():
        path.unlink()
    z = now_z()
    append_observer_run_record(
        path,
        ObserverRunRecord(
            run_id="obs_br_blocked_off",
            started_at=z,
            finished_at=z,
            requested_cycles=2,
            completed_cycles=2,
            appended_shadow_decision_count=0,
            appended_forecast_outcome_count=0,
            duplicate_snapshot_skipped_count=0,
            skip_duplicate_snapshot=True,
            blocked_by=EXPECTED_BLOCKED_BY,
            would_send_to_broker=False,
            bounded=True,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_command_note_readiness_observer_details_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = default_observer_run_ledger_path(ensure=True)
        for path in (command_path, mode_state_path):
            if path.exists():
                path.unlink()
        seed_observer(observer_path)
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        before_observer_count = len(observer_path.read_text(encoding="utf-8").splitlines())
        built_record, built_readiness = build_mode_change_command_request_record(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            requested_by="guard",
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=999999999,
            max_lines=100,
        )
        built_note = parse_note(built_record)
        after_build_command_count = len(read_command_ledger(command_path))
        submit_result = submit_mode_change_command_request(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            requested_by="guard",
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=999999999,
            max_lines=100,
            path=command_path,
        )
        submitted_note = parse_note(submit_result.command_record)
        after_command_count = len(read_command_ledger(command_path))
        after_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        after_observer_count = len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    source = function_source(TARGET_FILE, "_readiness_note")
    text = TARGET_FILE.read_text(encoding="utf-8")
    checks = {
        "readiness_note_source_has_observer_latest_fields": all(field in source for field in NOTE_FIELDS),
        "build_record_note_has_observer_details": built_note.get("observer_latest_run_id") == "obs_br_blocked_off" and tuple(built_note.get("observer_latest_blocked_by") or ()) == EXPECTED_BLOCKED_BY and built_note.get("observer_latest_would_send_to_broker") is False and built_note.get("observer_latest_bounded") is True,
        "submitted_command_note_has_observer_details": submitted_note.get("observer_latest_run_id") == "obs_br_blocked_off" and tuple(submitted_note.get("observer_latest_blocked_by") or ()) == EXPECTED_BLOCKED_BY and submitted_note.get("observer_latest_would_send_to_broker") is False and submitted_note.get("observer_latest_bounded") is True,
        "note_preserves_readiness_blockers": "observer_run_latest_blocked_for_live_target" in tuple(submitted_note.get("blocked_by") or ()) and "mode_off" in tuple(submitted_note.get("blocked_by") or ()),
        "build_record_does_not_append_command": before_command_count == 0 and after_build_command_count == before_command_count,
        "submit_appends_exactly_one_command": after_command_count == before_command_count + 1 and submit_result.appended is True and submit_result.accepted is False,
        "mode_state_not_appended": before_mode_count == 0 and after_mode_count == before_mode_count,
        "observer_run_not_appended_by_request": before_observer_count == 1 and after_observer_count == before_observer_count,
        "no_ui_runner_applier_or_broker": bool(source) and not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BR: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_br_command_note_readiness_observer_details_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "readiness_note_source_has_observer_latest_fields": checks["readiness_note_source_has_observer_latest_fields"],
            "build_record_note_has_observer_details": checks["build_record_note_has_observer_details"],
            "submitted_command_note_has_observer_details": checks["submitted_command_note_has_observer_details"],
            "note_preserves_readiness_blockers": checks["note_preserves_readiness_blockers"],
            "build_record_does_not_append_command": checks["build_record_does_not_append_command"],
            "submit_appends_exactly_one_command": checks["submit_appends_exactly_one_command"],
            "mode_state_not_appended": checks["mode_state_not_appended"],
            "observer_run_not_appended_by_request": checks["observer_run_not_appended_by_request"],
            "no_ui_runner_applier_or_broker": checks["no_ui_runner_applier_or_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "built_note": built_note,
        "submitted_note": submitted_note,
        "built_readiness_ready": built_readiness.ready,
        "submit_result": submit_result.to_dict(),
        "before_command_count": before_command_count,
        "after_build_command_count": after_build_command_count,
        "after_command_count": after_command_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
        "before_observer_count": before_observer_count,
        "after_observer_count": after_observer_count,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
