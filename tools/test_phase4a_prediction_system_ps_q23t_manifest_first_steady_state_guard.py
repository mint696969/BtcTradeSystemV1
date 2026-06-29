# path: ./tools/test_phase4a_prediction_system_ps_q23t_manifest_first_steady_state_guard.py
# desc: Focused pytest guard for PS-Q23T manifest-first WarRoom steady state.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23t_manifest_first_steady_state_guard import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    EXPECTED_FULL_RECORD_COUNT,
    EXPECTED_LEGACY_COMPACT_RECORD_COUNT,
    LATEST_MANIFEST_RELATIVE_PATH,
    run_manifest_first_steady_state_guard,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23T_MANIFEST_FIRST_STEADY_STATE_GUARD_HARDENING_2026-06-29.md"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23t_manifest_first_steady_state_guard.py"


def test_spec_declares_q23t_manifest_first_steady_state_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23t_manifest_first_steady_state_guard_hardening=true",
        "base_reentry=PS_Q23R_CLOSEOUT_STEADY_STATE_GUARD_SYNCED",
        "q23r_closeout_guard_ready=true",
        "q23e_manifest_first_live_diagnostic_distributed=true",
        "q23j_display_default_manifest_first=true",
        "latest_manifest_full_sidecars_retained=true",
        "legacy_fallback_ready=true",
        "legacy_latest_compact_record_count=24",
        "manifest_record_count=110",
        "forecast_records_line_count=110",
        "panel_prediction_rows_visible=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_live_manifest_first_steady_state_ready() -> None:
    result = run_manifest_first_steady_state_guard()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    q23r = result["q23r_closeout"]
    assert q23r["ready"] is True
    artifact = q23r["artifact_summary"]
    assert artifact["legacy_compact_record_count"] == EXPECTED_LEGACY_COMPACT_RECORD_COUNT
    assert artifact["legacy_original_record_count"] == EXPECTED_FULL_RECORD_COUNT
    assert artifact["manifest_record_count"] == EXPECTED_FULL_RECORD_COUNT
    assert artifact["forecast_records_line_count"] == EXPECTED_FULL_RECORD_COUNT
    q23e = result["q23e_manifest_first_live"]
    assert q23e["ok"] is True
    assert q23e["source_artifact_mode"] == "distributed"
    assert q23e["selected_record_count"] == EXPECTED_FULL_RECORD_COUNT
    assert q23e["distributed_reader_ready"] is True
    assert q23e["distributed_stale_vs_legacy"] is False
    assert q23e["legacy_fallback_ready"] is True
    assert q23e["payload_status_source_artifact_relative_path"] == LATEST_MANIFEST_RELATIVE_PATH
    assert q23e["read_model_source_artifact_relative_path"] == LATEST_MANIFEST_RELATIVE_PATH
    panel = result["display_panel_default"]
    assert panel["ok"] is True
    assert panel["source_artifact_mode"] == "distributed"
    assert panel["source_artifact_relative_path"] == LATEST_MANIFEST_RELATIVE_PATH
    assert panel["distributed_reader_ready"] is True
    assert panel["distributed_stale_vs_legacy"] is False
    assert panel["legacy_fallback_ready"] is True
    assert panel["prediction_row_count"] > 0
    assert panel["runtime_artifact_write_allowed"] is False
    assert panel["status_artifact_write_allowed"] is False
    assert panel["prediction_artifact_write_allowed"] is False
    assert panel["view_artifact_write_allowed"] is False
    assert panel["autotrade_trigger_allowed"] is False
    assert panel["broker_private_api_allowed"] is False
    assert panel["would_send_to_broker"] is False
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
    assert safety["latest_prediction_artifact_written"] is False
    assert safety["status_artifact_written"] is False
    assert safety["latest_manifest_written"] is False
    assert safety["run_sidecars_written"] is False
    assert safety["runtime_artifact_write_enabled"] is False
    assert safety["scheduler_action_changed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["would_send_to_broker"] is False


def test_diagnostic_is_no_write_no_scheduler_no_broker() -> None:
    text = DIAG.read_text(encoding="utf-8")
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
    test_spec_declares_q23t_manifest_first_steady_state_contract()
    test_live_manifest_first_steady_state_ready()
    test_diagnostic_is_no_write_no_scheduler_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
