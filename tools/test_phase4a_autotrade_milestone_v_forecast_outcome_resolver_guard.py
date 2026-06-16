# path: ./tools/test_phase4a_autotrade_milestone_v_forecast_outcome_resolver_guard.py
# desc: Guard due shadow forecasts are resolved against latest market_state and appended to forecast outcome ledger.

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

from btcts.autotrade.ledger import read_forecast_outcome_links, resolve_due_shadow_forecast_outcomes  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
from btcts.core.env import ENV_DATA_DIR  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/forecast_resolution.py",
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


def write_market_state_file(data_root: Path, anchor: datetime) -> Path:
    date_dir = data_root / "market_state/exchange=bitflyer/symbol=BTC_JPY/type=market.overview" / f"date={anchor.date().isoformat()}"
    date_dir.mkdir(parents=True, exist_ok=True)
    part = date_dir / "part-0000.jsonl"
    part.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in market_rows(anchor)) + "\n", encoding="utf-8")
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
    data_root = REPO_ROOT / "tmp/_autotrade_v_data"
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_v_guard"
    shadow_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_DATA_DIR] = str(data_root)
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if outcome_path.exists():
            outcome_path.unlink()
        anchor = datetime.now(timezone.utc).replace(microsecond=0)
        part = write_market_state_file(data_root, anchor)
        shadow_path.parent.mkdir(parents=True, exist_ok=True)
        due_target = (anchor - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
        future_target = (anchor + timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
        shadow_path.write_text(
            "\n".join(
                json.dumps(row, ensure_ascii=False, sort_keys=True)
                for row in (
                    shadow_row("due_hit", target_ts=due_target, direction="down"),
                    shadow_row("future_skip", target_ts=future_target, direction="down"),
                    shadow_row("due_miss", target_ts=due_target, direction="up"),
                )
            ) + "\n",
            encoding="utf-8",
        )
        first = resolve_due_shadow_forecast_outcomes(persist=True)
        second = resolve_due_shadow_forecast_outcomes(persist=True)
        links = read_forecast_outcome_links()
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
    results = {record.forecast_id: record.result for record in links}
    checks = {
        "market_state_part_written": part.exists() and "market_state" in part.parts,
        "due_forecasts_resolved": first.due_count == 2 and first.appended_count == 2 and first.unresolved_count == 0,
        "future_forecast_not_due": "fcst_future_skip" not in results,
        "hit_and_miss_scored": results.get("fcst_due_hit") == "hit" and results.get("fcst_due_miss") == "miss",
        "dedupe_second_run": second.appended_count == 0 and second.duplicate_skipped_count == 2,
        "outcome_ledger_written": outcome_path.exists() and len(outcome_path.read_text(encoding="utf-8").splitlines()) == 2,
        "result_summary_json_safe": json.loads(json.dumps(first.to_dict(), ensure_ascii=False))["appended_count"] == 2,
        "no_broker_read_only_inputs": first.would_send_to_broker is False and first.read_only_inputs is True,
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
    failures.extend(f"protected lower-layer dirty during milestone V: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_v_forecast_outcome_resolver_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "due_shadow_forecast_outcome_resolver_present": checks["due_forecasts_resolved"],
            "hit_miss_scoring_present": checks["hit_and_miss_scored"],
            "not_due_skipped": checks["future_forecast_not_due"],
            "duplicate_forecast_resolution_suppressed": checks["dedupe_second_run"],
            "outcome_ledger_persistence_present": checks["outcome_ledger_written"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"] and checks["no_broker_read_only_inputs"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "first": first.to_dict(),
        "second": second.to_dict(),
        "links": [link.to_dict() for link in links],
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
