# path: ./tools/test_phase4a_autotrade_milestone_aj_mode_change_command_request_ledger_guard.py
# desc: Guard mode-change command requests are readiness-gated ledger records only.

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

from btcts.autotrade.execution import read_command_ledger, submit_mode_change_command_request  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_change_request.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py",
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
        "decision_id": "dec_mode_request",
        "mode": "SHADOW",
        "snapshot_id": "snap_mode_request",
        "forecast_id": "fcst_mode_request",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_mode_request", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["mode_request_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict:
    return {
        "forecast_id": "fcst_mode_request",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_mode_request",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_mode_request",
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
    write_jsonl(root / "autotrade/decisions/observer_runs.jsonl", [observer_row("obs_mode_request", observer_ts)])
    write_jsonl(root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row()])
    write_jsonl(root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row()])


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_request_hot"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    command_path = hot_root / "autotrade/commands/command_requests.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if command_path.exists():
            command_path.unlink()
        seed_ledgers(hot_root, observer_ts=fresh_ts)
        accepted = submit_mode_change_command_request(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            requested_by="guard",
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        unconfirmed = submit_mode_change_command_request(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            requested_by="guard",
            human_confirmed=False,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        seed_ledgers(hot_root, observer_ts=stale_ts)
        stale = submit_mode_change_command_request(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            requested_by="guard",
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
        rows = read_command_ledger(command_path)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    accepted_note = json.loads(accepted.command_record.command.note)
    checks = {
        "mode_change_request_helper_present": "submit_mode_change_command_request" in all_text and "ModeChangeCommandRequestResult" in all_text,
        "accepted_ready_request_appended": accepted.accepted is True and accepted.appended is True and accepted.readiness.ready is True and accepted.command_record.command.command_type.value == "REQUEST_MODE_CHANGE",
        "readiness_snapshot_embedded": accepted_note.get("kind") == "autotrade.mode_change_readiness_snapshot" and accepted_note.get("ready") is True and accepted_note.get("runtime_live_ready") is True,
        "unconfirmed_request_rejected": unconfirmed.accepted is False and "human_confirmation_required" in unconfirmed.blocked_by,
        "stale_request_rejected": stale.accepted is False and "readiness_preflight_not_ready" in stale.blocked_by and "observer_run_stale" in stale.blocked_by,
        "ledger_records_appended": command_path.exists() and len(rows) == 3 and rows[0].accepted is True and rows[1].accepted is False and rows[2].accepted is False,
        "no_mode_change_no_broker": accepted.mode_changed is False and accepted.would_send_to_broker is False and stale.mode_changed is False and stale.would_send_to_broker is False,
        "json_safe_result": json.loads(json.dumps(accepted.to_dict(), ensure_ascii=False, default=str))["accepted"] is True,
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
    failures.extend(f"protected lower-layer dirty during milestone AJ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_aj_mode_change_command_request_ledger_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_change_command_request_present": checks["mode_change_request_helper_present"],
            "accepted_when_readiness_ready": checks["accepted_ready_request_appended"],
            "readiness_snapshot_embedded": checks["readiness_snapshot_embedded"],
            "blocked_when_unconfirmed_or_not_ready": checks["unconfirmed_request_rejected"] and checks["stale_request_rejected"],
            "ledger_append_only_present": checks["ledger_records_appended"],
            "no_mode_change_no_broker": checks["no_mode_change_no_broker"] and checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "accepted": accepted.to_dict(),
        "unconfirmed": unconfirmed.to_dict(),
        "stale": stale.to_dict(),
        "ledger_rows": [row.to_dict() for row in rows],
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
