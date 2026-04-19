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
        )

        assert built["answer"] == "mock-answer"
        assert built["runtime_source"] == "mock-runtime"
        assert built["advisory_note_used"] == (
            "Use the following explanation context when generating the advisory answer.\n"
            "Treat it as supporting context, not as a final decision contract.\n"
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
        )

        assert empty["answer"] == "mock-answer"
        assert empty["runtime_source"] == "mock-runtime"
        assert empty["advisory_note_used"] == ""
        assert len(calls) == 2
        assert calls[1]["note"] == ""
    finally:
        advisory.generate_answer = original_generate_answer

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())