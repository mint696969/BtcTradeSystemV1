# path: ./tools/test_phase4a_prediction_system_ps_q11b_invalidation_rewrite_trace_guard.py
# desc: Close guard for PS-Q11B Scenario Core invalidation/rewrite trace; advisory/read-only only.

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
    "tools/test_phase4a_prediction_system_ps_q11b_invalidation_rewrite_trace_guard.py",
}
FORBIDDEN_RUNTIME_TOKENS = (
    "would_send_to_broker=True",
    "would_send_to_broker = True",
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
                "interpretation_reason": "ps_q11b_close_guard",
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


def _build_replay_feedback(*, focus: str = "unknown") -> dict:
    calibration_review = {
        "review_priority": "high",
        "primary_focus": "invalidation_review",
        "invalidation_review": "raise_invalidation_sensitivity",
    }
    if focus != "unknown":
        calibration_review["scenario_trace_focus"] = focus
    return build_prediction_replay_feedback(
        PredictionReplayFeedbackBuildInput(
            calibration_review=calibration_review,
            evaluation_report={
                "entry_count": 4,
                "missed_count": 3,
                "high_priority_count": 3,
            },
        )
    )


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
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                failures.append(f"forbidden runtime token in {path.relative_to(REPO_ROOT)}: {token}")

    scenario_text = _read(SCENARIO)
    required_markers = (
        "def _build_invalidation_rewrite_trace(",
        "prediction_invalidation_rewrite_trace",
        "invalidation_rewrite_trace",
        "invalidation_rewrite_state",
        "trace_focus_rewrite_action",
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
        raised_trace = dict(
            raised_output.scenario_trace.get("invalidation_rewrite_trace") or {}
        )
        raised_checks = {
            "raised_trace_type": raised_trace.get("trace_type") == "prediction_invalidation_rewrite_trace",
            "raised_rewrite_state": raised_trace.get("rewrite_state") == "rewrite_watch",
            "raised_rewrite_priority": raised_trace.get("rewrite_priority") == "medium",
            "raised_signal_count": raised_trace.get("invalidation_signal_count") == len(raised_output.invalidation_signals),
            "raised_feedback_effect": raised_trace.get("replay_feedback_rewrite_effect") == "raise_rewrite_sensitivity",
            "raised_diagnostics": raised_output.diagnostics.get("invalidation_rewrite_state") == "rewrite_watch",
            "raised_no_broker_request": not bool(raised_output.diagnostics.get("would_send_to_broker")),
        }
        failures.extend(f"check failed: {name}" for name, ok in raised_checks.items() if not ok)

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
        transition_trace = dict(
            transition_output.scenario_trace.get("invalidation_rewrite_trace") or {}
        )
        transition_checks = {
            "transition_rewrite_state": transition_trace.get("rewrite_state") == "rewrite_required",
            "transition_rewrite_priority": transition_trace.get("rewrite_priority") == "high",
        }
        failures.extend(f"check failed: {name}" for name, ok in transition_checks.items() if not ok)

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
        reversal_trace = dict(
            reversal_output.scenario_trace.get("invalidation_rewrite_trace") or {}
        )
        reversal_checks = {
            "reversal_rewrite_state": reversal_trace.get("rewrite_state") == "rewrite_prepared",
            "reversal_rewrite_priority": reversal_trace.get("rewrite_priority") == "high",
            "reversal_trace_focus_action": reversal_trace.get("trace_focus_rewrite_action") == "prioritize_switch_reason_review",
        }
        failures.extend(f"check failed: {name}" for name, ok in reversal_checks.items() if not ok)
    except Exception as exc:
        failures.append(f"scenario invalidation rewrite smoke failed: {exc}")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q11b_invalidation_rewrite_trace",
        "phase": "phase3_prediction_system_reentry_scenario_prediction_core_strengthening",
        "contract": {
            "scenario_core_only": not failures,
            "advisory_read_only_only": not failures,
            "no_broker_mode_order_ledger_runtime_path": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q11b_invalidation_rewrite_trace_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
