# path: ./tools/test_phase4a_autotrade_milestone_r_shadow_cycle_once_guard.py
# desc: Guard one-shot shadow cycle reads market_state file layout and writes hot shadow ledger only.

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
from btcts.autotrade.shadow_cycle import run_shadow_cycle_once  # noqa: E402
from btcts.core.env import ENV_DATA_DIR  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/shadow_cycle.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_shadow_once.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py",
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
    data_root = REPO_ROOT / "tmp/_autotrade_r_data"
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_r_guard"
    ledger_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    try:
        os.environ[ENV_DATA_DIR] = str(data_root)
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if ledger_path.exists():
            ledger_path.unlink()
        part = write_market_state_file(data_root)
        result = run_shadow_cycle_once(persist=True)
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
    ledger_record = json.loads(lines[0]) if lines else {}
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))

    checks = {
        "market_state_part_written": part.exists() and "market_state" in part.parts,
        "cycle_appended_one_decision": result.appended is True and len(lines) == 1,
        "cycle_result_entry_sell": result.result.candidate_action == "ENTRY_SELL" and result.result.risk_allowed is True,
        "ledger_record_shadow_medium": ledger_record.get("mode") == "SHADOW" and ((ledger_record.get("forecast_5m") or {}).get("confidence") == "medium"),
        "ledger_path_hot_runtime": str(ledger_path) == str(result.result.ledger_path),
        "cycle_no_loop_no_broker": result.loop_started is False and result.would_send_to_broker is False and result.result.would_send_to_broker is False,
        "runtime_diag_available": result.runtime_diagnostics.paths.command_ledger_path is not None and "autotrade" in result.runtime_diagnostics.paths.decision_ledger_dir.parts,
        "json_safe_result": json.loads(json.dumps(result.to_dict(), ensure_ascii=False))["would_send_to_broker"] is False,
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
    failures.extend(f"protected lower-layer dirty during milestone R: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_r_shadow_cycle_once_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "one_shot_shadow_cycle_present": checks["cycle_appended_one_decision"] and checks["cycle_result_entry_sell"],
            "reads_market_state_file_layout": checks["market_state_part_written"],
            "writes_hot_shadow_decision_ledger": checks["ledger_path_hot_runtime"],
            "shadow_only_no_loop_no_broker": checks["cycle_no_loop_no_broker"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "part": str(part),
        "ledger_path": str(ledger_path),
        "cycle_result": result.to_dict(),
        "ledger_record": ledger_record,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
