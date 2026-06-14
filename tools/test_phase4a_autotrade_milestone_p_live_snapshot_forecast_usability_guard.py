# path: ./tools/test_phase4a_autotrade_milestone_p_live_snapshot_forecast_usability_guard.py
# desc: Guard live market-state snapshot can become forecast-usable when fresh trade + temporal flow are present.

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
from btcts.autotrade.read_model.forecast import build_rule_based_forecast_5m  # noqa: E402
from btcts.autotrade.read_model.live_input_adapter import LiveInputAdapterDiagnostics, snapshot_from_market_state_row  # noqa: E402
from btcts.autotrade.read_model.models import Confidence, ForecastDirection  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/read_model/live_input_adapter.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/read_model/forecast.py",
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


def rows(anchor: datetime, *, with_trade: bool = True) -> list[dict]:
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
        row = {
            "collector_ts": ts,
            "mid_price": mid,
            "imbalance": imb,
            "wall_ratio": wall,
            "spread": spread,
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "interpretation_reason": "ask_pressure sell",
            "market_uid": "bitflyer.spot.BTC_JPY",
        }
        if with_trade:
            row["trade_delta"] = delta
        out.append(row)
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


def stale_diag() -> LiveInputAdapterDiagnostics:
    return LiveInputAdapterDiagnostics(
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


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    anchor = datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc)

    good_rows = rows(anchor, with_trade=True)
    good_snapshot = snapshot_from_market_state_row(good_rows[-1], parameter_set=ps, diagnostics=fresh_diag(), temporal_rows=good_rows)
    good_forecast = build_rule_based_forecast_5m(good_snapshot, ps)

    no_trade_rows = rows(anchor, with_trade=False)
    no_trade_snapshot = snapshot_from_market_state_row(no_trade_rows[-1], parameter_set=ps, diagnostics=fresh_diag(), temporal_rows=no_trade_rows)
    no_trade_forecast = build_rule_based_forecast_5m(no_trade_snapshot, ps)

    stale_snapshot = snapshot_from_market_state_row(good_rows[-1], parameter_set=ps, diagnostics=stale_diag(), temporal_rows=good_rows)
    stale_forecast = build_rule_based_forecast_5m(stale_snapshot, ps)

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "fresh_snapshot_live_inputs_usable": good_snapshot.usability.live_inputs_usable is True,
        "fresh_snapshot_trade_and_temporal_true": good_snapshot.usability.trade is True and good_snapshot.usability.temporal is True,
        "fresh_forecast_not_blocked_by_trade_or_temporal": "trade_unusable" not in good_forecast.blocked_by and "temporal_flow_unusable" not in good_forecast.blocked_by,
        "fresh_forecast_medium_sell": good_forecast.confidence == Confidence.MEDIUM and good_forecast.forecast_direction == ForecastDirection.DOWN,
        "missing_trade_blocks_forecast": no_trade_snapshot.usability.trade is False and "trade_unusable" in no_trade_forecast.blocked_by and no_trade_forecast.confidence == Confidence.LOW,
        "stale_blocks_live_usable": stale_snapshot.usability.live_inputs_usable is False and "market_state_preferred_row_stale" in stale_forecast.blocked_by,
        "json_safe_snapshot_forecast": json.loads(json.dumps(good_snapshot.to_dict(), ensure_ascii=False))["usability"]["live_inputs_usable"] is True and json.loads(json.dumps(good_forecast.to_dict(), ensure_ascii=False))["confidence"] == "medium",
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
    failures.extend(f"protected lower-layer dirty during milestone P: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_p_live_snapshot_forecast_usability_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "fresh_trade_temporal_snapshot_live_usable": checks["fresh_snapshot_live_inputs_usable"],
            "forecast_not_downgraded_when_inputs_usable": checks["fresh_forecast_not_blocked_by_trade_or_temporal"] and checks["fresh_forecast_medium_sell"],
            "missing_trade_fail_closed": checks["missing_trade_blocks_forecast"],
            "stale_fail_closed": checks["stale_blocks_live_usable"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "fresh_snapshot": good_snapshot.to_dict(),
        "fresh_forecast": good_forecast.to_dict(),
        "no_trade_forecast": no_trade_forecast.to_dict(),
        "stale_forecast": stale_forecast.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
