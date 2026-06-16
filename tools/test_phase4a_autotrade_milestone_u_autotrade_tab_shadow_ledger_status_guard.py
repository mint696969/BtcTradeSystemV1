# path: ./tools/test_phase4a_autotrade_milestone_u_autotrade_tab_shadow_ledger_status_guard.py
# desc: Guard AutoTrade UI tab displays shadow decision ledger summary read-only.

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

from btcts.autotrade.ledger import summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
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


def make_row(decision_id: str, action: str, confidence: str) -> dict:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {
            "forecast_id": f"fcst_{decision_id}",
            "forecast_direction": "down",
            "confidence": confidence,
        },
        "candidate": {"action": action, "entry_quality": 90},
        "risk_gate": {"allowed": True, "executable": False, "blocked_by": []},
        "final_action": action,
        "reason_codes": ["forecast_aligned_sell", "entry_threshold_met"],
        "blocked_by": [],
        "would_order": None,
    }


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_u_guard"
    ledger_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(
            "\n".join(
                json.dumps(row, ensure_ascii=False, sort_keys=True)
                for row in (
                    make_row("001", "WAIT", "low"),
                    make_row("002", "ENTRY_SELL", "medium"),
                )
            ) + "\n",
            encoding="utf-8",
        )
        summary = summarize_shadow_decision_ledger(max_lines=20)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    checks = {
        "ui_imports_shadow_summary": "btcts.autotrade.ledger" in imports and "summarize_shadow_decision_ledger" in text,
        "ui_has_shadow_status_panel": "_render_shadow_decision_status" in text and "Shadow Decision Ledger" in text,
        "ui_displays_summary_fields": all(token in text for token in ("latest_action", "latest_forecast_confidence", "latest_risk_allowed", "action_counts", "blocked_by_counts", "reason_code_counts")),
        "ui_marks_read_only_no_broker": "shadow ledger summary is read-only" in text.lower() and "would_send_to_broker" in text,
        "summary_contract_still_works": summary.total_rows == 2 and summary.latest_action == "ENTRY_SELL" and summary.latest_forecast_confidence == "medium",
        "ui_does_not_run_shadow_cycle_or_append_decision": not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone U: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_u_autotrade_tab_shadow_ledger_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_shadow_ledger_status_present": checks["ui_imports_shadow_summary"] and checks["ui_has_shadow_status_panel"],
            "summary_fields_displayed": checks["ui_displays_summary_fields"],
            "ui_read_only_no_shadow_cycle_execution": checks["ui_does_not_run_shadow_cycle_or_append_decision"],
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
