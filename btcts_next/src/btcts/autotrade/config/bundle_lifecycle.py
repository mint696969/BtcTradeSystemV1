# path: ./btcts_next/src/btcts/autotrade/config/bundle_lifecycle.py
# desc: Parameter bundle lifecycle helpers. Writes bundle JSON, registry JSON, and event JSONL.

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

from btcts.autotrade.config.bundle_events import (
    ParameterBundleEvent,
    ParameterBundleEventType,
    append_parameter_bundle_event_jsonl,
    build_bundle_activation_event,
    build_bundle_created_event,
    build_bundle_rollback_event,
)
from btcts.autotrade.config.models import ParameterSetBundle, ParameterSetBundleRegistry, ParameterSetBundleStatus
from btcts.autotrade.config.registry import write_bundle_registry, write_parameter_bundle


@dataclass(frozen=True)
class ParameterBundleLifecycleResult:
    registry: ParameterSetBundleRegistry
    event: ParameterBundleEvent
    bundle_path: Path | None
    registry_path: Path
    event_ledger_path: Path
    bundle_written: bool
    registry_written: bool
    event_appended: bool


def parameter_bundle_json_path(bundle_dir: Path, parameter_bundle_id: str) -> Path:
    safe_id = str(parameter_bundle_id).strip()
    if not safe_id:
        raise ValueError("parameter_bundle_id is required")
    return bundle_dir / "bundles" / f"{safe_id}.json"


def _append_unique(values: tuple[str, ...], value: str) -> tuple[str, ...]:
    if value in values:
        return values
    return values + (value,)


def registry_after_bundle_saved(
    *,
    registry: ParameterSetBundleRegistry,
    bundle: ParameterSetBundle,
) -> ParameterSetBundleRegistry:
    status = bundle.status
    bundle_id = bundle.parameter_bundle_id

    if status == ParameterSetBundleStatus.DRAFT:
        return replace(registry, pending_draft_bundle_id=bundle_id)
    if status == ParameterSetBundleStatus.SHADOW:
        return replace(registry, active_shadow_bundle_id=bundle_id)
    if status == ParameterSetBundleStatus.PAPER:
        return replace(registry, active_paper_bundle_id=bundle_id)
    if status == ParameterSetBundleStatus.LIVE_ACTIVE:
        return replace(registry, active_live_bundle_id=bundle_id, last_known_good_bundle_id=bundle_id)
    if status == ParameterSetBundleStatus.ROLLBACK_CANDIDATE:
        return replace(registry, rollback_bundle_id=bundle_id)
    if status == ParameterSetBundleStatus.RETIRED:
        return replace(registry, retired_bundle_ids=_append_unique(registry.retired_bundle_ids, bundle_id))
    raise ValueError(f"unsupported bundle status: {status!r}")


