# path: ./btcts_next/src/btcts/autotrade/config/bundle_runtime_store.py
# desc: Runtime store helpers for parameter bundle files, registry, and event ledger.

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from btcts.autotrade.config.bundle_events import ParameterBundleEventType
from btcts.autotrade.config.bundle_lifecycle import (
    ParameterBundleLifecycleResult,
    activate_bundle_lifecycle,
    rollback_bundle_lifecycle,
    save_bundle_created_lifecycle,
)
from btcts.autotrade.config.defaults import initial_parameter_bundle_v0_1
from btcts.autotrade.config.models import ParameterSetBundle, ParameterSetBundleRegistry
from btcts.autotrade.config.registry import read_json
from btcts.autotrade.runtime_paths import (
    parameter_bundle_event_ledger_path,
    parameter_registry_path,
)


def parameter_bundle_registry_from_dict(data: dict[str, Any]) -> ParameterSetBundleRegistry:
    return ParameterSetBundleRegistry(
        active_shadow_bundle_id=data.get("active_shadow_bundle_id"),
        active_paper_bundle_id=data.get("active_paper_bundle_id"),
        active_live_bundle_id=data.get("active_live_bundle_id"),
        last_known_good_bundle_id=data.get("last_known_good_bundle_id"),
        rollback_bundle_id=data.get("rollback_bundle_id"),
        pending_draft_bundle_id=data.get("pending_draft_bundle_id"),
        retired_bundle_ids=tuple(data.get("retired_bundle_ids") or ()),
    )


def read_parameter_bundle_registry_or_default(
    path: Path,
    *,
    default: ParameterSetBundleRegistry | None = None,
) -> ParameterSetBundleRegistry:
    if not path.exists():
        return default or ParameterSetBundleRegistry()
    return parameter_bundle_registry_from_dict(read_json(path))


def runtime_parameter_bundle_root(registry_path: Path) -> Path:
    return registry_path.parent


def initialize_default_parameter_bundle_runtime(
    *,
    event_ts: str,
    reason: str,
    created_by: str,
    registry_path: Path | None = None,
    event_ledger_path: Path | None = None,
    bundle: ParameterSetBundle | None = None,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    resolved_registry_path = registry_path or parameter_registry_path(ensure=True)
    resolved_event_path = event_ledger_path or parameter_bundle_event_ledger_path(ensure=True)
    resolved_bundle = bundle or initial_parameter_bundle_v0_1()
    registry = read_parameter_bundle_registry_or_default(resolved_registry_path)

    return save_bundle_created_lifecycle(
        bundle=resolved_bundle,
        registry=registry,
        bundle_dir=runtime_parameter_bundle_root(resolved_registry_path),
        registry_path=resolved_registry_path,
        event_ledger_path=resolved_event_path,
        event_ts=event_ts,
        reason=reason,
        created_by=created_by,
        source_decision_ids=source_decision_ids,
        gpt_review_ids=gpt_review_ids,
        human_approval_id=human_approval_id,
        notes=notes,
    )


def activate_parameter_bundle_runtime(
    *,
    event_type: ParameterBundleEventType,
    event_ts: str,
    new_bundle_id: str,
    reason: str,
    approved_by: str,
    registry_path: Path | None = None,
    event_ledger_path: Path | None = None,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    resolved_registry_path = registry_path or parameter_registry_path(ensure=True)
    resolved_event_path = event_ledger_path or parameter_bundle_event_ledger_path(ensure=True)
    registry = read_parameter_bundle_registry_or_default(resolved_registry_path)

    return activate_bundle_lifecycle(
        registry=registry,
        registry_path=resolved_registry_path,
        event_ledger_path=resolved_event_path,
        event_type=event_type,
        event_ts=event_ts,
        new_bundle_id=new_bundle_id,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=source_decision_ids,
        gpt_review_ids=gpt_review_ids,
        human_approval_id=human_approval_id,
        notes=notes,
    )


def rollback_parameter_bundle_runtime(
    *,
    event_ts: str,
    rollback_bundle_id: str,
    target_stage: str,
    reason: str,
    approved_by: str,
    registry_path: Path | None = None,
    event_ledger_path: Path | None = None,
    source_decision_ids: Iterable[str] | None = None,
    gpt_review_ids: Iterable[str] | None = None,
    human_approval_id: str | None = None,
    notes: str = "",
) -> ParameterBundleLifecycleResult:
    resolved_registry_path = registry_path or parameter_registry_path(ensure=True)
    resolved_event_path = event_ledger_path or parameter_bundle_event_ledger_path(ensure=True)
    registry = read_parameter_bundle_registry_or_default(resolved_registry_path)

    return rollback_bundle_lifecycle(
        registry=registry,
        registry_path=resolved_registry_path,
        event_ledger_path=resolved_event_path,
        event_ts=event_ts,
        rollback_bundle_id=rollback_bundle_id,
        target_stage=target_stage,
        reason=reason,
        approved_by=approved_by,
        source_decision_ids=source_decision_ids,
        gpt_review_ids=gpt_review_ids,
        human_approval_id=human_approval_id,
        notes=notes,
    )
