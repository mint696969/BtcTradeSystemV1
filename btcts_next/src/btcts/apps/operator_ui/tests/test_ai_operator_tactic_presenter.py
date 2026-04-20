# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_tactic_presenter.py
# desc: Verify operator tactic presentation wording stays stable and execution-safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (  # noqa: E402
    advisory_support_caption,
    build_tactic_stance_display_lines,
    build_tactic_stance_lines,
    build_tactic_stance_note,
    prediction_snapshot_section_title,
    tactic_stance_section_title,
    tactic_stance_support_caption,
)


def main() -> int:
    assert tactic_stance_section_title("en") == "Tactic stance proposal"
    assert tactic_stance_section_title("ja") == "戦術スタンス提案"
    assert tactic_stance_support_caption("en") == (
        "Supporting operating-stance context only. Not an execution instruction."
    )
    assert tactic_stance_support_caption("ja") == (
        "これは執行指示ではなく、運用上の構えを補助的に示す文脈です。"
    )
    assert advisory_support_caption("en") == (
        "advisory support context prepared (supporting context only, not final decision)"
    )
    assert advisory_support_caption("ja") == (
        "advisory 補助文脈を準備しました（最終判断ではありません）"
    )
    assert prediction_snapshot_section_title("en") == "Prediction snapshot"
    assert prediction_snapshot_section_title("ja") == "予測スナップショット"

    tactic_context = {
        "primary_tactic_key": "reversal_prepare",
        "proposal_state": "proposed",
        "scenario_regime": "reversal_watch",
        "profile_kind": "candidate",
        "rollback_ready": True,
        "review_needed": True,
        "selection_bias_tags": ("overlay:prefer_reversal_prepare",),
    }
    assert build_tactic_stance_lines(tactic_context) == (
        "operating_stance=reversal_prepare",
        "scenario_regime=reversal_watch",
        "proposal_state=proposed",
        "profile_kind=candidate",
        "review_needed=true",
        "rollback_ready=true",
        "selection_bias_tags=overlay:prefer_reversal_prepare",
    )
    assert build_tactic_stance_display_lines(
        build_tactic_stance_lines(tactic_context),
        "en",
    ) == (
        "Operating Stance: reversal_prepare",
        "Scenario Regime: reversal_watch",
        "Proposal State: proposed",
        "Profile Kind: candidate",
        "Review Needed: Yes",
        "Rollback Ready: Yes",
        "Selection Bias Tags: overlay:prefer_reversal_prepare",
    )
    assert build_tactic_stance_display_lines(
        build_tactic_stance_lines(tactic_context),
        "ja",
    ) == (
        "運用スタンス: reversal_prepare",
        "シナリオ地合い: reversal_watch",
        "提案状態: proposed",
        "プロファイル種別: candidate",
        "レビュー要否: はい",
        "ロールバック準備: はい",
        "選択バイアスタグ: overlay:prefer_reversal_prepare",
    )
    assert build_tactic_stance_note(tactic_context) == (
        "tactic_stance_context: "
        "operating_stance=reversal_prepare | "
        "scenario_regime=reversal_watch | "
        "proposal_state=proposed | "
        "profile_kind=candidate | "
        "review_needed=true | "
        "rollback_ready=true | "
        "selection_bias_tags=overlay:prefer_reversal_prepare"
    )
    assert build_tactic_stance_lines(None) == ()
    assert build_tactic_stance_note(None) == ""

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())