def save_bundle_created_lifecycle(
    *,
    bundle: ParameterSetBundle,
    registry: ParameterSetBundleRegistry,
    bundle_dir: Path,
    registry_path: Path,
    event_ledger_path: Path,
    event_ts: str,
    reason: str,
    created_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    bundle_path = parameter_bundle_json_path(bundle_dir, bundle.parameter_bundle_id)
    next_registry = registry_after_bundle_saved(registry=registry, bundle=bundle)
    event = build_bundle_created_event(
        bundle=bundle,
        event_ts=event_ts,
        reason=reason,
        created_by=created_by,
        source_decision_ids=source_decision_ids,
        gpt_review_ids=gpt_review_ids,
        human_approval_id=human_approval_id,
        notes=notes,
    )

    write_parameter_bundle(bundle_path, bundle)
    write_bundle_registry(registry_path, next_registry)
    append_parameter_bundle_event_jsonl(event_ledger_path, event)

    return ParameterBundleLifecycleResult(
        registry=next_registry,
        event=event,
        bundle_path=bundle_path,
        registry_path=registry_path,
        event_ledger_path=event_ledger_path,
        bundle_written=True,
        registry_written=True,
        event_appended=True,
    )


def activate_bundle_lifecycle(
    *,
    registry: ParameterSetBundleRegistry,
    registry_path: Path,
    event_ledger_path: Path,
    event_type: ParameterBundleEventType,
    event_ts: str,
    new_bundle_id: str,
    reason: str,
    approved_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    if event_type == ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW:
        previous = registry.active_shadow_bundle_id
        next_registry = replace(registry, active_shadow_bundle_id=new_bundle_id)
    elif event_type == ParameterBundleEventType.BUNDLE_ACTIVATED_PAPER:
        previous = registry.active_paper_bundle_id
        next_registry = replace(registry, active_paper_bundle_id=new_bundle_id)
    elif event_type == ParameterBundleEventType.BUNDLE_ACTIVATED_LIVE:
        previous = registry.active_live_bundle_id
        next_registry = replace(
            registry,
            active_live_bundle_id=new_bundle_id,
            last_known_good_bundle_id=new_bundle_id,
            rollback_bundle_id=previous,
        )
    else:
        raise ValueError(f"activation event_type required, got {event_type!r}")

    event = build_bundle_activation_event(
        event_type=event_type,
        event_ts=event_ts,
        previous_bundle_id=previous,
        new_bundle_id=new_bundle_id,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=source_decision_ids,
        gpt_review_ids=gpt_review_ids,
        human_approval_id=human_approval_id,
        notes=notes,
    )

    write_bundle_registry(registry_path, next_registry)
    append_parameter_bundle_event_jsonl(event_ledger_path, event)

    return ParameterBundleLifecycleResult(
        registry=next_registry,
        event=event,
        bundle_path=None,
        registry_path=registry_path,
        event_ledger_path=event_ledger_path,
        bundle_written=False,
        registry_written=True,
        event_appended=True,
    )


def rollback_bundle_lifecycle(
    *,
    registry: ParameterSetBundleRegistry,
    registry_path: Path,
    event_ledger_path: Path,
    event_ts: str,
    rollback_bundle_id: str,
    target_stage: str,
    reason: str,
    approved_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    stage = str(target_stage).strip().lower()
    if stage == "shadow":
        previous = registry.active_shadow_bundle_id
        next_registry = replace(registry, active_shadow_bundle_id=rollback_bundle_id, rollback_bundle_id=previous)
    elif stage == "paper":
        previous = registry.active_paper_bundle_id
        next_registry = replace(registry, active_paper_bundle_id=rollback_bundle_id, rollback_bundle_id=previous)
    elif stage == "live":
        previous = registry.active_live_bundle_id
        next_registry = replace(
            registry,
            active_live_bundle_id=rollback_bundle_id,
            last_known_good_bundle_id=rollback_bundle_id,
            rollback_bundle_id=previous,
        )
    else:
        raise ValueError(f"target_stage must be shadow, paper, or live: {target_stage!r}")

    event = build_bundle_rollback_event(
        event_ts=event_ts,
        previous_bundle_id=previous or "",
        rollback_bundle_id=rollback_bundle_id,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=source_decision_ids,
        gpt_review_ids=gpt_review_ids,
        human_approval_id=human_approval_id,
        notes=notes,
    )

    write_bundle_registry(registry_path, next_registry)
    append_parameter_bundle_event_jsonl(event_ledger_path, event)

    return ParameterBundleLifecycleResult(
        registry=next_registry,
        event=event,
        bundle_path=None,
        registry_path=registry_path,
        event_ledger_path=event_ledger_path,
        bundle_written=False,
        registry_written=True,
        event_appended=True,
    )


def retire_bundle_lifecycle(
    *,
    registry: ParameterSetBundleRegistry,
    registry_path: Path,
    event_ledger_path: Path,
    event_ts: str,
    parameter_bundle_id: str,
    reason: str,
    approved_by: str,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    next_registry = replace(
        registry,
        retired_bundle_ids=_append_unique(registry.retired_bundle_ids, parameter_bundle_id),
    )
    event = ParameterBundleEvent(
        event_id=f"pbevt_{event_ts.replace(':', '').replace('-', '').replace('+', '_')}_bundle_retired_{parameter_bundle_id}",
        event_ts=event_ts,
        event_type=ParameterBundleEventType.BUNDLE_RETIRED,
        parameter_bundle_id=parameter_bundle_id,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=tuple(source_decision_ids or ()),
        gpt_review_ids=tuple(gpt_review_ids or ()),
        human_approval_id=human_approval_id,
        notes=notes,
    )

    write_bundle_registry(registry_path, next_registry)
    append_parameter_bundle_event_jsonl(event_ledger_path, event)

    return ParameterBundleLifecycleResult(
        registry=next_registry,
        event=event,
        bundle_path=None,
        registry_path=registry_path,
        event_ledger_path=event_ledger_path,
        bundle_written=False,
        registry_written=True,
        event_appended=True,
    )
