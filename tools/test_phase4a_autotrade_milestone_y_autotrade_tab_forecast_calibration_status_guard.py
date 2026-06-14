# path: ./tools/test_phase4a_autotrade_milestone_y_autotrade_tab_forecast_calibration_status_guard.py
# desc: Guard AutoTrade UI tab displays forecast outcome calibration summary read-only.

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

from btcts.autotrade.ledger import summarize_forecast_outcome_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
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


def outcome_row(forecast_id: str, *, result: str, confidence: str, divergence: list[str] | None = None) -> dict:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": f"snap_{forecast_id}",
        "target_ts": "2026-06-13T01:00:00Z",
        "actual_snapshot_id": f"actual_{forecast_id}",
        "forecast_direction": "down",
        "forecast_confidence": confidence,
        "expected_change": "strengthen_sell",
        "drivers": ["sell_pressure_or_ground"],
        "blocked_by": divergence or [],
        "result": result,
        "direction_hit": result == "hit",
        "change_type_hit": result == "hit",
        "divergence_reasons": divergence or [],
    }


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_y_guard"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        outcome_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            outcome_row("fcst_hit", result="hit", confidence="medium"),
            outcome_row("fcst_miss", result="miss", confidence="medium", divergence=["direction_mismatch"]),
            outcome_row("fcst_unscorable", result="unscorable", confidence="low", divergence=["actual_snapshot_too_far"]),
        ]
        outcome_path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")
        summary = summarize_forecast_outcome_ledger(max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    checks = {
        "ui_imports_forecast_outcome_summary": "btcts.autotrade.ledger" in imports and "summarize_forecast_outcome_ledger" in text,
        "ui_has_forecast_calibration_panel": "_render_forecast_calibration_status" in text and "Forecast Outcomes / Calibration" in text,
        "ui_displays_calibration_fields": all(token in text for token in ("hit_rate", "miss_rate", "unscorable_rate", "divergence_reason_counts", "by_confidence", "by_driver", "by_parameter_set")),
        "ui_marks_read_only_no_broker": "forecast outcome summary is read-only" in text.lower() and "would_send_to_broker" in text,
        "summary_contract_still_works": summary.total_rows == 3 and summary.calibration.hit_count == 1 and summary.divergence_reason_counts.get("direction_mismatch") == 1,
        "ui_does_not_resolve_or_append_outcomes": not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone Y: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_y_autotrade_tab_forecast_calibration_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_forecast_calibration_status_present": checks["ui_imports_forecast_outcome_summary"] and checks["ui_has_forecast_calibration_panel"],
            "calibration_fields_displayed": checks["ui_displays_calibration_fields"],
            "ui_read_only_no_resolver_execution": checks["ui_does_not_resolve_or_append_outcomes"],
            "summary_contract_still_works": checks["summary_contract_still_works"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
