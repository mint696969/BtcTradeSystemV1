# path: ./tools/test_phase4a_prediction_system_ps_q19p_periodic_producer_scheduling_decision.py
# desc: Focused guard for PS-Q19P periodic producer scheduling decision helper.

from __future__ import annotations

from datetime import datetime, timezone
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.check_prediction_warroom_periodic_producer_scheduling_decision_ps_q19p import (  # noqa: E402
    PS_Q19P_SCHEDULING_DECISION_VERSION,
    build_ps_q19p_scheduling_decision_packet,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19P_PERIODIC_PRODUCER_SCHEDULING_DECISION_2026-06-25.md"
TOOL = REPO_ROOT / "tools/check_prediction_warroom_periodic_producer_scheduling_decision_ps_q19p.py"

REQUIRED_MARKERS = (
    "ps_q19p_periodic_producer_scheduling_decision=true",
    "scheduling_decision_helper_added=true",
    "allowed_mode=ack_gated_bounded_foreground_observation",
)

FALSE_BOUNDARIES = (
    "scheduler_install_performed=false",
    "scheduler_enabled=false",
    "scheduled_loop_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "ui_triggered_runner_execution=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _payload() -> dict:
    return {
        "run_identity": {"generated_at": "2026-06-25T00:00:00Z"},
        "outputs": [
            {"family": "trend_bias", "horizon_sec": 15, "primary_label": "neutral_bias", "warnings": [], "drivers": ["ok"]},
            {"family": "macro_risk_context", "horizon_sec": 14400, "primary_label": "macro_context_neutral", "warnings": [], "drivers": ["ok"]},
        ],
        "warnings": [],
    }


def _status() -> dict:
    return {
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_generated_at": "2026-06-25T00:00:00Z",
        "last_warning_count": 1,
        "consecutive_failure_count": 0,
        "producer_enabled": False,
        "scheduler_enabled": False,
        "safe_flags": {"would_send_to_broker_false": True},
    }


def test_spec_declares_decision_helper_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_scheduling_decision_allows_bounded_foreground_when_quality_gates_clear() -> None:
    packet = build_ps_q19p_scheduling_decision_packet(
        root="D:/btc_ts_hot",
        payload=_payload(),
        status_payload=_status(),
        now=datetime(2026, 6, 25, 0, 1, 0, tzinfo=timezone.utc),
    )
    assert packet["ok"] is True
    assert packet["ps_q19p_version"] == PS_Q19P_SCHEDULING_DECISION_VERSION
    assert packet["decision"] == "allow_ack_gated_bounded_foreground_observation"
    assert packet["ready_for_bounded_foreground_observation"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["would_send_to_broker"] is False
    assert "PS_Q19K_RUN_BOUNDED_PERIODIC_PREDICTION_PRODUCER" in packet["recommended_bounded_command"]


def test_scheduling_decision_blocks_when_context_profile_missing_sources_remain() -> None:
    payload = _payload()
    payload["outputs"][0]["warnings"] = ["context_profile_family_minimum_sources_missing"]
    payload["outputs"][0]["missing_minimum_required_sources"] = ["macro_context"]
    packet = build_ps_q19p_scheduling_decision_packet(
        root="D:/btc_ts_hot",
        payload=payload,
        status_payload=_status(),
        now=datetime(2026, 6, 25, 0, 1, 0, tzinfo=timezone.utc),
    )
    assert packet["decision"] == "keep_manual_or_fix_blockers_first"
    assert packet["ready_for_bounded_foreground_observation"] is False
    assert "context_profile_minimum_sources_still_missing" in packet["blocked_reasons"]


def test_scheduling_decision_blocks_scheduler_or_producer_status_true() -> None:
    status = _status()
    status["scheduler_enabled"] = True
    packet = build_ps_q19p_scheduling_decision_packet(
        root="D:/btc_ts_hot",
        payload=_payload(),
        status_payload=status,
        now=datetime(2026, 6, 25, 0, 1, 0, tzinfo=timezone.utc),
    )
    assert packet["decision"] == "keep_manual_or_fix_blockers_first"
    assert "unexpected_status_scheduler_enabled_true" in packet["blocked_reasons"]


def test_tool_has_no_execution_or_scheduler_install_behavior() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "scheduler_install_performed" in text
    assert "build_ps_q19p_scheduling_decision_packet" in text
    assert "recommended_bounded_command" in text
    assert "build_ps_q19k_periodic_producer_packet(" not in text
    assert "execute_periodic_producer=True" not in text


if __name__ == "__main__":
    test_spec_declares_decision_helper_and_safety_boundaries()
    test_scheduling_decision_allows_bounded_foreground_when_quality_gates_clear()
    test_scheduling_decision_blocks_when_context_profile_missing_sources_remain()
    test_scheduling_decision_blocks_scheduler_or_producer_status_true()
    test_tool_has_no_execution_or_scheduler_install_behavior()
    print('{"ok": true}')
