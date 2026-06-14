# path: ./tools/test_phase4a_autotrade_milestone_bi_bounded_shadow_runtime_gate_guard.py
# desc: Guard bounded shadow runner respects mode_runtime_gate for OFF block and SHADOW allow. No broker execution.

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
from btcts.autotrade.live_shadow import ShadowDecisionVerticalResult, default_shadow_decision_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
import btcts.autotrade.shadow_cycle as shadow_cycle  # noqa: E402

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
            changed_at="2026-06-13T07:50:00Z",
            source_command_id=f"cmd_bi_{mode.value.lower()}",
            requested_by="guard",
            accepted=True,
            mode_changed=mode != AutoTradeMode.OFF,
            reason_codes=("guard", "bounded_shadow_gate"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    original_shadow_impl = shadow_cycle.run_latest_market_state_shadow_decision
    hot_root = REPO_ROOT / "tmp/btc_ts_bounded_shadow_gate_hot"
    calls = {"off_shadow_impl": 0, "shadow_impl": 0, "shadow_persist_true": 0, "shadow_persist_false": 0}

    def forbidden_shadow_impl(*args, **kwargs):
        calls["off_shadow_impl"] += 1
        raise AssertionError("shadow implementation should not run when OFF gate blocks")

    def fake_shadow_impl(*args, **kwargs):
        calls["shadow_impl"] += 1
        persist = bool(kwargs.get("persist"))
        if persist:
            calls["shadow_persist_true"] += 1
        else:
            calls["shadow_persist_false"] += 1
        n = calls["shadow_impl"]
        return ShadowDecisionVerticalResult(
            snapshot_id=f"snap_bi_shadow_allowed_{n}",
            forecast_id=f"fcst_bi_shadow_allowed_{n}",
            decision_id=f"dec_bi_shadow_allowed_{n}",
            candidate_action="WAIT",
            risk_allowed=False,
            appended=persist,
            ledger_path=default_shadow_decision_ledger_path(ensure=False),
            blocked_by=(),
            would_send_to_broker=False,
            decision=None,
            diagnostics=None,
        )

    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        write_mode(mode_path, AutoTradeMode.OFF)
        shadow_cycle.run_latest_market_state_shadow_decision = forbidden_shadow_impl
        off_bounded = shadow_cycle.run_shadow_cycle_bounded(max_cycles=2, interval_sec=0.0, persist=True, skip_duplicate_snapshot=True)

        write_mode(mode_path, AutoTradeMode.SHADOW)
        shadow_cycle.run_latest_market_state_shadow_decision = fake_shadow_impl
        shadow_bounded = shadow_cycle.run_shadow_cycle_bounded(max_cycles=2, interval_sec=0.0, persist=True, skip_duplicate_snapshot=True)
    finally:
        shadow_cycle.run_latest_market_state_shadow_decision = original_shadow_impl
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    shadow_text = SHADOW_FILE.read_text(encoding="utf-8")
    bounded_source = function_source(SHADOW_FILE, "run_shadow_cycle_bounded")
    once_source = function_source(SHADOW_FILE, "run_shadow_cycle_once")
    checks = {
        "off_bounded_blocks_without_shadow_impl": calls["off_shadow_impl"] == 0 and off_bounded.completed_cycles == 2 and off_bounded.appended_count == 0,
        "off_bounded_results_gate_blocked": all("mode_off" in item.blocked_by and "mode_runtime_gate_blocked_shadow_decision_append" in item.blocked_by and item.appended is False for item in off_bounded.results),
        "off_bounded_no_snapshot_no_duplicate": off_bounded.duplicate_skipped_count == 0 and all(item.result.snapshot_id is None for item in off_bounded.results),
        "shadow_bounded_allows_shadow_impl": calls["shadow_impl"] == 4 and calls["shadow_persist_false"] == 2 and calls["shadow_persist_true"] == 2,
        "shadow_bounded_counts_allowed_appends": shadow_bounded.completed_cycles == 2 and shadow_bounded.appended_count == 2 and shadow_bounded.duplicate_skipped_count == 0,
        "shadow_bounded_results_not_gate_blocked": all("mode_runtime_gate_blocked_shadow_decision_append" not in item.blocked_by and "mode_off" not in item.blocked_by and "mode_halted" not in item.blocked_by for item in shadow_bounded.results),
        "shadow_bounded_results_report_shadow_gate": all(item.mode_runtime_gate is not None and item.mode_runtime_gate.current_mode == AutoTradeMode.SHADOW and item.mode_runtime_gate.allow_shadow_decision_append and not item.mode_runtime_gate.blocked_by for item in shadow_bounded.results),
        "bounded_code_uses_one_shot_gate_path": "run_shadow_cycle_once" in bounded_source and "should_persist" in bounded_source and "mode_runtime_gate_blocked_shadow_decision_append" in once_source,
        "no_broker_or_ui_imports": not any(token in shadow_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BI: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bi_bounded_shadow_runtime_gate_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "off_bounded_blocks_without_shadow_impl": checks["off_bounded_blocks_without_shadow_impl"],
            "off_bounded_results_gate_blocked": checks["off_bounded_results_gate_blocked"],
            "shadow_bounded_allows_shadow_impl": checks["shadow_bounded_allows_shadow_impl"],
            "shadow_bounded_counts_allowed_appends": checks["shadow_bounded_counts_allowed_appends"],
            "shadow_bounded_results_not_gate_blocked": checks["shadow_bounded_results_not_gate_blocked"],
            "shadow_bounded_results_report_shadow_gate": checks["shadow_bounded_results_report_shadow_gate"],
            "no_broker_or_ui_imports": checks["no_broker_or_ui_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "calls": calls,
        "off_bounded": off_bounded.to_dict(),
        "shadow_bounded": shadow_bounded.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
