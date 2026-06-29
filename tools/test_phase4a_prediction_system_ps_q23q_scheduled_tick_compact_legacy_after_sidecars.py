# path: ./tools/test_phase4a_prediction_system_ps_q23q_scheduled_tick_compact_legacy_after_sidecars.py
# desc: Focused guard for PS-Q23Q scheduled tick compact legacy latest after successful sidecar dual-write.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import (  # noqa: E402
    compact_legacy_latest_after_sidecar_dual_write_once,
    run_mountain2_actual_scheduled_latest_refresh_tick_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23Q_SCHEDULED_TICK_COMPACT_LEGACY_AFTER_SIDECARS_2026-06-29.md"
Q22S = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py"


def test_spec_declares_scheduled_compact_legacy_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23q_scheduled_tick_compact_legacy_after_sidecars=true",
        "scheduled_sidecar_dual_write_required=true",
        "compact_legacy_latest_after_sidecar=true",
        "legacy_latest_backup_per_tick=false",
        "latest_manifest_full_sidecars_retained=true",
        "scheduler_action_changed=false",
        "trigger_added=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_q22s_wires_compactor_after_sidecar_success() -> None:
    text = Q22S.read_text(encoding="utf-8")
    assert "compact_legacy_latest_after_sidecar_dual_write_once" in text
    assert "legacy_latest_compactor: LegacyLatestCompactor | None = None" in text
    assert "sidecar_dual_write_payload.get(\"sidecar_dual_write_success\") is True" in text
    assert "compact_legacy_latest_backup_written" in text
    assert "Q23M_COMPACTOR_VERSION" in text


def test_q22s_has_no_scheduler_action_or_broker_code() -> None:
    text = Q22S.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "send_order(",
        "place_order(",
    ):
        assert forbidden not in text, forbidden


def test_symbols_importable() -> None:
    assert callable(run_mountain2_actual_scheduled_latest_refresh_tick_once)
    assert callable(compact_legacy_latest_after_sidecar_dual_write_once)


if __name__ == "__main__":
    test_spec_declares_scheduled_compact_legacy_contract()
    test_q22s_wires_compactor_after_sidecar_success()
    test_q22s_has_no_scheduler_action_or_broker_code()
    test_symbols_importable()
    print(json.dumps({"ok": True}))
