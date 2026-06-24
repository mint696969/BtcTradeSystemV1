# path: ./tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune.py
# desc: Unit tests for PS-Q18BA WarRoom legacy prediction dev helper/import prune.

from __future__ import annotations

import inspect
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.views.warroom_page as warroom_page  # noqa: E402

REMOVED_HELPERS = (
    "_render_prediction_warroom_ui_mount_review_section",
    "_render_prediction_warroom_lowered_display_packet_visibility_review_section",
    "_render_prediction_warroom_prediction_widgets_disabled_section_review_mount",
    "_render_prediction_warroom_prediction_widget_source_readiness_preflight_section",
    "_render_prediction_warroom_prediction_widget_source_read_probe_status_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_props_candidate_status_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_mapped_payload_value_rows_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_operator_value_summary_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section",
    "_render_prediction_warroom_latest_prediction_summary_widget_safe_display_mount_section",
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


def test_ps_q18ba_pruned_legacy_helpers_but_kept_quick_status_and_cleanup_packet() -> None:
    for name in REMOVED_HELPERS:
        assert not hasattr(warroom_page, name), name
    assert hasattr(warroom_page, "_render_prediction_warroom_latest_prediction_observation_cleanup_summary_section")
    assert hasattr(warroom_page, "_warroom_operator_first_render_path_cleanup_packet")
    packet = warroom_page._warroom_operator_first_render_path_cleanup_packet()
    assert packet["cleanup_state"] == "normal_warroom_ui_operator_first_dev_preflight_sections_removed"
    assert packet["future_extension_contracts_preserved"] is True
    assert packet["legacy_dev_helpers_deleted_this_slice"] is False
    body_source = inspect.getsource(warroom_page._render_warroom_page_body)
    assert "Prediction WarRoom latest summary observation quick status" in body_source
    assert "Prediction WarRoom real payload review" not in body_source
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
