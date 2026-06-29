# path: ./tools/test_phase4a_prediction_system_ps_q24a_autotrade_read_only_prediction_consumption_planning.py
# desc: Focused pytest guard for PS-Q24A AutoTrade read-only prediction consumption planning.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q24a_autotrade_read_only_prediction_consumption_planning import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    EXPECTED_COMPACT_RECORD_COUNT,
    EXPECTED_FULL_RECORD_COUNT,
    run_autotrade_read_only_prediction_consumption_planning,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q24A_AUTOTRADE_READ_ONLY_PREDICTION_CONSUMPTION_PLANNING_2026-06-29.md"
DIAG = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q24a_autotrade_read_only_prediction_consumption_planning.py"


def test_spec_declares_q24a_read_only_consumption_planning_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q24a_autotrade_read_only_prediction_consumption_planning=true",
        "base_reentry=PS_Q23T_MANIFEST_FIRST_STEADY_STATE_GUARD_HARDENED",
        "q23t_manifest_first_guard_ready=true",
        "autotrade_prediction_preview_status_contract_present=true",
        "autotrade_shadow_prediction_context_contract_present=true",
        "autotrade_prediction_preview_artifact_preflight_contract_present=true",
        "autotrade_consumption_chain_in_memory_only=true",
        "legacy_latest_compact_record_count=24",
        "manifest_record_count=110",
        "forecast_records_line_count=110",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
        "ledger_append=false",
        "mode_apply=false",
        "parameter_apply=false",
    ):
        assert marker in text, marker


def test_live_q24a_read_only_consumption_planning_ready() -> None:
    result = run_autotrade_read_only_prediction_consumption_planning()
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    q23t = result["q23t_manifest_first"]
    artifact = q23t["artifact_summary"]
    assert q23t["ready"] is True
    assert q23t["source_artifact_mode"] == "distributed"
    assert q23t["selected_record_count"] == EXPECTED_FULL_RECORD_COUNT
    assert q23t["legacy_fallback_ready"] is True
    assert q23t["display_panel_source_artifact_mode"] == "distributed"
    assert int(q23t["display_panel_prediction_row_count"]) > 0
    assert artifact["legacy_compact_record_count"] == EXPECTED_COMPACT_RECORD_COUNT
    assert artifact["manifest_record_count"] == EXPECTED_FULL_RECORD_COUNT
    assert artifact["forecast_records_line_count"] == EXPECTED_FULL_RECORD_COUNT
    chain = result["autotrade_read_only_chain"]
    assert chain["status_state"] == "ok"
    assert chain["status_usable"] is True
    assert chain["context_state"] == "ok"
    assert chain["context_usable"] is True
    assert chain["preflight_state"] == "ready"
    assert chain["preflight_ready_for_future_write"] is True
    assert chain["display_state"] == "ok"
    assert chain["display_status_available"] is True
    assert chain["in_memory_only"] is True
    assert chain["not_runtime_wiring"] is True
    safety = result["safety"]
    assert safety["read_only_diagnostic"] is True
    assert safety["runtime_artifact_write_enabled"] is False
    assert safety["scheduler_action_changed"] is False
    assert safety["shadow_decision_append_allowed"] is False
    assert safety["mode_apply_allowed"] is False
    assert safety["prearmed_grant_execution_allowed"] is False
    assert safety["command_or_approval_ledger_allowed"] is False
    assert safety["parameter_apply_allowed"] is False
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
        "create_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
        "shutil.copy2",
        "Copy-Item",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_q24a_read_only_consumption_planning_contract()
    test_live_q24a_read_only_consumption_planning_ready()
    test_diagnostic_is_no_write_no_scheduler_no_broker()
    print(json.dumps({"ok": True}, ensure_ascii=False))
