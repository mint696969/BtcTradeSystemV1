# path: ./tools/test_phase4a_autotrade_milestone_av_mode_change_applier_readiness_recheck_guard.py
# desc: Guard readiness-rechecked mode-change applier. Rechecks runtime health before writing mode_state. No broker execution.

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

from btcts.autotrade.execution import (  # noqa: E402
    apply_latest_mode_change_command_once_with_readiness_recheck,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    read_mode_state_records,
)
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_rechecked_once.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py",
)
FORBIDDEN_TEXT_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_rechecked_once.py",
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
            "requested_at": "2026-06-13T05:40:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "readiness_recheck"],
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
        "reason_codes": ["readiness_recheck_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row(forecast_id: str) -> dict:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_readiness_recheck",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_readiness_recheck",
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
    write_jsonl(root / "autotrade/decisions/observer_runs.jsonl", [observer_row("obs_readiness_recheck", observer_finished_at)])
    write_jsonl(root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row("dec_readiness_recheck")])
    write_jsonl(root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row("fcst_readiness_recheck")])


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_recheck_hot"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()

        write_jsonl(command_path, [command_row("cmd_av_shadow", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="SHADOW", blocked_by=[])])
        seed_health_ledgers(hot_root, observer_finished_at=fresh_ts)
        applied = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=60, allow_warnings=True)
        rows_after_apply = read_mode_state_records(mode_path, max_lines=100)
        second = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=60, allow_warnings=True)

        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(command_path, [command_row("cmd_av_live_stale", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="LIVE_MIN_SIZE", blocked_by=[])])
        seed_health_ledgers(hot_root, observer_finished_at=stale_ts)
        rejected = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=60, allow_warnings=True)
        rows_after_reject = read_mode_state_records(mode_path, max_lines=100)
        rejected_second = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=60, allow_warnings=True)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        cli_proc = subprocess.run(
            [sys.executable, "-m", "btcts.apps.autotrade_apply_mode_change_rechecked_once", "--max-lines", "100", "--max-observer-run-age-sec", "60", "--allow-warnings"],
            cwd=REPO_ROOT,
            env={**env, ENV_AUTOTRADE_RUNTIME_ROOT: str(hot_root)},
            text=True,
            capture_output=True,
        )
        cli_payload = json.loads(cli_proc.stdout) if cli_proc.stdout.strip() else {}
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    forbidden_text = "\n".join(path.read_text(encoding="utf-8") for path in FORBIDDEN_TEXT_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "readiness_recheck_applier_present": "ModeChangeCommandReadinessApplyResult" in all_text and "apply_latest_mode_change_command_once_with_readiness_recheck" in all_text,
        "fresh_readiness_applies": applied.applied is True and applied.readiness_ready is True and applied.command_id == "cmd_av_shadow" and applied.current_mode_after == "SHADOW" and len(rows_after_apply.rows) == 1,
        "applied_idempotent_skip": second.applied is False and second.skipped is True and second.skip_reason == "no_unapplied_accepted_mode_change_command",
        "stale_readiness_rejects_and_records": rejected.applied is False and rejected.rejected_by_readiness is True and rejected.record_appended is True and "observer_run_stale" in rejected.blocked_by and len(rows_after_reject.rows) == 1 and rows_after_reject.rows[-1].mode_changed is False,
        "rejected_idempotent_skip": rejected_second.applied is False and rejected_second.skipped is True and rejected_second.skip_reason == "no_unapplied_accepted_mode_change_command",
        "cli_skip_exit_semantics": cli_proc.returncode == 2 and cli_payload.get("skipped") is True,
        "json_safe_result": json.loads(json.dumps(rejected.to_dict(), ensure_ascii=False, default=str))["rejected_by_readiness"] is True,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in all_imports) and "streamlit" not in all_imports,
        "no_forbidden_tokens": not any(token in forbidden_text for token in FORBIDDEN_TOKENS),
        "no_broker": applied.would_send_to_broker is False and rejected.would_send_to_broker is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if cli_proc.returncode not in (0, 2):
        failures.append(f"cli stderr: {cli_proc.stderr}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AV: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_av_mode_change_applier_readiness_recheck_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "readiness_recheck_applier_present": checks["readiness_recheck_applier_present"],
            "fresh_readiness_applies": checks["fresh_readiness_applies"],
            "stale_readiness_rejects_and_records": checks["stale_readiness_rejects_and_records"],
            "idempotency_present": checks["applied_idempotent_skip"] and checks["rejected_idempotent_skip"],
            "cli_exit_semantics_present": checks["cli_skip_exit_semantics"],
            "no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"] and checks["no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "applied": applied.to_dict(),
        "second": second.to_dict(),
        "rejected": rejected.to_dict(),
        "rejected_second": rejected_second.to_dict(),
        "rows_after_reject": rows_after_reject.to_dict(),
        "cli": {"returncode": cli_proc.returncode, "payload": cli_payload},
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
