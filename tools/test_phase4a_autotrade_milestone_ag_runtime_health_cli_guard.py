# path: ./tools/test_phase4a_autotrade_milestone_ag_runtime_health_cli_guard.py
# desc: Guard AutoTrade runtime health one-shot CLI is read-only and uses health exit semantics.

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

from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CLI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_health_once.py"
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
        "decision_id": "dec_health_cli",
        "mode": "SHADOW",
        "snapshot_id": "snap_health_cli",
        "forecast_id": "fcst_health_cli",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_health_cli", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["health_cli_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict:
    return {
        "forecast_id": "fcst_health_cli",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_health_cli",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_health_cli",
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


def parse_json(stdout: str) -> dict:
    return json.loads(stdout)


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_ag_guard"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    run_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
    shadow_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        write_jsonl(run_path, [observer_row("obs_health_cli_fresh", fresh_ts)])
        write_jsonl(shadow_path, [shadow_row()])
        write_jsonl(outcome_path, [outcome_row()])
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        base_cmd = [sys.executable, "-m", "btcts.apps.autotrade_health_once", "--max-observer-run-age-sec", "60"]
        fresh_proc = subprocess.run(base_cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        fresh_payload = parse_json(fresh_proc.stdout) if fresh_proc.stdout.strip() else {}
        strict_proc = subprocess.run(base_cmd + ["--strict-warn"], cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        strict_payload = parse_json(strict_proc.stdout) if strict_proc.stdout.strip() else {}
        write_jsonl(run_path, [observer_row("obs_health_cli_stale", stale_ts)])
        stale_proc = subprocess.run(base_cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        stale_payload = parse_json(stale_proc.stdout) if stale_proc.stdout.strip() else {}
        run_path.unlink()
        missing_proc = subprocess.run(base_cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        missing_payload = parse_json(missing_proc.stdout) if missing_proc.stdout.strip() else {}
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = CLI_FILE.read_text(encoding="utf-8")
    imports = imports_from(CLI_FILE)
    checks = {
        "cli_present": CLI_FILE.exists() and "build_autotrade_runtime_health_snapshot" in text,
        "fresh_warn_exit_zero": fresh_proc.returncode == 0 and fresh_payload.get("observer_run_fresh") is True and fresh_payload.get("would_send_to_broker") is False,
        "strict_warn_exit_one": strict_proc.returncode == 1 and strict_payload.get("health_state") == "warn",
        "stale_exit_two": stale_proc.returncode == 2 and "observer_run_stale" in stale_payload.get("blocked_by", []),
        "missing_exit_two": missing_proc.returncode == 2 and "observer_run_missing" in missing_payload.get("blocked_by", []),
        "json_safe_cli_output": fresh_payload.get("observer_runs", {}).get("total_rows") == 1,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in imports) and "streamlit" not in imports,
        "no_forbidden_tokens": not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if fresh_proc.returncode not in (0, 1, 2):
        failures.append(f"fresh stderr: {fresh_proc.stderr}")
    if strict_proc.returncode not in (0, 1, 2):
        failures.append(f"strict stderr: {strict_proc.stderr}")
    if stale_proc.returncode not in (0, 1, 2):
        failures.append(f"stale stderr: {stale_proc.stderr}")
    if missing_proc.returncode not in (0, 1, 2):
        failures.append(f"missing stderr: {missing_proc.stderr}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AG: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ag_runtime_health_cli_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "runtime_health_cli_present": checks["cli_present"],
            "fresh_health_exit_semantics": checks["fresh_warn_exit_zero"] and checks["strict_warn_exit_one"],
            "blocked_health_exit_semantics": checks["stale_exit_two"] and checks["missing_exit_two"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "fresh": {"returncode": fresh_proc.returncode, "payload": fresh_payload},
        "strict_warn": {"returncode": strict_proc.returncode, "payload": strict_payload},
        "stale": {"returncode": stale_proc.returncode, "payload": stale_payload},
        "missing": {"returncode": missing_proc.returncode, "payload": missing_payload},
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
