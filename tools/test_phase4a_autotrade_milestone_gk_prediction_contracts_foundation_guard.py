# path: ./tools/test_phase4a_autotrade_milestone_gk_prediction_contracts_foundation_guard.py
# desc: Guard S122 prediction contracts remain non-executing, serializable, horizon-complete, and separated from collection/broker/AutoTrade execution.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    CONTEXT_HORIZONS_SEC,
    EXECUTION_MICRO_HORIZONS_SEC,
    PRIMARY_TRADE_HORIZONS_SEC,
    InferenceBundle,
    ParameterSetIdentity,
    PredictionConfidence,
    PredictionFamily,
    PredictionOutput,
    SourceIdentity,
    build_default_horizons,
    horizon_by_seconds,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "horizons.py",
    PREDICTION_ROOT / "contracts.py",
)
EXPECTED_HORIZONS = (15, 30, 60, 180, 300, 900, 1800, 3600, 14400, 86400)
EXPECTED_FAMILIES = (
    "market_regime",
    "trend_bias",
    "reversal_zone",
    "volatility_risk",
    "liquidity_execution_quality",
    "breakout_false_break",
    "opportunity_participation",
    "cross_venue_confirmation",
    "macro_risk_context",
    "human_technical_structure",
    "algorithmic_participant_footprint",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.pipeline",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "append_command_ledger_record(",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "apply_latest_mode_change_command_once",
    "would_send_to_broker=True",
    "broker_execution_requested=True",
    "mode_apply_requested=True",
    "command_ledger_append_requested=True",
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


def _sample_bundle() -> InferenceBundle:
    source = SourceIdentity(
        source_id="bitflyer_fx_public_board",
        source_family="bitflyer_public_market_data",
        venue="bitflyer",
        symbol="FX_BTC_JPY",
        market_role="execution_market_reference",
        public_data_only=True,
        execution_enabled=False,
    )
    param = ParameterSetIdentity(
        parameter_set_id="trend_prediction_contract_v0",
        parameter_family="TrendPredictionParameterSet",
        version="0.0.0",
    )
    horizon = horizon_by_seconds(300)
    output = PredictionOutput(
        prediction_id="pred_contract_sample_001",
        generated_at="2026-06-18T00:00:00Z",
        family=PredictionFamily.TREND_BIAS,
        horizon=horizon,
        parameter_set=param,
        sources=(source,),
        confidence=PredictionConfidence.MEDIUM,
        primary_label="long_bias",
        score=0.62,
        drivers=("unit_contract_driver",),
        blockers=(),
        warnings=("contract_only",),
        values={"trend_strength": 0.62},
    )
    return InferenceBundle(
        bundle_id="bundle_contract_sample_001",
        generated_at="2026-06-18T00:00:00Z",
        logic_version="prediction_contracts.s122.v1",
        outputs=(output,),
        source_quality_summary={"usable": True},
        cross_family_agreement={"sample": "not_evaluated"},
        risk_context={"sample": "none"},
        operator_explanation=("contract serialization sample",),
    )


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

    horizons = build_default_horizons()
    bundle = _sample_bundle()
    data = bundle.to_dict()
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True)
    decoded = json.loads(encoded)
    checks = {
        "prediction_package_present": PREDICTION_ROOT.exists(),
        "all_expected_horizons_present": tuple(h.horizon_sec for h in horizons) == EXPECTED_HORIZONS,
        "micro_horizons_present": EXECUTION_MICRO_HORIZONS_SEC == (15, 30, 60, 180),
        "primary_horizons_present": PRIMARY_TRADE_HORIZONS_SEC == (300, 900, 1800),
        "context_horizons_present": CONTEXT_HORIZONS_SEC == (3600, 14400, 86400),
        "all_prediction_families_present": tuple(f.value for f in PredictionFamily) == EXPECTED_FAMILIES,
        "sample_bundle_serializes": decoded.get("bundle_id") == "bundle_contract_sample_001" and decoded.get("outputs", [{}])[0].get("family") == "trend_bias",
        "source_identity_non_executing": decoded["outputs"][0]["sources"][0]["public_data_only"] is True and decoded["outputs"][0]["sources"][0]["execution_enabled"] is False,
        "output_false_execution_flags": decoded["outputs"][0]["would_send_to_broker"] is False and decoded["outputs"][0]["broker_execution_requested"] is False and decoded["outputs"][0]["mode_apply_requested"] is False and decoded["outputs"][0]["command_ledger_append_requested"] is False,
        "bundle_false_execution_flags": decoded["would_send_to_broker"] is False and decoded["broker_execution_requested"] is False and decoded["mode_apply_requested"] is False and decoded["command_ledger_append_requested"] is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/execution/" in line]
    failures.extend(f"protected execution/collector dirty during GK: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gk_prediction_contracts_foundation_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_execution_and_collector_untouched": not protected_dirty_hits},
        "sample_bundle": {
            "families_present": data.get("families_present"),
            "horizons_present_sec": data.get("horizons_present_sec"),
            "non_executing": data.get("non_executing"),
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_contracts_foundation_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
