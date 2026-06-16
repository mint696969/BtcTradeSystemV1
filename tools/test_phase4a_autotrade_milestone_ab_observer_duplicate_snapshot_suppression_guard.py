# path: ./tools/test_phase4a_autotrade_milestone_ab_observer_duplicate_snapshot_suppression_guard.py
# desc: Guard bounded observer cycle suppresses duplicate snapshot shadow appends without disabling outcome resolution.

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

from btcts.autotrade.ledger import read_forecast_outcome_links, summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.observer_cycle import run_observer_cycle_bounded  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
from btcts.core.env import ENV_DATA_DIR  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/observer_cycle.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_observer_bounded.py",
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
    "while True",
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


def actual_row(ts: datetime, *, reason: str, mid: int) -> dict:
    text = ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "collector_ts": text,
        "exchange_ts": text,
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "mid_price": mid,
        "imbalance": -0.3 if "sell" in reason else 0.3,
        "wall_ratio": -0.5 if "sell" in reason else 0.5,
        "spread": 4200,
        "trade_delta": -1.2 if "sell" in reason else 1.2,
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "interpretation_reason": reason,
    }


def write_market_state_file(data_root: Path, rows: list[dict]) -> Path:
    latest_ts = datetime.fromisoformat(rows[-1]["collector_ts"].replace("Z", "+00:00"))
    date_dir = data_root / "market_state/exchange=bitflyer/symbol=BTC_JPY/type=market.overview" / f"date={latest_ts.date().isoformat()}"
    date_dir.mkdir(parents=True, exist_ok=True)
    part = date_dir / "part-0000.jsonl"
    part.write_text(chr(10).join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + chr(10), encoding="utf-8")
    return part


def shadow_row(decision_id: str, *, target_ts: str, direction: str = "down") -> dict:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {
            "forecast_id": f"fcst_{decision_id}",
            "created_at": "2026-06-13T00:00:00Z",
            "target_ts": target_ts,
            "source_snapshot_id": f"snap_{decision_id}",
            "parameter_set_id": "params_fx_balanced_v0_1",
            "logic_version": "autotrade_logic_v0_1",
            "forecast_direction": direction,
            "expected_change": "strengthen_sell",
            "confidence": "medium",
            "drivers": ["sell_pressure_or_ground"],
            "blocked_by": [],
        },
        "candidate": {"action": "ENTRY_SELL", "entry_quality": 100},
        "risk_gate": {"allowed": True, "executable": False, "blocked_by": []},
        "final_action": "ENTRY_SELL",
        "reason_codes": ["forecast_aligned_sell"],
        "blocked_by": [],
        "would_order": None,
    }


def main() -> int:
    failures: list[str] = []
    original_data = os.environ.get(ENV_DATA_DIR)
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    data_root = REPO_ROOT / "tmp/_autotrade_ab_data"
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_ab_guard"
    shadow_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_DATA_DIR] = str(data_root)
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if outcome_path.exists():
            outcome_path.unlink()
        if shadow_path.exists():
            shadow_path.unlink()
        base = datetime.now(timezone.utc).replace(microsecond=0)
        target = base - timedelta(seconds=90)
        rows = [
            actual_row(target - timedelta(seconds=30), reason="ask_pressure sell", mid=9990000),
            actual_row(target + timedelta(seconds=5), reason="ask_pressure sell", mid=9989000),
            actual_row(base, reason="ask_pressure sell", mid=9988000),
        ]
        part = write_market_state_file(data_root, rows)
        shadow_path.parent.mkdir(parents=True, exist_ok=True)
        target_text = target.isoformat().replace("+00:00", "Z")
        shadow_path.write_text(json.dumps(shadow_row("preexisting_due_hit", target_ts=target_text, direction="down"), ensure_ascii=False, sort_keys=True) + chr(10), encoding="utf-8")

        result = run_observer_cycle_bounded(max_cycles=3, interval_sec=0.0, persist=True, max_actual_match_age_sec=45)
        shadow_summary = summarize_shadow_decision_ledger(max_lines=100)
        links = read_forecast_outcome_links()
        allow_duplicate = run_observer_cycle_bounded(max_cycles=2, interval_sec=0.0, persist=True, max_actual_match_age_sec=45, skip_duplicate_snapshot=False)
        shadow_summary_after_allow = summarize_shadow_decision_ledger(max_lines=100)
    finally:
        if original_data is None:
            os.environ.pop(ENV_DATA_DIR, None)
        else:
            os.environ[ENV_DATA_DIR] = original_data
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    snapshot_ids = [item.snapshot_id for item in result.results]
    checks = {
        "market_state_part_written": part.exists() and "market_state" in part.parts,
        "bounded_observer_completed_three": result.completed_cycles == 3 and result.requested_cycles == 3,
        "duplicate_snapshot_suppressed": result.appended_shadow_decision_count == 1 and result.duplicate_snapshot_skipped_count == 2 and len(set(snapshot_ids)) == 1,
        "forecast_outcome_resolution_still_runs": result.appended_forecast_outcome_count == 1 and len(links) == 1 and links[0].forecast_id == "fcst_preexisting_due_hit",
        "allow_duplicate_snapshot_supported": allow_duplicate.skip_duplicate_snapshot is False and allow_duplicate.duplicate_snapshot_skipped_count == 0 and allow_duplicate.appended_shadow_decision_count == 2 and shadow_summary_after_allow.total_rows >= shadow_summary.total_rows + 2,
        "bounded_no_loop_no_broker": result.bounded is True and result.would_send_to_broker is False and all(item.would_send_to_broker is False for item in result.results),
        "json_safe_result": json.loads(json.dumps(result.to_dict(), ensure_ascii=False))["duplicate_snapshot_skipped_count"] == 2,
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
    failures.extend(f"protected lower-layer dirty during milestone AB: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ab_observer_duplicate_snapshot_suppression_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "observer_duplicate_snapshot_suppression_present": checks["duplicate_snapshot_suppressed"],
            "forecast_resolution_still_runs": checks["forecast_outcome_resolution_still_runs"],
            "allow_duplicate_snapshot_supported": checks["allow_duplicate_snapshot_supported"],
            "bounded_no_loop_no_broker": checks["bounded_no_loop_no_broker"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "part": str(part),
        "result": result.to_dict(),
        "allow_duplicate": allow_duplicate.to_dict(),
        "shadow_summary": shadow_summary.to_dict(),
        "shadow_summary_after_allow": shadow_summary_after_allow.to_dict(),
        "links": [link.to_dict() for link in links],
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
