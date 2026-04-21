# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_watch_store_tactic_summary_lines.py
# desc: Verify watch_store preserves tactic_summary_lines for operator watch persistence.

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.watch_store as watch_store  # noqa: E402


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_watch_store_tactic_summary_lines_test"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    os.environ["BTC_TS_DATA_DIR"] = str(tmp_root / "data")

    first = {
        "ts": "2026-04-20T12:00:00Z",
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
        "primary_tactic_interpretation_line": (
            "overlay influence is present, so the stance should be read as context-shaped"
        ),
        "tactic_primary_summary_line": (
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "overlay influence is present, so the stance should be read as context-shaped | "
            "review_only"
        ),
    }

    second = {
        "ts": "2026-04-20T12:01:00Z",
        "regime": "continuation",
        "action": "long_watch",
        "risk": "low",
        "tactic_summary_lines": (
            "operating_stance=continuation_follow",
            "scenario_regime=continuation",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-continuation-follow",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
        "primary_tactic_interpretation_line": (
            "current set is being compared as a candidate relative to baseline"
        ),
        "tactic_primary_summary_line": (
            "continuation_follow | "
            "candidate_vs_baseline | "
            "current set is being compared as a candidate relative to baseline | "
            "review_only"
        ),
    }

    recent, persisted = watch_store.append_watch(first, max_items_hint=12)
    assert persisted is True
    assert recent[0] == {
        "ts": "2026-04-20T12:00:00Z",
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
        "primary_tactic_interpretation_line": (
            "overlay influence is present, so the stance should be read as context-shaped"
        ),
        "tactic_primary_summary_line": (
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "overlay influence is present, so the stance should be read as context-shaped | "
            "review_only"
        ),
    }

    recent, persisted = watch_store.append_watch(second, max_items_hint=12)
    assert persisted is True
    assert recent[0] == {
        "ts": "2026-04-20T12:01:00Z",
        "regime": "continuation",
        "action": "long_watch",
        "risk": "low",
        "tactic_summary_lines": (
            "operating_stance=continuation_follow",
            "scenario_regime=continuation",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-continuation-follow",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
        "primary_tactic_interpretation_line": (
            "current set is being compared as a candidate relative to baseline"
        ),
        "tactic_primary_summary_line": (
            "continuation_follow | "
            "candidate_vs_baseline | "
            "current set is being compared as a candidate relative to baseline | "
            "review_only"
        ),
    }

    loaded = watch_store.load_recent_watch_list(max_items=12)
    assert loaded == [
        {
            "ts": "2026-04-20T12:01:00Z",
            "regime": "continuation",
            "action": "long_watch",
            "risk": "low",
            "tactic_summary_lines": (
                "operating_stance=continuation_follow",
                "scenario_regime=continuation",
                "proposal_state=proposed",
                "profile_kind=candidate",
                "review_needed=true",
                "rollback_ready=true",
                "adoption_ready=true",
                "rollback_target_available=true",
                "selected_set_id=candidate-continuation-follow",
                "rollback_target_ref=baseline-default",
                "comparison_relation=candidate_vs_baseline",
            ),
            "tactic_interpretation_lines": (
                "current set is being compared as a candidate relative to baseline",
                "rollback review target is available: baseline-default",
                "current set is adoption-ready for review, not an automatic decision",
            ),
            "primary_tactic_interpretation_line": (
                "current set is being compared as a candidate relative to baseline"
            ),
            "tactic_primary_summary_line": (
                "continuation_follow | "
                "candidate_vs_baseline | "
                "current set is being compared as a candidate relative to baseline | "
                "review_only"
            ),
        },
        {
            "ts": "2026-04-20T12:00:00Z",
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
            "primary_tactic_interpretation_line": (
                "overlay influence is present, so the stance should be read as context-shaped"
            ),
            "tactic_primary_summary_line": (
                "reversal_prepare | "
                "candidate_vs_baseline | "
                "overlay influence is present, so the stance should be read as context-shaped | "
                "review_only"
            ),
        },
    ]

    duplicate_recent, duplicate_persisted = watch_store.append_watch(
        second,
        max_items_hint=12,
    )
    assert duplicate_persisted is True
    assert duplicate_recent == loaded

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())