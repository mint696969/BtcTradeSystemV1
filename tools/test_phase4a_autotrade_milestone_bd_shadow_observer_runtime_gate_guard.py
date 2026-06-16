# path: ./tools/test_phase4a_autotrade_milestone_bd_shadow_observer_runtime_gate_guard.py
# desc: Guard shadow/observer runners respect mode_runtime_gate for OFF/HALTED. No broker execution.

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

from btcts.autotrade.execution import append_mode_state_record, default_mode_state_ledger_path  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.ledger import default_forecast_outcome_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
import btcts.autotrade.shadow_cycle as shadow_cycle  # noqa: E402
import btcts.autotrade.observer_cycle as observer_cycle  # noqa: E402

SHADOW_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/shadow_cycle.py"
OBSERVER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/observer_cycle.py"
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


def write_mode(path: Path, mode: AutoTradeMode) -> None:
    if path.exists():
        path.unlink()
    append_mode_state_record(
        path,
        ModeStateRecord(
            current_mode=mode,
            previous_mode=AutoTradeMode.OFF,
            changed_at="2026-06-13T07:00:00Z",
            source_command_id=f"cmd_bd_{mode.value.lower()}",
            requested_by="guard",
            accepted=True,
            mode_changed=mode != AutoTradeMode.OFF,
            reason_codes=("guard", "runner_gate"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_shadow_impl = shadow_cycle.run_latest_market_state_shadow_decision
    original_resolve_impl = observer_cycle.resolve_due_shadow_forecast_outcomes
    hot_root = REPO_ROOT / "tmp/btc_ts_runner_gate_hot"
    calls = {"shadow_impl": 0, "resolve": 0}

    def forbidden_shadow_impl(*args, **kwargs):
        calls["shadow_impl"] += 1
        raise AssertionError("shadow implementation should not run when mode gate blocks")

    def forbidden_resolve(*args, **kwargs):
        calls["resolve"] += 1
        raise AssertionError("forecast resolution should not run when mode gate blocks")

    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        write_mode(mode_path, AutoTradeMode.OFF)
        shadow_cycle.run_latest_market_state_shadow_decision = forbidden_shadow_impl
        observer_cycle.resolve_due_shadow_forecast_outcomes = forbidden_resolve
        off_shadow = shadow_cycle.run_shadow_cycle_once(persist=True)
        off_observer = observer_cycle.run_observer_cycle_once(persist=True)
        off_bounded = observer_cycle.run_observer_cycle_bounded(max_cycles=2, interval_sec=0, persist=True, persist_run_record=True)
        outcome_path = default_forecast_outcome_ledger_path(ensure=False)
        outcome_exists_after_off = outcome_path.exists()

        write_mode(mode_path, AutoTradeMode.HALTED)
        halted_shadow = shadow_cycle.run_shadow_cycle_once(persist=True)
    finally:
        shadow_cycle.run_latest_market_state_shadow_decision = original_shadow_impl
        observer_cycle.resolve_due_shadow_forecast_outcomes = original_resolve_impl
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    shadow_text = SHADOW_FILE.read_text(encoding="utf-8")
    observer_text = OBSERVER_FILE.read_text(encoding="utf-8")
    shadow_once_source = function_source(SHADOW_FILE, "run_shadow_cycle_once")
    observer_once_source = function_source(OBSERVER_FILE, "run_observer_cycle_once")
    bounded_source = function_source(OBSERVER_FILE, "run_observer_cycle_bounded")
    combined_text = shadow_text + "\n" + observer_text
    checks = {
        "shadow_cycle_uses_mode_runtime_gate": "build_mode_runtime_gate" in shadow_text and "allow_shadow_decision_append" in shadow_once_source and "mode_runtime_gate_blocked_shadow_decision_append" in shadow_text,
        "observer_cycle_uses_mode_runtime_gate": "build_mode_runtime_gate" in observer_text and "allow_forecast_outcome_resolution" in observer_once_source and "mode_runtime_gate_blocked_forecast_outcome_resolution" in observer_text,
        "off_shadow_does_not_call_shadow_impl": calls["shadow_impl"] == 0 and off_shadow.appended is False and "mode_off" in off_shadow.blocked_by and "mode_runtime_gate_blocked_shadow_decision_append" in off_shadow.blocked_by,
        "off_observer_does_not_resolve_outcomes": calls["resolve"] == 0 and off_observer.appended_shadow_decision is False and off_observer.appended_forecast_outcomes == 0 and "mode_runtime_gate_blocked_forecast_outcome_resolution" in off_observer.blocked_by,
        "off_bounded_records_blocked_run_without_appends": off_bounded.completed_cycles == 2 and off_bounded.appended_shadow_decision_count == 0 and off_bounded.appended_forecast_outcome_count == 0 and "mode_off" in off_bounded.blocked_by,
        "halted_shadow_blocked": halted_shadow.appended is False and "mode_halted" in halted_shadow.blocked_by,
        "outcome_not_created_by_blocked_off_observer": outcome_exists_after_off is False,
        "no_broker_or_ui_imports": not any(token in combined_text for token in FORBIDDEN_TOKENS),
        "bounded_probe_uses_gate": "run_shadow_cycle_once" in bounded_source,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BD: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bd_shadow_observer_runtime_gate_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "shadow_cycle_uses_mode_runtime_gate": checks["shadow_cycle_uses_mode_runtime_gate"],
            "observer_cycle_uses_mode_runtime_gate": checks["observer_cycle_uses_mode_runtime_gate"],
            "off_shadow_does_not_call_shadow_impl": checks["off_shadow_does_not_call_shadow_impl"],
            "off_observer_does_not_resolve_outcomes": checks["off_observer_does_not_resolve_outcomes"],
            "off_bounded_records_blocked_run_without_appends": checks["off_bounded_records_blocked_run_without_appends"],
            "halted_shadow_blocked": checks["halted_shadow_blocked"],
            "no_broker_or_ui_imports": checks["no_broker_or_ui_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "calls": calls,
        "off_shadow": off_shadow.to_dict(),
        "off_observer": off_observer.to_dict(),
        "off_bounded": off_bounded.to_dict(),
        "halted_shadow": halted_shadow.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
