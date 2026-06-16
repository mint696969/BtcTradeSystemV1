# path: ./tools/test_phase4a_autotrade_milestone_ae_runtime_health_snapshot_guard.py
# desc: Guard AutoTrade runtime health snapshot is read-only and detects stale/missing observer status.

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

from btcts.autotrade.health import build_autotrade_runtime_health_snapshot  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/health.py",
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
        "decision_id": "dec_health",
        "mode": "SHADOW",
        "snapshot_id": "snap_health",
        "forecast_id": "fcst_health",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_health", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["health_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict:
    return {
        "forecast_id": "fcst_health",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_health",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_health",
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
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_ae_guard"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    stale_ts = (now - timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    run_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
    shadow_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        write_jsonl(run_path, [observer_row("obs_fresh", fresh_ts)])
        write_jsonl(shadow_path, [shadow_row()])
        write_jsonl(outcome_path, [outcome_row()])
        fresh = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=60, now=now)
        stale = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=1, now=now)
        write_jsonl(run_path, [observer_row("obs_stale", stale_ts)])
        stale_by_time = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=60, now=now)
        run_path.unlink()
        missing = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=60, now=now)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    fresh_data = fresh.to_dict()
    checks = {
        "health_snapshot_present": fresh.observer_runs.total_rows == 1 and fresh.shadow_decisions.total_rows == 1 and fresh.forecast_outcomes.total_rows == 1,
        "fresh_observer_detected": fresh.observer_run_fresh is True and fresh.observer_run_age_sec is not None and fresh.observer_run_age_sec <= 60,
        "stale_threshold_blocks": stale.health_state == "blocked" and "observer_run_stale" in stale.blocked_by,
        "stale_finished_at_blocks": stale_by_time.health_state == "blocked" and "observer_run_stale" in stale_by_time.blocked_by,
        "missing_observer_blocks": missing.health_state == "blocked" and "observer_run_missing" in missing.blocked_by,
        "json_safe_snapshot": json.loads(json.dumps(fresh_data, ensure_ascii=False))["observer_runs"]["total_rows"] == 1,
        "read_only_no_broker": fresh.would_send_to_broker is False and fresh.read_only is True,
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
    failures.extend(f"protected lower-layer dirty during milestone AE: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ae_runtime_health_snapshot_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "runtime_health_snapshot_present": checks["health_snapshot_present"],
            "observer_freshness_present": checks["fresh_observer_detected"],
            "stale_observer_blocks": checks["stale_threshold_blocks"] and checks["stale_finished_at_blocks"],
            "missing_observer_blocks": checks["missing_observer_blocks"],
            "read_only_no_ui_no_broker": checks["read_only_no_broker"] and checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "fresh": fresh.to_dict(),
        "stale_threshold": stale.to_dict(),
        "stale_by_time": stale_by_time.to_dict(),
        "missing": missing.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
