# path: ./tools/test_phase4a_autotrade_milestone_de_mode_runtime_gate_malformed_mode_state_failsoft_guard.py
# desc: Guard ModeRuntimeGate uses latest valid mode_state row and remains read-only when mode_state contains malformed rows.

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

from btcts.autotrade.execution import current_mode_state, default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger_rows, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.mode_runtime_gate import build_mode_runtime_gate  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

MODE_RUNTIME_GATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/mode_runtime_gate.py"
MODE_STATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
LATEST_SOURCE = "cmd_de_live_min_size_valid"
OLD_SOURCE = "cmd_de_off_old_valid"
RUNTIME_GATE_PANEL_FIELDS = (
    "current_mode",
    "source_command_id",
    "changed_at",
    "allow_observer_cycle",
    "allow_shadow_decision_append",
    "allow_forecast_outcome_resolution",
    "allow_paper_order",
    "allow_armed_dry_run",
    "allow_live_order_capability",
    "live_requires_readiness_risk_execution_safety",
    "blocked_by",
    "warnings",
    "would_send_to_broker",
    "read_only",
)
FORBIDDEN_GATE_TOKENS = (
    "append_mode_state_record",
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


def mode_state_row(*, current_mode: str, previous_mode: str, source_command_id: str, changed_at: str, accepted: bool = True, mode_changed: bool = True) -> dict[str, Any]:
    return {
        "current_mode": current_mode,
        "previous_mode": previous_mode,
        "changed_at": changed_at,
        "source_command_id": source_command_id,
        "requested_by": "operator_ui",
        "accepted": accepted,
        "mode_changed": mode_changed,
        "reason_codes": ["guard", "mode_runtime_gate_malformed_mode_state_failsoft", source_command_id],
        "blocked_by": [],
        "ledger_event": "autotrade.mode_state_recorded",
        "would_send_to_broker": False,
    }


def write_mode_state_with_malformed_and_latest_live(path: Path) -> None:
    rows = [
        mode_state_row(current_mode="OFF", previous_mode="OFF", source_command_id=OLD_SOURCE, changed_at=now_z(-30), accepted=True, mode_changed=False),
        mode_state_row(current_mode="LIVE_MIN_SIZE", previous_mode="ARMED_DRY_RUN", source_command_id=LATEST_SOURCE, changed_at=now_z(-10), accepted=True, mode_changed=True),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_runtime_gate_malformed_mode_state_failsoft_hot"
    before_command_count = 0
    after_gate_command_count = 0
    before_mode_count = -1
    after_gate_mode_count = -2
    before_observer_count = 0
    after_observer_count = 0
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
        for path in (command_path, mode_state_path, observer_path):
            if path.exists():
                path.unlink()
        write_mode_state_with_malformed_and_latest_live(mode_state_path)
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_before = read_mode_state_records(mode_state_path, max_lines=100)
        before_mode_count = len(mode_read_before.rows)
        before_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        current_before = current_mode_state(mode_state_path, max_lines=100).to_dict()
        summary_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        gate = build_mode_runtime_gate(mode_state_path, max_lines=100)
        gate_data = gate.to_dict()
        current_after = current_mode_state(mode_state_path, max_lines=100).to_dict()
        summary_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        mode_read_after = read_mode_state_records(mode_state_path, max_lines=100)
        after_gate_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        after_gate_mode_count = len(mode_read_after.rows)
        after_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    gate_source = function_source(MODE_RUNTIME_GATE_FILE, "build_mode_runtime_gate")
    blocked_source = function_source(MODE_RUNTIME_GATE_FILE, "_blocked_for_mode")
    current_mode_source = function_source(MODE_STATE_FILE, "current_mode_state")
    read_mode_source = function_source(MODE_STATE_FILE, "read_mode_state_records")
    ui_gate_source = function_source(UI_FILE, "_render_mode_runtime_gate_status")
    checks = {
        "mode_state_reader_skips_malformed_but_keeps_latest_valid_live_row": before_mode_count == 2 and mode_read_before.skipped_count == 1 and tuple(mode_read_before.error_samples) != () and current_before.get("current_mode") == "LIVE_MIN_SIZE" and current_before.get("source_command_id") == LATEST_SOURCE,
        "mode_state_summary_surfaces_skipped_and_latest_valid_live_row": summary_before.get("total_rows") == 2 and summary_before.get("skipped_rows") == 1 and tuple(summary_before.get("error_samples") or ()) != () and summary_before.get("current_mode") == "LIVE_MIN_SIZE" and summary_before.get("latest_source_command_id") == LATEST_SOURCE and summary_before.get("read_only") is True,
        "runtime_gate_uses_latest_valid_live_mode_not_malformed_row": gate_data.get("current_mode") == "LIVE_MIN_SIZE" and gate_data.get("source_command_id") == LATEST_SOURCE and gate_data.get("changed_at") == current_before.get("changed_at"),
        "runtime_gate_live_min_size_capabilities_and_warning_are_correct": gate_data.get("allow_observer_cycle") is True and gate_data.get("allow_shadow_decision_append") is True and gate_data.get("allow_forecast_outcome_resolution") is True and gate_data.get("allow_paper_order") is True and gate_data.get("allow_armed_dry_run") is True and gate_data.get("allow_live_order_capability") is True and gate_data.get("live_requires_readiness_risk_execution_safety") is True and tuple(gate_data.get("blocked_by") or ()) == () and tuple(gate_data.get("warnings") or ()) == ("live_order_capability_requires_readiness_risk_execution_safety",) and gate_data.get("read_only") is True and gate_data.get("would_send_to_broker") is False,
        "runtime_gate_is_read_only_no_ledger_append": after_gate_command_count == before_command_count == 0 and after_gate_mode_count == before_mode_count == 2 and mode_read_after.skipped_count == 1 and after_observer_count == before_observer_count,
        "mode_state_after_gate_still_latest_valid_live_row": current_after.get("current_mode") == "LIVE_MIN_SIZE" and current_after.get("source_command_id") == LATEST_SOURCE and summary_after.get("skipped_rows") == 1 and summary_after.get("latest_source_command_id") == LATEST_SOURCE,
        "runtime_gate_source_uses_current_mode_state_and_is_read_only": bool(gate_source) and "current_mode_state" in gate_source and "read_only=True" in gate_source and "would_send_to_broker=False" in gate_source and not any(token in gate_source for token in FORBIDDEN_GATE_TOKENS),
        "mode_state_current_mode_uses_failsoft_reader": bool(current_mode_source) and "read_mode_state_records" in current_mode_source and "read.rows[-1]" in current_mode_source and bool(read_mode_source) and "skipped += 1" in read_mode_source,
        "blocked_modes_are_explicit_and_live_warning_only": bool(blocked_source) and "mode_off" in blocked_source and "mode_halted" in blocked_source and "live_order_capability_requires_readiness_risk_execution_safety" in gate_source,
        "ui_mode_runtime_gate_panel_displays_gate_fields_and_is_read_only": bool(ui_gate_source) and all(field in ui_gate_source for field in RUNTIME_GATE_PANEL_FIELDS) and not any(token in ui_gate_source for token in FORBIDDEN_GATE_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DE: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_de_mode_runtime_gate_malformed_mode_state_failsoft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_state_reader_skips_malformed_but_keeps_latest_valid_live_row": checks["mode_state_reader_skips_malformed_but_keeps_latest_valid_live_row"],
            "mode_state_summary_surfaces_skipped_and_latest_valid_live_row": checks["mode_state_summary_surfaces_skipped_and_latest_valid_live_row"],
            "runtime_gate_uses_latest_valid_live_mode_not_malformed_row": checks["runtime_gate_uses_latest_valid_live_mode_not_malformed_row"],
            "runtime_gate_live_min_size_capabilities_and_warning_are_correct": checks["runtime_gate_live_min_size_capabilities_and_warning_are_correct"],
            "runtime_gate_is_read_only_no_ledger_append": checks["runtime_gate_is_read_only_no_ledger_append"],
            "mode_state_after_gate_still_latest_valid_live_row": checks["mode_state_after_gate_still_latest_valid_live_row"],
            "runtime_gate_source_uses_current_mode_state_and_is_read_only": checks["runtime_gate_source_uses_current_mode_state_and_is_read_only"],
            "mode_state_current_mode_uses_failsoft_reader": checks["mode_state_current_mode_uses_failsoft_reader"],
            "blocked_modes_are_explicit_and_live_warning_only": checks["blocked_modes_are_explicit_and_live_warning_only"],
            "ui_mode_runtime_gate_panel_displays_gate_fields_and_is_read_only": checks["ui_mode_runtime_gate_panel_displays_gate_fields_and_is_read_only"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "mode_read_before": mode_read_before.to_dict(),
        "current_before": current_before,
        "summary_before": summary_before,
        "gate": gate_data,
        "current_after": current_after,
        "summary_after": summary_after,
        "mode_read_after": mode_read_after.to_dict(),
        "before_command_count": before_command_count,
        "after_gate_command_count": after_gate_command_count,
        "before_mode_count": before_mode_count,
        "after_gate_mode_count": after_gate_mode_count,
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
