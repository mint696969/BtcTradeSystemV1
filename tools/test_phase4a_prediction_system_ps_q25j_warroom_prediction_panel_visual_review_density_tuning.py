# path: ./tools/test_phase4a_prediction_system_ps_q25j_warroom_prediction_panel_visual_review_density_tuning.py
# desc: Focused pytest guard for PS-Q25J WarRoom prediction panel visual review and density tuning.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q25j_warroom_prediction_panel_visual_review_density_tuning import run_warroom_prediction_panel_visual_review_density_tuning_diagnostic  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25J_WARROOM_PREDICTION_PANEL_VISUAL_REVIEW_DENSITY_TUNING_2026-06-30.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"


def test_q25j_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in ("ps_q25j_warroom_prediction_panel_visual_review_density_tuning=true", "prediction_density_tuning_added=true", "detail_checks_folded_default=true", "detail_checks_still_available=true", "layout_only_change=true", "producer_cadence_changed=false", "scheduler_action_changed=false", "autotrade_trigger_allowed=false", "broker_private_api_allowed=false"):
        assert marker in text, marker


def test_q25j_diagnostic_ready() -> None:
    result = run_warroom_prediction_panel_visual_review_density_tuning_diagnostic()
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    density = result["density_tuning"]
    assert density["density_tuning_version"] == "prediction_warroom.prediction_panel_visual_review_density_tuning.ps_q25j.v1"
    assert density["compact_header_kept_top"] is True
    assert density["detail_checks_folded_default"] is True
    assert density["detail_checks_still_available"] is True
    assert density["detail_sections_folded_count"] == 5
    assert density["layout_only_change"] is True
    safety = result["safety"]
    assert safety["warroom_display_only"] is True
    assert safety["producer_cadence_changed"] is False
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


def test_q25j_panel_safe_and_markers() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for marker in ("WARROOM_PREDICTION_DENSITY_TUNING_VERSION", "latest_prediction_warroom_density_tuning_packet", "_render_prediction_detail_checks_foldout", "density_tuning_rendered", "detail_checks_folded_default=True"):
        assert marker in text, marker
    for forbidden in ("Set-ScheduledTask", "Enable-ScheduledTask", "Disable-ScheduledTask", "Register-ScheduledTask", "New-ScheduledTaskTrigger", "append_decision_jsonl", "run_shadow_decision_from_snapshot", "submit_mode_change_command_request", "validate_and_append_command", "send_order(", "place_order(", "create_order(", ".write_text(", ".write_bytes(", "os.replace", "shutil.copy2"):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_q25j_doc_markers()
    test_q25j_diagnostic_ready()
    test_q25j_panel_safe_and_markers()
    print(json.dumps({"ok": True}, ensure_ascii=False))
