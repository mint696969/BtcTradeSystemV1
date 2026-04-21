# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_advisory.py
# desc: Verify ai_operator advisory boundary keeps explanation note shaping stable.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.ai_operator_advisory as advisory  # noqa: E402


def main() -> int:
    original_generate_answer = advisory.generate_answer

    calls: list[dict] = []

    def _fake_generate_answer(**kwargs):
        calls.append(dict(kwargs))
        return "mock-answer", "mock-runtime"

    try:
        advisory.generate_answer = _fake_generate_answer

        built = advisory.read_operator_advisory_answer(
            lang="en",
            ai_mode="local",
            operator_prompt="Explain current market state",
            intent="decide",
            style="normal",
            state={
                "spread": 1200.0,
                "imbalance": 0.22,
                "delta": 0.31,
                "wall_ratio": 0.18,
            },
            memory=[],
            note=(
                "watch_context: caption=watch ts=2026-04-17T02:30:00Z / "
                "regime=transition / action=trap_caution / risk=high\n"
                "summary_context: caption=summary:market_summary\n"
                "prediction_context: scenario_switch_hint=watch_reversal_path"
            ),
            tactic_summary_lines=(
                "operating_stance=reversal_prepare",
                "scenario_regime=reversal_watch",
                "proposal_state=proposed",
                "adoption_ready=true",
                "rollback_target_ref=baseline-default",
                "comparison_relation=candidate_vs_baseline",
                "overlay_influence=overlay_bias",
            ),
            tactic_interpretation_lines=(
                "comparison_hint: current set is being read as a candidate relative to baseline.",
                "overlay_hint: overlay influence is present, so treat the stance as context-shaped rather than baseline-only.",
                "rollback_hint: a rollback target is available for review context.",
                "adoption_hint: the current set is marked as adoption-ready for review, not as an automatic decision.",
            ),
            primary_tactic_interpretation_line=(
                "overlay_hint: overlay influence is present, so treat the stance as context-shaped rather than baseline-only."
            ),
            tactic_primary_summary_line=(
                "reversal_prepare | "
                "candidate_vs_baseline | "
                "overlay influence is present, so the stance should be read as context-shaped | "
                "review_only"
            ),
        )

        assert built["answer"] == "mock-answer"
        assert built["runtime_source"] == "mock-runtime"
        assert built["advisory_note_used"] == (
            "Use the following explanation context when generating the advisory answer.\n"
            "Treat it as supporting context, not as a final decision contract.\n"
            "Treat any tactic stance context as an operating stance proposal, not as an execution instruction.\n"
            "Use the following tactic stance summary lines as ordered supporting context.\n"
            "tactic_stance_summary_lines: "
            "operating_stance=reversal_prepare | "
            "scenario_regime=reversal_watch | "
            "proposal_state=proposed | "
            "adoption_ready=true | "
            "rollback_target_ref=baseline-default | "
            "comparison_relation=candidate_vs_baseline | "
            "overlay_influence=overlay_bias\n"
            "primary_tactic_stance_summary: "
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "overlay influence is present, so the stance should be read as context-shaped | "
            "review_only\n"
            "Treat the following tactic stance interpretation as review guidance, not as a final decision.\n"
            "primary_tactic_stance_interpretation: overlay_hint: overlay influence is present, so treat the stance as context-shaped rather than baseline-only.\n"
            "tactic_stance_interpretation: "
            "comparison_hint: current set is being read as a candidate relative to baseline. | "
            "overlay_hint: overlay influence is present, so treat the stance as context-shaped rather than baseline-only. | "
            "rollback_hint: a rollback target is available for review context. | "
            "adoption_hint: the current set is marked as adoption-ready for review, not as an automatic decision.\n"
            "watch_context: caption=watch ts=2026-04-17T02:30:00Z / "
            "regime=transition / action=trap_caution / risk=high\n"
            "summary_context: caption=summary:market_summary\n"
            "prediction_context: scenario_switch_hint=watch_reversal_path"
        )

        assert len(calls) == 1
        assert calls[0]["mode"] == "local"
        assert calls[0]["lang"] == "en"
        assert calls[0]["prompt"] == "Explain current market state"
        assert calls[0]["intent"] == "decide"
        assert calls[0]["style"] == "normal"
        assert calls[0]["note"] == built["advisory_note_used"]

        explicit = advisory.read_operator_advisory_answer(
            lang="en",
            ai_mode="local",
            operator_prompt="Explain current market state",
            intent="decide",
            style="normal",
            state={
                "spread": 1200.0,
                "imbalance": 0.22,
                "delta": 0.31,
                "wall_ratio": 0.18,
            },
            memory=[],
            note="summary_context: caption=summary:market_summary",
            tactic_summary_lines=(
                "operating_stance=reversal_prepare",
                "scenario_regime=reversal_watch",
                "proposal_state=proposed",
                "adoption_ready=true",
                "rollback_target_ref=baseline-default",
                "comparison_relation=candidate_vs_baseline",
                "overlay_influence=overlay_bias",
            ),
            tactic_interpretation_lines=(
                "explicit_hint: prefer explicit interpretation payload.",
            ),
            primary_tactic_interpretation_line=(
                "explicit_hint: prefer explicit interpretation payload."
            ),
            tactic_primary_summary_line=(
                "reversal_prepare | "
                "candidate_vs_baseline | "
                "explicit_hint: prefer explicit interpretation payload. | "
                "review_only"
            ),
        )

        assert explicit["advisory_note_used"] == (
            "Use the following explanation context when generating the advisory answer.\n"
            "Treat it as supporting context, not as a final decision contract.\n"
            "Treat any tactic stance context as an operating stance proposal, not as an execution instruction.\n"
            "Use the following tactic stance summary lines as ordered supporting context.\n"
            "tactic_stance_summary_lines: "
            "operating_stance=reversal_prepare | "
            "scenario_regime=reversal_watch | "
            "proposal_state=proposed | "
            "adoption_ready=true | "
            "rollback_target_ref=baseline-default | "
            "comparison_relation=candidate_vs_baseline | "
            "overlay_influence=overlay_bias\n"
            "primary_tactic_stance_summary: "
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "explicit_hint: prefer explicit interpretation payload. | "
            "review_only\n"
            "Treat the following tactic stance interpretation as review guidance, not as a final decision.\n"
            "primary_tactic_stance_interpretation: explicit_hint: prefer explicit interpretation payload.\n"
            "tactic_stance_interpretation: "
            "explicit_hint: prefer explicit interpretation payload.\n"
            "summary_context: caption=summary:market_summary"
        )
        assert len(calls) == 2
        assert calls[1]["note"] == explicit["advisory_note_used"]

        empty = advisory.read_operator_advisory_answer(
            lang="en",
            ai_mode="local",
            operator_prompt="Explain current market state",
            intent="decide",
            style="normal",
            state={
                "spread": 1200.0,
                "imbalance": 0.22,
                "delta": 0.31,
                "wall_ratio": 0.18,
            },
            memory=[],
            note="",
            tactic_summary_lines=(),
            tactic_interpretation_lines=(),
            primary_tactic_interpretation_line="",
            tactic_primary_summary_line="",
        )

        assert empty["answer"] == "mock-answer"
        assert empty["runtime_source"] == "mock-runtime"
        assert empty["advisory_note_used"] == ""
        assert len(calls) == 3
        assert calls[2]["note"] == ""
    finally:
        advisory.generate_answer = original_generate_answer

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())