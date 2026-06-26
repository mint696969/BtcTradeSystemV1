# path: ./tools/test_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke.py
# desc: Focused guard for PS-Q21B WarRoom prediction auto-refresh visual smoke helper.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.smoke_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke import (  # noqa: E402
    SMOKE_VERSION,
    run_smoke,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21B_WARROOM_PREDICTION_AUTO_REFRESH_VISUAL_SMOKE_2026-06-26.md"
SMOKE = REPO_ROOT / "tools/smoke_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke.py"

REQUIRED_MARKERS = (
    "ps_q21b_warroom_prediction_auto_refresh_visual_smoke=true",
    "non_ui_packet_heartbeat_changed=true",
    "manual_ui_smoke_required=true",
    "manual_ui_smoke_command=.\\tools\\run_operator_ui_sr_fx_dhot.ps1 -Port 501",
    "refresh_target=latest_prediction_warroom_read_model_display_panel",
    "refresh_interval_sec=5",
    "broad_page_reload_disabled=true",
)

FALSE_BOUNDARIES = (
    "runtime_enablement_allowed=false",
    "loader_binding_runtime_allowed=false",
    "component_runtime_binding_allowed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def test_spec_declares_visual_smoke_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_smoke_packet_heartbeat_changes_and_keeps_safety_false() -> None:
    result = run_smoke(sleep_sec=1.05)
    assert result["ok"] is True
    assert result["smoke_version"] == SMOKE_VERSION
    assert result["non_ui_packet_heartbeat_changed"] is True
    assert result["refresh_interval_sec"] == 5
    assert result["refresh_target"] == "latest_prediction_warroom_read_model_display_panel"
    assert result["warroom_prediction_display_auto_refresh_enabled"] is True
    assert result["operator_visible_refresh_heartbeat"] is True
    assert result["broad_page_reload_disabled"] is True
    assert result["manual_ui_smoke_required"] is True
    assert result["unsafe_flags"] == []
    assert result["missing_markers"] == []
    assert result["runtime_enablement_allowed"] is False
    assert result["loader_binding_runtime_allowed"] is False
    assert result["scheduler_enabled"] is False
    assert result["producer_enabled"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_smoke_helper_is_read_only_no_ui_automation_or_artifact_write() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "append_jsonl(",
        "subprocess.run(",
        "streamlit run",
        "playwright",
        "selenium",
        "send_order(",
        "place_order(",
        "runtime_artifact_write_allowed: bool = True",
        "view_artifact_write_allowed: bool = True",
        "scheduler_enabled: bool = True",
        "producer_enabled: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "broker_private_api_allowed: bool = True",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_visual_smoke_and_safety_boundaries()
    test_smoke_packet_heartbeat_changes_and_keeps_safety_false()
    test_smoke_helper_is_read_only_no_ui_automation_or_artifact_write()
    print('{"ok": true}')
