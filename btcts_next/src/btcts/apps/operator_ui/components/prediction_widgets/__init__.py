# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/__init__.py
# desc: PS-Q17S Prediction WarRoom read-only widget skeleton package metadata. This package is not imported by warroom_page.py in PS-Q17S.

from __future__ import annotations

PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_PACKAGE_VERSION = "prediction_warroom_widget_component_skeleton_package.ps_q17s.v1"
WIDGET_FAMILY_ORDER = (
    "latest_prediction_summary_widget",
    "prediction_delta_widget",
    "scenario_trace_widget",
    "evidence_weighting_widget",
    "invalidation_rewrite_widget",
    "source_quality_freshness_widget",
    "warning_blocker_widget",
    "signal_strength_calibration_widget",
    "parameter_candidate_comparison_widget",
    "replay_outcome_calibration_widget",
    "producer_freshness_status_widget",
    "runtime_boundary_safety_widget",
)

__all__ = (
    "PREDICTION_WARROOM_WIDGET_COMPONENT_SKELETON_PACKAGE_VERSION",
    "WIDGET_FAMILY_ORDER",
)
