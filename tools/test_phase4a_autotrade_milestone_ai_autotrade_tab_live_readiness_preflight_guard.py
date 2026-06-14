# path: ./tools/test_phase4a_autotrade_milestone_ai_autotrade_tab_live_readiness_preflight_guard.py
# desc: Guard AutoTrade UI tab displays live readiness preflight read-only.

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

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "append_observer_run_record",
    "resolve_due_shadow_forecast_outcomes",
    "append_forecast_outcome_link",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "run_latest_market_state_shadow_decision",
    "run_shadow_decision_from_snapshot",
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


def observer_row(finished_at: str) -> dict:
    return {
        "run_id": "obs_ui_readiness",
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
        "decision_id": "dec_ui_readiness",
        "mode": "SHADOW",
        "snapshot_id": "snap_ui_readiness",
        "forecast_id": "fcst_ui_readiness",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_ui_readiness", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["ui_readiness_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict:
    return {
        "forecast_id": "fcst_ui_readiness",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_ui_readiness",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_ui_readiness",
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_ui_readiness_hot"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        write_jsonl(hot_root / "autotrade/decisions/observer_runs.jsonl", [observer_row(fresh_ts)])
        write_jsonl(hot_root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row()])
        write_jsonl(hot_root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row()])
        readiness = evaluate_autotrade_live_readiness(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            target_mode=AutoTradeMode.LIVE_MIN_SIZE,
            human_confirmed=True,
            allow_warnings=True,
            max_observer_run_age_sec=60,
            max_lines=100,
        )
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    checks = {
        "ui_imports_readiness": "btcts.autotrade.readiness" in imports and "evaluate_autotrade_live_readiness" in text,
        "ui_has_readiness_panel": "_render_live_readiness_preflight" in text and "Live Readiness Preflight" in text,
        "ui_displays_readiness_fields": all(token in text for token in ("current_mode", "target_mode", "ready", "transition_allowed", "human_confirmation_required", "human_confirmed", "allow_warnings", "mode_changed", "blocked_by", "warnings")),
        "ui_marks_read_only_no_mode_change": "readiness preflight is read-only" in text.lower() and "mode_changed" in text and "would_send_to_broker" in text,
        "readiness_contract_still_works": readiness.ready is True and readiness.mode_changed is False and readiness.would_send_to_broker is False,
        "ui_does_not_run_or_append_or_broker": not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AI: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ai_autotrade_tab_live_readiness_preflight_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_live_readiness_preflight_present": checks["ui_imports_readiness"] and checks["ui_has_readiness_panel"],
            "readiness_fields_displayed": checks["ui_displays_readiness_fields"],
            "ui_read_only_no_mode_change_no_broker": checks["ui_marks_read_only_no_mode_change"] and checks["ui_does_not_run_or_append_or_broker"],
            "readiness_contract_still_works": checks["readiness_contract_still_works"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "readiness": readiness.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
