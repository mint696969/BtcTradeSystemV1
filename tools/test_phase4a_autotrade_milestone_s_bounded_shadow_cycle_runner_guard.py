# path: ./tools/test_phase4a_autotrade_milestone_s_bounded_shadow_cycle_runner_guard.py
# desc: Guard bounded AutoTrade shadow cycle runner is finite, de-duplicates unchanged snapshots, and never brokers.

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

from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
from btcts.autotrade.shadow_cycle import MAX_BOUNDED_SHADOW_CYCLES, run_shadow_cycle_bounded  # noqa: E402
from btcts.core.env import ENV_DATA_DIR  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/shadow_cycle.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_shadow_bounded.py",
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


def market_rows(anchor: datetime) -> list[dict]:
    rows = []
    for sec, mid, imb, wall, spread, delta in [
        (300, 10000000, -0.05, -0.10, 3500, -0.2),
        (240, 9999000, -0.06, -0.12, 3550, -0.25),
        (180, 9998000, -0.08, -0.16, 3600, -0.3),
        (120, 9996500, -0.10, -0.20, 3800, -0.4),
        (60, 9995000, -0.14, -0.25, 4100, -0.5),
        (45, 9993500, -0.17, -0.29, 4300, -0.65),
        (30, 9992500, -0.20, -0.34, 4500, -0.8),
        (15, 9991000, -0.24, -0.42, 4900, -1.0),
        (10, 9990600, -0.26, -0.45, 5000, -1.15),
        (5, 9990300, -0.28, -0.47, 5100, -1.25),
        (0, 9990000, -0.30, -0.50, 5200, -1.4),
    ]:
        ts = (anchor - timedelta(seconds=sec)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        rows.append({
            "collector_ts": ts,
            "exchange_ts": ts,
            "exchange": "bitflyer",
            "symbol_raw": "BTC_JPY",
            "market_uid": "bitflyer.spot.BTC_JPY",
            "source_series_id": "guard_series",
            "mid_price": mid,
            "imbalance": imb,
            "wall_ratio": wall,
            "spread": spread,
            "trade_delta": delta,
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "interpretation_reason": "ask_pressure sell",
        })
    return rows


def write_market_state_file(data_root: Path) -> Path:
    anchor = datetime.now(timezone.utc).replace(microsecond=0)
    date_dir = data_root / "market_state/exchange=bitflyer/symbol=BTC_JPY/type=market.overview" / f"date={anchor.date().isoformat()}"
    date_dir.mkdir(parents=True, exist_ok=True)
    part = date_dir / "part-0000.jsonl"
    part.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in market_rows(anchor)) + "\n", encoding="utf-8")
    return part


def main() -> int:
    failures: list[str] = []
    original_data = os.environ.get(ENV_DATA_DIR)
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    data_root = REPO_ROOT / "tmp/_autotrade_s_data"
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_s_guard"
    ledger_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    try:
        os.environ[ENV_DATA_DIR] = str(data_root)
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if ledger_path.exists():
            ledger_path.unlink()
        part = write_market_state_file(data_root)
        result = run_shadow_cycle_bounded(max_cycles=3, interval_sec=0.0, persist=True, skip_duplicate_snapshot=True)
        no_persist = run_shadow_cycle_bounded(max_cycles=1, interval_sec=0.0, persist=False)
        invalid_max_ok = False
        invalid_interval_ok = False
        try:
            run_shadow_cycle_bounded(max_cycles=0, interval_sec=0.0)
        except ValueError:
            invalid_max_ok = True
        try:
            run_shadow_cycle_bounded(max_cycles=1, interval_sec=-0.1)
        except ValueError:
            invalid_interval_ok = True
    finally:
        if original_data is None:
            os.environ.pop(ENV_DATA_DIR, None)
        else:
            os.environ[ENV_DATA_DIR] = original_data
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    lines = ledger_path.read_text(encoding="utf-8").splitlines() if ledger_path.exists() else []
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))

    checks = {
        "market_state_part_written": part.exists() and "market_state" in part.parts,
        "bounded_completed_three": result.completed_cycles == 3 and len(result.results) == 3,
        "dedupe_appended_once": result.appended_count == 1 and result.duplicate_skipped_count == 2 and len(lines) == 1,
        "all_cycles_no_broker": all(item.would_send_to_broker is False and item.result.would_send_to_broker is False for item in result.results),
        "bounded_no_unbounded_loop": result.bounded is True and result.loop_started is True and result.requested_cycles == 3,
        "no_persist_does_not_append": no_persist.appended_count == 0,
        "invalid_args_fail_closed": invalid_max_ok and invalid_interval_ok and MAX_BOUNDED_SHADOW_CYCLES == 1000,
        "json_safe_result": json.loads(json.dumps(result.to_dict(), ensure_ascii=False))["appended_count"] == 1,
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
    failures.extend(f"protected lower-layer dirty during milestone S: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_s_bounded_shadow_cycle_runner_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "bounded_shadow_runner_present": checks["bounded_completed_three"] and checks["bounded_no_unbounded_loop"],
            "duplicate_snapshot_append_suppression_present": checks["dedupe_appended_once"],
            "persist_false_supported": checks["no_persist_does_not_append"],
            "invalid_args_fail_closed": checks["invalid_args_fail_closed"],
            "shadow_only_no_broker": checks["all_cycles_no_broker"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "part": str(part),
        "ledger_path": str(ledger_path),
        "result": result.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
