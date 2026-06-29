# path: ./tools/test_phase4a_prediction_system_ps_q23r_scheduled_compact_legacy_tick_observation.py
# desc: Focused guard for PS-Q23R scheduled compact legacy tick observation.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23r_scheduled_compact_legacy_tick_observation import (  # noqa: E402
    COMPACT_LEGACY_MAX_BYTES,
    DIAGNOSTIC_VERSION,
    EXPECTED_FULL_RECORD_COUNT_MIN,
    run_scheduled_compact_legacy_tick_observation,
)
from tools.run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once import RUNNER_VERSION as Q23M_RUNNER_VERSION  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23R_SCHEDULED_COMPACT_LEGACY_TICK_OBSERVATION_2026-06-29.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23r_scheduled_compact_legacy_tick_observation.py"
DIRTY_ONLY_BLOCKERS = {
    "repo_clean_required_for_q23r_closeout",
    "q23k_no_write_readiness_blockers_unexpected",
}


def test_spec_declares_q23r_observation_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23r_scheduled_compact_legacy_tick_observation=true",
        "scheduled_tick_after_q23q_observed=true",
        "legacy_latest_compact_after_scheduled_tick=true",
        "legacy_latest_compact_record_count=24",
        "sidecar_forecast_records_full_count=110",
        "latest_manifest_full_sidecars_retained=true",
        "manifest_legacy_size_metadata_pre_compaction_expected=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_live_observation_ready_or_only_dirty_blocked_and_no_write() -> None:
    result = run_scheduled_compact_legacy_tick_observation()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    if result["repo_status_short"]:
        assert set(result["blockers"]).issubset(DIRTY_ONLY_BLOCKERS), result["blockers"]
    else:
        assert result["scheduled_compact_legacy_tick_observation_ready"] is True
        assert result["blockers"] == []
    legacy = result["legacy_latest"]
    manifest = result["latest_manifest"]
    sidecar = result["forecast_records_sidecar"]
    assert legacy["shrunk_by"] == Q23M_RUNNER_VERSION
    assert legacy["source_manifest_relative_path"] == "prediction/latest_manifest.json"
    assert 0 < legacy["meta"]["size_bytes"] <= COMPACT_LEGACY_MAX_BYTES
    assert legacy["compact_legacy_max_bytes"] == COMPACT_LEGACY_MAX_BYTES
    assert legacy["compact_record_count"] > 0
    assert legacy["original_record_count"] > legacy["compact_record_count"]
    assert legacy["forecast_batch_record_count"] == legacy["record_count_loaded"] == legacy["compact_record_count"]
    assert legacy["read_model_ok"] is True
    assert manifest["record_count"] == legacy["original_record_count"]
    assert manifest["record_count"] >= EXPECTED_FULL_RECORD_COUNT_MIN
    assert manifest["run_dir_exists"] is True
    assert sidecar["meta"]["exists"] is True
    assert sidecar["line_count"] == manifest["record_count"]
    assert sidecar["meta"]["size_bytes"] > legacy["meta"]["size_bytes"]
    assert result["q23e"]["source_artifact_mode"] == "distributed"
    assert result["q23e"]["payload_status_source_artifact_relative_path"] == "prediction/latest_manifest.json"
    assert result["q23e"]["read_model_source_artifact_relative_path"] == "prediction/latest_manifest.json"
    assert result["q23e"]["distributed_reader_ready"] is True
    assert result["q23e"]["distributed_stale_vs_legacy"] is False
    assert result["q23e"]["legacy_fallback_ready"] is True
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["runtime_artifact_write_enabled"] is False
    assert result["scheduler_action_changed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_diagnostic_has_no_write_scheduler_or_broker_code() -> None:
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
        "Copy-Item",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_q23r_observation_contract()
    test_live_observation_ready_or_only_dirty_blocked_and_no_write()
    test_diagnostic_has_no_write_scheduler_or_broker_code()
    print(json.dumps({"ok": True}))
