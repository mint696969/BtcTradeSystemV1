# path: ./tools/test_phase4a_prediction_system_ps_q26k_allowed_tech_term_label_help_text.py
# desc: Focused pytest guard for PS-Q26K allowed technical term label/help text.

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

from tools.diagnose_phase4a_prediction_system_ps_q26k_allowed_tech_term_label_help_text import run_allowed_tech_term_label_help_text_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26K_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_2026-07-01.md"


def test_q26k_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26k_allowed_tech_term_label_help_text=true", "allowed_technical_terms_preserved=true", "japanese_helper_wording_added=true", "legacy_searchable_compatibility_preserved=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26k_diagnostic_ready_and_safe() -> None:
    result = run_allowed_tech_term_label_help_text_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["term_count"] == 7
    assert result["q26i_legacy_compat_count"] == 4
    assert result["legacy_searchable_compatibility_preserved"] is True
    joined = json.dumps(result, ensure_ascii=False)
    assert "画面更新確認時刻" in joined
    assert "安全側の表示理由" in joined
    assert "実データprops接続" in joined
    assert "枠内だけの表示更新" in joined
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26k_doc_markers()
    test_q26k_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
