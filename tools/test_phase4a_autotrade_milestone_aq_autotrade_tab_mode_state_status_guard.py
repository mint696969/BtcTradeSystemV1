# path: ./tools/test_phase4a_autotrade_milestone_aq_autotrade_tab_mode_state_status_guard.py
# desc: Guard AutoTrade UI tab displays mode-state status read-only and reads current mode from mode_state ledger.

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

from btcts.autotrade.execution import append_mode_state_record, current_mode_state, default_mode_state_ledger_path, summarize_mode_state  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
STATUS_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_state_ui_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        append_mode_state_record(
            mode_path,
            ModeStateRecord(
                current_mode=AutoTradeMode.SHADOW,
                previous_mode=AutoTradeMode.OFF,
                changed_at="2026-06-13T04:50:00Z",
                source_command_id="cmd_ui_mode_state_shadow",
                requested_by="guard",
                accepted=True,
                mode_changed=True,
                reason_codes=("guard",),
                blocked_by=(),
                would_send_to_broker=False,
            ),
        )
        current = current_mode_state(max_lines=100)
        summary = summarize_mode_state(max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    mode_status_source = function_source(UI_FILE, "_render_mode_state_status")
    top_source = function_source(UI_FILE, "_render_top_critical_state")
    render_source = function_source(UI_FILE, "render")
    checks = {
        "ui_imports_mode_state_readers": "btcts.autotrade.execution" in imports and "current_mode_state" in text and "summarize_mode_state" in text,
        "top_critical_reads_mode_state": "current_mode_state" in top_source and "AutoTradeMode.SHADOW" not in top_source,
        "mode_state_status_panel_present": "_render_mode_state_status" in text and "Mode State" in text,
        "mode_state_fields_displayed": all(token in text for token in ("current_mode", "previous_mode", "latest_changed_at", "latest_source_command_id", "latest_mode_changed", "mode_counts", "blocked_by_counts")),
        "mode_state_status_read_only": bool(mode_status_source) and not any(token in mode_status_source for token in STATUS_FORBIDDEN_TOKENS),
        "mode_state_panel_rendered": "_render_mode_state_status()" in render_source,
        "summary_contract_still_works": current.current_mode == AutoTradeMode.SHADOW and summary.current_mode == AutoTradeMode.SHADOW and summary.total_rows == 1,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AQ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_aq_autotrade_tab_mode_state_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_mode_state_status_present": checks["ui_imports_mode_state_readers"] and checks["mode_state_status_panel_present"],
            "top_critical_state_reads_mode_state": checks["top_critical_reads_mode_state"],
            "mode_state_fields_displayed": checks["mode_state_fields_displayed"],
            "mode_state_status_read_only_no_apply_no_broker": checks["mode_state_status_read_only"],
            "summary_contract_still_works": checks["summary_contract_still_works"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
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
