# path: ./tools/test_phase4a_autotrade_milestone_bn_mode_change_applier_rejects_latest_observer_blocked_guard.py
# desc: Guard mode-change applier readiness recheck rejects live target when latest observer_run is fresh but blocked. No broker.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    CommandRequest,
    CommandType,
    append_mode_state_record,
    current_mode_state,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    read_mode_state_records,
    validate_and_append_command,
)
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.execution.mode_command_applier import (  # noqa: E402
    apply_latest_mode_change_command_once_with_readiness_recheck,
    preview_latest_mode_change_command_apply_with_readiness_recheck,
)
from btcts.autotrade.ledger import ObserverRunRecord, append_observer_run_record, default_observer_run_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
READINESS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/readiness.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
    "streamlit",
    "btcts.apps.operator_ui",
)


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def seed_mode_state(path: Path, mode: AutoTradeMode) -> None:
    if path.exists():
        path.unlink()
    append_mode_state_record(
        path,
        ModeStateRecord(
            current_mode=mode,
            previous_mode=AutoTradeMode.PAPER_OR_REPLAY,
            changed_at=now_z(),
            source_command_id="cmd_bn_seed_armed",
            requested_by="guard",
            accepted=True,
            mode_changed=True,
            reason_codes=("guard", "seed_armed"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def seed_mode_change_command(path: Path) -> None:
    if path.exists():
        path.unlink()
    validate_and_append_command(
        path,
        CommandRequest(
            command_id="cmd_bn_live_min_size_from_armed",
            command_type=CommandType.REQUEST_MODE_CHANGE,
            requested_by="guard",
            requested_at=now_z(),
            current_mode=AutoTradeMode.ARMED_DRY_RUN.value,
            target=AutoTradeMode.LIVE_MIN_SIZE.value,
            confirmation=True,
            reason_codes=("guard", "live_readiness_recheck_latest_observer_blocked"),
            note="guard only",
        ),
    )


def seed_blocked_observer(path: Path) -> None:
    if path.exists():
        path.unlink()
    z = now_z()
    append_observer_run_record(
        path,
        ObserverRunRecord(
            run_id="obs_bn_blocked_off",
            started_at=z,
            finished_at=z,
            requested_cycles=2,
            completed_cycles=2,
            appended_shadow_decision_count=0,
            appended_forecast_outcome_count=0,
            duplicate_snapshot_skipped_count=0,
            skip_duplicate_snapshot=True,
            blocked_by=("mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution"),
            would_send_to_broker=False,
            bounded=True,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_change_applier_latest_observer_blocked_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = default_observer_run_ledger_path(ensure=True)
        seed_mode_state(mode_state_path, AutoTradeMode.ARMED_DRY_RUN)
        seed_mode_change_command(command_path)
        seed_blocked_observer(observer_path)
        before_mode_rows = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        before_observer_rows = len(observer_path.read_text(encoding="utf-8").splitlines())
        preview = preview_latest_mode_change_command_apply_with_readiness_recheck(
            max_lines=100,
            max_observer_run_age_sec=999999999,
            allow_warnings=True,
        )
        after_preview_mode_rows = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        apply_result = apply_latest_mode_change_command_once_with_readiness_recheck(
            max_lines=100,
            max_observer_run_age_sec=999999999,
            allow_warnings=True,
        )
        after_apply_read = read_mode_state_records(mode_state_path, max_lines=100)
        after_mode_rows = len(after_apply_read.rows)
        after_observer_rows = len(observer_path.read_text(encoding="utf-8").splitlines())
        latest_mode = current_mode_state(mode_state_path, max_lines=100)
        second_apply = apply_latest_mode_change_command_once_with_readiness_recheck(
            max_lines=100,
            max_observer_run_age_sec=999999999,
            allow_warnings=True,
        )
        after_second_rows = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    applier_text = APPLIER_FILE.read_text(encoding="utf-8")
    readiness_source = function_source(READINESS_FILE, "evaluate_autotrade_live_readiness")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    combined_text = applier_text + "\n" + READINESS_FILE.read_text(encoding="utf-8")
    expected_blockers = (
        "readiness_recheck_not_ready",
        "observer_run_latest_blocked_for_live_target",
        "mode_off",
        "mode_runtime_gate_blocked_shadow_decision_append",
        "mode_runtime_gate_blocked_forecast_outcome_resolution",
    )
    checks = {
        "preview_rejects_live_target_on_latest_observer_blocked": preview.would_apply is False and preview.would_reject_by_readiness is True and all(item in preview.blocked_by for item in expected_blockers),
        "preview_is_read_only_no_mode_state_append": before_mode_rows == 1 and after_preview_mode_rows == before_mode_rows,
        "apply_rejects_and_appends_rejected_mode_state": apply_result.applied is False and apply_result.rejected_by_readiness is True and apply_result.record_appended is True and after_mode_rows == before_mode_rows + 1,
        "rejected_record_carries_latest_observer_blockers": apply_result.mode_state_record is not None and apply_result.mode_state_record.accepted is False and apply_result.mode_state_record.mode_changed is False and apply_result.mode_state_record.ledger_event == "autotrade.mode_state_readiness_recheck_rejected" and all(item in apply_result.mode_state_record.blocked_by for item in expected_blockers),
        "mode_did_not_escalate_to_live": latest_mode.current_mode == AutoTradeMode.ARMED_DRY_RUN and latest_mode.previous_mode == AutoTradeMode.ARMED_DRY_RUN,
        "observer_run_not_appended_by_applier": before_observer_rows == 1 and after_observer_rows == before_observer_rows,
        "second_apply_idempotent_after_rejection": second_apply.applied is False and second_apply.skipped is True and second_apply.skip_reason == "no_unapplied_accepted_mode_change_command" and after_second_rows == after_mode_rows,
        "applier_uses_readiness_recheck_path": "evaluate_autotrade_live_readiness" in apply_source and "evaluate_autotrade_live_readiness" in preview_source,
        "readiness_has_latest_observer_blocked_gate": "observer_run_latest_blocked_for_live_target" in readiness_source and "latest_blocked_by" in readiness_source,
        "no_ui_runner_or_broker": not any(token in combined_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BN: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bn_mode_change_applier_rejects_latest_observer_blocked_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "preview_rejects_live_target_on_latest_observer_blocked": checks["preview_rejects_live_target_on_latest_observer_blocked"],
            "preview_is_read_only_no_mode_state_append": checks["preview_is_read_only_no_mode_state_append"],
            "apply_rejects_and_appends_rejected_mode_state": checks["apply_rejects_and_appends_rejected_mode_state"],
            "rejected_record_carries_latest_observer_blockers": checks["rejected_record_carries_latest_observer_blockers"],
            "mode_did_not_escalate_to_live": checks["mode_did_not_escalate_to_live"],
            "observer_run_not_appended_by_applier": checks["observer_run_not_appended_by_applier"],
            "second_apply_idempotent_after_rejection": checks["second_apply_idempotent_after_rejection"],
            "no_ui_runner_or_broker": checks["no_ui_runner_or_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "preview": preview.to_dict(),
        "apply_result": apply_result.to_dict(),
        "second_apply": second_apply.to_dict(),
        "mode_state_rows": [row.to_dict() for row in after_apply_read.rows],
        "before_mode_rows": before_mode_rows,
        "after_preview_mode_rows": after_preview_mode_rows,
        "after_mode_rows": after_mode_rows,
        "after_second_rows": after_second_rows,
        "before_observer_rows": before_observer_rows,
        "after_observer_rows": after_observer_rows,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
