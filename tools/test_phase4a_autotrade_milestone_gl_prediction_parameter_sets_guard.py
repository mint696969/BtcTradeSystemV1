# path: ./tools/test_phase4a_autotrade_milestone_gl_prediction_parameter_sets_guard.py
# desc: Guard S123 prediction parameter-set skeletons are complete, immutable, serializable, and non-executing.

from __future__ import annotations

import ast
import json
import subprocess
from dataclasses import FrozenInstanceError
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    AlgorithmicParticipantFootprintParameterSet,
    BreakoutFalseBreakPredictionParameterSet,
    CrossVenueConfirmationParameterSet,
    HumanTechnicalStructureParameterSet,
    LiquidityExecutionQualityParameterSet,
    MacroRiskContextParameterSet,
    MarketRegimePredictionParameterSet,
    OpportunityParticipationParameterSet,
    PredictionFamily,
    ReversalPredictionParameterSet,
    TrendPredictionParameterSet,
    VolatilityRiskPredictionParameterSet,
    build_default_prediction_parameter_sets,
    default_prediction_parameter_set_for_family,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_ROOT = REPO_ROOT / "btcts_next/src/btcts/prediction"
CHECK_FILES = (
    PREDICTION_ROOT / "__init__.py",
    PREDICTION_ROOT / "parameter_sets.py",
)
EXPECTED_CLASS_NAMES = (
    "MarketRegimePredictionParameterSet",
    "TrendPredictionParameterSet",
    "ReversalPredictionParameterSet",
    "VolatilityRiskPredictionParameterSet",
    "LiquidityExecutionQualityParameterSet",
    "BreakoutFalseBreakPredictionParameterSet",
    "OpportunityParticipationParameterSet",
    "CrossVenueConfirmationParameterSet",
    "MacroRiskContextParameterSet",
    "HumanTechnicalStructureParameterSet",
    "AlgorithmicParticipantFootprintParameterSet",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "append_command_ledger_record(",
    "submit_mode_change_command_request",
    "apply_latest_mode_change_command_once",
    "live_mutation_allowed: bool = True",
    "non_executing: bool = False",
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

    defaults = build_default_prediction_parameter_sets()
    data = [item.to_dict() for item in defaults]
    roundtrip = json.loads(json.dumps(data, ensure_ascii=False, sort_keys=True))
    family_values = tuple(item["family"] for item in roundtrip)
    class_names = tuple(type(item).__name__ for item in defaults)
    lookup_ok = all(default_prediction_parameter_set_for_family(family).family == family for family in PredictionFamily)
    immutable_ok = False
    try:
        defaults[0].parameter_set_id = "mutated"  # type: ignore[misc]
    except FrozenInstanceError:
        immutable_ok = True
    except Exception:
        immutable_ok = True

    checks = {
        "all_11_parameter_sets_present": len(defaults) == 11,
        "one_parameter_set_per_family": family_values == tuple(f.value for f in PredictionFamily),
        "expected_classes_present": class_names == EXPECTED_CLASS_NAMES,
        "all_have_supported_horizons": all(item["supported_horizons_sec"] == [15, 30, 60, 180, 300, 900, 1800, 3600, 14400, 86400] for item in roundtrip),
        "all_have_required_feature_families": all(bool(item["required_feature_families"]) for item in roundtrip),
        "all_non_executing_read_only": all(item["non_executing"] is True and item["read_only"] is True for item in roundtrip),
        "all_disallow_live_mutation": all(item["live_mutation_allowed"] is False for item in roundtrip),
        "all_identities_serialize": all(item["identity"]["parameter_set_id"] == item["parameter_set_id"] for item in roundtrip),
        "lookup_by_family_ok": lookup_ok,
        "immutable_dataclasses": immutable_ok,
        "exports_available": all(cls is not None for cls in (
            MarketRegimePredictionParameterSet,
            TrendPredictionParameterSet,
            ReversalPredictionParameterSet,
            VolatilityRiskPredictionParameterSet,
            LiquidityExecutionQualityParameterSet,
            BreakoutFalseBreakPredictionParameterSet,
            OpportunityParticipationParameterSet,
            CrossVenueConfirmationParameterSet,
            MacroRiskContextParameterSet,
            HumanTechnicalStructureParameterSet,
            AlgorithmicParticipantFootprintParameterSet,
        )),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if "btcts_next/src/btcts/collector_vnext/" in line or "btcts_next/src/btcts/autotrade/execution/" in line]
    failures.extend(f"protected execution/collector dirty during GL: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gl_prediction_parameter_sets_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_execution_and_collector_untouched": not protected_dirty_hits},
        "families": family_values,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_parameter_sets_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
