# path: ./tools/test_phase4a_autotrade_milestone_al_command_request_ledger_status_guard.py
# desc: Guard command request ledger status summary is read-only and fail-soft.

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

from btcts.autotrade.execution import summarize_command_ledger, read_command_ledger_rows  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py",
)
FORBIDDEN_TEXT_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py",
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
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "append_command_ledger_record(",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "resolve_due_shadow_forecast_outcomes",
    "append_forecast_outcome_link",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "append_decision_jsonl",
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


def command_row(command_id: str, *, command_type: str, accepted: bool, target: str | None, blocked_by: list[str]) -> dict:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated" if command_type == "REQUEST_MODE_CHANGE" else "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "guard",
            "requested_at": "2026-06-13T04:00:00Z",
            "current_mode": "ARMED_DRY_RUN",
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard"],
            "note": "{}",
            "confirmation_required": True,
        },
    }


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_command_status_hot"
    command_path = hot_root / "autotrade/commands/command_requests.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            command_row("cmd_mode_ok", command_type="REQUEST_MODE_CHANGE", accepted=True, target="LIVE_MIN_SIZE", blocked_by=[]),
            command_row("cmd_mode_blocked", command_type="REQUEST_MODE_CHANGE", accepted=False, target="LIVE_CONTROLLED", blocked_by=["readiness_preflight_not_ready", "observer_run_stale"]),
            command_row("cmd_halt", command_type="REQUEST_HALT_NEW", accepted=True, target="halt_new", blocked_by=[]),
        ]
        command_path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n{broken_json\n", encoding="utf-8")
        read = read_command_ledger_rows(max_lines=100)
        summary = summarize_command_ledger(max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    forbidden_text = "\n".join(path.read_text(encoding="utf-8") for path in FORBIDDEN_TEXT_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "command_status_present": "CommandLedgerSummary" in all_text and "summarize_command_ledger" in all_text and "read_command_ledger_rows" in all_text,
        "read_rows_fail_soft": len(read.rows) == 3 and read.skipped_count == 1 and read.error_samples,
        "summary_counts_present": summary.total_rows == 3 and summary.accepted_count == 2 and summary.rejected_count == 1 and summary.skipped_rows == 1,
        "latest_fields_present": summary.latest_command_id == "cmd_halt" and summary.latest_command_type == "REQUEST_HALT_NEW" and summary.latest_target == "halt_new" and summary.latest_accepted is True,
        "grouped_counts_present": summary.command_type_counts.get("REQUEST_MODE_CHANGE") == 2 and summary.target_counts.get("LIVE_MIN_SIZE") == 1,
        "blocked_counts_present": summary.blocked_by_counts.get("readiness_preflight_not_ready") == 1 and summary.blocked_by_counts.get("observer_run_stale") == 1,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["accepted_count"] == 2,
        "read_only_no_broker": summary.read_only is True and summary.would_send_to_broker is False,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in all_imports) and "streamlit" not in all_imports,
        "no_forbidden_tokens": not any(token in forbidden_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AL: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_al_command_request_ledger_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "command_request_ledger_status_present": checks["command_status_present"],
            "fail_soft_corrupt_jsonl_present": checks["read_rows_fail_soft"],
            "summary_counts_present": checks["summary_counts_present"],
            "grouped_counts_present": checks["grouped_counts_present"],
            "read_only_no_append_no_broker": checks["read_only_no_broker"] and checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "read": read.to_dict(),
        "summary": summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
