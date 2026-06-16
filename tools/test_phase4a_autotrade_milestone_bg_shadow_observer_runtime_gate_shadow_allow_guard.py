# path: ./tools/test_phase4a_autotrade_milestone_bg_shadow_observer_runtime_gate_shadow_allow_guard.py
# desc: Guard SHADOW mode passes through mode_runtime_gate to shadow implementation and forecast resolver. No broker execution.

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
from btcts.autotrade.ledger import ForecastOutcomeResolutionResult  # noqa: E402
from btcts.autotrade.live_shadow import ShadowDecisionVerticalResult, default_shadow_decision_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT, decision_ledger_path  # noqa: E402
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
            changed_at="2026-06-13T07:30:00Z",
            source_command_id=f"cmd_bg_{mode.value.lower()}",
            requested_by="guard",
            accepted=True,
            mode_changed=mode != AutoTradeMode.OFF,
            reason_codes=("guard", "runner_gate_shadow_allow"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_shadow_impl = shadow_cycle.run_latest_market_state_shadow_decision
    original_resolve_impl = observer_cycle.resolve_due_shadow_forecast_outcomes
    hot_root = REPO_ROOT / "tmp/btc_ts_runner_gate_shadow_allow_hot"
    calls = {"shadow_impl": 0, "resolve": 0}

    def fake_shadow_impl(*args, **kwargs):
        calls["shadow_impl"] += 1
        if kwargs.get("persist") is not True:
            raise AssertionError(f"shadow persist was not True: {kwargs.get('persist')!r}")
        return ShadowDecisionVerticalResult(
            snapshot_id="snap_bg_shadow_allowed",
            forecast_id="fcst_bg_shadow_allowed",
            decision_id="dec_bg_shadow_allowed",
            candidate_action="WAIT",
            risk_allowed=False,
            appended=True,
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
        return ForecastOutcomeResolutionResult(
            shadow_decision_path=default_shadow_decision_ledger_path(ensure=False),
            outcome_ledger_path=decision_ledger_path("forecast_outcomes.jsonl", ensure=False),
            actual_snapshot_id="actual_bg_shadow_allowed",
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
        shadow_result = shadow_cycle.run_shadow_cycle_once(persist=True)
        observer_result = observer_cycle.run_observer_cycle_once(persist=True)
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
    combined_text = shadow_text + "\n" + observer_text
    checks = {
        "shadow_cycle_gate_allows_shadow_impl": calls["shadow_impl"] >= 2 and shadow_result.appended is True and shadow_result.result.snapshot_id == "snap_bg_shadow_allowed",
        "shadow_gate_reports_allowed_mode": shadow_result.mode_runtime_gate is not None and shadow_result.mode_runtime_gate.current_mode == AutoTradeMode.SHADOW and shadow_result.mode_runtime_gate.allow_shadow_decision_append is True and not shadow_result.mode_runtime_gate.blocked_by,
        "shadow_result_not_gate_blocked": "mode_runtime_gate_blocked_shadow_decision_append" not in shadow_result.blocked_by and "mode_off" not in shadow_result.blocked_by and "mode_halted" not in shadow_result.blocked_by,
        "observer_cycle_gate_allows_resolver": calls["resolve"] == 1 and observer_result.appended_shadow_decision is True and observer_result.appended_forecast_outcomes == 1,
        "observer_gate_reports_allowed_mode": observer_result.mode_runtime_gate is not None and observer_result.mode_runtime_gate.current_mode == AutoTradeMode.SHADOW and observer_result.mode_runtime_gate.allow_forecast_outcome_resolution is True and not observer_result.mode_runtime_gate.blocked_by,
        "observer_result_not_gate_blocked": "mode_runtime_gate_blocked_forecast_outcome_resolution" not in observer_result.blocked_by and "mode_off" not in observer_result.blocked_by and "mode_halted" not in observer_result.blocked_by,
        "shadow_code_has_both_block_and_allow_paths": "mode_runtime_gate_blocked_shadow_decision_append" in shadow_once_source and "run_latest_market_state_shadow_decision" in shadow_once_source,
        "observer_code_has_both_block_and_allow_paths": "mode_runtime_gate_blocked_forecast_outcome_resolution" in observer_text and "resolve_due_shadow_forecast_outcomes" in observer_once_source,
        "no_broker_or_ui_imports": not any(token in combined_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BG: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bg_shadow_observer_runtime_gate_shadow_allow_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "shadow_cycle_gate_allows_shadow_impl": checks["shadow_cycle_gate_allows_shadow_impl"],
            "shadow_gate_reports_allowed_mode": checks["shadow_gate_reports_allowed_mode"],
            "shadow_result_not_gate_blocked": checks["shadow_result_not_gate_blocked"],
            "observer_cycle_gate_allows_resolver": checks["observer_cycle_gate_allows_resolver"],
            "observer_gate_reports_allowed_mode": checks["observer_gate_reports_allowed_mode"],
            "observer_result_not_gate_blocked": checks["observer_result_not_gate_blocked"],
            "no_broker_or_ui_imports": checks["no_broker_or_ui_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "calls": calls,
        "shadow_result": shadow_result.to_dict(),
        "observer_result": observer_result.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
