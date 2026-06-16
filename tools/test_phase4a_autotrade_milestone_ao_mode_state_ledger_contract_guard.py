# path: ./tools/test_phase4a_autotrade_milestone_ao_mode_state_ledger_contract_guard.py
# desc: Guard AutoTrade mode-state ledger contract. No broker/order execution.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    CommandLedgerRecord,
    CommandRequest,
    CommandType,
    append_mode_state_record,
    build_mode_state_record_from_command,
    current_mode_state,
    default_mode_state_ledger_path,
    read_mode_state_records,
    summarize_mode_state,
)
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py",
)
FORBIDDEN_TEXT_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "btcts.apps.operator_ui",
    "streamlit",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


def imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def command_record(command_id: str, *, command_type: CommandType, accepted: bool, current_mode: str, target: str | None, blocked_by: tuple[str, ...] = ()) -> CommandLedgerRecord:
    command = CommandRequest(
        command_id=command_id,
        command_type=command_type,
        requested_by="guard",
        requested_at="2026-06-13T04:30:00Z",
        current_mode=current_mode,
        target=target,
        confirmation=True,
        reason_codes=("guard",),
        note="{}",
    )
    return CommandLedgerRecord(
        command_id=command_id,
        accepted=accepted,
        blocked_by=blocked_by,
        command=command,
        ledger_event="autotrade.mode_change_command_request_validated" if command_type == CommandType.REQUEST_MODE_CHANGE else "autotrade.command_request_validated",
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_state_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        path = default_mode_state_ledger_path(ensure=True)
        if path.exists():
            path.unlink()

        default_state = current_mode_state(path)
        accepted_command = command_record(
            "cmd_mode_state_shadow",
            command_type=CommandType.REQUEST_MODE_CHANGE,
            accepted=True,
            current_mode="OFF",
            target="SHADOW",
        )
        accepted_record = build_mode_state_record_from_command(
            current_mode=AutoTradeMode.OFF,
            command_record=accepted_command,
            changed_at="2026-06-13T04:31:00Z",
        )
        append_mode_state_record(path, accepted_record)

        rejected_command = command_record(
            "cmd_mode_state_rejected",
            command_type=CommandType.REQUEST_MODE_CHANGE,
            accepted=False,
            current_mode="SHADOW",
            target="LIVE_MIN_SIZE",
            blocked_by=("readiness_preflight_not_ready",),
        )
        rejected_record = build_mode_state_record_from_command(
            current_mode=AutoTradeMode.SHADOW,
            command_record=rejected_command,
            changed_at="2026-06-13T04:32:00Z",
        )
        append_mode_state_record(path, rejected_record)

        non_mode_command = command_record(
            "cmd_mode_state_halt",
            command_type=CommandType.REQUEST_HALT_NEW,
            accepted=True,
            current_mode="SHADOW",
            target="halt_new",
        )
        non_mode_record = build_mode_state_record_from_command(
            current_mode=AutoTradeMode.SHADOW,
            command_record=non_mode_command,
            changed_at="2026-06-13T04:33:00Z",
        )
        append_mode_state_record(path, non_mode_record)
        with path.open("a", encoding="utf-8") as fh:
            fh.write("{broken_json\n")

        read = read_mode_state_records(path, max_lines=100)
        current = current_mode_state(path, max_lines=100)
        summary = summarize_mode_state(path, max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    forbidden_text = "\n".join(path.read_text(encoding="utf-8") for path in FORBIDDEN_TEXT_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "mode_state_contract_present": "ModeStateRecord" in all_text and "summarize_mode_state" in all_text and "current_mode_state" in all_text,
        "default_off_when_missing": default_state.current_mode == AutoTradeMode.OFF and default_state.mode_changed is False,
        "accepted_mode_change_recorded": accepted_record.current_mode == AutoTradeMode.SHADOW and accepted_record.previous_mode == AutoTradeMode.OFF and accepted_record.mode_changed is True,
        "rejected_does_not_change_mode": rejected_record.current_mode == AutoTradeMode.SHADOW and rejected_record.mode_changed is False and "source_command_not_accepted" in rejected_record.blocked_by,
        "non_mode_command_does_not_change_mode": non_mode_record.current_mode == AutoTradeMode.SHADOW and non_mode_record.mode_changed is False and "not_mode_change_command" in non_mode_record.blocked_by,
        "read_fail_soft": len(read.rows) == 3 and read.skipped_count == 1 and read.error_samples,
        "summary_current_mode_present": current.current_mode == AutoTradeMode.SHADOW and summary.current_mode == AutoTradeMode.SHADOW and summary.total_rows == 3,
        "summary_counts_present": summary.mode_counts.get("SHADOW") == 3 and summary.blocked_by_counts.get("readiness_preflight_not_ready") == 1,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["current_mode"] == "SHADOW",
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in all_imports) and "streamlit" not in all_imports,
        "no_forbidden_tokens": not any(token in forbidden_text for token in FORBIDDEN_TOKENS),
        "no_broker": summary.would_send_to_broker is False and summary.read_only is True and accepted_record.would_send_to_broker is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AO: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ao_mode_state_ledger_contract_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_state_ledger_contract_present": checks["mode_state_contract_present"],
            "default_off_when_missing": checks["default_off_when_missing"],
            "accepted_request_changes_mode_state": checks["accepted_mode_change_recorded"],
            "rejected_or_non_mode_request_does_not_change_mode": checks["rejected_does_not_change_mode"] and checks["non_mode_command_does_not_change_mode"],
            "fail_soft_jsonl_present": checks["read_fail_soft"],
            "summary_current_mode_present": checks["summary_current_mode_present"],
            "no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"] and checks["no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "default_state": default_state.to_dict(),
        "accepted_record": accepted_record.to_dict(),
        "rejected_record": rejected_record.to_dict(),
        "non_mode_record": non_mode_record.to_dict(),
        "read": read.to_dict(),
        "current": current.to_dict(),
        "summary": summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
