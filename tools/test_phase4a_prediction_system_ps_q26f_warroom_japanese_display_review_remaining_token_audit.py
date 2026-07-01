# path: ./tools/test_phase4a_prediction_system_ps_q26f_warroom_japanese_display_review_remaining_token_audit.py
# desc: Focused pytest guard for PS-Q26F WarRoom Japanese display review and remaining token audit.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q26f_warroom_japanese_display_review_remaining_token_audit import run_warroom_japanese_display_review_remaining_token_audit  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26F_WARROOM_JAPANESE_DISPLAY_REVIEW_REMAINING_TOKEN_AUDIT_2026-07-01.md"


def test_q26f_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26f_warroom_japanese_display_review_remaining_token_audit=true", "audit_only=true", "source_rendered_rows_audited=true", "production_ui_code_changed=false", "remaining_token_findings_recorded=true", "next_polish_priorities_recorded=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26f_audit_ready_and_safe() -> None:
    result = run_warroom_japanese_display_review_remaining_token_audit()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["audit_only"] is True
    assert result["production_ui_code_changed"] is False
    assert result["finding_count"] > 0
    assert result["p1_finding_count"] > 0
    assert result["q18aj_finding_count"] > 0
    assert result["q18ak_finding_count"] > 0
    joined = json.dumps(result["next_priorities"], ensure_ascii=False)
    assert "PS_Q26G_Q18AJ_Q18AK_LEGACY_PANEL_JAPANESE_LOCALIZATION_DISPLAY_ONLY" in joined
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["audit_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26f_doc_markers()
    test_q26f_audit_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
