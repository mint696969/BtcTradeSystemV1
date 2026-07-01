# path: ./tools/test_phase4a_prediction_system_ps_q26l_warroom_japanese_display_final_audit_stop_point.py
# desc: Focused pytest guard for PS-Q26L WarRoom Japanese display final audit and stop point.

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

from tools.diagnose_phase4a_prediction_system_ps_q26l_warroom_japanese_display_final_audit_stop_point import run_warroom_japanese_display_final_audit_stop_point_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26L_WARROOM_JAPANESE_DISPLAY_FINAL_AUDIT_AND_STOP_POINT_2026-07-01.md"


def test_q26l_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q26l_warroom_japanese_display_final_audit_and_stop_point=true",
        "final_audit_only=true",
        "production_ui_code_changed=false",
        "stop_point_reached=true",
        "human_next_lane_choice_required=true",
        "automatic_next_implementation_disallowed=true",
        "recommended_next_slice=HUMAN_CHOICE_REQUIRED",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_q26l_final_audit_ready_and_stop_point() -> None:
    result = run_warroom_japanese_display_final_audit_stop_point_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["stop_point_reached"] is True
    assert result["human_next_lane_choice_required"] is True
    assert result["recommended_next_slice"] == "HUMAN_CHOICE_REQUIRED"
    final = result["final_packet"]
    assert final["final_audit_only"] is True
    assert final["production_ui_code_changed"] is False
    assert final["q26i_audit_ready"] is True
    assert final["q26j_polish_ready"] is True
    assert final["q26k_help_text_ready"] is True
    assert final["warroom_japanese_display_cycle_complete"] is True
    assert final["stop_point_reached"] is True
    assert final["human_next_lane_choice_required"] is True
    assert final["automatic_next_implementation_disallowed"] is True
    assert final["q26i_legacy_compat_count"] == 4
    assert final["q26j_legacy_compat_count"] == 4
    assert final["q26k_legacy_compat_count"] == 4
    assert final["q26j_post_review_candidate_count"] < final["q26j_baseline_review_candidate_count"]
    assert final["q26k_term_count"] == 7
    assert len(final["next_lane_choices"]) >= 5
    joined = json.dumps(result, ensure_ascii=False)
    assert "UI actual screenshot review" in joined
    assert "WarRoom data freshness" in joined
    assert "Prediction producer 60s disabled dry-run gate planning" in joined
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26l_doc_markers()
    test_q26l_final_audit_ready_and_stop_point()
    print(json.dumps({"ok": True}, ensure_ascii=False))
