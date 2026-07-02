# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/contracts.py
# desc: WarRoom v2 widget read-model and update-event contracts. No Streamlit, D-hot reads, transport, or execution behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .safety import WidgetSafetyFlags

WARROOM_V2_WIDGET_READ_MODEL_VERSION = "prediction_warroom.v2.widget_read_model.ps_q29a.v1"
WARROOM_V2_WIDGET_UPDATE_EVENT_VERSION = "prediction_warroom.v2.widget_update_event.ps_q29a.v1"


@dataclass(frozen=True)
class WidgetReadModel:
    widget_id: str
    topic: str
    generated_at: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    title: str = ""
    version: str = WARROOM_V2_WIDGET_READ_MODEL_VERSION
    freshness: str = "unknown"
    fingerprint: str = ""
    detail_available: bool = False
    scenario_area: bool = False
    debug_payload_available: bool = False
    source_kind: str = "read_model_contract_only"
    safety: WidgetSafetyFlags = field(default_factory=WidgetSafetyFlags)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["payload"] = dict(self.payload)
        data["safety"] = self.safety.to_dict()
        data["read_model_consumer_only"] = True
        data["widget_owns_artifact_scanning"] = False
        data["widget_owns_classifier_invocation"] = False
        data["widget_owns_cache_invalidation"] = False
        data["future_push_compatible"] = True
        return data


@dataclass(frozen=True)
class WidgetUpdateEvent:
    event_id: str
    topic: str
    generated_at: str
    read_model: WidgetReadModel
    sequence: int = 0
    previous_fingerprint: str = ""
    current_fingerprint: str = ""
    source_kind: str = "poll_fingerprint_check"
    version: str = WARROOM_V2_WIDGET_UPDATE_EVENT_VERSION
    safety: WidgetSafetyFlags = field(default_factory=WidgetSafetyFlags)

    @property
    def changed(self) -> bool:
        return self.previous_fingerprint != self.current_fingerprint

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": True,
            "event_id": self.event_id,
            "event_version": self.version,
            "topic": self.topic,
            "sequence": int(self.sequence),
            "generated_at": self.generated_at,
            "previous_fingerprint": self.previous_fingerprint,
            "current_fingerprint": self.current_fingerprint,
            "changed": self.changed,
            "source_kind": self.source_kind,
            "event_source_replaceable": True,
            "current_source_can_be_poll_fingerprint": True,
            "future_websocket_compatible": True,
            "future_sse_compatible": True,
            "read_model": self.read_model.to_dict(),
            "safety": self.safety.to_dict(),
        }


def build_empty_widget_read_model(
    *,
    widget_id: str,
    topic: str,
    generated_at: str,
    title: str = "",
    payload: Mapping[str, Any] | None = None,
    freshness: str = "unknown",
    fingerprint: str = "",
    detail_available: bool = False,
    scenario_area: bool = False,
    debug_payload_available: bool = False,
) -> dict[str, Any]:
    return WidgetReadModel(
        widget_id=widget_id,
        topic=topic,
        generated_at=generated_at,
        title=title,
        payload=dict(payload or {}),
        freshness=freshness,
        fingerprint=fingerprint,
        detail_available=detail_available,
        scenario_area=scenario_area,
        debug_payload_available=debug_payload_available,
    ).to_dict()


def build_widget_update_event(
    *,
    widget_id: str,
    topic: str,
    generated_at: str,
    previous_fingerprint: str,
    current_fingerprint: str,
    sequence: int = 0,
    title: str = "",
    payload: Mapping[str, Any] | None = None,
    source_kind: str = "poll_fingerprint_check",
) -> dict[str, Any]:
    read_model = WidgetReadModel(
        widget_id=widget_id,
        topic=topic,
        generated_at=generated_at,
        title=title,
        payload=dict(payload or {}),
        fingerprint=current_fingerprint,
        source_kind=source_kind,
    )
    return WidgetUpdateEvent(
        event_id=f"{topic}:{int(sequence)}:{current_fingerprint or 'none'}",
        topic=topic,
        generated_at=generated_at,
        read_model=read_model,
        sequence=sequence,
        previous_fingerprint=previous_fingerprint,
        current_fingerprint=current_fingerprint,
        source_kind=source_kind,
    ).to_dict()
