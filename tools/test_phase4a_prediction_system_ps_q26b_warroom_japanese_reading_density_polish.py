# path: ./tools/test_phase4a_prediction_system_ps_q26b_warroom_japanese_reading_density_polish.py
# desc: Focused pytest guard for PS-Q26B WarRoom Japanese reading density polish.

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

from tools.diagnose_phase4a_prediction_system_ps_q26b_warroom_japanese_reading_density_polish import run_warroom_japanese_reading_density_polish_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26B_WARROOM_JAPANESE_READING_DENSITY_POLISH_2026-06-30.md"


def test_q26b_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26b_warroom_japanese_reading_density_polish=true", "nowcast_density_polish_added=true", "prediction_density_polish_added=true", "operator_visible_compact_japanese_rows=true", "trade_guidance_added=false", "trade_signal_added=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26b_diagnostic_ready_and_safe() -> None:
    result = run_warroom_japanese_reading_density_polish_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
    assert result["nowcast_density_polish"]["compact_row_count"] == 5
    assert result["prediction_density_polish"]["compact_row_count"] == 5


if __name__ == "__main__":
    test_q26b_doc_markers()
    test_q26b_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
