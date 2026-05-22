# path: ./tools/test_phase4a_direction_position_execution_entry_criteria_guard.py
# desc: Phase 4-A Direction / Position / Execution entry criteria boundary guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

SPEC_PATH = "tmp/docs/architecture/PHASE4A_DIRECTION_POSITION_EXECUTION_ENTRY_CRITERIA_2026-05-17.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"

COMPILE_TARGETS = [
    "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py",
    "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_reading_caption.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_health_top_panels_digest_caption.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
]

PREMATURE_RUNTIME_TOKENS = [
    "PredictionPositionHint",
    "PredictionExecutionHint",
    "build_prediction_position",
    "build_prediction_execution",
]

SOURCE_SCAN_ROOTS = [
    "btcts_next/src/btcts/processing/l4_consumer_models",
    "btcts_next/src/btcts/apps/operator_ui",
]

REVIEW_ONLY_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py",
    "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py",
]

FORBIDDEN_REVIEW_ONLY_FRAGMENTS = [
    "execution=instruction",
    "review_mode=auto_execution",
    "final_decision",
    "automatic decision",
    "broker_order",
    "place_order",
    "order_placement",
    "live_order_placement",
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


def _check_docs_entry_criteria(failures: List[str]) -> Dict[str, Any]:
    spec_text = _read_text(SPEC_PATH)
    index_text = _read_text(INDEX_PATH)

    required_spec_fragments = [
        "Direction / Position / Execution は、まだ runtime 実装に入らない。",
        "Direction layer",
        "Position layer",
        "Execution layer",
        "live order placement",
        "broker/order automation",
        "runtime implementation ではなく、",
        "tools/test_phase4a_direction_position_execution_entry_criteria_guard.py",
    ]

    required_index_fragments = [
        "PHASE4A_DIRECTION_POSITION_EXECUTION_ENTRY_CRITERIA_GUARD_CONNECTION_2026-05-17.md",
        "PHASE4A_DIRECTION_POSITION_EXECUTION_ENTRY_CRITERIA_2026-05-17.md",
        "Direction contract skeleton guard alignment",
        "Direction contract skeleton は repo に追加済み",
        "Direction is read-only market interpretation contract.",
        "Position / Execution layers remain closed.",
    ]

    missing: List[Dict[str, str]] = []

    if not (REPO_ROOT / SPEC_PATH).exists():
        failures.append(f"entry criteria spec missing: {SPEC_PATH}")
        missing.append({"path": SPEC_PATH, "fragment": "__file_missing__"})

    if not (REPO_ROOT / INDEX_PATH).exists():
        failures.append(f"docs index missing: {INDEX_PATH}")
        missing.append({"path": INDEX_PATH, "fragment": "__file_missing__"})

    for fragment in required_spec_fragments:
        if fragment not in spec_text:
            failures.append(f"entry criteria spec fragment missing: {fragment}")
            missing.append({"path": SPEC_PATH, "fragment": fragment})

    for fragment in required_index_fragments:
        if fragment not in index_text:
            failures.append(f"docs index fragment missing: {fragment}")
            missing.append({"path": INDEX_PATH, "fragment": fragment})

    first_current_pos = index_text.find("### current formal spec")
    spec_pos = index_text.find("PHASE4A_DIRECTION_POSITION_EXECUTION_ENTRY_CRITERIA_2026-05-17.md")
    phase_de_pos = index_text.find("PHASE4A_PHASE_D_E_HEALTH_WARROOM_OPERATIONAL_READING_CLOSE_2026-05-17.md")

    ordering_ok = (
        first_current_pos >= 0
        and spec_pos >= 0
        and phase_de_pos >= 0
        and first_current_pos < spec_pos < phase_de_pos
    )
    if not ordering_ok:
        failures.append("entry criteria spec must be the first current formal spec in docs/_INDEX.md")

    return {
        "missing_count": len(missing),
        "missing": missing,
        "ordering_ok": bool(ordering_ok),
    }


def _check_room_current_focus(failures: List[str]) -> Dict[str, Any]:
    status_text = _read_text(STATUS_PATH)
    focus_text = _read_text(FOCUS_PATH)

    required_fragments = {
        STATUS_PATH: [
            "Direction contract skeleton guard alignment",
            "Direction / Position / Execution entry criteria guard は primary guard に接続済み",
            "Direction contract skeleton は repo に追加済み",
            "Direction contract は read-only market interpretation contract",
            "Position / Execution runtime behavior はまだ開かない",
        ],
        FOCUS_PATH: [
            "phase4a_direction_contract_skeleton_guard_alignment_then_thin_builder_skeleton",
            "treat_direction_position_execution_entry_criteria_guard_as_guarded",
            "direction_contract_skeleton_is_opened_as_read_only_contract_only",
            "keep_position_and_execution_layers_closed",
            "next_update_entry_criteria_guard_to_allow_direction_contract_skeleton",
            "then_add_thin_direction_builder_skeleton_only",
        ],
    }

    missing: List[Dict[str, str]] = []

    if not (REPO_ROOT / STATUS_PATH).exists():
        failures.append(f"STATUS missing: {STATUS_PATH}")
        missing.append({"path": STATUS_PATH, "fragment": "__file_missing__"})

    if not (REPO_ROOT / FOCUS_PATH).exists():
        failures.append(f"FOCUS missing: {FOCUS_PATH}")
        missing.append({"path": FOCUS_PATH, "fragment": "__file_missing__"})

    texts = {
        STATUS_PATH: status_text,
        FOCUS_PATH: focus_text,
    }

    for rel_path, fragments in required_fragments.items():
        text = texts[rel_path]
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"room current focus fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
    }


