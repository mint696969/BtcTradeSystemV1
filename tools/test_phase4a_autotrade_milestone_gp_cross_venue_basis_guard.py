# path: ./tools/test_phase4a_autotrade_milestone_gp_cross_venue_basis_guard.py
# desc: Guard S127 cross-venue/Spot-FX basis contracts remain deterministic, non-API, non-collecting, and non-executing.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    CrossVenueReferenceSummary,
    LeadLagSkeleton,
    SourceTrustState,
    SpotFxBasisSummary,
    VenueReferencePrice,
    assess_source_quality,
    build_cross_venue_reference_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "cross_venue.py",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "requests.get",
    "httpx.get",
    "connect_and_stream",
    "write_canonical(",
    "write_raw(",
    "append_jsonl(",
    "place_order(",
    "send_order(",
    "would_call_external_api: bool = True",
    "would_collect_public_source: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _snapshots() -> list[dict[str, object]]:
    return [
        {"source_id": "bf_fx", "venue": "bitflyer", "symbol": "FX_BTC_JPY", "price": 10050000.0, "market_role": "bitflyer_fx", "event_ts": "2026-06-18T00:00:00Z"},
        {"source_id": "bf_spot", "venue": "bitflyer", "symbol": "BTC_JPY", "price": 10000000.0, "market_role": "bitflyer_spot", "event_ts": "2026-06-18T00:00:00Z"},
        {"source_id": "binance_spot", "venue": "binance", "symbol": "BTC_JPY_REF", "price": 10002000.0, "market_role": "global_spot", "event_ts": "2026-06-18T00:00:00Z"},
        {"source_id": "coinbase_spot", "venue": "coinbase", "symbol": "BTC_JPY_REF", "price": 9999000.0, "market_role": "global_spot", "event_ts": "2026-06-18T00:00:00Z"},
        {"source_id": "kraken_spot", "venue": "kraken", "symbol": "BTC_JPY_REF", "price": 10001000.0, "market_role": "global_spot", "event_ts": "2026-06-18T00:00:00Z"},
    ]


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            compile(text, str(path), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {path.relative_to(REPO_ROOT)}: {exc}")
        imports = _imports_from(path)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {path.relative_to(REPO_ROOT)}: {prefix}")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")

    now = datetime(2026, 6, 18, 0, 0, 10, tzinfo=timezone.utc)
    quality = {
        "bf_fx": assess_source_quality(source_id="bf_fx", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now),
        "bf_spot": assess_source_quality(source_id="bf_spot", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now),
        "binance_spot": assess_source_quality(source_id="binance_spot", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now),
        "coinbase_spot": assess_source_quality(source_id="coinbase_spot", source_family="unit", latest_event_ts="2026-06-17T23:59:00Z", now=now, max_age_sec=30),
        "kraken_spot": assess_source_quality(source_id="kraken_spot", source_family="unit", latest_event_ts="2026-06-18T00:00:00Z", now=now, trust_state=SourceTrustState.DEGRADED),
    }
    summary = build_cross_venue_reference_summary(_snapshots(), source_quality_by_id=quality, now=now)
    missing = build_cross_venue_reference_summary([], now=now)
    data = summary.to_dict()
    decoded = json.loads(json.dumps(data, ensure_ascii=False, sort_keys=True))

    checks = {
        "exports_available": all(item is not None for item in (CrossVenueReferenceSummary, LeadLagSkeleton, SpotFxBasisSummary, VenueReferencePrice, build_cross_venue_reference_summary)),
        "summary_usable": summary.usable is True and summary.usable_venue_count == 4,
        "stale_source_excluded": any(item.source_id == "coinbase_spot" and item.usable is False for item in summary.venue_prices),
        "quality_warning_visible": "venue_snapshot_quality_blocked" in summary.warnings,
        "reference_price_visible": summary.reference_price is not None and summary.min_price is not None and summary.max_price is not None,
        "agreement_state_visible": summary.agreement_state in ("confirmed", "divergent"),
        "spot_fx_basis_visible": summary.spot_fx_basis.basis == 50000.0 and summary.spot_fx_basis.premium_discount_state == "fx_premium",
        "lead_lag_skeleton_visible": summary.lead_lag.leading_venue is not None and summary.lead_lag.lagging_venue is not None,
        "missing_snapshots_blocked": missing.usable is False and "venue_reference_snapshots_missing_or_unusable" in missing.blockers,
        "summary_serializes": decoded["logic_version"] == "prediction_cross_venue_basis.s127.v1" and decoded["usable"] is True,
        "non_executing_flags_false": decoded["would_call_external_api"] is False and decoded["would_collect_public_source"] is False and decoded["would_write_runtime_artifact"] is False and decoded["would_send_to_broker"] is False,
        "venue_prices_non_execution": all(item["public_data_only"] is True and item["execution_enabled"] is False for item in decoded["venue_prices"]),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/execution/" in line]
    failures.extend(f"protected execution/collector dirty during GP: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gp_cross_venue_basis_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_execution_and_collector_untouched": not protected_dirty_hits},
        "sample": {
            "venue_count": summary.venue_count,
            "usable_venue_count": summary.usable_venue_count,
            "reference_price": summary.reference_price,
            "basis_pct": summary.spot_fx_basis.basis_pct,
            "agreement_state": summary.agreement_state,
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_cross_venue_basis_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
