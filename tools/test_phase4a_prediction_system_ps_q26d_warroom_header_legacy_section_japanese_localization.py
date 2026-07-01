# path: ./tools/test_phase4a_prediction_system_ps_q26d_warroom_header_legacy_section_japanese_localization.py
# desc: Focused pytest guard for PS-Q26D WarRoom header and legacy section Japanese localization.

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

from tools.diagnose_phase4a_prediction_system_ps_q26d_warroom_header_legacy_section_japanese_localization import run_warroom_header_legacy_section_japanese_localization_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26D_WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_2026-07-01.md"


def test_q26d_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26d_warroom_header_legacy_section_japanese_localization=true", "quick_status_japanese_localized=true", "legacy_section_titles_japanese_localized=true", "section_description_japanese_localized=true", "warroom_header_source_label_japanese_localized=true", "prediction_footer_token_japanese_localized=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26d_diagnostic_ready_and_safe() -> None:
    result = run_warroom_header_legacy_section_japanese_localization_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    joined = json.dumps(result, ensure_ascii=False)
    assert "PS-Q18AU 予測最新 quick status" in joined
    assert "blocked_not_ready_to_enable" not in result["quick_status_plain_text"]
    assert result["footer_token_ja"] == "PS-Q19I 予測表示の日本語説明"
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26d_doc_markers()
    test_q26d_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
