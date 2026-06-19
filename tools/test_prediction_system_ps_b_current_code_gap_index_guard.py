# path: ./tools/test_prediction_system_ps_b_current_code_gap_index_guard.py
# desc: Guard for PS-B Prediction System current code inventory and gap index document.

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_CURRENT_CODE_GAP_INDEX_BTC_BITFLYER_2026-06-19.md"

REQUIRED = [
    "PS-B current code inventory and gap index",
    "Prediction System itself is still mostly foundation-level",
    "btcts_next/src/btcts/prediction/",
    "contracts.py",
    "horizons.py",
    "parameter_sets.py",
    "feature_registry.py",
    "source_quality.py",
    "ohlcv.py",
    "technical.py",
    "cross_venue.py",
    "rule_based_v0.py",
    "bundle_assembly.py",
    "forecast_ledger.py",
    "outcome_ledger.py",
    "calibration.py",
    "shadow_adapter.py",
    "replay_validation.py",
    "prearmed_readiness.py",
    "5/11 families implemented",
    "reversal_zone",
    "liquidity_execution_quality",
    "breakout_false_break",
    "opportunity_participation",
    "macro_risk_context",
    "algorithmic_participant_footprint",
    "no top-level PredictionSystemInput / PredictionSystemResult orchestrator",
    "10m missing",
    "collector_vnext hits in btcts_next/src/btcts/prediction/*.py: 0",
    "AutoTrade-facing content",
    "PS-C: standalone contracts and result shape",
]

FORBIDDEN = [
    "broker execution is allowed",
    "mode apply is allowed",
    "Collector runtime import is acceptable for core",
]


def main() -> int:
    if not DOC.exists():
        raise AssertionError(f"missing PS-B gap index document: {DOC}")
    text = DOC.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED if item not in text]
    if missing:
        raise AssertionError(f"missing required PS-B anchors: {missing}")
    forbidden = [item for item in FORBIDDEN if item in text]
    if forbidden:
        raise AssertionError(f"forbidden PS-B language found: {forbidden}")
    print("[OK] Prediction System PS-B current code gap index guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
