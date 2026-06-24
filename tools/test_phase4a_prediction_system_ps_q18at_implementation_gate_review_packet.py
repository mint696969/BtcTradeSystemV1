# path: ./tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet.py
# desc: Unit tests for PS-Q18AT implementation-gate review packet.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import (  # noqa: E402
    REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_real_render_prototype_packet,
)

IMPLEMENTATION_GATE_REVIEW_BLOCKERS = (
    "real_renderer_implementation_not_present",
    "warroom_runtime_binding_not_present",
    "manual_ui_review_for_real_renderer_not_present",
    "rollback_smoke_for_real_renderer_not_present",
    "implementation_gate_not_opened",
    "operator_approval_for_enablement_not_present",
)


def build_ps_q18at_implementation_gate_review_packet() -> dict:
    prototype = build_latest_prediction_summary_widget_real_render_prototype_packet(
        requested_enable_real_render=True,
        implementation_gate_open=False,
        manual_ui_review_passed=False,
        rollback_plan_ready=True,
    )
    packet = {
        "ok": True,
        "ps_q18at_review_packet_version": "prediction_warroom.latest_prediction_summary_widget.q18at_implementation_gate_review_packet.v1",
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "reviewed_prototype_state": prototype.get("prototype_state"),
        "prototype_skeleton_packet_preserved": prototype.get("skeleton_packet_preserved"),
        "prototype_real_rendering_enabled": prototype.get("real_rendering_enabled"),
        "future_implementation_gate_required": True,
        "manual_ui_review_required_before_enablement": True,
        "rollback_target": "read_only_component_skeleton_render_disabled",
        "blockers": list(IMPLEMENTATION_GATE_REVIEW_BLOCKERS),
        "blocker_count": len(IMPLEMENTATION_GATE_REVIEW_BLOCKERS),
        "next_safe_slice": "WarRoom observation cleanup or separate still-disabled renderer implementation skeleton with no WarRoom binding",
    }
    packet.update({key: False for key in REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES})
    return packet


def test_ps_q18at_review_packet_blocks_enablement() -> None:
    packet = build_ps_q18at_implementation_gate_review_packet()
    assert packet["ok"] is True
    assert packet["implementation_gate_review_result"] == "blocked_not_ready_to_enable"
    assert packet["reviewed_prototype_state"] == "still_disabled_real_render_prototype_blocked"
    assert packet["prototype_skeleton_packet_preserved"] is True
    assert packet["prototype_real_rendering_enabled"] is False
    assert packet["future_implementation_gate_required"] is True
    assert packet["manual_ui_review_required_before_enablement"] is True
    assert packet["rollback_target"] == "read_only_component_skeleton_render_disabled"
    assert packet["blocker_count"] == 6
    for blocker in IMPLEMENTATION_GATE_REVIEW_BLOCKERS:
        assert blocker in packet["blockers"]
    for key in REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES:
        assert packet[key] is False, key
