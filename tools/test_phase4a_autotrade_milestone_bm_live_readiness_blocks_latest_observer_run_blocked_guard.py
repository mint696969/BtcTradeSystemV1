# path: ./tools/test_phase4a_autotrade_milestone_bm_live_readiness_blocks_latest_observer_run_blocked_guard.py
# desc: Guard live readiness blocks dangerous targets when latest observer_run is fresh but blocked. No append from readiness, no broker.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.ledger import ObserverRunRecord, append_observer_run_record, default_observer_run_ledger_path  # noqa: E402
from btcts.autotrade.readiness import evaluate_autotrade_live_readiness  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

READINESS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/readiness.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "append_observer_run_record",
    "append_mode_state_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
    "streamlit",
    "btcts.apps.operator_ui",
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


def write_observer_run(path: Path, *, blocked: bool) -> None:
    if path.exists():
        path.unlink()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    append_observer_run_record(
        path,
        ObserverRunRecord(
            run_id="obs_bm_blocked" if blocked else "obs_bm_allowed",
            started_at=now,
            finished_at=now,
            requested_cycles=2,
            completed_cycles=2,
            appended_shadow_decision_count=0 if blocked else 2,
            appended_forecast_outcome_count=0 if blocked else 2,
            duplicate_snapshot_skipped_count=0,
            skip_duplicate_snapshot=True,
            blocked_by=("mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution") if blocked else (),
            would_send_to_broker=False,
            bounded=True,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_live_readiness_latest_observer_blocked_hot"
    before_rows = -1
    after_rows = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        observer_path = default_observer_run_ledger_path(ensure=True)
        write_observer_run(observer_path, blocked=True)
        before_rows = len(observer_path.read_text(encoding="utf-8").splitlines())
        blocked_live = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=999999999,
            max_lines=100,
        )
        blocked_non_live = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.SHADOW,
            target_mode=AutoTradeMode.PAPER_OR_REPLAY,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=999999999,
            max_lines=100,
        )
        write_observer_run(observer_path, blocked=False)
        allowed_live = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=999999999,
            max_lines=100,
        )
        after_rows = len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = READINESS_FILE.read_text(encoding="utf-8")
    source = function_source(READINESS_FILE, "evaluate_autotrade_live_readiness")
    checks = {
        "readiness_checks_latest_observer_blocked_for_dangerous_modes": "observer_run_latest_blocked_for_live_target" in source and "latest_blocked_by" in source and "DANGEROUS_MODES" in source,
        "fresh_blocked_observer_blocks_live_target": blocked_live.ready is False and "observer_run_latest_blocked_for_live_target" in blocked_live.blocked_by and "mode_runtime_gate_blocked_shadow_decision_append" in blocked_live.blocked_by,
        "fresh_blocked_observer_preserved_in_health_payload": tuple(blocked_live.health.observer_runs.latest_blocked_by) == ("mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution"),
        "fresh_blocked_observer_not_applied_to_non_live_target": "observer_run_latest_blocked_for_live_target" not in blocked_non_live.blocked_by,
        "allowed_observer_does_not_add_latest_blocked_reason": "observer_run_latest_blocked_for_live_target" not in allowed_live.blocked_by,
        "readiness_eval_did_not_append_observer_rows": before_rows == 1 and after_rows == 1,
        "readiness_no_ui_runner_or_broker": not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BM: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bm_live_readiness_blocks_latest_observer_run_blocked_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "readiness_checks_latest_observer_blocked_for_dangerous_modes": checks["readiness_checks_latest_observer_blocked_for_dangerous_modes"],
            "fresh_blocked_observer_blocks_live_target": checks["fresh_blocked_observer_blocks_live_target"],
            "fresh_blocked_observer_not_applied_to_non_live_target": checks["fresh_blocked_observer_not_applied_to_non_live_target"],
            "allowed_observer_does_not_add_latest_blocked_reason": checks["allowed_observer_does_not_add_latest_blocked_reason"],
            "readiness_eval_did_not_append_observer_rows": checks["readiness_eval_did_not_append_observer_rows"],
            "readiness_no_ui_runner_or_broker": checks["readiness_no_ui_runner_or_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "blocked_live": blocked_live.to_dict(),
        "blocked_non_live": blocked_non_live.to_dict(),
        "allowed_live": allowed_live.to_dict(),
        "before_rows": before_rows,
        "after_rows": after_rows,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
