# path: ./tools/test_phase4a_autotrade_milestone_az_mode_state_latest_rejection_visibility_guard.py
# desc: Guard mode_state summary/UI exposes latest rejection reason read-only.

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

from btcts.autotrade.execution import append_mode_state_record, default_mode_state_ledger_path, summarize_mode_state  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

MODE_STATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py"
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
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
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
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_state_rejection_visibility_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        append_mode_state_record(
            mode_path,
            ModeStateRecord(
                current_mode=AutoTradeMode.OFF,
                previous_mode=AutoTradeMode.OFF,
                changed_at="2026-06-13T06:20:00Z",
                source_command_id="cmd_az_rejected_live",
                requested_by="guard",
                accepted=False,
                mode_changed=False,
                reason_codes=("guard", "readiness_recheck"),
                blocked_by=("readiness_recheck_not_ready", "observer_run_stale"),
                ledger_event="autotrade.mode_state_readiness_recheck_rejected",
                would_send_to_broker=False,
            ),
        )
        summary = summarize_mode_state(max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    mode_state_text = MODE_STATE_FILE.read_text(encoding="utf-8")
    ui_text = UI_FILE.read_text(encoding="utf-8")
    ui_source = function_source(UI_FILE, "_render_mode_state_status")
    checks = {
        "summary_fields_present": all(token in mode_state_text for token in ("latest_ledger_event", "latest_reason_codes", "latest_blocked_by", "latest_would_send_to_broker")),
        "summary_exposes_latest_rejection": summary.latest_ledger_event == "autotrade.mode_state_readiness_recheck_rejected" and tuple(summary.latest_blocked_by) == ("readiness_recheck_not_ready", "observer_run_stale") and tuple(summary.latest_reason_codes) == ("guard", "readiness_recheck") and summary.latest_would_send_to_broker is False,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["latest_blocked_by"] == ["readiness_recheck_not_ready", "observer_run_stale"],
        "ui_mode_state_displays_latest_rejection_fields": all(token in ui_source for token in ("latest_ledger_event", "latest_reason_codes", "latest_blocked_by", "latest_would_send_to_broker")),
        "ui_mode_state_status_read_only": bool(ui_source) and not any(token in ui_source for token in STATUS_FORBIDDEN_TOKENS),
        "ui_still_renders_mode_state_panel": "_render_mode_state_status()" in function_source(UI_FILE, "render"),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AZ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_az_mode_state_latest_rejection_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_state_summary_latest_rejection_fields_present": checks["summary_fields_present"],
            "summary_exposes_latest_rejection": checks["summary_exposes_latest_rejection"],
            "ui_mode_state_displays_latest_rejection_fields": checks["ui_mode_state_displays_latest_rejection_fields"],
            "ui_mode_state_status_read_only_no_apply_no_broker": checks["ui_mode_state_status_read_only"],
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
