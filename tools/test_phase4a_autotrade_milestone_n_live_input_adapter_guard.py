# path: ./tools/test_phase4a_autotrade_milestone_n_live_input_adapter_guard.py
# desc: Guard AutoTrade live-input adapter contract is read-only, non-UI, and freshness-aware.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.read_model.live_input_adapter import (  # noqa: E402
    LiveInputAdapterDiagnostics,
    snapshot_from_market_state_row,
)
from btcts.autotrade.read_model.models import GroundDirection  # noqa: E402

CHECK_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/read_model/live_input_adapter.py"
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
    "write_text(",
    "open(\"a",
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


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    fresh_diag = LiveInputAdapterDiagnostics(
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
    stale_diag = LiveInputAdapterDiagnostics(
        data_root=REPO_ROOT / "tmp/data",
        market_state_root=REPO_ROOT / "tmp/data/market_state",
        latest_part_path=REPO_ROOT / "tmp/data/market_state/part.jsonl",
        latest_part_exists=True,
        preferred_row_freshness="STALE",
        preferred_row_age_sec=999.0,
        preferred_row_is_stale=True,
        blocked_by=("market_state_preferred_row_stale",),
        warnings=(),
    )
    row = {
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "collector_ts": "2026-06-12T12:00:00Z",
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "interpretation_reason": "bid_support sell_absent",
        "spread": 3500.0,
        "imbalance": 0.25,
        "wall_ratio": 0.4,
        "mid_price": 10000000.0,
    }
    fresh_snapshot = snapshot_from_market_state_row(row, parameter_set=ps, diagnostics=fresh_diag)
    stale_snapshot = snapshot_from_market_state_row(row, parameter_set=ps, diagnostics=stale_diag)
    text = CHECK_FILE.read_text(encoding="utf-8")
    imports = imports_from(CHECK_FILE)

    checks = {
        "fresh_snapshot_created": fresh_snapshot is not None and fresh_snapshot.snapshot_id.startswith("snap_"),
        "fresh_uses_source_refs": fresh_snapshot.source_refs.get("adapter") == "autotrade.read_model.live_input_adapter",
        "fresh_l4_usable_but_trade_temporal_false": fresh_snapshot.usability.l4 is True and fresh_snapshot.usability.trade is False and fresh_snapshot.usability.temporal is False,
        "stale_does_not_raise_confidence": stale_snapshot.usability.live_inputs_usable is False and "market_state_preferred_row_stale" in stale_snapshot.stale_reasons,
        "ground_from_row": fresh_snapshot.ground.direction in {GroundDirection.BUY_LEANING, GroundDirection.SELL_LEANING, GroundDirection.MIXED, GroundDirection.UNKNOWN},
        "json_safe_diag": json.loads(json.dumps(fresh_diag.to_dict(), ensure_ascii=False))["preferred_row_freshness"] == "LIVE",
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in imports) and "streamlit" not in imports,
        "no_forbidden_tokens": not any(token in text for token in FORBIDDEN_TOKENS),
        "read_only_contract_tokens": "write_text(" not in text and "path.open(\"a" not in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone N: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_n_live_input_adapter_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "live_input_adapter_contract_present": checks["fresh_snapshot_created"] and checks["fresh_uses_source_refs"],
            "freshness_preserved_and_stale_blocks": checks["stale_does_not_raise_confidence"],
            "no_ui_import_dependency": checks["no_ui_imports"],
            "read_only_no_broker": checks["no_forbidden_tokens"] and checks["read_only_contract_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "fresh_snapshot": fresh_snapshot.to_dict(),
        "stale_snapshot": stale_snapshot.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
