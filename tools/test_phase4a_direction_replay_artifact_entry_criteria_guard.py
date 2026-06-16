# path: ./tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py
# desc: Phase 4-A Direction replay artifact entry criteria guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

SPEC_PATH = "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CRITERIA_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
LOCAL_BUNDLE_CLOSE_DOC = "tmp/docs/architecture/PHASE4A_DIRECTION_READ_ONLY_LOCAL_MODEL_BUNDLE_CLOSE_2026-05-22.md"
READ_ONLY_GUARD_CONNECTION_DOC = "tmp/docs/architecture/PHASE4A_DIRECTION_READ_ONLY_BOUNDARY_GUARD_CONNECTION_2026-05-22.md"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
    PRIMARY_GUARD_PATH,
]

DIRECTION_CONTRACT_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py"
DIRECTION_BUILDER_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py"

SCAN_ROOTS_FOR_WIRING = [
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
]

DIRECTION_TOKENS = [
    "PredictionDirectionOutput",
    "PredictionDirectionBuildInput",
    "build_prediction_direction_input_from_scenario",
    "build_prediction_direction_output",
    "prediction_direction_output_to_snapshot",
    "prediction_direction_builder",
    "prediction_direction_contract",
]

POSITION_EXECUTION_TOKENS = [
    "PredictionPositionHint",
    "PredictionExecutionHint",
    "build_prediction_position",
    "build_prediction_execution",
]

FORBIDDEN_DIRECTION_FIELDS = [
    "position_size",
    "leverage",
    "entry_price",
    "exit_price",
    "order_price",
    "order_size",
    "broker_account",
    "place_order",
    "broker_order",
    "broker_adapter",
    "live_order_placement",
    "auto_trade",
    "autonomous execution",
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


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required_files = [
        SPEC_PATH,
        INDEX_PATH,
        STATUS_PATH,
        FOCUS_PATH,
        LOCAL_BUNDLE_CLOSE_DOC,
        READ_ONLY_GUARD_CONNECTION_DOC,
    ]
    missing: List[Dict[str, str]] = []

    for rel_path in required_files:
        if not (REPO_ROOT / rel_path).exists():
            failures.append(f"required doc missing: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing__"})

    required_by_file = {
        SPEC_PATH: [
            "Direction replay artifact entry criteria",
            "artifact-only / read-only",
            "Direction replay artifact entry != replay runtime wiring",
            "Direction replay artifact entry != live runtime wiring",
            "Direction replay artifact entry != UI surfacing",
            "Direction replay artifact entry != market_engine integration",
            "Position / Execution remain closed",
            "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py",
        ],
        INDEX_PATH: [
            "PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CRITERIA_2026-05-23.md",
            "Direction replay artifact entry criteria planning",
            "Direction read-only local model bundle は close 済み",
        ],
        STATUS_PATH: [
            "Direction replay artifact entry criteria guard/spec",
            "runtime / UI / market_engine へはまだ接続しない",
            "Position / Execution は閉じたまま維持する",
        ],
        FOCUS_PATH: [
            "phase4a_direction_replay_artifact_entry_criteria_planning",
            "next_add_direction_replay_artifact_entry_criteria_guard_or_spec",
            "then_allow_read_only_artifact_only_replay_entry_if_guarded",
        ],
        LOCAL_BUNDLE_CLOSE_DOC: [
            "Direction read-only local model bundle は close",
            "Next step is Direction-only replay artifact entry planning",
        ],
        READ_ONLY_GUARD_CONNECTION_DOC: [
            "Direction contract skeleton と thin Direction builder skeleton は read-only boundary guard",
            "replay / runtime / UI / market_engine への downstream wiring はまだ開かれていない",
        ],
    }

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    new_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CRITERIA_2026-05-23.md")
    local_close_pos = index_text.find("PHASE4A_DIRECTION_READ_ONLY_LOCAL_MODEL_BUNDLE_CLOSE_2026-05-22.md")
    ordering_ok = current_pos >= 0 and new_pos >= 0 and local_close_pos >= 0 and current_pos < new_pos < local_close_pos
    if not ordering_ok:
        failures.append("Direction replay artifact entry criteria spec must be first current formal spec")

    return {
        "missing_count": len(missing),
        "missing": missing,
        "ordering_ok": bool(ordering_ok),
    }


