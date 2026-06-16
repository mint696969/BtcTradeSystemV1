# path: ./tools/test_phase4a_autotrade_milestone_ax_autotrade_tab_rechecked_apply_preview_guard.py
# desc: Guard AutoTrade UI tab apply preview uses readiness-rechecked preview and remains read-only.

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
    default_command_ledger_path,
    default_mode_state_ledger_path,
    preview_latest_mode_change_command_apply_with_readiness_recheck,
    read_mode_state_records,
)
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
PREVIEW_STATUS_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
    "st.button(",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
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


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


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
            "requested_at": "2026-06-13T06:00:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "ui_rechecked_preview"],
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
        "reason_codes": ["ui_rechecked_preview_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row(forecast_id: str) -> dict:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_ui_rechecked_preview",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_ui_rechecked_preview",
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
    write_jsonl(root / "autotrade/decisions/observer_runs.jsonl", [observer_row("obs_ui_rechecked_preview", observer_finished_at)])
    write_jsonl(root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row("dec_ui_rechecked_preview")])
    write_jsonl(root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row("fcst_ui_rechecked_preview")])


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_ui_rechecked_preview_hot"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(command_path, [command_row("cmd_ax_live_stale", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="LIVE_MIN_SIZE", blocked_by=[])])
        seed_health_ledgers(hot_root, observer_finished_at=stale_ts)
        before_rows = read_mode_state_records(mode_path, max_lines=100)
        preview = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=60, allow_warnings=True)
        after_rows = read_mode_state_records(mode_path, max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    source = function_source(UI_FILE, "_render_mode_change_apply_preview_status")
    checks = {
        "ui_imports_rechecked_preview": "btcts.autotrade.execution" in imports and "preview_latest_mode_change_command_apply_with_readiness_recheck" in text,
        "ui_no_longer_imports_plain_preview": "preview_latest_mode_change_command_apply," not in text,
        "preview_status_uses_rechecked_function": "preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=500" in source,
        "preview_status_shows_recheck_fields": all(token in source for token in ("would_reject_by_readiness", "readiness_ready", "readiness", "blocked_by", "warnings", "health_state")),
        "preview_status_read_only_no_apply_no_broker": bool(source) and not any(token in source for token in PREVIEW_STATUS_FORBIDDEN_TOKENS),
        "rechecked_preview_contract_still_read_only": preview.would_apply is False and preview.would_reject_by_readiness is True and "observer_run_stale" in preview.blocked_by and len(before_rows.rows) == 0 and len(after_rows.rows) == 0,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AX: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ax_autotrade_tab_rechecked_apply_preview_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_uses_rechecked_apply_preview": checks["ui_imports_rechecked_preview"] and checks["preview_status_uses_rechecked_function"],
            "plain_apply_preview_removed_from_ui": checks["ui_no_longer_imports_plain_preview"],
            "readiness_recheck_fields_displayed": checks["preview_status_shows_recheck_fields"],
            "preview_status_read_only_no_apply_no_broker": checks["preview_status_read_only_no_apply_no_broker"],
            "rechecked_preview_contract_still_read_only": checks["rechecked_preview_contract_still_read_only"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "preview": preview.to_dict(),
        "mode_state_rows_after_preview": after_rows.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
