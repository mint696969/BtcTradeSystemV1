# path: ./tools/test_phase4a_autotrade_milestone_am_autotrade_tab_command_request_status_guard.py
# desc: Guard AutoTrade UI tab displays command request ledger status read-only.

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

from btcts.autotrade.execution import summarize_command_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
STATUS_FORBIDDEN_TOKENS = (
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "append_command_ledger_record",
    "st.button(",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
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


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


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
            "requested_at": "2026-06-13T04:10:00Z",
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
    hot_root = REPO_ROOT / "tmp/btc_ts_command_status_ui_hot"
    command_path = hot_root / "autotrade/commands/command_requests.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            command_row("cmd_ui_mode_ok", command_type="REQUEST_MODE_CHANGE", accepted=True, target="LIVE_MIN_SIZE", blocked_by=[]),
            command_row("cmd_ui_mode_blocked", command_type="REQUEST_MODE_CHANGE", accepted=False, target="LIVE_CONTROLLED", blocked_by=["readiness_preflight_not_ready"]),
            command_row("cmd_ui_halt", command_type="REQUEST_HALT_NEW", accepted=True, target="halt_new", blocked_by=[]),
        ]
        command_path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")
        summary = summarize_command_ledger(max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    status_source = function_source(UI_FILE, "_render_command_request_status")
    render_source = function_source(UI_FILE, "render")
    checks = {
        "ui_imports_command_summary": "btcts.autotrade.execution" in imports and "summarize_command_ledger" in text,
        "ui_has_command_request_status_panel": "_render_command_request_status" in text and "Command Requests" in text,
        "ui_displays_command_summary_fields": all(token in text for token in ("accepted_count", "rejected_count", "latest_command_type", "latest_target", "latest_accepted", "command_type_counts", "blocked_by_counts", "skipped_rows")),
        "status_panel_read_only": bool(status_source) and not any(token in status_source for token in STATUS_FORBIDDEN_TOKENS),
        "status_panel_rendered": "_render_command_request_status()" in render_source,
        "summary_contract_still_works": summary.total_rows == 3 and summary.accepted_count == 2 and summary.rejected_count == 1 and summary.command_type_counts.get("REQUEST_MODE_CHANGE") == 2,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AM: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_am_autotrade_tab_command_request_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_command_request_status_present": checks["ui_imports_command_summary"] and checks["ui_has_command_request_status_panel"],
            "command_summary_fields_displayed": checks["ui_displays_command_summary_fields"],
            "status_panel_read_only_no_append_no_broker": checks["status_panel_read_only"],
            "summary_contract_still_works": checks["summary_contract_still_works"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
