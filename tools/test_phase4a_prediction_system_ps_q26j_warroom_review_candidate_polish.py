# path: ./tools/test_phase4a_prediction_system_ps_q26j_warroom_review_candidate_polish.py
# desc: Focused pytest guard for PS-Q26J WarRoom operator-visible review-candidate polish.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q26j_warroom_review_candidate_polish import run_warroom_review_candidate_polish_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26J_WARROOM_REVIEW_CANDIDATE_POLISH_2026-07-01.md"


def test_q26j_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26j_warroom_review_candidate_polish=true", "operator_visible_review_candidates_polished=true", "q26i_review_candidate_count_after_q26j_less_than_baseline=true", "allowlisted_technical_terms_preserved=true", "legacy_searchable_compatibility_preserved=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26j_diagnostic_ready_counts_and_safe() -> None:
    result = run_warroom_review_candidate_polish_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["post_q26j_review_candidate_count"] < result["baseline_review_candidate_count"]
    assert result["post_q26j_legacy_compat_count"] == 4
    assert result["legacy_searchable_compatibility_preserved"] is True
    joined = json.dumps(result, ensure_ascii=False)
    assert "表示専用の現在状態レイヤー" in joined
    assert "view artifact write=none" in joined
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26j_doc_markers()
    test_q26j_diagnostic_ready_counts_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
