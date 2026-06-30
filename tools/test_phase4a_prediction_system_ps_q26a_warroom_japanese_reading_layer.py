# path: ./tools/test_phase4a_prediction_system_ps_q26a_warroom_japanese_reading_layer.py
# desc: Focused pytest guard for PS-Q26A WarRoom Japanese reading layer.

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

from tools.diagnose_phase4a_prediction_system_ps_q26a_warroom_japanese_reading_layer import run_warroom_japanese_reading_layer_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26A_WARROOM_JAPANESE_READING_LAYER_2026-06-30.md"


def test_q26a_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q26a_warroom_japanese_reading_layer=true", "nowcast_japanese_reading_layer_added=true", "prediction_japanese_reading_layer_added=true", "operator_visible_japanese_rows=true", "trade_guidance_added=false", "broker_private_api_allowed=false", "would_send_to_broker=false"):
        assert marker in text, marker


def test_q26a_diagnostic_ready_and_safe() -> None:
    result = run_warroom_japanese_reading_layer_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    assert safety["trade_guidance_added"] is False
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False
    assert result["nowcast_layer"]["row_count"] >= 5
    assert result["prediction_layer"]["row_count"] >= 5


if __name__ == "__main__":
    test_q26a_doc_markers()
    test_q26a_diagnostic_ready_and_safe()
    print(json.dumps({"ok": True}, ensure_ascii=False))
