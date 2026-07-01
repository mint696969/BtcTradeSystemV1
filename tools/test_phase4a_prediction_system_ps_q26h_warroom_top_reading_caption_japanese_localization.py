# path: ./tools/test_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization.py
# desc: Focused pytest guard for PS-Q26H WarRoom top reading caption and page-level token Japanese localization.

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

from tools.diagnose_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization import run_warroom_top_reading_caption_japanese_localization_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26H_WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_2026-07-01.md"


def test_q26h_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26h_warroom_top_reading_caption_japanese_localization=true", "reading_block_captions_japanese_localized=true", "quick_status_plain_text_japanese_localized=true", "quick_status_rows_japanese_localized=true", "page_level_false_fragments_reduced=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26h_diagnostic_ready_and_safe() -> None:
    result = run_warroom_top_reading_caption_japanese_localization_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    joined = json.dumps(result, ensure_ascii=False)
    assert "現在の市場summary" in joined
    assert "安全fallback理由" in joined
    assert "実render=なし" in joined
    assert "real_render=false" not in result["sample_plain_text"]
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26h_doc_markers()
    test_q26h_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
