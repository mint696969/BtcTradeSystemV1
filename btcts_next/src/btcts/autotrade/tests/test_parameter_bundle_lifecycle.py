# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_lifecycle.py
# desc: Guards parameter bundle lifecycle writes, registry updates, and event JSONL history.

from __future__ import annotations

import json

from btcts.autotrade.config import initial_bundle_registry, initial_parameter_bundle_v0_1
from btcts.autotrade.config.bundle_events import ParameterBundleEventType, read_parameter_bundle_events_jsonl
from btcts.autotrade.config.bundle_lifecycle import (
    activate_bundle_lifecycle,
    parameter_bundle_json_path,
    rollback_bundle_lifecycle,
    save_bundle_created_lifecycle,
    retire_bundle_lifecycle,
)
from btcts.autotrade.config.models import ParameterSetBundleRegistry


def test_save_bundle_created_lifecycle_writes_bundle_registry_and_event(tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    registry = ParameterSetBundleRegistry()
    bundle_dir = tmp_path / "sets"
    registry_path = tmp_path / "registry.json"
    event_path = tmp_path / "parameter_bundle_events.jsonl"

    result = save_bundle_created_lifecycle(
        bundle=bundle,
        registry=registry,
        bundle_dir=bundle_dir,
        registry_path=registry_path,
        event_ledger_path=event_path,
        event_ts="2026-06-16T12:00:00+09:00",
        reason="Create initial lifecycle bundle.",
        created_by="human_gpt",
        source_decision_ids=("dec_create_001",),
        gpt_review_ids=("gpt_review_create_001",),
        human_approval_id="approval_create_001",
    )

    expected_bundle_path = parameter_bundle_json_path(bundle_dir, bundle.parameter_bundle_id)
    assert result.bundle_path == expected_bundle_path
    assert expected_bundle_path.exists()
    assert registry_path.exists()
    assert event_path.exists()

    bundle_data = json.loads(expected_bundle_path.read_text(encoding="utf-8"))
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = read_parameter_bundle_events_jsonl(event_path)

    assert bundle_data["parameter_bundle_id"] == bundle.parameter_bundle_id
    assert registry_data["active_shadow_bundle_id"] == bundle.parameter_bundle_id
    assert rows[0].event_type == ParameterBundleEventType.BUNDLE_CREATED
    assert rows[0].parameter_bundle_id == bundle.parameter_bundle_id
    assert rows[0].regime_parameter_set_id == bundle.regime_parameter_set_id
    assert rows[0].trade_parameter_set_id == bundle.trade_parameter_set_id
    assert rows[0].source_decision_ids == ("dec_create_001",)


def test_activate_bundle_lifecycle_updates_stage_and_appends_event(tmp_path) -> None:
    registry = ParameterSetBundleRegistry(active_shadow_bundle_id="pb_old")
    registry_path = tmp_path / "registry.json"
    event_path = tmp_path / "parameter_bundle_events.jsonl"

    result = activate_bundle_lifecycle(
        registry=registry,
        registry_path=registry_path,
        event_ledger_path=event_path,
        event_type=ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW,
        event_ts="2026-06-16T12:30:00+09:00",
        new_bundle_id="pb_new",
        reason="Shadow activation approved.",
        approved_by="human",
        source_decision_ids=("dec_shadow_001",),
        gpt_review_ids=("gpt_review_shadow_001",),
        human_approval_id="approval_shadow_001",
    )

    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = read_parameter_bundle_events_jsonl(event_path)

    assert result.registry.active_shadow_bundle_id == "pb_new"
    assert registry_data["active_shadow_bundle_id"] == "pb_new"
    assert rows[0].event_type == ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW
    assert rows[0].previous_bundle_id == "pb_old"
    assert rows[0].new_bundle_id == "pb_new"
    assert rows[0].human_approval_id == "approval_shadow_001"


def test_live_activation_sets_last_known_good_and_rollback_candidate(tmp_path) -> None:
    registry = ParameterSetBundleRegistry(active_live_bundle_id="pb_live_old")
    registry_path = tmp_path / "registry.json"
    event_path = tmp_path / "parameter_bundle_events.jsonl"

    result = activate_bundle_lifecycle(
        registry=registry,
        registry_path=registry_path,
        event_ledger_path=event_path,
        event_type=ParameterBundleEventType.BUNDLE_ACTIVATED_LIVE,
        event_ts="2026-06-16T13:00:00+09:00",
        new_bundle_id="pb_live_new",
        reason="Live activation approved.",
        approved_by="human",
    )

    assert result.registry.active_live_bundle_id == "pb_live_new"
    assert result.registry.last_known_good_bundle_id == "pb_live_new"
    assert result.registry.rollback_bundle_id == "pb_live_old"


def test_rollback_bundle_lifecycle_restores_target_stage_and_appends_event(tmp_path) -> None:
    registry = ParameterSetBundleRegistry(
        active_live_bundle_id="pb_bad",
        last_known_good_bundle_id="pb_bad",
        rollback_bundle_id="pb_good",
    )
    registry_path = tmp_path / "registry.json"
    event_path = tmp_path / "parameter_bundle_events.jsonl"

    result = rollback_bundle_lifecycle(
        registry=registry,
        registry_path=registry_path,
        event_ledger_path=event_path,
        event_ts="2026-06-16T13:30:00+09:00",
        rollback_bundle_id="pb_good",
        target_stage="live",
        reason="Rollback after decision review.",
        approved_by="human",
        source_decision_ids=("dec_bad_001",),
    )

    rows = read_parameter_bundle_events_jsonl(event_path)

    assert result.registry.active_live_bundle_id == "pb_good"
    assert result.registry.last_known_good_bundle_id == "pb_good"
    assert result.registry.rollback_bundle_id == "pb_bad"
    assert rows[0].event_type == ParameterBundleEventType.BUNDLE_ROLLBACK
    assert rows[0].previous_bundle_id == "pb_bad"
    assert rows[0].new_bundle_id == "pb_good"
    assert rows[0].source_decision_ids == ("dec_bad_001",)


def test_retire_bundle_lifecycle_records_retired_id_once(tmp_path) -> None:
    registry = initial_bundle_registry()
    registry_path = tmp_path / "registry.json"
    event_path = tmp_path / "parameter_bundle_events.jsonl"

    first = retire_bundle_lifecycle(
        registry=registry,
        registry_path=registry_path,
        event_ledger_path=event_path,
        event_ts="2026-06-16T14:00:00+09:00",
        parameter_bundle_id="pb_retired",
        reason="Retire old bundle.",
        approved_by="human",
    )
    second = retire_bundle_lifecycle(
        registry=first.registry,
        registry_path=registry_path,
        event_ledger_path=event_path,
        event_ts="2026-06-16T14:05:00+09:00",
        parameter_bundle_id="pb_retired",
        reason="Retire old bundle again.",
        approved_by="human",
    )

    rows = read_parameter_bundle_events_jsonl(event_path)

    assert second.registry.retired_bundle_ids == ("pb_retired",)
    assert len(rows) == 2
    assert rows[-1].event_type == ParameterBundleEventType.BUNDLE_RETIRED
