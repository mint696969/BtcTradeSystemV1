# path: ./btcts_next/src/btcts/autotrade/config/bundle_events.py
# desc: Parameter bundle event ledger models and JSONL helpers.

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from btcts.autotrade.config.models import ParameterSetBundle


class ParameterBundleEventType(str, Enum):
    BUNDLE_CREATED = "bundle_created"
    BUNDLE_ACTIVATED_SHADOW = "bundle_activated_shadow"
    BUNDLE_ACTIVATED_PAPER = "bundle_activated_paper"
    BUNDLE_ACTIVATED_LIVE = "bundle_activated_live"
    BUNDLE_ROLLBACK = "bundle_rollback"
    BUNDLE_RETIRED = "bundle_retired"


def _as_tuple(values: Iterable[str] | None) -> Tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values if str(value or "").strip())


def build_parameter_bundle_event_id(
    *,
    event_ts: str,
    event_type: ParameterBundleEventType | str,
    parameter_bundle_id: str | None = None,
    previous_bundle_id: str | None = None,
    new_bundle_id: str | None = None,
    reason: str = "",
) -> str:
    event_type_value = event_type.value if isinstance(event_type, ParameterBundleEventType) else str(event_type)
    safe_ts = re.sub(r"[^0-9A-Za-z]+", "_", str(event_ts)).strip("_")
    payload = "|".join(
        [
            str(event_ts),
            event_type_value,
            str(parameter_bundle_id or ""),
            str(previous_bundle_id or ""),
            str(new_bundle_id or ""),
            str(reason or ""),
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:10]
    return f"pbevt_{safe_ts}_{event_type_value}_{digest}"


@dataclass(frozen=True)
class ParameterBundleEvent:
    event_id: str
    event_ts: str
    event_type: ParameterBundleEventType
    parameter_bundle_id: str | None = None
    previous_bundle_id: str | None = None
    new_bundle_id: str | None = None
    parent_parameter_bundle_id: str | None = None
    regime_parameter_set_id: str | None = None
    trade_parameter_set_id: str | None = None
    reason: str = ""
    created_by: str | None = None
    approved_by: str | None = None
    source_decision_ids: Tuple[str, ...] = ()
    gpt_review_ids: Tuple[str, ...] = ()
    human_approval_id: str | None = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = "autotrade_parameter_bundle_event.v1"
        data["event_type"] = self.event_type.value
        data["source_decision_ids"] = list(self.source_decision_ids)
        data["gpt_review_ids"] = list(self.gpt_review_ids)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParameterBundleEvent":
        return cls(
            event_id=str(data["event_id"]),
            event_ts=str(data["event_ts"]),
            event_type=ParameterBundleEventType(str(data["event_type"])),
            parameter_bundle_id=data.get("parameter_bundle_id"),
            previous_bundle_id=data.get("previous_bundle_id"),
            new_bundle_id=data.get("new_bundle_id"),
            parent_parameter_bundle_id=data.get("parent_parameter_bundle_id"),
            regime_parameter_set_id=data.get("regime_parameter_set_id"),
            trade_parameter_set_id=data.get("trade_parameter_set_id"),
            reason=str(data.get("reason") or ""),
            created_by=data.get("created_by"),
            approved_by=data.get("approved_by"),
            source_decision_ids=_as_tuple(data.get("source_decision_ids")),
            gpt_review_ids=_as_tuple(data.get("gpt_review_ids")),
            human_approval_id=data.get("human_approval_id"),
            notes=str(data.get("notes") or ""),
            metadata=dict(data.get("metadata") or {}),
        )


def build_bundle_created_event(
    *,
    bundle: ParameterSetBundle,
    event_ts: str,
    reason: str,
    created_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
    metadata: Dict[str, Any] | None = None,
) -> ParameterBundleEvent:
    return ParameterBundleEvent(
        event_id=build_parameter_bundle_event_id(
            event_ts=event_ts,
            event_type=ParameterBundleEventType.BUNDLE_CREATED,
            parameter_bundle_id=bundle.parameter_bundle_id,
            reason=reason,
        ),
        event_ts=event_ts,
        event_type=ParameterBundleEventType.BUNDLE_CREATED,
        parameter_bundle_id=bundle.parameter_bundle_id,
        parent_parameter_bundle_id=bundle.parent_parameter_bundle_id,
        regime_parameter_set_id=bundle.regime_parameter_set_id,
        trade_parameter_set_id=bundle.trade_parameter_set_id,
        reason=reason,
        created_by=created_by,
        source_decision_ids=_as_tuple(source_decision_ids),
        gpt_review_ids=_as_tuple(gpt_review_ids),
        human_approval_id=human_approval_id,
        notes=notes,
        metadata=dict(metadata or {}),
    )


def build_bundle_activation_event(
    *,
    event_type: ParameterBundleEventType,
    event_ts: str,
    previous_bundle_id: str | None,
    new_bundle_id: str,
    reason: str,
    approved_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
    metadata: Dict[str, Any] | None = None,
) -> ParameterBundleEvent:
    if event_type not in {
        ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW,
        ParameterBundleEventType.BUNDLE_ACTIVATED_PAPER,
        ParameterBundleEventType.BUNDLE_ACTIVATED_LIVE,
    }:
        raise ValueError(f"activation event_type required, got {event_type!r}")

    return ParameterBundleEvent(
        event_id=build_parameter_bundle_event_id(
            event_ts=event_ts,
            event_type=event_type,
            previous_bundle_id=previous_bundle_id,
            new_bundle_id=new_bundle_id,
            reason=reason,
        ),
        event_ts=event_ts,
        event_type=event_type,
        parameter_bundle_id=new_bundle_id,
        previous_bundle_id=previous_bundle_id,
        new_bundle_id=new_bundle_id,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=_as_tuple(source_decision_ids),
        gpt_review_ids=_as_tuple(gpt_review_ids),
        human_approval_id=human_approval_id,
        notes=notes,
        metadata=dict(metadata or {}),
    )


def build_bundle_rollback_event(
    *,
    event_ts: str,
    previous_bundle_id: str,
    rollback_bundle_id: str,
    reason: str,
    approved_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
    metadata: Dict[str, Any] | None = None,
) -> ParameterBundleEvent:
    return ParameterBundleEvent(
        event_id=build_parameter_bundle_event_id(
            event_ts=event_ts,
            event_type=ParameterBundleEventType.BUNDLE_ROLLBACK,
            previous_bundle_id=previous_bundle_id,
            new_bundle_id=rollback_bundle_id,
            reason=reason,
        ),
        event_ts=event_ts,
        event_type=ParameterBundleEventType.BUNDLE_ROLLBACK,
        parameter_bundle_id=rollback_bundle_id,
        previous_bundle_id=previous_bundle_id,
        new_bundle_id=rollback_bundle_id,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=_as_tuple(source_decision_ids),
        gpt_review_ids=_as_tuple(gpt_review_ids),
        human_approval_id=human_approval_id,
        notes=notes,
        metadata=dict(metadata or {}),
    )


def append_parameter_bundle_event_jsonl(path: Path, event: ParameterBundleEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def read_parameter_bundle_events_jsonl(path: Path) -> Tuple[ParameterBundleEvent, ...]:
    if not path.exists():
        return ()
    rows: list[ParameterBundleEvent] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(ParameterBundleEvent.from_dict(json.loads(line)))
    return tuple(rows)