def _scan_premature_runtime_tokens(failures: List[str]) -> Dict[str, Any]:
    hits: List[Dict[str, str]] = []

    for root_rel in SOURCE_SCAN_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")

            for token in PREMATURE_RUNTIME_TOKENS:
                if token in text:
                    hits.append({"path": rel, "token": token})
                    failures.append(
                        "Direction / Position / Execution runtime contract appears "
                        f"before entry criteria guard is explicitly opened: {rel}: {token}"
                    )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_direction_contract_skeleton(failures: List[str]) -> Dict[str, Any]:
    contract_path = (
        "btcts_next/src/btcts/processing/l4_consumer_models/contracts/"
        "prediction_direction_contract.py"
    )
    init_path = "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py"
    boundary_test_path = (
        "btcts_next/src/btcts/processing/l4_consumer_models/tests/"
        "test_prediction_direction_contract_boundary.py"
    )

    required_by_file = {
        contract_path: [
            "class HorizonDirectionReading",
            "class PredictionDirectionOutput",
            "scenario_ref",
            "primary_direction_bias",
            "horizon_direction_readings",
            "evidence_trace_refs",
            "not execution instruction",
            "not broker/order automation",
        ],
        init_path: [
            "HorizonDirectionReading",
            "PredictionDirectionOutput",
            "__all__",
        ],
        boundary_test_path: [
            "test_prediction_direction_contract_is_not_position_owner",
            "test_prediction_direction_contract_is_read_model_only",
            "position_size",
            "order_size",
            "broker_account",
        ],
    }

    builder_path = (
        "btcts_next/src/btcts/processing/l4_consumer_models/shared/"
        "prediction_direction_builder.py"
    )
    shared_init_path = "btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py"
    builder_test_path = (
        "btcts_next/src/btcts/processing/l4_consumer_models/tests/"
        "test_prediction_direction_builder.py"
    )

    required_by_file.update(
        {
            builder_path: [
                "class PredictionDirectionBuildInput",
                "def build_prediction_direction_output(",
                "PredictionDirectionOutput(",
                "HorizonDirectionReading(",
                "builder_stage",
                "thin_skeleton",
                "read_only_contract",
                "not_position_owner",
                "not_execution_instruction",
                "not_broker_automation",
            ],
            shared_init_path: [
                "PredictionDirectionBuildInput",
                "build_prediction_direction_output",
            ],
            builder_test_path: [
                "test_prediction_direction_builder_returns_read_only_contract",
                "test_prediction_direction_builder_does_not_emit_position_or_execution_fields",
                "builder_stage",
                "thin_skeleton",
                "not_position_owner",
                "not_execution_instruction",
                "not_broker_automation",
            ],
        }
    )

    forbidden_by_contract = [
        "position_size",
        "leverage",
        "entry_price",
        "exit_price",
        "order_price",
        "order_size",
        "broker_account",
        "place_order",
        "broker_order",
    ]

    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"direction contract file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing_or_empty__"})
            continue

        for fragment in fragments:
            if fragment not in text:
                failures.append(f"direction contract fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    contract_text = _read_text(contract_path)
    builder_text = _read_text(builder_path)

    for fragment in forbidden_by_contract:
        if fragment in contract_text:
            failures.append(f"direction contract must not own position/execution field: {fragment}")
            forbidden.append({"path": contract_path, "fragment": fragment})
        if fragment in builder_text:
            failures.append(f"direction builder must not own position/execution field: {fragment}")
            forbidden.append({"path": builder_path, "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
    }


def _check_review_only_operational_reading(failures: List[str]) -> Dict[str, Any]:
    required_by_file = {
        "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py": [
            "build_warroom_operational_reading_caption",
            "review_mode=operator_review_only",
            "execution=not_instruction",
            "active_event_compact_reading_line",
        ],
        "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py": [
            "build_health_digest_operational_reading_caption",
            "review_mode=operator_review_only",
            "execution=not_instruction",
            "active_event_compact_reading_line",
        ],
    }

    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"review-only file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing_or_empty__"})
            continue

        for fragment in fragments:
            if fragment not in text:
                failures.append(f"review-only operational reading fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

        for fragment in FORBIDDEN_REVIEW_ONLY_FRAGMENTS:
            if fragment in text:
                failures.append(f"operational reading must remain review-only: {rel_path}: {fragment}")
                forbidden.append({"path": rel_path, "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
    }


def _check_tactic_stance_not_execution_instruction(failures: List[str]) -> Dict[str, Any]:
    tactic_spec_path = (
        "tmp/docs/strategy/"
        "PHASE4A_ADAPTIVE_SCENARIO_TACTIC_MINIMAL_CONTRACT_BTC_BITFLYER_2026-04-19.md"
    )
    text = _read_text(tactic_spec_path)

    required_fragments = [
        "tactic は execution ではなく **operating stance** として扱う",
        "tactic proposal を execution owner にしない",
        "execution owner を作らずに operating stance proposal を返せる",
    ]

    missing: List[str] = []

    if not text:
        failures.append(f"tactic spec missing or empty: {tactic_spec_path}")
        missing.append("__file_missing_or_empty__")

    for fragment in required_fragments:
        if fragment not in text:
            failures.append(f"tactic stance fragment missing: {fragment}")
            missing.append(fragment)

    return {
        "path": tactic_spec_path,
        "missing_count": len(missing),
        "missing": missing,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    docs_entry_criteria = _check_docs_entry_criteria(failures)
    room_focus = _check_room_current_focus(failures)
    premature_runtime_tokens = _scan_premature_runtime_tokens(failures)
    direction_contract_skeleton = _check_direction_contract_skeleton(failures)
    review_only_operational_reading = _check_review_only_operational_reading(failures)
    tactic_stance = _check_tactic_stance_not_execution_instruction(failures)

    summary = {
        "phase": "phase4a_direction_position_execution_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "docs_entry_criteria": docs_entry_criteria,
            "room_focus": room_focus,
            "premature_runtime_tokens": premature_runtime_tokens,
            "direction_contract_skeleton": direction_contract_skeleton,
            "review_only_operational_reading": review_only_operational_reading,
            "tactic_stance": tactic_stance,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())