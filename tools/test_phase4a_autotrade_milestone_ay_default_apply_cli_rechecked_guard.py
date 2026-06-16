# path: ./tools/test_phase4a_autotrade_milestone_ay_default_apply_cli_rechecked_guard.py
# desc: Guard default mode-change apply CLI uses readiness recheck. No broker/order execution.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_mode_state_records  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CLI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_once.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "btcts.apps.operator_ui",
    "streamlit",
    "apply_latest_mode_change_command_once(",
    "from btcts.autotrade.execution import apply_latest_mode_change_command_once\n",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "submit_mode_change_command_request",
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


def command_row(command_id: str, *, command_type: str, accepted: bool, current_mode: str, target: str | None, blocked_by: list[str]) -> dict:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated" if command_type == "REQUEST_MODE_CHANGE" else "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "guard",
            "requested_at": "2026-06-13T06:10:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "default_cli_rechecked"],
            "note": "{}",
            "confirmation_required": True,
        },
    }


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


def shadow_row(decision_id: str) -> dict:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": f"fcst_{decision_id}", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["default_cli_rechecked_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row(forecast_id: str) -> dict:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_default_cli_rechecked",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_default_cli_rechecked",
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


def seed_health_ledgers(root: Path, *, observer_finished_at: str) -> None:
    write_jsonl(root / "autotrade/decisions/observer_runs.jsonl", [observer_row("obs_default_cli_rechecked", observer_finished_at)])
    write_jsonl(root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row("dec_default_cli_rechecked")])
    write_jsonl(root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row("fcst_default_cli_rechecked")])


def run_cli(root: Path, *args: str) -> tuple[int, dict]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "btcts.apps.autotrade_apply_mode_change_once", *args],
        cwd=REPO_ROOT,
        env={**env, ENV_AUTOTRADE_RUNTIME_ROOT: str(root)},
        text=True,
        capture_output=True,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    if proc.returncode not in (0, 2):
        payload = {"stdout": proc.stdout, "stderr": proc.stderr}
    return proc.returncode, payload


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_default_cli_rechecked_hot"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(command_path, [command_row("cmd_ay_shadow", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="SHADOW", blocked_by=[])])
        seed_health_ledgers(hot_root, observer_finished_at=fresh_ts)
        fresh_rc, fresh_payload = run_cli(hot_root, "--max-lines", "100", "--max-observer-run-age-sec", "60", "--allow-warnings")
        rows_after_fresh = read_mode_state_records(mode_path, max_lines=100)
        fresh_skip_rc, fresh_skip_payload = run_cli(hot_root, "--max-lines", "100", "--max-observer-run-age-sec", "60", "--allow-warnings")

        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(command_path, [command_row("cmd_ay_live_stale", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="LIVE_MIN_SIZE", blocked_by=[])])
        seed_health_ledgers(hot_root, observer_finished_at=stale_ts)
        stale_rc, stale_payload = run_cli(hot_root, "--max-lines", "100", "--max-observer-run-age-sec", "60", "--allow-warnings")
        rows_after_stale = read_mode_state_records(mode_path, max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = CLI_FILE.read_text(encoding="utf-8")
    imports = imports_from(CLI_FILE)
    checks = {
        "default_cli_imports_rechecked_applier": "apply_latest_mode_change_command_once_with_readiness_recheck" in text,
        "default_cli_no_plain_applier_call": not any(token in text for token in FORBIDDEN_TOKENS),
        "default_cli_args_include_recheck_controls": "--max-observer-run-age-sec" in text and "--allow-warnings" in text,
        "fresh_cli_applies_with_recheck": fresh_rc == 0 and fresh_payload.get("applied") is True and fresh_payload.get("readiness_ready") is True and fresh_payload.get("command_id") == "cmd_ay_shadow" and len(rows_after_fresh.rows) == 1,
        "fresh_cli_idempotent_skip": fresh_skip_rc == 2 and fresh_skip_payload.get("skipped") is True and fresh_skip_payload.get("skip_reason") == "no_unapplied_accepted_mode_change_command",
        "stale_cli_rejects_and_records": stale_rc == 2 and stale_payload.get("rejected_by_readiness") is True and "observer_run_stale" in (stale_payload.get("blocked_by") or []) and len(rows_after_stale.rows) == 1 and rows_after_stale.rows[-1].mode_changed is False,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in imports) and "streamlit" not in imports,
        "no_broker": fresh_payload.get("would_send_to_broker") is False and stale_payload.get("would_send_to_broker") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AY: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ay_default_apply_cli_rechecked_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "default_apply_cli_uses_readiness_recheck": checks["default_cli_imports_rechecked_applier"] and checks["default_cli_no_plain_applier_call"],
            "default_apply_cli_recheck_args_present": checks["default_cli_args_include_recheck_controls"],
            "fresh_cli_applies_with_recheck": checks["fresh_cli_applies_with_recheck"],
            "stale_cli_rejects_and_records": checks["stale_cli_rejects_and_records"],
            "idempotency_present": checks["fresh_cli_idempotent_skip"],
            "no_ui_no_broker": checks["no_ui_imports"] and checks["no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "fresh_cli": {"returncode": fresh_rc, "payload": fresh_payload},
        "fresh_skip_cli": {"returncode": fresh_skip_rc, "payload": fresh_skip_payload},
        "stale_cli": {"returncode": stale_rc, "payload": stale_payload},
        "rows_after_stale": rows_after_stale.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
