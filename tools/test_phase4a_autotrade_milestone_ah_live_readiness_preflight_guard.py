# path: ./tools/test_phase4a_autotrade_milestone_ah_live_readiness_preflight_guard.py
# desc: Guard AutoTrade live readiness preflight is read-only and blocks unsafe live escalation.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.readiness import evaluate_autotrade_live_readiness  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/readiness.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_readiness_once.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/__init__.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "btcts.apps.operator_ui",
    "streamlit",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "append_observer_run_record",
    "resolve_due_shadow_forecast_outcomes",
    "append_forecast_outcome_link",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "append_decision_jsonl",
    "validate_and_append_command",
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


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def observer_row(run_id: str, finished_at: str) -> dict:
    return {
        "run_id": run_id,
        "started_at": finished_at,
        "finished_at": finished_at,
        "requested_cycles": 2,
        "completed_cycles": 2,
        "appended_shadow_decision_count": 1,
        "appended_forecast_outcome_count": 1,
        "duplicate_snapshot_skipped_count": 1,
        "skip_duplicate_snapshot": True,
        "blocked_by": [],
        "would_send_to_broker": False,
        "bounded": True,
        "source": "autotrade.observer_cycle_bounded",
    }


def shadow_row() -> dict:
    return {
        "decision_id": "dec_readiness",
        "mode": "SHADOW",
        "snapshot_id": "snap_readiness",
        "forecast_id": "fcst_readiness",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_readiness", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["readiness_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict:
    return {
        "forecast_id": "fcst_readiness",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_readiness",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_readiness",
        "forecast_direction": "down",
        "forecast_confidence": "medium",
        "expected_change": "strengthen_sell",
        "drivers": ["sell_pressure_or_ground"],
        "blocked_by": [],
        "result": "hit",
        "direction_hit": True,
        "change_type_hit": True,
        "divergence_reasons": [],
    }


def seed_ledgers(root: Path, *, observer_ts: str) -> None:
    write_jsonl(root / "autotrade/decisions/observer_runs.jsonl", [observer_row("obs_readiness", observer_ts)])
    write_jsonl(root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row()])
    write_jsonl(root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row()])


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    hot_root = REPO_ROOT / "tmp/btc_ts_hot"
    cold_named_root = REPO_ROOT / "tmp/btc_ts_cold"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        seed_ledgers(hot_root, observer_ts=fresh_ts)
        ready = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        unconfirmed = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=False,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        warnings_blocked = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=False,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        seed_ledgers(hot_root, observer_ts=stale_ts)
        stale = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(cold_named_root)
        seed_ledgers(cold_named_root, observer_ts=fresh_ts)
        cold = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        seed_ledgers(hot_root, observer_ts=fresh_ts)
        cli_ready = subprocess.run(
            [sys.executable, "-m", "btcts.apps.autotrade_readiness_once", "--current-mode", "ARMED_DRY_RUN", "--target-mode", "LIVE_MIN_SIZE", "--human-confirmed", "--allow-warnings", "--max-observer-run-age-sec", "60"],
            cwd=REPO_ROOT,
            env={**env, ENV_AUTOTRADE_RUNTIME_ROOT: str(hot_root)},
            text=True,
            capture_output=True,
        )
        cli_blocked = subprocess.run(
            [sys.executable, "-m", "btcts.apps.autotrade_readiness_once", "--current-mode", "ARMED_DRY_RUN", "--target-mode", "LIVE_MIN_SIZE", "--max-observer-run-age-sec", "60"],
            cwd=REPO_ROOT,
            env={**env, ENV_AUTOTRADE_RUNTIME_ROOT: str(hot_root)},
            text=True,
            capture_output=True,
        )
        cli_ready_payload = json.loads(cli_ready.stdout) if cli_ready.stdout.strip() else {}
        cli_blocked_payload = json.loads(cli_blocked.stdout) if cli_blocked.stdout.strip() else {}
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "readiness_result_present": ready.ready is True and ready.target_mode == AutoTradeMode.LIVE_MIN_SIZE,
        "human_confirmation_blocks": unconfirmed.ready is False and "human_confirmation_required" in unconfirmed.blocked_by,
        "warnings_can_block": warnings_blocked.ready is False and "runtime_health_warnings_present" in warnings_blocked.blocked_by,
        "stale_observer_blocks": stale.ready is False and "observer_run_stale" in stale.blocked_by,
        "cold_runtime_blocks_live": cold.ready is False and "autotrade_runtime_not_live_ready" in cold.blocked_by,
        "cli_exit_semantics": cli_ready.returncode == 0 and cli_ready_payload.get("ready") is True and cli_blocked.returncode == 2 and cli_blocked_payload.get("ready") is False,
        "read_only_no_mode_change_no_broker": ready.would_send_to_broker is False and ready.read_only is True and ready.mode_changed is False,
        "json_safe_result": json.loads(json.dumps(ready.to_dict(), ensure_ascii=False))["ready"] is True,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in all_imports) and "streamlit" not in all_imports,
        "no_forbidden_tokens": not any(token in all_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AH: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ah_live_readiness_preflight_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "live_readiness_preflight_present": checks["readiness_result_present"],
            "human_confirmation_blocks_live": checks["human_confirmation_blocks"],
            "runtime_health_blocks_live": checks["stale_observer_blocks"] and checks["cold_runtime_blocks_live"],
            "warning_policy_present": checks["warnings_can_block"],
            "cli_exit_semantics_present": checks["cli_exit_semantics"],
            "read_only_no_mode_change_no_broker": checks["read_only_no_mode_change_no_broker"] and checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "ready": ready.to_dict(),
        "unconfirmed": unconfirmed.to_dict(),
        "warnings_blocked": warnings_blocked.to_dict(),
        "stale": stale.to_dict(),
        "cold": cold.to_dict(),
        "cli_ready": {"returncode": cli_ready.returncode, "payload": cli_ready_payload},
        "cli_blocked": {"returncode": cli_blocked.returncode, "payload": cli_blocked_payload},
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
