# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/__init__.py
# desc: WarRoom v2 push-ready widget contracts. No Streamlit page mount or runtime side effects.

from __future__ import annotations

from .card_axis_policy import (
    WARROOM_V2_CARD_AXIS_POLICY_VERSION,
    WARROOM_V2_HORIZON_LABELS,
    build_warroom_v2_card_axis_policy,
)
from .contracts import (
    WARROOM_V2_WIDGET_READ_MODEL_VERSION,
    WARROOM_V2_WIDGET_UPDATE_EVENT_VERSION,
    WidgetReadModel,
    WidgetUpdateEvent,
    build_empty_widget_read_model,
    build_widget_update_event,
)
from .layout_policy import (
    WARROOM_V2_LAYOUT_POLICY_VERSION,
    build_warroom_v2_layout_policy,
)
from .placeholder_read_models import (
    WARROOM_V2_PLACEHOLDER_READ_MODELS_VERSION,
    build_warroom_v2_placeholder_read_models,
    build_warroom_v2_placeholder_read_models_packet,
)
from .shell_preview import (
    WARROOM_V2_SHELL_PREVIEW_VERSION,
    build_warroom_v2_shell_preview_packet,
)
from .safety import WidgetSafetyFlags, warroom_v2_safety_flags
from .topics import (
    WARROOM_V2_TOPIC_CATALOG_VERSION,
    WARROOM_V2_WIDGET_TOPICS,
    build_warroom_v2_widget_topic_catalog,
)

__all__ = [
    "build_warroom_v2_card_axis_policy",
    "WARROOM_V2_HORIZON_LABELS",
    "WARROOM_V2_CARD_AXIS_POLICY_VERSION",
    "WARROOM_V2_LAYOUT_POLICY_VERSION",
    "WARROOM_V2_PLACEHOLDER_READ_MODELS_VERSION",
    "WARROOM_V2_SHELL_PREVIEW_VERSION",
    "WARROOM_V2_TOPIC_CATALOG_VERSION",
    "WARROOM_V2_WIDGET_READ_MODEL_VERSION",
    "WARROOM_V2_WIDGET_TOPICS",
    "WARROOM_V2_WIDGET_UPDATE_EVENT_VERSION",
    "WidgetReadModel",
    "WidgetSafetyFlags",
    "WidgetUpdateEvent",
    "build_empty_widget_read_model",
    "build_warroom_v2_placeholder_read_models",
    "build_warroom_v2_placeholder_read_models_packet",
    "build_warroom_v2_shell_preview_packet",
    "build_warroom_v2_layout_policy",
    "build_warroom_v2_widget_topic_catalog",
    "build_widget_update_event",
    "warroom_v2_safety_flags",
]
