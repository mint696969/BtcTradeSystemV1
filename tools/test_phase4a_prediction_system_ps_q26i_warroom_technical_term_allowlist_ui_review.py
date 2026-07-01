# path: ./tools/test_phase4a_prediction_system_ps_q26i_warroom_technical_term_allowlist_ui_review.py
# desc: Focused pytest guard for PS-Q26I WarRoom technical term allowlist and UI review audit.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q26i_warroom_technical_term_allowlist_ui_review import run_warroom_technical_term_allowlist_ui_review_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26I_WARROOM_TECHNICAL_TERM_ALLOWLIST_UI_REVIEW_2026-07-01.md"


def test_q26i_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26i_warroom_technical_term_allowlist_ui_review=true", "audit_only=true", "technical_term_allowlist_recorded=true", "ui_review_classification_recorded=true", "production_ui_code_changed=false", "legacy_searchable_compatibility_preserved=true", "allowlist_hit_count_recorded=true", "review_candidate_count_recorded=true", "legacy_compat_count_recorded=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26i_diagnostic_ready_counts_and_safe() -> None:
    result = run_warroom_technical_term_allowlist_ui_review_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["audit_only"] is True
    assert result["production_ui_code_changed"] is False
    assert result["legacy_searchable_compatibility_preserved"] is True
    assert result["allowlist_hit_count"] > 0
    assert result["legacy_compat_count"] > 0
    assert result["review_candidate_count"] > 0
    joined = json.dumps(result, ensure_ascii=False)
    assert "heartbeat" in joined
    assert "fallback" in joined
    assert "PS_Q26J_WARROOM_UI_REVIEW_REMAINING_REVIEW_CANDIDATE_POLISH_DISPLAY_ONLY" in joined
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["audit_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26i_doc_markers()
    test_q26i_diagnostic_ready_counts_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
