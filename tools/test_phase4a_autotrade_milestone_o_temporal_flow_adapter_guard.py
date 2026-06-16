# path: ./tools/test_phase4a_autotrade_milestone_o_temporal_flow_adapter_guard.py
# desc: Guard AutoTrade temporal-flow adapter computes recent flow read-only and stale/insufficient data blocks confidence.

from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.read_model.live_input_adapter import LiveInputAdapterDiagnostics, snapshot_from_market_state_row  # noqa: E402
from btcts.autotrade.read_model.temporal_flow_adapter import build_temporal_flow_features_from_rows  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/read_model/temporal_flow_adapter.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/read_model/live_input_adapter.py",
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


def rows(anchor: datetime) -> list[dict]:
    out = []
    # Dense enough for min_points_per_window=3 even in the shortest 15s window.
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
        out.append({"collector_ts": ts, "mid_price": mid, "imbalance": imb, "wall_ratio": wall, "spread": spread, "trade_delta": delta, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use", "interpretation_reason": "ask_pressure sell", "market_uid": "bitflyer.spot.BTC_JPY"})
    return out


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    anchor = datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc)
    temporal, diag = build_temporal_flow_features_from_rows(rows(anchor), parameter_set=ps, now=anchor)
    stale_temporal, stale_diag = build_temporal_flow_features_from_rows(rows(anchor), parameter_set=ps, now=anchor + timedelta(seconds=30))
    sparse_temporal, sparse_diag = build_temporal_flow_features_from_rows(rows(anchor)[-1:], parameter_set=ps, now=anchor)
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
    snap = snapshot_from_market_state_row(rows(anchor)[-1], parameter_set=ps, diagnostics=fresh_diag, temporal_rows=rows(anchor))

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "temporal_features_usable": temporal.usable is True and diag.usable is True,
        "pressure_acceleration_sell": temporal.temporal_pressure_flow.get("pressure_acceleration") == "sell",
        "mid_return_300_negative": isinstance(temporal.temporal_price_flow.get("mid_return_300s"), float) and temporal.temporal_price_flow.get("mid_return_300s") < 0,
        "spread_change_positive": temporal.temporal_liquidity_flow.get("spread_change_300s") == 1700,
        "pattern_flags_present": "breakout_attempt" in temporal.temporal_pattern_flags and "board_trade_divergence" in temporal.temporal_pattern_flags,
        "stale_blocks_temporal": stale_temporal.usable is False and "temporal_feature_stale" in stale_temporal.blocked_by,
        "sparse_blocks_temporal": sparse_temporal.usable is False and "temporal_window_insufficient_points" in sparse_temporal.blocked_by,
        "snapshot_accepts_temporal_rows": snap.usability.temporal is True and snap.temporal_flow.usable is True,
        "json_safe_diag": json.loads(json.dumps(diag.to_dict(), ensure_ascii=False))["usable"] is True,
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
    failures.extend(f"protected lower-layer dirty during milestone O: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_o_temporal_flow_adapter_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "temporal_flow_adapter_present": checks["temporal_features_usable"],
            "pressure_price_liquidity_flow_present": checks["pressure_acceleration_sell"] and checks["mid_return_300_negative"] and checks["spread_change_positive"],
            "stale_and_sparse_windows_block": checks["stale_blocks_temporal"] and checks["sparse_blocks_temporal"],
            "snapshot_temporal_wiring_present": checks["snapshot_accepts_temporal_rows"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "temporal": temporal.to_dict(),
        "diag": diag.to_dict(),
        "stale_diag": stale_diag.to_dict(),
        "sparse_diag": sparse_diag.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
