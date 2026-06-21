# path: ./tools/test_phase4a_prediction_system_ps_q11f_operator_review_handoff_guard.py
# desc: Close guard for PS-Q11F Scenario Core operator review handoff shape; manual-review/read-only/non-executing only.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    MarketSummaryBuildInput,
    PredictionReplayFeedbackBuildInput,
    PredictionScenarioBuildInput,
    PredictionSystemBuildInput,
    build_market_summary,
    build_prediction_replay_feedback,
    build_prediction_scenario_output,
    build_prediction_system_input,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO = REPO_ROOT / "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py"
INVALIDATION_TEST = REPO_ROOT / "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder_replay_feedback_invalidation.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder_replay_feedback_invalidation.py",
    "tools/test_phase4a_prediction_system_ps_q11f_operator_review_handoff_guard.py",
}
FORBIDDEN_RUNTIME_TRUE_TOKENS = (
    "would_send_to_broker=True",
    "would_send_to_broker = True",
    "would_append_ledger=True",
    "would_append_ledger = True",
    "would_write_runtime_artifact=True",
    "would_write_runtime_artifact = True",
    "broker_execution_requested=True",
    "broker_execution_requested = True",
    "command_ledger_append_requested=True",
    "command_ledger_append_requested = True",
    "approval_append_requested=True",
    "approval_append_requested = True",
    "mode_apply_requested=True",
    "mode_apply_requested = True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _build_market_summary(*, interpretation_bucket: str = "allow_structural_use") -> object:
    return build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-18T03:20:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": interpretation_bucket,
                "interpretation_reason": "ps_q11f_close_guard",
                "semantic_observer_status": "healthy",
                "semantic_usage_summary": {
                    "source_kind": "market_state_semantic_usage_summary",
                    "contract_source": "l3_event_usage_policy",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "observer_status": "healthy",
                    "active_event_count": 1,
                    "mapped_event_count": 1,
                    "unknown_event_count": 0,
                },
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["near_wall"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 1.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )


def _build_replay_feedback(*, focus: str = "unknown", lower: bool = False) -> dict:
    calibration_review = {
        "review_priority": "normal" if lower else "high",
        "primary_focus": "invalidation_review",
        "invalidation_review": (
            "lower_invalidation_sensitivity"
            if lower
            else "raise_invalidation_sensitivity"
        ),
    }
    if focus != "unknown":
        calibration_review["scenario_trace_focus"] = focus
    return build_prediction_replay_feedback(
        PredictionReplayFeedbackBuildInput(
            calibration_review=calibration_review,
            evaluation_report={
                "entry_count": 4,
                "missed_count": 0 if lower else 3,
                "high_priority_count": 0 if lower else 3,
            },
        )
    )


def _check_handoff(output, label: str, expected_priority: str, expected_route: str, expected_status: str, failures: list[str]) -> None:
    scenario_trace = dict(output.scenario_trace or {})
    handoff = dict(scenario_trace.get("operator_review_handoff_shape") or {})
    checks = {
        f"{label}_trace_type": handoff.get("trace_type") == "prediction_operator_review_handoff_shape",
        f"{label}_handoff_status": handoff.get("handoff_status") == expected_status,
        f"{label}_priority": handoff.get("review_priority") == expected_priority,
        f"{label}_route": handoff.get("review_route") == expected_route,
        f"{label}_manual_review_only": handoff.get("manual_review_only") is True,
        f"{label}_advisory_read_only": handoff.get("advisory_read_only") is True,
        f"{label}_non_executing": handoff.get("non_executing") is True,
        f"{label}_would_send_to_broker_false": handoff.get("would_send_to_broker") is False,
        f"{label}_would_append_ledger_false": handoff.get("would_append_ledger") is False,
        f"{label}_would_write_runtime_artifact_false": handoff.get("would_write_runtime_artifact") is False,
        f"{label}_execution_surface_none": handoff.get("execution_surface") == "none",
        f"{label}_runtime_write_surface_none": handoff.get("runtime_write_surface") == "none",
        f"{label}_contract_review_only": "review_only" in tuple(handoff.get("operator_action_contract") or ()),
        f"{label}_contract_no_auto_trade": "no_auto_trade" in tuple(handoff.get("operator_action_contract") or ()),
        f"{label}_contract_no_runtime_write": "no_runtime_write" in tuple(handoff.get("operator_action_contract") or ()),
        f"{label}_diag_status": output.diagnostics.get("operator_review_handoff_status") == expected_status,
        f"{label}_diag_priority": output.diagnostics.get("operator_review_handoff_priority") == expected_priority,
        f"{label}_diag_route": output.diagnostics.get("operator_review_handoff_route") == expected_route,
        f"{label}_diag_manual_only": output.diagnostics.get("operator_review_handoff_manual_only") is True,
        f"{label}_diag_read_only": output.diagnostics.get("operator_review_handoff_read_only") is True,
        f"{label}_diag_non_executing": output.diagnostics.get("operator_review_handoff_non_executing") is True,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)


def main() -> int:
    failures: list[str] = []

    for path in (SCENARIO, INVALIDATION_TEST):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
        for token in FORBIDDEN_RUNTIME_TRUE_TOKENS:
            if token in text:
                failures.append(f"forbidden runtime true token in {path.relative_to(REPO_ROOT)}: {token}")

    scenario_text = _read(SCENARIO)
    required_markers = (
        "def _build_operator_review_handoff_shape(",
        "prediction_operator_review_handoff_shape",
        "operator_review_handoff_shape",
        "operator_review_handoff_status",
        "operator_review_handoff_priority",
        "operator_review_handoff_route",
        "manual_review_only",
        "operator_action_contract",
        "no_auto_trade",
        "no_broker_send",
        "no_order_place",
        "no_ledger_append",
        "no_runtime_write",
        "would_send_to_broker",
        "would_append_ledger",
        "would_write_runtime_artifact",
        "runtime_write_surface",
        "execution_surface",
    )
    for marker in required_markers:
        if marker not in scenario_text:
            failures.append(f"missing scenario marker: {marker}")

    try:
        raised_input = build_prediction_system_input(
            PredictionSystemBuildInput(
                market_summary=_build_market_summary(),
                replay_feedback=_build_replay_feedback(),
            )
        )
        raised_output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=raised_input)
        )
        _check_handoff(
            raised_output,
            "raised",
            "medium",
            "watch_path_review",
            "ready_for_operator_review",
            failures,
        )

        lowered_input = build_prediction_system_input(
            PredictionSystemBuildInput(
                market_summary=_build_market_summary(),
                replay_feedback=_build_replay_feedback(lower=True),
            )
        )
        lowered_output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=lowered_input)
        )
        _check_handoff(
            lowered_output,
            "lowered",
            "normal",
            "optional_review",
            "optional_operator_review",
            failures,
        )

        transition_input = build_prediction_system_input(
            PredictionSystemBuildInput(
                market_summary=_build_market_summary(
                    interpretation_bucket="reanchor_required"
                ),
            )
        )
        transition_output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=transition_input)
        )
        _check_handoff(
            transition_output,
            "transition",
            "high",
            "priority_switch_review",
            "ready_for_operator_review",
            failures,
        )

        reversal_input = build_prediction_system_input(
            PredictionSystemBuildInput(
                market_summary=_build_market_summary(),
                regime_turning_point={
                    "transition_sign": "weakening_continuation",
                    "turning_point_risk": "high",
                },
                replay_feedback=_build_replay_feedback(
                    focus="switch_reason:watch_reversal_path"
                ),
            )
        )
        reversal_output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=reversal_input)
        )
        _check_handoff(
            reversal_output,
            "reversal",
            "high",
            "priority_switch_review",
            "ready_for_operator_review",
            failures,
        )

        absent_output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=None)
        )
        _check_handoff(
            absent_output,
            "absent",
            "high",
            "priority_operator_review",
            "ready_for_operator_review",
            failures,
        )
    except Exception as exc:
        failures.append(f"operator handoff smoke failed: {exc}")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q11f_operator_review_handoff",
        "phase": "phase3_prediction_system_reentry_scenario_prediction_core_strengthening",
        "contract": {
            "scenario_core_only": not failures,
            "manual_review_only": not failures,
            "advisory_read_only_only": not failures,
            "non_executing_only": not failures,
            "no_broker_mode_order_ledger_runtime_path": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q11f_operator_review_handoff_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
