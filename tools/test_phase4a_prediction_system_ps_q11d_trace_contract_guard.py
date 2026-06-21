# path: ./tools/test_phase4a_prediction_system_ps_q11d_trace_contract_guard.py
# desc: Close guard for PS-Q11D Scenario Core trace contract consolidation; advisory/read-only only.

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
    "tools/test_phase4a_prediction_system_ps_q11d_trace_contract_guard.py",
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
EXPECTED_TRACE_NAMES = (
    "evidence_weighting_trace",
    "invalidation_rewrite_trace",
    "scenario_switch_trace",
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
                "interpretation_reason": "ps_q11d_close_guard",
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


def _check_contract(output, label: str, failures: list[str]) -> None:
    scenario_trace = dict(output.scenario_trace or {})
    evidence_trace = dict(scenario_trace.get("evidence_weighting_trace") or {})
    rewrite_trace = dict(scenario_trace.get("invalidation_rewrite_trace") or {})
    switch_trace = dict(scenario_trace.get("scenario_switch_trace") or {})
    contract = dict(scenario_trace.get("trace_contract_summary") or {})

    checks = {
        f"{label}_evidence_trace_type": evidence_trace.get("trace_type") == "prediction_evidence_weighting_trace",
        f"{label}_rewrite_trace_type": rewrite_trace.get("trace_type") == "prediction_invalidation_rewrite_trace",
        f"{label}_switch_trace_type": switch_trace.get("trace_type") == "prediction_scenario_switch_trace",
        f"{label}_contract_trace_type": contract.get("trace_type") == "prediction_scenario_trace_contract",
        f"{label}_contract_status": contract.get("contract_status") == "complete",
        f"{label}_contract_count": contract.get("trace_count") == 3,
        f"{label}_contract_names": contract.get("trace_names") == EXPECTED_TRACE_NAMES,
        f"{label}_contract_missing_empty": contract.get("missing_trace_names") == (),
        f"{label}_contract_advisory": contract.get("advisory_read_only") is True,
        f"{label}_contract_execution_surface": contract.get("execution_surface") == "none",
        f"{label}_contract_runtime_surface": contract.get("runtime_write_surface") == "none",
        f"{label}_diag_status": output.diagnostics.get("scenario_trace_contract_status") == "complete",
        f"{label}_diag_count": output.diagnostics.get("scenario_trace_contract_trace_count") == 3,
        f"{label}_diag_advisory": output.diagnostics.get("scenario_trace_contract_advisory_read_only") is True,
        f"{label}_no_broker_request": not bool(output.diagnostics.get("would_send_to_broker")),
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
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                failures.append(f"forbidden runtime token in {path.relative_to(REPO_ROOT)}: {token}")

    scenario_text = _read(SCENARIO)
    required_markers = (
        "def _build_trace_contract_summary(",
        "prediction_scenario_trace_contract",
        "trace_contract_summary",
        "scenario_trace_contract_status",
        "scenario_trace_contract_trace_count",
        "scenario_trace_contract_advisory_read_only",
        "execution_surface",
        "runtime_write_surface",
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
        _check_contract(raised_output, "raised", failures)

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
        _check_contract(transition_output, "transition", failures)

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
        _check_contract(reversal_output, "reversal", failures)

        absent_output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=None)
        )
        _check_contract(absent_output, "absent", failures)
    except Exception as exc:
        failures.append(f"trace contract smoke failed: {exc}")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q11d_trace_contract",
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


def test_ps_q11d_trace_contract_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
