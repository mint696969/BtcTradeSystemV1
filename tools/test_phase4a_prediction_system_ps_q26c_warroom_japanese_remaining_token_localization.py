# path: ./tools/test_phase4a_prediction_system_ps_q26c_warroom_japanese_remaining_token_localization.py
# desc: Focused pytest guard for PS-Q26C WarRoom Japanese remaining token localization.

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

from tools.diagnose_phase4a_prediction_system_ps_q26c_warroom_japanese_remaining_token_localization import run_warroom_japanese_remaining_token_localization_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26C_WARROOM_JAPANESE_REMAINING_TOKEN_LOCALIZATION_2026-07-01.md"


def test_q26c_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26c_warroom_japanese_remaining_token_localization=true", "nowcast_remaining_token_localization_added=true", "prediction_remaining_token_localization_added=true", "remaining_prediction_rows_readable_as_current_artifact_localized=true", "english_table_header_reduction=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26c_diagnostic_ready_and_safe() -> None:
    result = run_warroom_japanese_remaining_token_localization_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    joined = json.dumps(result, ensure_ascii=False)
    assert "prediction_rows_readable_as_current_artifact" not in json.dumps(result["prediction_localized_rows"], ensure_ascii=False)
    assert "予測表示: 現在artifactとして読める" in joined
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


if __name__ == "__main__":
    test_q26c_doc_markers()
    test_q26c_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
