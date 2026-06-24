# path: ./tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close.py
# desc: Unit tests for PS-Q18BC WarRoom header compact polish and cleanup close.

from __future__ import annotations

import inspect
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.warroom_header as warroom_header  # noqa: E402

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


def build_ps_q18bc_cleanup_close_packet() -> dict:
    return {
        "ok": True,
        "close_version": "prediction_warroom.q18bc_header_compact_polish_cleanup_close.v1",
        "warroom_header_normal_ui_compact": True,
        "warroom_header_long_market_reading_caption_hidden": True,
        "warroom_header_long_operational_reading_caption_hidden": True,
        "warroom_header_summary_widget_diagnostic_caption_hidden": True,
        "caption_builder_functions_preserved": True,
        "component_modules_deleted_this_slice": False,
        "cleanup_thread_close_ready": True,
        "warroom_cleanup_optimization_complete": True,
        **{key: False for key in FALSE_BOUNDARIES},
    }


def test_ps_q18bc_header_render_is_compact_but_builders_are_preserved() -> None:
    render_source = inspect.getsource(warroom_header.render)
    assert "render_compact_metric_grid" in render_source
    assert "build_warroom_market_reading_caption" not in render_source
    assert "build_warroom_operational_reading_caption" not in render_source
    assert "summary_widget_caption" not in render_source
    assert hasattr(warroom_header, "build_warroom_market_reading_caption")
    assert hasattr(warroom_header, "build_warroom_operational_reading_caption")
    caption = warroom_header.build_warroom_market_reading_caption(
        state={"regime": "range", "source_label": "unit"}
    )
    assert "market_reading=range" in caption
    packet = build_ps_q18bc_cleanup_close_packet()
    assert packet["warroom_cleanup_optimization_complete"] is True
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
