# path: ./tools/test_phase4a_autotrade_milestone_t_shadow_decision_ledger_status_guard.py
# desc: Guard shadow decision ledger read-model summarizes jsonl read-only and fail-soft.

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

from btcts.autotrade.ledger import read_shadow_decision_rows, summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/decision_status.py",
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


def row(decision_id: str, *, action: str, confidence: str, blocked_by: list[str] | None = None) -> dict:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {
            "forecast_id": f"fcst_{decision_id}",
            "forecast_direction": "down" if action == "ENTRY_SELL" else "unknown",
            "confidence": confidence,
        },
        "candidate": {"action": action, "entry_quality": 80},
        "risk_gate": {"allowed": not blocked_by, "executable": False, "blocked_by": blocked_by or []},
        "final_action": action,
        "reason_codes": ["forecast_aligned_sell"] if action == "ENTRY_SELL" else ["trade_unusable"],
        "blocked_by": blocked_by or [],
        "would_order": None,
    }


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_t_guard"
    ledger_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            row("001", action="ENTRY_SELL", confidence="medium"),
            "{broken json",
            row("002", action="WAIT", confidence="low", blocked_by=["trade_unusable"]),
            row("003", action="ENTRY_SELL", confidence="medium"),
        ]
        ledger_path.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) if isinstance(r, dict) else r for r in rows) + "\n", encoding="utf-8")
        read = read_shadow_decision_rows(max_lines=10)
        summary = summarize_shadow_decision_ledger(max_lines=10)
        missing_summary = summarize_shadow_decision_ledger(hot_root / "autotrade/decisions/missing.jsonl")
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "read_rows_fail_soft": len(read.rows) == 3 and read.skipped_count == 1 and read.error_samples,
        "summary_latest_decision": summary.latest_decision_id == "003" and summary.latest_action == "ENTRY_SELL",
        "summary_counts": summary.total_rows == 3 and summary.action_counts.get("ENTRY_SELL") == 2 and summary.action_counts.get("WAIT") == 1,
        "summary_confidence_counts": summary.forecast_confidence_counts.get("medium") == 2 and summary.forecast_confidence_counts.get("low") == 1,
        "summary_blocked_reason_counts": summary.blocked_by_counts.get("trade_unusable") == 1 and summary.reason_code_counts.get("forecast_aligned_sell") == 2,
        "summary_no_broker_read_only": summary.would_send_to_broker is False and summary.read_only is True and summary.latest_executable is False,
        "missing_summary_safe": missing_summary.exists is False and missing_summary.total_rows == 0 and missing_summary.skipped_rows == 0,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["total_rows"] == 3,
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
    failures.extend(f"protected lower-layer dirty during milestone T: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_t_shadow_decision_ledger_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "shadow_decision_ledger_read_model_present": checks["read_rows_fail_soft"] and checks["summary_latest_decision"],
            "summary_counts_present": checks["summary_counts"] and checks["summary_confidence_counts"],
            "fail_soft_corrupt_jsonl_present": checks["read_rows_fail_soft"],
            "read_only_no_broker": checks["summary_no_broker_read_only"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "read": read.to_dict(),
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
