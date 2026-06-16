# path: ./tools/test_phase4a_autotrade_milestone_q_market_state_shadow_decision_guard.py
# desc: Guard market-state snapshot -> forecast -> strategy -> risk -> shadow decision ledger vertical slice.

from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.live_shadow import (  # noqa: E402
    default_shadow_decision_ledger_path,
    run_shadow_decision_from_snapshot,
)
from btcts.autotrade.read_model.live_input_adapter import LiveInputAdapterDiagnostics, snapshot_from_market_state_row  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/runtime_paths.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/decision_log.py",
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


def rows(anchor: datetime) -> list[dict]:
    out = []
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
        out.append({
            "collector_ts": ts,
            "mid_price": mid,
            "imbalance": imb,
            "wall_ratio": wall,
            "spread": spread,
            "trade_delta": delta,
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "interpretation_reason": "ask_pressure sell",
            "market_uid": "bitflyer.spot.BTC_JPY",
        })
    return out


def fresh_diag() -> LiveInputAdapterDiagnostics:
    return LiveInputAdapterDiagnostics(
        data_root=REPO_ROOT / "tmp/data",
        market_state_root=REPO_ROOT / "tmp/data/market_state",
        latest_part_path=REPO_ROOT / "tmp/data/market_state/part.jsonl",
        latest_part_exists=True,
        preferred_row_freshness="LIVE",
        preferred_row_age_sec=1.0,
        preferred_row_is_stale=False,
        blocked_by=(),
        warnings=(),
    )


def main() -> int:
    failures: list[str] = []
    original_root = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    guard_root = REPO_ROOT / "tmp/_autotrade_hot_q_guard"
    ledger_path = guard_root / "autotrade/decisions/shadow_decisions.jsonl"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(guard_root)
        if ledger_path.exists():
            ledger_path.unlink()
        ps = initial_parameter_set_v0_1()
        anchor = datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc)
        source_rows = rows(anchor)
        snapshot = snapshot_from_market_state_row(source_rows[-1], parameter_set=ps, diagnostics=fresh_diag(), temporal_rows=source_rows)
        result = run_shadow_decision_from_snapshot(snapshot=snapshot, parameter_set=ps, persist=True)
        default_path = default_shadow_decision_ledger_path(ensure=False)
    finally:
        if original_root is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_root

    lines = ledger_path.read_text(encoding="utf-8").splitlines() if ledger_path.exists() else []
    first = json.loads(lines[0]) if lines else {}
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))

    checks = {
        "result_has_decision": result.decision_id is not None and result.forecast_id is not None,
        "entry_sell_shadow_allowed": result.candidate_action == "ENTRY_SELL" and result.risk_allowed is True,
        "ledger_appended_one_line": result.appended is True and len(lines) == 1,
        "ledger_path_under_hot_autotrade_decisions": default_path == ledger_path and "autotrade" in default_path.parts and "decisions" in default_path.parts,
        "ledger_record_shadow_no_order": first.get("mode") == "SHADOW" and first.get("would_order") is None,
        "ledger_record_forecast_medium": ((first.get("forecast_5m") or {}).get("confidence") == "medium"),
        "would_send_to_broker_false": result.would_send_to_broker is False,
        "json_safe_result": json.loads(json.dumps(result.to_dict(), ensure_ascii=False))["would_send_to_broker"] is False,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in all_imports) and "streamlit" not in all_imports,
        "no_forbidden_tokens": not any(token in all_text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone Q: {hit}" for hit in protected_dirty_hits)

    result_payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_q_market_state_shadow_decision_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "market_state_shadow_vertical_slice_present": checks["result_has_decision"] and checks["entry_sell_shadow_allowed"],
            "shadow_decision_ledger_persistence_present": checks["ledger_appended_one_line"],
            "decision_ledger_routed_to_hot_runtime": checks["ledger_path_under_hot_autotrade_decisions"],
            "shadow_no_broker_no_order": checks["ledger_record_shadow_no_order"] and checks["would_send_to_broker_false"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "result": result.to_dict(),
        "ledger_path": str(ledger_path),
        "ledger_record": first,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result_payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
