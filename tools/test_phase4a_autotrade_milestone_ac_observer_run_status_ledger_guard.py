# path: ./tools/test_phase4a_autotrade_milestone_ac_observer_run_status_ledger_guard.py
# desc: Guard observer bounded runs append observer_runs.jsonl summary records without broker.

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

from btcts.autotrade.ledger import read_observer_run_records, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.observer_cycle import run_observer_cycle_bounded  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
from btcts.core.env import ENV_DATA_DIR  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/observer_run_status.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/observer_cycle.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_observer_bounded.py",
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


def main() -> int:
    failures: list[str] = []
    original_data = os.environ.get(ENV_DATA_DIR)
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    data_root = REPO_ROOT / "tmp/_autotrade_ac_data"
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_ac_guard"
    run_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
    try:
        os.environ[ENV_DATA_DIR] = str(data_root)
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if run_path.exists():
            run_path.unlink()
        base = datetime.now(timezone.utc).replace(microsecond=0)
        rows = [
            actual_row(base - timedelta(seconds=20), reason="ask_pressure sell", mid=9990000),
            actual_row(base - timedelta(seconds=10), reason="ask_pressure sell", mid=9989000),
            actual_row(base, reason="ask_pressure sell", mid=9988000),
        ]
        part = write_market_state_file(data_root, rows)
        result = run_observer_cycle_bounded(max_cycles=2, interval_sec=0.0, persist=True, persist_run_record=True, max_actual_match_age_sec=45)
        records = read_observer_run_records()
        summary = summarize_observer_run_ledger()
        no_record = run_observer_cycle_bounded(max_cycles=1, interval_sec=0.0, persist=False, persist_run_record=False, max_actual_match_age_sec=45)
        records_after_no_record = read_observer_run_records()
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
    latest = records[-1] if records else None
    checks = {
        "market_state_part_written": part.exists() and "market_state" in part.parts,
        "observer_run_record_appended": result.observer_run_record_appended is True and run_path.exists() and len(records) == 1,
        "observer_run_record_fields": latest is not None and latest.run_id == result.run_id and latest.completed_cycles == result.completed_cycles and latest.duplicate_snapshot_skipped_count == result.duplicate_snapshot_skipped_count,
        "observer_run_summary_counts": summary.total_rows == 1 and summary.total_completed_cycles == result.completed_cycles and summary.latest_run_id == result.run_id,
        "no_run_record_supported": no_record.observer_run_record_appended is False and len(records_after_no_record) == 1,
        "json_safe_result_and_summary": json.loads(json.dumps(result.to_dict(), ensure_ascii=False))["observer_run_record_appended"] is True and json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["total_rows"] == 1,
        "no_broker": result.would_send_to_broker is False and latest is not None and latest.would_send_to_broker is False and summary.would_send_to_broker is False,
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
    failures.extend(f"protected lower-layer dirty during milestone AC: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ac_observer_run_status_ledger_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "observer_run_ledger_present": checks["observer_run_record_appended"],
            "observer_run_summary_present": checks["observer_run_summary_counts"],
            "no_run_record_supported": checks["no_run_record_supported"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"] and checks["no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "part": str(part),
        "result": result.to_dict(),
        "no_record": no_record.to_dict(),
        "records": [record.to_dict() for record in records],
        "summary": summary.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