def _check_direction_snapshot_entry_prereq(failures: List[str]) -> Dict[str, Any]:
    contract_text = _read_text(DIRECTION_CONTRACT_PATH)
    builder_text = _read_text(DIRECTION_BUILDER_PATH)

    required = {
        DIRECTION_CONTRACT_PATH: [
            "class PredictionDirectionOutput",
            "class HorizonDirectionReading",
            "scenario_ref",
            "primary_direction_bias",
            "horizon_direction_readings",
            "evidence_trace_refs",
            "not execution instruction",
            "not broker/order automation",
        ],
        DIRECTION_BUILDER_PATH: [
            "def prediction_direction_output_to_snapshot(",
            "snapshot_stage",
            "direction_read_only_local_snapshot",
            "read_only_contract",
            "not_runtime_wiring",
            "not_replay_wiring",
            "not_ui_wiring",
        ],
    }

    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    texts = {
        DIRECTION_CONTRACT_PATH: contract_text,
        DIRECTION_BUILDER_PATH: builder_text,
    }

    for rel_path, fragments in required.items():
        for fragment in fragments:
            if fragment not in texts[rel_path]:
                failures.append(f"Direction artifact entry prerequisite missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    for rel_path, text in texts.items():
        for token in FORBIDDEN_DIRECTION_FIELDS:
            if token in text:
                failures.append(f"Direction file contains forbidden artifact-entry field/term: {rel_path}: {token}")
                forbidden.append({"path": rel_path, "token": token})

    return {
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
    }


ALLOWED_REPLAY_ARTIFACT_DIRECTION_REFERENCES = {
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
}


def _check_artifact_only_downstream_wiring(failures: List[str]) -> Dict[str, Any]:
    hits: List[Dict[str, str]] = []
    allowed_hits: List[Dict[str, str]] = []

    for root_rel in SCAN_ROOTS_FOR_WIRING:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in DIRECTION_TOKENS:
                if token not in text:
                    continue
                if rel in ALLOWED_REPLAY_ARTIFACT_DIRECTION_REFERENCES:
                    allowed_hits.append({"path": rel, "token": token})
                    continue
                hits.append({"path": rel, "token": token})
                failures.append(
                    "Direction replay artifact entry may only appear in artifact-only replay files; "
                    f"runtime/UI/market_engine wiring is still closed: {rel}: {token}"
                )

    return {
        "hit_count": len(hits),
        "hits": hits,
        "allowed_artifact_hit_count": len(allowed_hits),
        "allowed_artifact_hits": allowed_hits,
    }


def _check_position_execution_closed(failures: List[str]) -> Dict[str, Any]:
    roots = [
        "btcts_next/src/btcts/processing/l4_consumer_models",
        "btcts_next/src/btcts/replay",
        "btcts_next/src/btcts/apps/operator_ui",
        "btcts_next/src/btcts/market_engine",
    ]
    hits: List[Dict[str, str]] = []

    for root_rel in roots:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in POSITION_EXECUTION_TOKENS:
                if token in text:
                    hits.append({"path": rel, "token": token})
                    failures.append(f"Position / Execution must remain closed: {rel}: {token}")

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_primary_connection(failures: List[str]) -> Dict[str, Any]:
    primary_text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        NEW_GUARD_NAME,
        "direction_replay_artifact_entry_criteria_guard",
    ]
    missing = []
    for fragment in required:
        if fragment not in primary_text:
            failures.append(f"primary guard connection missing: {fragment}")
            missing.append(fragment)
    return {
        "missing_count": len(missing),
        "missing": missing,
    }


NEW_GUARD_NAME = "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py"


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    docs = _check_docs(failures)
    snapshot_prereq = _check_direction_snapshot_entry_prereq(failures)
    downstream_wiring = _check_artifact_only_downstream_wiring(failures)
    position_execution = _check_position_execution_closed(failures)
    primary_connection = _check_primary_connection(failures)

    summary = {
        "phase": "phase4a_direction_replay_artifact_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "docs": docs,
            "direction_snapshot_entry_prereq": snapshot_prereq,
            "downstream_wiring": downstream_wiring,
            "position_execution_closed": position_execution,
            "primary_connection": primary_connection,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
