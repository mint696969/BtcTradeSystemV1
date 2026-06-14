# path: ./tools/test_phase4a_autotrade_milestone_bh_bounded_observer_runtime_gate_shadow_allow_guard.py
# desc: Guard bounded observer SHADOW mode passes through mode_runtime_gate and records allowed run summary. No broker execution.

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
from btcts.autotrade.ledger import ForecastOutcomeResolutionResult, read_observer_run_records, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.live_shadow import ShadowDecisionVerticalResult, default_shadow_decision_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT, decision_ledger_path  # noqa: E402
import btcts.autotrade.shadow_cycle as shadow_cycle  # noqa: E402
import btcts.autotrade.observer_cycle as observer_cycle  # noqa: E402

OBSERVER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/observer_cycle.py"
SHADOW_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/shadow_cycle.py"
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
            changed_at="2026-06-13T07:40:00Z",
            source_command_id=f"cmd_bh_{mode.value.lower()}",
            requested_by="guard",
            accepted=True,
            mode_changed=mode != AutoTradeMode.OFF,
            reason_codes=("guard", "bounded_runner_gate_shadow_allow"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_shadow_impl = shadow_cycle.run_latest_market_state_shadow_decision
    original_resolve_impl = observer_cycle.resolve_due_shadow_forecast_outcomes
    hot_root = REPO_ROOT / "tmp/btc_ts_bounded_runner_gate_shadow_allow_hot"
    calls = {"shadow_impl": 0, "shadow_persist_true": 0, "shadow_persist_false": 0, "resolve": 0}

    def fake_shadow_impl(*args, **kwargs):
        calls["shadow_impl"] += 1
        persist = bool(kwargs.get("persist"))
        if persist:
            calls["shadow_persist_true"] += 1
        else:
            calls["shadow_persist_false"] += 1
        n = calls["shadow_impl"]
        return ShadowDecisionVerticalResult(
            snapshot_id=f"snap_bh_shadow_allowed_{n}",
            forecast_id=f"fcst_bh_shadow_allowed_{n}",
            decision_id=f"dec_bh_shadow_allowed_{n}",
            candidate_action="WAIT",
            risk_allowed=False,
            appended=persist,
            ledger_path=default_shadow_decision_ledger_path(ensure=False),
            blocked_by=(),
            would_send_to_broker=False,
            decision=None,
            diagnostics=None,
        )

    def fake_resolve(*args, **kwargs):
        calls["resolve"] += 1
        if kwargs.get("persist") is not True:
            raise AssertionError(f"resolver persist was not True: {kwargs.get('persist')!r}")
        n = calls["resolve"]
        return ForecastOutcomeResolutionResult(
            shadow_decision_path=default_shadow_decision_ledger_path(ensure=False),
            outcome_ledger_path=decision_ledger_path("forecast_outcomes.jsonl", ensure=False),
            actual_snapshot_id=f"actual_bh_shadow_allowed_{n}",
            actual_ground_direction="sell_leaning",
            due_count=1,
            appended_count=1,
            duplicate_skipped_count=0,
            unresolved_count=0,
            blocked_by=(),
            records=(),
            would_send_to_broker=False,
            read_only_inputs=True,
        )

    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        write_mode(mode_path, AutoTradeMode.SHADOW)
        shadow_cycle.run_latest_market_state_shadow_decision = fake_shadow_impl
        observer_cycle.resolve_due_shadow_forecast_outcomes = fake_resolve
        bounded = observer_cycle.run_observer_cycle_bounded(
            max_cycles=2,
            interval_sec=0.0,
            persist=True,
            skip_duplicate_snapshot=True,
            persist_run_record=True,
        )
        observer_rows = read_observer_run_records(max_lines=100)
        observer_summary = summarize_observer_run_ledger(max_lines=100)
    finally:
        shadow_cycle.run_latest_market_state_shadow_decision = original_shadow_impl
        observer_cycle.resolve_due_shadow_forecast_outcomes = original_resolve_impl
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    observer_text = OBSERVER_FILE.read_text(encoding="utf-8")
    shadow_text = SHADOW_FILE.read_text(encoding="utf-8")
    bounded_source = function_source(OBSERVER_FILE, "run_observer_cycle_bounded")
    combined_text = observer_text + "\n" + shadow_text
    latest_row = observer_rows[-1] if observer_rows else None
    checks = {
        "bounded_shadow_mode_completes_cycles": bounded.requested_cycles == 2 and bounded.completed_cycles == 2,
        "bounded_shadow_mode_calls_shadow_impl": calls["shadow_impl"] == 4 and calls["shadow_persist_false"] == 2 and calls["shadow_persist_true"] == 2,
        "bounded_shadow_mode_calls_resolver": calls["resolve"] == 2,
        "bounded_counts_allowed_appends": bounded.appended_shadow_decision_count == 2 and bounded.appended_forecast_outcome_count == 2 and bounded.duplicate_snapshot_skipped_count == 0,
        "bounded_results_not_gate_blocked": all("mode_runtime_gate_blocked_shadow_decision_append" not in item.blocked_by and "mode_runtime_gate_blocked_forecast_outcome_resolution" not in item.blocked_by and "mode_off" not in item.blocked_by and "mode_halted" not in item.blocked_by for item in bounded.results),
        "bounded_results_report_shadow_gate": all(item.mode_runtime_gate is not None and item.mode_runtime_gate.current_mode == AutoTradeMode.SHADOW and item.mode_runtime_gate.allow_observer_cycle and item.mode_runtime_gate.allow_shadow_decision_append and item.mode_runtime_gate.allow_forecast_outcome_resolution and not item.mode_runtime_gate.blocked_by for item in bounded.results),
        "observer_run_record_appended_allowed_summary": bounded.observer_run_record_appended is True and latest_row is not None and latest_row.completed_cycles == 2 and latest_row.appended_shadow_decision_count == 2 and latest_row.appended_forecast_outcome_count == 2 and not latest_row.blocked_by,
        "observer_summary_reflects_allowed_run": observer_summary.latest_completed_cycles == 2 and observer_summary.latest_appended_shadow_decision_count == 2 and observer_summary.latest_appended_forecast_outcome_count == 2 and observer_summary.blocked_by_counts == {},
        "bounded_code_uses_one_shot_gate_path": "run_observer_cycle_once" in bounded_source and "should_persist_shadow_and_outcomes" in bounded_source,
        "no_broker_or_ui_imports": not any(token in combined_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BH: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bh_bounded_observer_runtime_gate_shadow_allow_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "bounded_shadow_mode_completes_cycles": checks["bounded_shadow_mode_completes_cycles"],
            "bounded_shadow_mode_calls_shadow_impl": checks["bounded_shadow_mode_calls_shadow_impl"],
            "bounded_shadow_mode_calls_resolver": checks["bounded_shadow_mode_calls_resolver"],
            "bounded_counts_allowed_appends": checks["bounded_counts_allowed_appends"],
            "bounded_results_not_gate_blocked": checks["bounded_results_not_gate_blocked"],
            "observer_run_record_appended_allowed_summary": checks["observer_run_record_appended_allowed_summary"],
            "observer_summary_reflects_allowed_run": checks["observer_summary_reflects_allowed_run"],
            "no_broker_or_ui_imports": checks["no_broker_or_ui_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "calls": calls,
        "bounded": bounded.to_dict(),
        "observer_rows": [row.to_dict() for row in observer_rows],
        "observer_summary": observer_summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
