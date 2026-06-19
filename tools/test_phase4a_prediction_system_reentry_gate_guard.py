# path: ./tools/test_phase4a_prediction_system_reentry_gate_guard.py
# desc: Guard the thread closeout re-entry point so the next thread starts from Prediction System / Scenario Prediction Core, not S204 visibility-chain continuation or AutoTrade execution.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    DEFAULT_PREDICTION_SYSTEM_VERSION,
    DEFAULT_REQUESTED_HORIZONS,
    PredictionCalibrationHint,
    PredictionScenarioOutput,
    PredictionSystemInput,
)
from btcts.processing.l4_consumer_models.shared.prediction_scenario_builder import (
    PredictionScenarioBuildInput,
    build_prediction_scenario_output,
)
from btcts.replay.prediction_calibration_review import (
    PredictionCalibrationReviewBuildInput,
    build_prediction_calibration_review,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md"
ROADMAP = REPO_ROOT / "tmp/gpt_room/memory/roadmaps/PHASE3_PREDICTION_PROCESS_ENTRY_ROADMAP_2026-04-16.md"
NAVIGATOR = REPO_ROOT / "tmp/gpt_room/memory/notes/PHASE3_CURRENT_MAINLINE_NAVIGATOR_2026-04-18.md"
STATE = REPO_ROOT / "tmp/gpt_room/11_STATE.json"
FOCUS = REPO_ROOT / "tmp/gpt_room/09_FOCUS.json"
PREDICTION_FILES = (
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_system_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_system_input.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_liquidity_board_history.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_regime_turning_point.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_replay_feedback.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_calibration_hint_builder.py",
    "btcts_next/src/btcts/replay/prediction_evaluation_entry.py",
    "btcts_next/src/btcts/replay/prediction_evaluation_report.py",
    "btcts_next/src/btcts/replay/prediction_calibration_review.py",
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_prediction_feedback.py",
)
PREDICTION_TESTS = (
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_system_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_system_input.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder_replay_feedback_caution.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder_replay_feedback_invalidation.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_liquidity_board_history.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_regime_turning_point.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_calibration_hint_builder.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_evaluation_entry.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_evaluation_report.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_calibration_review.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_prediction_feedback_scenario_bridge.py",
)
FORBIDDEN_DOC_TOKENS = (
    "resume AutoTrade automatically",
    "continue S204 automatically",
    "broker integration first",
    "order placement first",
)
ALLOWED_DIRTY_MARKERS = (
    "docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md",
    "tools/test_phase4a_prediction_system_reentry_gate_guard.py",
    "tools/test_phase4a_prediction_system_reentry_gate_close_guard.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _syntax_ok(path: Path) -> bool:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return True


def main() -> int:
    failures: list[str] = []
    for path in (DOC, ROADMAP, NAVIGATOR, STATE, FOCUS):
        if not path.exists():
            failures.append(f"missing required reentry artifact: {path.relative_to(REPO_ROOT)}")
    for rel in PREDICTION_FILES + PREDICTION_TESTS:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing prediction system file/test: {rel}")
    if not failures:
        doc_text = _read(DOC)
        roadmap_text = _read(ROADMAP)
        navigator_text = _read(NAVIGATOR)
        state = _json(STATE)
        focus = _json(FOCUS)
        for token in FORBIDDEN_DOC_TOKENS:
            if token in doc_text:
                failures.append(f"forbidden reentry doc token: {token}")
        checks = {
            "doc_declares_prediction_reentry": "Prediction System / Scenario Prediction Core strengthening" in doc_text and "Do not continue to S204 automatically" in doc_text,
            "doc_preserves_autotrade_bookmark": "kill switch / incident / heartbeat runtime scaffolding" in doc_text and "AutoTrade main roadmap remains paused/frozen" in doc_text,
            "doc_forbids_execution_first": "broker integration" in doc_text and "order placement" in doc_text and "mode apply" in doc_text,
            "roadmap_is_prediction_system_entry": "Phase 3 Prediction System Entry Roadmap" in roadmap_text and "Scenario Prediction Core" in roadmap_text,
            "roadmap_excludes_autotrade_execution": "full execution automation" in roadmap_text and "execution / auto-trading 本実装" in roadmap_text,
            "navigator_points_to_scenario_core": (
                "Scenario Prediction Core" in navigator_text
                and "PredictionSummary" in navigator_text
                and "mainline goal" in navigator_text
                and "誤読しない" in navigator_text
            ),
            "state_preserves_autotrade_pause_rule": "Do not resume automatically" in json.dumps(state, ensure_ascii=False) and "explicit human approval" in json.dumps(state, ensure_ascii=False),
            "focus_or_state_has_s203_or_prediction_reentry": ("S203 completed" in json.dumps(focus, ensure_ascii=False) or "prediction_system_reentry" in json.dumps(focus, ensure_ascii=False) or "Prediction System" in json.dumps(focus, ensure_ascii=False)),
            "contract_version": DEFAULT_PREDICTION_SYSTEM_VERSION == "phase3.v1alpha1",
            "default_horizons": DEFAULT_REQUESTED_HORIZONS == ("5m", "10m", "30m"),
            "scenario_output_is_advisory_only": hasattr(PredictionScenarioOutput, "__dataclass_fields__") and "outlooks" in PredictionScenarioOutput.__dataclass_fields__ and "scenario_switch_hint" in PredictionScenarioOutput.__dataclass_fields__,
            "prediction_input_shape": hasattr(PredictionSystemInput, "__dataclass_fields__") and "evidence_bundle" in PredictionSystemInput.__dataclass_fields__,
        }
        failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
        try:
            empty_scenario = build_prediction_scenario_output(PredictionScenarioBuildInput())
            requested_input = PredictionSystemInput()
            horizon_scenario = build_prediction_scenario_output(
                PredictionScenarioBuildInput(prediction_input=requested_input)
            )
            review = build_prediction_calibration_review(PredictionCalibrationReviewBuildInput())
            smoke_checks = {
                "scenario_empty_input_fails_safe": (
                    empty_scenario.current_caution_level == "blocked"
                    and empty_scenario.source_kind == "prediction_system_input"
                    and tuple(empty_scenario.outlooks) == ()
                ),
                "scenario_requested_horizons": (
                    tuple(item.horizon for item in horizon_scenario.outlooks)
                    == DEFAULT_REQUESTED_HORIZONS
                ),
                "calibration_review_default": review["review_type"] == "prediction_calibration_review" and review["review_priority"] in {"normal", "medium", "high"},
                "calibration_hint_shape": PredictionCalibrationHint().hint_version == "phase3.v1alpha1",
            }
            checks.update(smoke_checks)
            failures.extend(f"check failed: {name}" for name, ok in smoke_checks.items() if not ok)
        except Exception as exc:
            failures.append(f"prediction builder smoke failed: {exc}")
        try:
            _syntax_ok(Path(__file__))
        except Exception as exc:
            failures.append(f"guard syntax failed: {exc}")

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in ALLOWED_DIRTY_MARKERS)]
    failures.extend(f"unexpected dirty file during prediction reentry gate: {line}" for line in unexpected_dirty)
    payload = {
        "ok": not failures,
        "phase": "phase3_prediction_system_reentry_gate_thread_closeout",
        "status": "closed" if not failures else "open",
        "contract": {
            "next_thread_starts_from_prediction_system": not failures,
            "s204_not_continued_automatically": not failures,
            "autotrade_remains_paused": not failures,
            "autotrade_return_bookmark_preserved": not failures,
            "prediction_baseline_files_present": all((REPO_ROOT / rel).exists() for rel in PREDICTION_FILES),
            "prediction_baseline_tests_present": all((REPO_ROOT / rel).exists() for rel in PREDICTION_TESTS),
            "only_expected_files_dirty": not unexpected_dirty,
        },
        "next_thread": {
            "first_mainline": "Prediction System / Scenario Prediction Core strengthening",
            "first_do_not_do": ("S204 visibility-chain continuation", "AutoTrade execution", "broker/mode/order work"),
            "autotrade_return_bookmark": "kill switch / incident / heartbeat runtime scaffolding",
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_system_reentry_gate_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
