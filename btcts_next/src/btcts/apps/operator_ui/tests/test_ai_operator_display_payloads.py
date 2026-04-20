# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_display_payloads.py
# desc: Verify ai_operator display payload builder keeps watch/summary/prediction display lowering stable.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.ai_operator_display_payloads as payloads  # noqa: E402


def main() -> int:
    original_summary_widget_caption = payloads.summary_widget_caption
    original_prediction_snapshot_lines = payloads.prediction_snapshot_lines

    try:
        payloads.summary_widget_caption = lambda widget: f"summary:{widget['kind']}"
        payloads.prediction_snapshot_lines = lambda widget: (
            []
            if not widget
            else [
                f"bias={widget['bias']}",
                f"trace_focus={widget['trace_focus']}",
                f"confidence={widget['confidence']}",
                f"trace_summary={widget['trace_summary']}",
                f"scenario_switch_hint={widget['scenario_switch_hint']}",
                f"invalidation_state={widget['invalidation_state']}",
                f"hypothesis_health={widget['hypothesis_health']}",
                f"caution={widget['caution']}",
            ]
        )

        display_payloads = payloads.build_operator_display_payloads(
            summary_widget={"kind": "market_summary"},
            prediction_widget={
                "bias": "bullish",
                "confidence": "0.72",
                "caution": "medium",
                "scenario_switch_hint": "watch_reversal_path",
                "invalidation_state": "caution_increase",
                "hypothesis_health": "caution_increase",
                "trace_summary": "transition_sign:weakening_continuation / watch_reversal_path",
                "trace_focus": "switch_bias(1.0)",
            },
            watch_note={
                "ts": "2026-04-17T02:30:00Z",
                "regime": "transition",
                "action": "trap_caution",
                "risk": "high",
            },
            is_live_market=False,
        )

        assert display_payloads["watch_note_caption"] == (
            "watch ts=2026-04-17T02:30:00Z / "
            "regime=transition / "
            "action=trap_caution / "
            "risk=high"
        )
        assert display_payloads["summary_caption"] == "summary:market_summary"
        assert display_payloads["prediction_lines"] == [
            "bias=bullish",
            "trace_focus=switch_bias(1.0)",
            "confidence=0.72",
            "trace_summary=transition_sign:weakening_continuation / watch_reversal_path",
            "scenario_switch_hint=watch_reversal_path",
            "invalidation_state=caution_increase",
            "hypothesis_health=caution_increase",
            "caution=medium",
        ]
        assert display_payloads["prediction_explanation_note"] == (
            "prediction_context: "
            "scenario_switch_hint=watch_reversal_path | "
            "invalidation_state=caution_increase | "
            "hypothesis_health=caution_increase | "
            "trace_summary=transition_sign:weakening_continuation / watch_reversal_path | "
            "trace_focus=switch_bias(1.0) | "
            "caution=medium | "
            "confidence=0.72"
        )
        assert display_payloads["operator_explanation_note"] == (
            "watch_context: caption=watch ts=2026-04-17T02:30:00Z / "
            "regime=transition / action=trap_caution / risk=high\n"
            "summary_context: caption=summary:market_summary\n"
            "prediction_context: "
            "scenario_switch_hint=watch_reversal_path | "
            "invalidation_state=caution_increase | "
            "hypothesis_health=caution_increase | "
            "trace_summary=transition_sign:weakening_continuation / watch_reversal_path | "
            "trace_focus=switch_bias(1.0) | "
            "caution=medium | "
            "confidence=0.72"
        )

        live_payloads = payloads.build_operator_display_payloads(
            summary_widget=None,
            prediction_widget=None,
            watch_note={
                "ts": "2026-04-17T02:30:00Z",
                "regime": "transition",
                "action": "trap_caution",
                "risk": "high",
            },
            is_live_market=True,
        )

        assert live_payloads["watch_note_caption"] is None
        assert live_payloads["summary_caption"] is None
        assert live_payloads["prediction_lines"] == []
        assert live_payloads["prediction_explanation_note"] == ""
        assert live_payloads["operator_explanation_note"] == ""

        partial_payloads = payloads.build_operator_display_payloads(
            summary_widget=None,
            prediction_widget={
                "bias": "bullish",
                "confidence": "0.72",
                "caution": "medium",
                "scenario_switch_hint": "watch_reversal_path",
                "invalidation_state": "caution_increase",
                "hypothesis_health": "caution_increase",
                "trace_summary": "transition_sign:weakening_continuation / watch_reversal_path",
                "trace_focus": "switch_bias(1.0)",
            },
            watch_note=None,
            is_live_market=False,
        )

        assert partial_payloads["watch_note_caption"] is None
        assert partial_payloads["summary_caption"] is None
        assert partial_payloads["prediction_explanation_note"] == (
            "prediction_context: "
            "scenario_switch_hint=watch_reversal_path | "
            "invalidation_state=caution_increase | "
            "hypothesis_health=caution_increase | "
            "trace_summary=transition_sign:weakening_continuation / watch_reversal_path | "
            "trace_focus=switch_bias(1.0) | "
            "caution=medium | "
            "confidence=0.72"
        )
        assert partial_payloads["operator_explanation_note"] == (
            "prediction_context: "
            "scenario_switch_hint=watch_reversal_path | "
            "invalidation_state=caution_increase | "
            "hypothesis_health=caution_increase | "
            "trace_summary=transition_sign:weakening_continuation / watch_reversal_path | "
            "trace_focus=switch_bias(1.0) | "
            "caution=medium | "
            "confidence=0.72"
        )

        tactic_payloads = payloads.build_operator_display_payloads(
            summary_widget=None,
            prediction_widget=None,
            watch_note=None,
            is_live_market=False,
            tactic_context={
                "primary_tactic_key": "reversal_prepare",
                "proposal_state": "proposed",
                "scenario_regime": "reversal_watch",
                "rollback_ready": True,
                "review_needed": True,
                "diagnostics": {
                    "parameter_trace": {"profile_kind": "candidate"},
                    "selection_trace": {
                        "selection_bias_tags": (
                            "overlay:prefer_reversal_prepare",
                        )
                    },
                },
            },
        )

        assert tactic_payloads["tactic_context"] == {
            "primary_tactic_key": "reversal_prepare",
            "proposal_state": "proposed",
            "scenario_regime": "reversal_watch",
            "profile_kind": "candidate",
            "rollback_ready": True,
            "review_needed": True,
            "selection_bias_tags": ("overlay:prefer_reversal_prepare",),
        }
        assert tactic_payloads["tactic_summary_lines"] == (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "selection_bias_tags=overlay:prefer_reversal_prepare",
        )
        assert tactic_payloads["tactic_explanation_note"] == (
            "tactic_stance_context: "
            "operating_stance=reversal_prepare | "
            "scenario_regime=reversal_watch | "
            "proposal_state=proposed | "
            "profile_kind=candidate | "
            "review_needed=true | "
            "rollback_ready=true | "
            "selection_bias_tags=overlay:prefer_reversal_prepare"
        )
        assert tactic_payloads["operator_explanation_note"] == (
            "tactic_stance_context: "
            "operating_stance=reversal_prepare | "
            "scenario_regime=reversal_watch | "
            "proposal_state=proposed | "
            "profile_kind=candidate | "
            "review_needed=true | "
            "rollback_ready=true | "
            "selection_bias_tags=overlay:prefer_reversal_prepare"
        )
    finally:
        payloads.summary_widget_caption = original_summary_widget_caption
        payloads.prediction_snapshot_lines = original_prediction_snapshot_lines

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())