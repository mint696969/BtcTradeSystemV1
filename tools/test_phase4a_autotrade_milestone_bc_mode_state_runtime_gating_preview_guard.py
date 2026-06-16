# path: ./tools/test_phase4a_autotrade_milestone_bc_mode_state_runtime_gating_preview_guard.py
# desc: Guard read-only mode_state-derived runtime capability gate. No runner execution, no broker execution.

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

from btcts.autotrade.execution import append_mode_state_record, default_mode_state_ledger_path, read_mode_state_records  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.mode_runtime_gate import build_mode_runtime_gate  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

MODULE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/mode_runtime_gate.py"
INIT_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/__init__.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "append_mode_state_record",
    "append_command_ledger_record",
    "validate_and_append_command",
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
    "streamlit",
    "btcts.apps.operator_ui",
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


def write_state(path: Path, mode: AutoTradeMode, *, command_id: str) -> None:
    if path.exists():
        path.unlink()
    append_mode_state_record(
        path,
        ModeStateRecord(
            current_mode=mode,
            previous_mode=AutoTradeMode.OFF,
            changed_at="2026-06-13T06:50:00Z",
            source_command_id=command_id,
            requested_by="guard",
            accepted=True,
            mode_changed=mode != AutoTradeMode.OFF,
            reason_codes=("guard", "runtime_gate"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_runtime_gate_hot"
    gates: dict[str, dict] = {}
    rows_after: dict[str, int] = {}
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        modes = (
            AutoTradeMode.OFF,
            AutoTradeMode.SHADOW,
            AutoTradeMode.PAPER_OR_REPLAY,
            AutoTradeMode.ARMED_DRY_RUN,
            AutoTradeMode.LIVE_MIN_SIZE,
            AutoTradeMode.LIVE_CONTROLLED,
            AutoTradeMode.HALTED,
        )
        for mode in modes:
            write_state(mode_path, mode, command_id=f"cmd_bc_{mode.value.lower()}")
            before_count = len(read_mode_state_records(mode_path, max_lines=100).rows)
            gate = build_mode_runtime_gate(max_lines=100)
            after_count = len(read_mode_state_records(mode_path, max_lines=100).rows)
            gates[mode.value] = gate.to_dict()
            rows_after[mode.value] = after_count
            if after_count != before_count:
                failures.append(f"gate mutated mode_state rows for {mode.value}: {before_count}->{after_count}")
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = MODULE_FILE.read_text(encoding="utf-8")
    imports = imports_from(MODULE_FILE)
    checks = {
        "module_present_and_exported": "ModeRuntimeGate" in text and "build_mode_runtime_gate" in text and "mode_runtime_gate" in INIT_FILE.read_text(encoding="utf-8"),
        "off_blocks_runtime": gates["OFF"]["allow_observer_cycle"] is False and gates["OFF"]["allow_shadow_decision_append"] is False and "mode_off" in gates["OFF"]["blocked_by"],
        "shadow_allows_shadow_only": gates["SHADOW"]["allow_observer_cycle"] is True and gates["SHADOW"]["allow_shadow_decision_append"] is True and gates["SHADOW"]["allow_paper_order"] is False and gates["SHADOW"]["allow_live_order_capability"] is False,
        "paper_allows_paper_not_live": gates["PAPER_OR_REPLAY"]["allow_paper_order"] is True and gates["PAPER_OR_REPLAY"]["allow_armed_dry_run"] is False and gates["PAPER_OR_REPLAY"]["allow_live_order_capability"] is False,
        "armed_allows_dry_not_live": gates["ARMED_DRY_RUN"]["allow_paper_order"] is True and gates["ARMED_DRY_RUN"]["allow_armed_dry_run"] is True and gates["ARMED_DRY_RUN"]["allow_live_order_capability"] is False,
        "live_modes_mark_capability_with_warning": gates["LIVE_MIN_SIZE"]["allow_live_order_capability"] is True and gates["LIVE_CONTROLLED"]["allow_live_order_capability"] is True and "live_order_capability_requires_readiness_risk_execution_safety" in gates["LIVE_MIN_SIZE"]["warnings"],
        "halted_blocks_runtime": gates["HALTED"]["allow_observer_cycle"] is False and "mode_halted" in gates["HALTED"]["blocked_by"],
        "read_only_no_runner_no_broker": not any(token in text for token in FORBIDDEN_TOKENS),
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in imports) and "streamlit" not in imports,
        "json_safe_gate": json.loads(json.dumps(gates["LIVE_MIN_SIZE"], ensure_ascii=False))["current_mode"] == "LIVE_MIN_SIZE",
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BC: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bc_mode_state_runtime_gating_preview_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_runtime_gate_present": checks["module_present_and_exported"],
            "off_blocks_runtime": checks["off_blocks_runtime"],
            "shadow_allows_shadow_only": checks["shadow_allows_shadow_only"],
            "paper_allows_paper_not_live": checks["paper_allows_paper_not_live"],
            "armed_allows_dry_not_live": checks["armed_allows_dry_not_live"],
            "live_modes_mark_capability_with_warning": checks["live_modes_mark_capability_with_warning"],
            "halted_blocks_runtime": checks["halted_blocks_runtime"],
            "read_only_no_runner_no_broker": checks["read_only_no_runner_no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "gates": gates,
        "rows_after": rows_after,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
