# path: ./tools/test_phase4a_direction_read_only_boundary_guard.py
# desc: Phase 4-A Direction read-only boundary guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

COMPILE_TARGETS = [
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
]

DIRECTION_FILES = [
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
]

SCAN_ROOTS_FOR_WIRING = [
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
]

ALLOWED_DIRECTION_REFERENCES = {
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
}

FORBIDDEN_DIRECTION_TERMS = [
    "place_order",
    "order_placement",
    "live_order_placement",
    "broker_order",
    "broker_adapter",
    "position_size",
    "order_size",
    "leverage",
    "live position mutation",
    "autonomous execution",
    "auto_trade",
]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []

    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"compile target missing: {rel_path}")
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"py_compile failed: {rel_path}: {exc}")

    return {
        "passed_count": len(passed),
        "failed": failed,
    }


def _check_direction_shape(failures: List[str]) -> Dict[str, Any]:
    required_by_file = {
        "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py": [
            "class PredictionDirectionOutput",
            "class HorizonDirectionReading",
            "scenario_ref",
            "primary_direction_bias",
            "horizon_direction_readings",
            "evidence_trace_refs",
            "not execution instruction",
            "not broker/order automation",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py": [
            "class PredictionDirectionBuildInput",
            "def build_prediction_direction_input_from_scenario(",
            "def build_prediction_direction_output(",
            "def prediction_direction_output_to_snapshot(",
            "PredictionDirectionOutput(",
            "scenario_to_direction_input",
            "thin_local_helper",
            "not_runtime_wiring",
            "not_replay_wiring",
            "not_ui_wiring",
            "direction_read_only_local_snapshot",
            "snapshot_stage",
            "builder_stage",
            "thin_skeleton",
            "read_only_contract",
            "not_position_owner",
            "not_execution_instruction",
            "not_broker_automation",
        ],
    }

    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"direction file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing_or_empty__"})
            continue

        for fragment in fragments:
            if fragment not in text:
                failures.append(f"direction shape fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

        for fragment in FORBIDDEN_DIRECTION_TERMS:
            if fragment in text:
                failures.append(f"direction read-only file has forbidden term: {rel_path}: {fragment}")
                forbidden.append({"path": rel_path, "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
    }


def _check_no_downstream_wiring(failures: List[str]) -> Dict[str, Any]:
    tokens = [
        "PredictionDirectionOutput",
        "PredictionDirectionBuildInput",
        "build_prediction_direction_input_from_scenario",
        "build_prediction_direction_output",
        "prediction_direction_output_to_snapshot",
        "prediction_direction_builder",
        "prediction_direction_contract",
    ]

    hits: List[Dict[str, str]] = []

    for root_rel in SCAN_ROOTS_FOR_WIRING:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel in ALLOWED_DIRECTION_REFERENCES:
                continue

            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token in text:
                    hits.append({"path": rel, "token": token})
                    failures.append(
                        f"Direction builder/contract is wired downstream before read-only guard opens it: {rel}: {token}"
                    )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    direction_shape = _check_direction_shape(failures)
    downstream_wiring = _check_no_downstream_wiring(failures)

    summary = {
        "phase": "phase4a_direction_read_only_boundary_guard",
        "checks": {
            "compile": compile_result,
            "direction_shape": direction_shape,
            "downstream_wiring": downstream_wiring,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())