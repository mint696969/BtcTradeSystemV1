# path: ./tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_preflight.py
# desc: Unit tests for PS-Q18AN real-widget rendering gate preflight.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
    build_latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
)

SOURCE_PACKET_FALSE_BOUNDARIES = {
    "q18ah": (
        "real_prediction_widget_rendering_allowed",
        "real_prediction_widget_render_invoked",
        "streamlit_render_invoked",
        "component_runtime_binding_allowed",
        "component_props_bound_to_runtime",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ),
    "q18aj": FALSE_BOUNDARIES,
    "q18ak": FALSE_BOUNDARIES,
}

GATE_RELEASE_REQUIREMENTS = (
    "exact_component_runtime_binding_boundary",
    "exact_streamlit_render_function_boundary",
    "props_to_rendered_ui_mapping_contract",
    "stale_source_fallback_behavior_during_render",
    "missing_source_failure_mode",
    "no_runtime_status_artifact_writes",
    "no_parameter_apply_or_staging",
    "no_ledger_append",
    "no_autotrade_trigger",
    "no_broker_private_api",
)


def build_ps_q18an_real_widget_rendering_gate_preflight_packet() -> dict:
    q18ah = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation_packet(
        execute_packet_builder_validation=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
    )
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        now_utc="2026-06-24T13:45:00Z",
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    failures: list[str] = []
    if q18ah.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("q18ah_component_packet_not_render_disabled")
    if q18ah.get("component_packet_valid") is not True:
        failures.append("q18ah_component_packet_not_valid")
    if q18aj.get("auto_refresh_enabled") is not True:
        failures.append("q18aj_auto_refresh_not_enabled")
    if q18ak.get("freshness_monitor_enabled") is not True:
        failures.append("q18ak_freshness_monitor_not_enabled")
    for packet_name, packet in (("q18ah", q18ah), ("q18aj", q18aj), ("q18ak", q18ak)):
        for key in SOURCE_PACKET_FALSE_BOUNDARIES[packet_name]:
            if packet.get(key) is not False:
                failures.append(f"{packet_name}:{key}_not_false")
    return {
        "ok": not failures,
        "ps_q18an_real_widget_rendering_gate_preflight_version": "prediction_warroom.latest_prediction_summary_widget.q18an_real_widget_rendering_gate_preflight.v1",
        "intermediate_goal_reached": q18aj.get("auto_refresh_enabled") is True,
        "auto_refresh_enabled": q18aj.get("auto_refresh_enabled"),
        "freshness_monitor_enabled": q18ak.get("freshness_monitor_enabled"),
        "component_packet_state": q18ah.get("component_packet_state"),
        "component_packet_valid": q18ah.get("component_packet_valid"),
        "real_widget_rendering_gate_state": "preflight_only_rendering_not_enabled",
        "real_widget_rendering_allowed": False,
        "gate_release_requirements": list(GATE_RELEASE_REQUIREMENTS),
        "gate_release_requirement_count": len(GATE_RELEASE_REQUIREMENTS),
        "recommended_next_slice": "manual UI smoke execution record or explicit real-widget rendering design gate",
        **{key: False for key in FALSE_BOUNDARIES},
        "failures": failures,
    }


def test_ps_q18an_real_widget_gate_preflight_keeps_rendering_disabled() -> None:
    packet = build_ps_q18an_real_widget_rendering_gate_preflight_packet()
    assert packet["ok"] is True
    assert packet["intermediate_goal_reached"] is True
    assert packet["auto_refresh_enabled"] is True
    assert packet["freshness_monitor_enabled"] is True
    assert packet["component_packet_state"] == "read_only_component_skeleton_render_disabled"
    assert packet["component_packet_valid"] is True
    assert packet["real_widget_rendering_gate_state"] == "preflight_only_rendering_not_enabled"
    assert packet["gate_release_requirement_count"] == 10
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
