# path: ./tools/test_phase4a_autotrade_milestone_gn_feature_registry_source_quality_guard.py
# desc: Guard S125 feature registry/source quality contracts are serializable, extensible, non-collecting, and non-executing.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    ContinuityState,
    FeatureFamily,
    FeatureRegistryEntry,
    FeatureSpec,
    SourceQualityStatus,
    SourceTrustState,
    assess_source_quality,
    build_default_feature_registry,
    feature_registry_by_id,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "source_quality.py",
    PREDICTION_ROOT / "feature_registry.py",
)
EXPECTED_FEATURE_IDS = (
    "ohlcv_multi_timeframe",
    "realized_volatility_atr",
    "liquidity_execution_quality",
    "orderbook_pressure",
    "tradeflow_dynamics",
    "spot_fx_basis",
    "cross_venue_confirmation",
    "human_technical_structure",
    "macro_risk_context",
    "algorithmic_participant_footprint",
    "opportunity_participation",
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

    now = datetime(2026, 6, 18, 0, 1, 0, tzinfo=timezone.utc)
    good = assess_source_quality(source_id="unit_good", source_family="unit", latest_event_ts="2026-06-18T00:00:50Z", now=now, max_age_sec=30)
    stale = assess_source_quality(source_id="unit_stale", source_family="unit", latest_event_ts="2026-06-17T23:59:00Z", now=now, max_age_sec=30)
    gapped = assess_source_quality(source_id="unit_gap", source_family="unit", latest_event_ts="2026-06-18T00:00:50Z", now=now, gap_count=1)
    degraded = assess_source_quality(source_id="unit_degraded", source_family="unit", latest_event_ts="2026-06-18T00:00:50Z", now=now, trust_state=SourceTrustState.DEGRADED)
    registry = build_default_feature_registry()
    registry_map = feature_registry_by_id()
    encoded = json.dumps({"quality": good.to_dict(), "features": [entry.to_dict() for entry in registry]}, ensure_ascii=False, sort_keys=True)
    decoded = json.loads(encoded)

    checks = {
        "exports_available": all(item is not None for item in (ContinuityState, FeatureFamily, FeatureRegistryEntry, FeatureSpec, SourceQualityStatus, SourceTrustState)),
        "source_quality_good_usable": good.usable is True and good.continuity_state == ContinuityState.CONTINUOUS,
        "source_quality_stale_blocks": stale.usable is False and "source_stale" in stale.blockers,
        "source_quality_gap_blocks": gapped.usable is False and "source_gapped" in gapped.blockers,
        "source_quality_degraded_warns": degraded.usable is True and "source_trust_degraded" in degraded.warnings,
        "source_quality_non_executing": decoded["quality"]["would_collect_public_source"] is False and decoded["quality"]["would_write_runtime_artifact"] is False and decoded["quality"]["would_send_to_broker"] is False,
        "default_registry_complete": tuple(entry.spec.feature_id for entry in registry) == EXPECTED_FEATURE_IDS,
        "registry_lookup_complete": tuple(registry_map.keys()) == EXPECTED_FEATURE_IDS,
        "registry_entries_have_sources": all(entry.spec.required_source_families for entry in registry),
        "registry_entries_have_prediction_users": all(entry.spec.used_by_prediction_families for entry in registry),
        "registry_non_executing": all(entry.to_dict()["would_collect_public_source"] is False and entry.to_dict()["would_write_runtime_artifact"] is False and entry.to_dict()["would_send_to_broker"] is False for entry in registry),
        "registry_serializes": decoded["features"][0]["spec"]["feature_id"] == "ohlcv_multi_timeframe",
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/execution/" in line]
    failures.extend(f"protected execution/collector dirty during GN: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gn_feature_registry_source_quality_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_execution_and_collector_untouched": not protected_dirty_hits},
        "feature_ids": tuple(entry.spec.feature_id for entry in registry),
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_feature_registry_source_quality_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
