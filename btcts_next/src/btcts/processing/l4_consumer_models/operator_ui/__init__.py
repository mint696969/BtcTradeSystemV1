# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/__init__.py
# desc: Thin operator UI adapter package over shared L4 bundles.

"""
Operator UI adapters.

Rules:
- thin conversion only
- do not redefine market meaning
- do not own layout or CSS
- do not produce widget-library-final render shapes
"""

from .health_digest_adapter import (
    HealthDigestWidgetModel,
    health_digest_status_payload,
    health_digest_widget_model,
)
from .market_summary_adapter import (
    MarketSummaryWidgetModel,
    market_summary_status_payload,
    market_summary_widget_model,
)
from .prediction_summary_adapter import (
    PredictionSummaryWidgetModel,
    prediction_summary_status_payload,
    prediction_summary_widget_model,
)
from .real_data_validation_evidence_consumption import (
    HealthWarRoomEvidenceConsumptionModel,
    build_health_warroom_evidence_consumption_model,
    health_warroom_evidence_consumption_model_to_snapshot,
    health_warroom_evidence_consumption_status_payload,
    HealthWarRoomEvidencePresentationModel,
    health_warroom_evidence_presentation_model,
    health_warroom_evidence_presentation_payload,
)
from .real_data_validation_evidence_presentation_upstream import (
    build_health_warroom_evidence_presentation_upstream_payload,
    health_snapshot_evidence_presentation_payload_fields,
    lower_health_warroom_evidence_presentation_payload,
    warroom_session_state_evidence_presentation_payload_fields,
)

__all__ = [
    "HealthDigestWidgetModel",
    "health_digest_status_payload",
    "health_digest_widget_model",
    "MarketSummaryWidgetModel",
    "market_summary_status_payload",
    "market_summary_widget_model",
    "PredictionSummaryWidgetModel",
    "prediction_summary_status_payload",
    "prediction_summary_widget_model",
    "HealthWarRoomEvidenceConsumptionModel",
    "build_health_warroom_evidence_consumption_model",
    "health_warroom_evidence_consumption_model_to_snapshot",
    "health_warroom_evidence_consumption_status_payload",
    "HealthWarRoomEvidencePresentationModel",
    "health_warroom_evidence_presentation_model",
    "health_warroom_evidence_presentation_payload",
    "build_health_warroom_evidence_presentation_upstream_payload",
    "health_snapshot_evidence_presentation_payload_fields",
    "lower_health_warroom_evidence_presentation_payload",
    "warroom_session_state_evidence_presentation_payload_fields",
]