# path: ./tools/test_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness.py
# desc: Focused guard for PS-Q23N final no-write readiness before live legacy latest shrink.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_final_live_legacy_latest_shrink_readiness,
)
from tools.run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once import REQUIRED_CONFIRMATION  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23N_FINAL_LIVE_LEGACY_LATEST_SHRINK_READINESS_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness.py"


def test_spec_declares_final_readiness_no_write_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23n_final_live_legacy_latest_shrink_readiness=true",
        "actual_legacy_latest_shrink_executed=false",
        "actual_legacy_latest_shrink_requires_confirmation=SHRINK_D_HOT_LEGACY_LATEST_TO_COMPACT_READ_MODEL_COMPAT_ONCE",
        "actual_shrink_command_candidate_ready=true",
        "rollback_command_candidate_ready=true",
        "backup_before_replace_required=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_live_final_readiness_is_no_write_and_candidate_is_valid() -> None:
    result = run_final_live_legacy_latest_shrink_readiness()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["required_confirmation"] == REQUIRED_CONFIRMATION
    assert result["q23m_default_probe"]["success"] is False
    assert result["q23m_default_probe"]["legacy_latest_shrink_executed"] is False
    for reason in (
        "exact_legacy_latest_shrink_confirmation_required",
        "execute_legacy_latest_shrink_once_flag_required",
        "operator_acknowledgement_required",
    ):
        assert reason in result["q23m_default_probe"]["blocked_reasons"]
    assert result["candidate"]["source_artifact_mode"] == "distributed"
    assert result["candidate"]["source_artifact_relative_path"] == "prediction/latest_manifest.json"
    assert result["candidate"]["distributed_reader_ready"] is True
    assert result["candidate"]["distributed_stale_vs_legacy"] is False
    assert result["candidate"]["candidate_read_model_ok"] is True
    assert result["candidate"]["compact_record_count"] > 0
    assert result["candidate"]["original_record_count"] > result["candidate"]["compact_record_count"]
    assert result["candidate"]["estimated_before_size_bytes"] > result["candidate"]["estimated_after_size_bytes"] > 0
    assert result["backup_candidate_ready"] is True
    assert "--execute-legacy-latest-shrink-once" in result["actual_shrink_command_candidate"]
    assert REQUIRED_CONFIRMATION in result["actual_shrink_command_candidate"]
    assert "Copy-Item" in result["rollback_command_template"]
    assert result["actual_legacy_latest_shrink_executed"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["backup_written"] is False
    assert result["scheduler_action_changed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_tool_has_no_writer_scheduler_or_broker_code() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
        "shutil.copy2",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_final_readiness_no_write_contract()
    test_live_final_readiness_is_no_write_and_candidate_is_valid()
    test_tool_has_no_writer_scheduler_or_broker_code()
    print(json.dumps({"ok": True}))
