# path: ./tools/test_phase4a_prediction_system_ps_q18as_still_disabled_real_render_prototype.py
# desc: Unit tests for PS-Q18AS still-disabled real-render prototype.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import (  # noqa: E402
    REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES,
    REAL_RENDER_PROTOTYPE_GATE_STATE,
    build_latest_prediction_summary_widget_real_render_prototype_packet,
    render_latest_prediction_summary_widget,
)


def test_ps_q18as_prototype_is_still_disabled_even_when_flags_true() -> None:
    packet = build_latest_prediction_summary_widget_real_render_prototype_packet(
        {"source_generated_at": "2026-06-24T00:00:00Z"},
        requested_enable_real_render=True,
        implementation_gate_open=True,
        manual_ui_review_passed=True,
        rollback_plan_ready=True,
    )
    assert packet["ok"] is True
    assert packet["prototype_state"] == REAL_RENDER_PROTOTYPE_GATE_STATE
    assert packet["prototype_state"] == "still_disabled_real_render_prototype_blocked"
    assert packet["skeleton_packet_preserved"] is True
    assert packet["skeleton_component_state"] == "read_only_component_skeleton_render_disabled"
    assert packet["flags"]["requested_enable_real_render"] is True
    assert packet["real_rendering_enabled"] is False
    assert packet["future_implementation_gate_required"] is True
    assert packet["manual_ui_review_required_before_enablement"] is True
    assert "separate_future_implementation_gate_required" in packet["prototype_blockers"]
    for key in REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18as_existing_render_function_still_returns_skeleton_packet() -> None:
    skeleton = render_latest_prediction_summary_widget()
    assert skeleton["component_state"] == "read_only_component_skeleton_render_disabled"
    assert skeleton["streamlit_render_allowed"] is False
    assert skeleton["streamlit_render_invoked"] is False
    assert skeleton["component_skeleton_only"] is True
    assert skeleton["broker_private_api_allowed"] is False
    assert skeleton["autotrade_trigger_allowed"] is False
