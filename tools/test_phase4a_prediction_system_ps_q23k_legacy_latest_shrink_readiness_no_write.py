# path: ./tools/test_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write.py
# desc: Focused guard for PS-Q23K legacy latest shrink readiness no-write diagnostic.

from __future__ import annotations

import json
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    legacy_reference_inventory,
    run_legacy_latest_shrink_readiness_no_write,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23K_LEGACY_LATEST_SHRINK_READINESS_NO_WRITE_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write.py"


def test_spec_declares_no_write_shrink_readiness_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23k_legacy_latest_shrink_readiness_no_write=true",
        "legacy_latest_shrink_executed=false",
        "legacy_latest_retained=true",
        "manifest_first_display_default_required=true",
        "reference_inventory_required=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_reference_inventory_allows_retired_legacy_widget_refs() -> None:
    inv = legacy_reference_inventory()
    assert inv["legacy_reference_count"] > 0
    assert inv["blocking_legacy_reference_count"] == 0
    assert "legacy_widget_or_mapping_reader" not in inv["blocking_legacy_reference_classes"]


def test_live_no_write_diagnostic_is_ready_or_only_dirty_blocked_after_retirement() -> None:
    result = run_legacy_latest_shrink_readiness_no_write()
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["ok"] is True
    assert result["legacy_reference_inventory"]["blocking_legacy_reference_count"] == 0
    assert "blocking_legacy_latest_references_remain" not in result["blockers"]
    assert result["q23j_display_default"]["source_artifact_mode"] == "distributed"
    assert result["q23j_display_default"]["source_artifact_relative_path"] == "prediction/latest_manifest.json"
    assert result["q23j_display_default"]["distributed_stale_vs_legacy"] is False
    assert result["q23j_display_default"]["legacy_fallback_ready"] is True
    assert result["legacy_latest_shrink_executed"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["scheduler_action_changed"] is False
    assert result["would_send_to_broker"] is False


def test_tool_has_no_writer_scheduler_or_broker_code() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "write_distributed_sidecars_once",
        "run_one_shot_write",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_no_write_shrink_readiness_contract()
    test_reference_inventory_allows_retired_legacy_widget_refs()
    test_live_no_write_diagnostic_is_ready_or_only_dirty_blocked_after_retirement()
    test_tool_has_no_writer_scheduler_or_broker_code()
    print(json.dumps({"ok": True}))
