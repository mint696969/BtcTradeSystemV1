# path: ./tools/test_phase4a_autotrade_milestone_x_forecast_outcome_ledger_status_guard.py
# desc: Guard forecast outcome ledger status summarizes calibration read-only.

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

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/forecast_outcome_status.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/__init__.py",
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
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
    "path.open(\"a",
    "write_text(",
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


def outcome_row(forecast_id: str, *, result: str, confidence: str, driver: str, divergence: list[str] | None = None) -> dict:
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
        "drivers": [driver],
        "blocked_by": divergence or [],
        "result": result,
        "direction_hit": result == "hit",
        "change_type_hit": result == "hit",
        "divergence_reasons": divergence or [],
    }


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_x_guard"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        outcome_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            outcome_row("fcst_hit", result="hit", confidence="medium", driver="sell_pressure_or_ground"),
            outcome_row("fcst_miss", result="miss", confidence="medium", driver="sell_pressure_or_ground", divergence=["direction_mismatch"]),
            outcome_row("fcst_unscorable", result="unscorable", confidence="low", driver="no_driver", divergence=["actual_snapshot_too_far"]),
        ]
        outcome_path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")
        summary = summarize_forecast_outcome_ledger(max_lines=100)
        missing_summary = summarize_forecast_outcome_ledger(hot_root / "autotrade/decisions/missing_forecast_outcomes.jsonl")
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    data = summary.to_dict()
    checks = {
        "summary_basic_counts": summary.exists is True and summary.total_rows == 3 and summary.calibration.total_forecast_count == 3,
        "summary_rates": summary.calibration.hit_count == 1 and summary.calibration.miss_count == 1 and summary.calibration.unscorable_count == 1 and summary.calibration.hit_rate == 0.5,
        "summary_group_by_confidence": "medium" in summary.by_confidence and summary.by_confidence["medium"].scorable_forecast_count == 2,
        "summary_group_by_driver": "sell_pressure_or_ground" in summary.by_driver and summary.by_driver["sell_pressure_or_ground"].total_forecast_count == 2,
        "summary_group_by_parameter_set": "params_fx_balanced_v0_1" in summary.by_parameter_set,
        "summary_divergence_counts": summary.divergence_reason_counts.get("direction_mismatch") == 1 and summary.divergence_reason_counts.get("actual_snapshot_too_far") == 1,
        "summary_latest_fields": summary.latest_forecast_id == "fcst_unscorable" and summary.latest_result == "unscorable" and "actual_snapshot_too_far" in summary.latest_divergence_reasons,
        "missing_summary_safe": missing_summary.exists is False and missing_summary.total_rows == 0 and missing_summary.calibration.total_forecast_count == 0,
        "json_safe_summary": json.loads(json.dumps(data, ensure_ascii=False))["total_rows"] == 3,
        "read_only_no_broker": summary.would_send_to_broker is False and summary.read_only is True,
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
    failures.extend(f"protected lower-layer dirty during milestone X: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_x_forecast_outcome_ledger_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "forecast_outcome_ledger_status_present": checks["summary_basic_counts"],
            "calibration_rates_present": checks["summary_rates"],
            "grouped_calibration_present": checks["summary_group_by_confidence"] and checks["summary_group_by_driver"] and checks["summary_group_by_parameter_set"],
            "divergence_counts_present": checks["summary_divergence_counts"],
            "read_only_no_ui_no_broker": checks["read_only_no_broker"] and checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary.to_dict(),
        "missing_summary": missing_summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
