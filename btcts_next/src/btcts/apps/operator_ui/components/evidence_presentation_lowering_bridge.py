# path: ./btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_lowering_bridge.py
# desc: Bounded operator-ui bridge for lowering evidence presentation payloads into UI-side containers.

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_presentation_upstream import (
    lower_health_snapshot_evidence_presentation_fields,
    lower_warroom_session_state_evidence_presentation_fields,
)


def lower_health_snapshot_evidence_presentation_for_ui(
    snapshot: Mapping[str, Any] | None,
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return a copied Health snapshot with already-built evidence payload fields.

    This is an operator-ui bridge only. It does not read files, scan D/E,
    write runtime state, build evidence from source artifacts, render UI,
    or mutate the input snapshot.
    """
    out = lower_health_snapshot_evidence_presentation_fields(snapshot, payload)
    out["evidence_presentation_wiring_bridge"] = "health_snapshot_ui_bridge"
    out["evidence_presentation_wiring_bridge_version"] = "phase4a.health_snapshot_ui_bridge.v1"
    out["not_runtime_wiring"] = True
    out["not_runtime_signal"] = True
    out["not_market_engine_input"] = True
    out["not_collector_writer"] = True
    out["not_broker_or_order_automation"] = True
    out["not_inference_or_training"] = True
    return out


def lower_warroom_session_state_evidence_presentation_for_ui(
    session_state: Mapping[str, Any] | None,
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return a copied WarRoom session-state mapping with already-built evidence payload fields.

    This is an operator-ui bridge only. It does not call Streamlit, mutate
    st.session_state, read files, scan D/E, write runtime state, build evidence
    from source artifacts, or place orders.
    """
    out = lower_warroom_session_state_evidence_presentation_fields(session_state, payload)
    out["evidence_presentation_wiring_bridge"] = "warroom_session_state_ui_bridge"
    out["evidence_presentation_wiring_bridge_version"] = "phase4a.warroom_session_state_ui_bridge.v1"
    out["not_runtime_wiring"] = True
    out["not_runtime_signal"] = True
    out["not_market_engine_input"] = True
    out["not_collector_writer"] = True
    out["not_broker_or_order_automation"] = True
    out["not_inference_or_training"] = True
    return out
