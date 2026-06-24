# path: ./tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup.py
# desc: Unit tests for PS-Q18AZ WarRoom operator-first render path cleanup packet.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    _warroom_operator_first_render_path_cleanup_packet,
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
    "would_send_to_broker",
)


def test_ps_q18az_cleanup_packet_is_operator_first_and_non_executing() -> None:
    packet = _warroom_operator_first_render_path_cleanup_packet()
    assert packet["ok"] is True
    assert packet["cleanup_state"] == "normal_warroom_ui_operator_first_dev_preflight_sections_removed"
    assert packet["normal_ui_path_operator_first"] is True
    assert packet["latest_prediction_quick_status_kept"] is True
    assert packet["prediction_warroom_dev_preflight_sections_rendered_in_normal_path"] is False
    assert packet["legacy_dev_helpers_deleted_this_slice"] is False
    assert packet["future_extension_contracts_preserved"] is True
    assert packet["removed_section_count"] == 12
    assert "Prediction WarRoom real payload review" in packet["removed_from_normal_ui_path"]
    assert "Prediction WarRoom latest summary safe display mount" in packet["removed_from_normal_ui_path"]
    assert "Prediction WarRoom mount review" in packet["removed_from_normal_ui_path"]
    assert "payload_to_widget_props_mapping_contract" in packet["preserved_for_future_extension"]
    assert packet["next_safe_slice"] == "PS-Q18BA WarRoom legacy prediction dev helper/import prune"
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
