# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_actions_watch_tactic_summary_lines.py
# desc: Verify mark_watch_item keeps tactic_summary_lines when lowering into session state.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.ai_operator_actions as actions  # noqa: E402


class _SessionState(dict):
    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value):
        self[name] = value


class _DummyStreamlit:
    def __init__(self) -> None:
        self.session_state = _SessionState()
        self.rerun_called = False

    def rerun(self) -> None:
        self.rerun_called = True


def main() -> int:
    dummy_st = _DummyStreamlit()
    original_st = actions.st
    original_append_watch = actions.append_watch

    watch_item = {
        "ts": "2026-04-20T12:10:00Z",
        "regime": "reversal_watch",
        "action": "trap_caution",
        "risk": "high",
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-reversal-watch",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
            "overlay_influence=overlay_bias",
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "overlay influence is present, so the stance should be read as context-shaped",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
    }

    try:
        actions.st = dummy_st

        def _fake_append_watch(item: dict, *, max_items_hint: int = 12):
            assert item == watch_item
            assert max_items_hint == 12
            return ([item], True)

        actions.append_watch = _fake_append_watch

        actions.mark_watch_item(watch_item)

        assert dummy_st.session_state.ai_operator_watch_list == [watch_item]
        assert dummy_st.session_state.ai_operator_watch_persisted is True
        assert dummy_st.session_state.ai_operator_watch_note == watch_item
        assert dummy_st.session_state.ai_operator_watch_note["tactic_summary_lines"] == (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-reversal-watch",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
            "overlay_influence=overlay_bias",
        )
        assert dummy_st.session_state.ai_operator_watch_note[
            "tactic_interpretation_lines"
        ] == (
            "current set is being compared as a candidate relative to baseline",
            "overlay influence is present, so the stance should be read as context-shaped",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        )
        assert dummy_st.session_state.ui_selected_page_key == "warroom"
        assert dummy_st.rerun_called is True
    finally:
        actions.st = original_st
        actions.append_watch = original_append_watch

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())