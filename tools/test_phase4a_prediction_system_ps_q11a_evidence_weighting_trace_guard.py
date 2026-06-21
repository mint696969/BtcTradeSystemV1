# path: ./tools/test_phase4a_prediction_system_ps_q11a_evidence_weighting_trace_guard.py
# desc: Close guard for PS-Q11A Scenario Core evidence weighting trace; advisory/read-only only.

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
SCENARIO_TEST = REPO_ROOT / "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder.py",
    "tools/test_phase4a_prediction_system_ps_q11a_evidence_weighting_trace_guard.py",
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
        if not line.strip():
            continue
        out.add(line[3:].replace("\\", "/"))
    return out


def _build_market_summary() -> object:
    return build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-18T03:20:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "interpretation_reason": "ps_q11a_close_guard",
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
                    "summary_slots_present": ["near_wall", "support"],
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


def main() -> int:
    failures: list[str] = []

    for path in (SCENARIO, SCENARIO_TEST):
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
                failures.append(
                    f"forbidden runtime token in {path.relative_to(REPO_ROOT)}: {token}"
                )

    scenario_text = _read(SCENARIO)
    required_markers = (
        "def _build_evidence_weighting_trace(",
        "prediction_evidence_weighting_trace",
        "evidence_weighting_trace",
        "evidence_weighting_summary",
        "evidence_weighting_active_weight_total",
    )
    for marker in required_markers:
        if marker not in scenario_text:
            failures.append(f"missing scenario marker: {marker}")

    try:
        prediction_input = build_prediction_system_input(
            PredictionSystemBuildInput(
                market_summary=_build_market_summary(),
                liquidity_board_history={
                    "history_window_sec": 120,
                    "wall_persistence_bias": "bid_support",
                },
                regime_turning_point={
                    "transition_sign": "stable_continuation",
                    "turning_point_risk": "low",
                },
                replay_feedback=build_prediction_replay_feedback(
                    PredictionReplayFeedbackBuildInput(
                        calibration_review={
                            "review_priority": "normal",
                            "primary_focus": "trace_review",
                        },
                        evaluation_report={
                            "entry_count": 2,
                            "missed_count": 0,
                            "high_priority_count": 0,
                        },
                    )
                ),
            )
        )
        output = build_prediction_scenario_output(
            PredictionScenarioBuildInput(prediction_input=prediction_input)
        )
        trace = dict(output.scenario_trace.get("evidence_weighting_trace") or {})
        summary = dict(output.evidence.get("evidence_weighting_summary") or {})
        checks = {
            "trace_type": trace.get("trace_type") == "prediction_evidence_weighting_trace",
            "family_count": trace.get("family_count") == 5,
            "active_weight_total": trace.get("active_weight_total") == 0.9,
            "missing_weight_total": trace.get("missing_weight_total") == 0.0,
            "primary_family": trace.get("primary_family") == "market_summary_anchor",
            "summary_matches_trace": summary.get("active_weight_total") == trace.get("active_weight_total"),
            "diagnostics_active_weight": output.diagnostics.get("evidence_weighting_active_weight_total") == 0.9,
            "advisory_no_broker_request": not bool(output.diagnostics.get("would_send_to_broker")),
        }
        failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    except Exception as exc:
        failures.append(f"scenario evidence weighting smoke failed: {exc}")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q11a_evidence_weighting_trace",
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


def test_ps_q11a_evidence_weighting_trace_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
