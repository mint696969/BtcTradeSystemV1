# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_runtime_store.py
# desc: Guards runtime store helpers for parameter bundle registry and event ledger.

from __future__ import annotations

import json

from btcts.autotrade.config.bundle_events import ParameterBundleEventType, read_parameter_bundle_events_jsonl
from btcts.autotrade.config.bundle_runtime_store import (
    activate_parameter_bundle_runtime,
    initialize_default_parameter_bundle_runtime,
    read_parameter_bundle_registry_or_default,
    rollback_parameter_bundle_runtime,
)
from btcts.autotrade.config.models import ParameterSetBundleRegistry
from btcts.autotrade.runtime_paths import parameter_bundle_event_ledger_path, parameter_registry_path


def test_initialize_default_parameter_bundle_runtime_writes_hot_runtime_files(monkeypatch, tmp_path) -> None:
    runtime_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(runtime_root))

    result = initialize_default_parameter_bundle_runtime(
        event_ts="2026-06-16T15:00:00+09:00",
        reason="Initialize runtime parameter bundle store.",
        created_by="human_gpt",
        source_decision_ids=("dec_runtime_init",),
        gpt_review_ids=("gpt_runtime_init",),
        human_approval_id="approval_runtime_init",
    )

    registry_path = parameter_registry_path(ensure=False)
    event_path = parameter_bundle_event_ledger_path(ensure=False)

    assert result.bundle_path is not None
    assert result.bundle_path.exists()
    assert result.bundle_path.parent.name == "bundles"
    assert registry_path.exists()
    assert event_path.exists()

    bundle_data = json.loads(result.bundle_path.read_text(encoding="utf-8"))
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
    events = read_parameter_bundle_events_jsonl(event_path)

    assert bundle_data["parameter_bundle_id"] == result.registry.active_shadow_bundle_id
    assert registry_data["active_shadow_bundle_id"] == result.registry.active_shadow_bundle_id
    assert events[0].event_type == ParameterBundleEventType.BUNDLE_CREATED
    assert events[0].source_decision_ids == ("dec_runtime_init",)
    assert str(runtime_root) in str(result.bundle_path)


def test_runtime_activation_reads_existing_registry_and_appends_event(monkeypatch, tmp_path) -> None:
    runtime_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(runtime_root))

    initialize_default_parameter_bundle_runtime(
        event_ts="2026-06-16T15:00:00+09:00",
        reason="Initialize runtime parameter bundle store.",
        created_by="human_gpt",
    )

    result = activate_parameter_bundle_runtime(
        event_type=ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW,
        event_ts="2026-06-16T15:30:00+09:00",
        new_bundle_id="pb_shadow_candidate",
        reason="Activate candidate shadow bundle.",
        approved_by="human",
        source_decision_ids=("dec_shadow_candidate",),
    )

    registry_path = parameter_registry_path(ensure=False)
    event_path = parameter_bundle_event_ledger_path(ensure=False)
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
    events = read_parameter_bundle_events_jsonl(event_path)

    assert result.registry.active_shadow_bundle_id == "pb_shadow_candidate"
    assert registry_data["active_shadow_bundle_id"] == "pb_shadow_candidate"
    assert len(events) == 2
    assert events[-1].event_type == ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW
    assert events[-1].new_bundle_id == "pb_shadow_candidate"
    assert events[-1].source_decision_ids == ("dec_shadow_candidate",)


def test_runtime_rollback_reads_existing_registry_and_restores_live(monkeypatch, tmp_path) -> None:
    runtime_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(runtime_root))

    registry_path = parameter_registry_path(ensure=True)
    event_path = parameter_bundle_event_ledger_path(ensure=True)
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "autotrade_parameter_bundle_registry.v1",
                "active_shadow_bundle_id": None,
                "active_paper_bundle_id": None,
                "active_live_bundle_id": "pb_bad",
                "last_known_good_bundle_id": "pb_bad",
                "rollback_bundle_id": "pb_good",
                "pending_draft_bundle_id": None,
                "retired_bundle_ids": [],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    result = rollback_parameter_bundle_runtime(
        event_ts="2026-06-16T16:00:00+09:00",
        rollback_bundle_id="pb_good",
        target_stage="live",
        reason="Rollback runtime live bundle.",
        approved_by="human",
        source_decision_ids=("dec_bad_runtime",),
    )

    registry = read_parameter_bundle_registry_or_default(registry_path)
    events = read_parameter_bundle_events_jsonl(event_path)

    assert result.registry.active_live_bundle_id == "pb_good"
    assert registry.active_live_bundle_id == "pb_good"
    assert registry.rollback_bundle_id == "pb_bad"
    assert events[-1].event_type == ParameterBundleEventType.BUNDLE_ROLLBACK
    assert events[-1].previous_bundle_id == "pb_bad"
    assert events[-1].new_bundle_id == "pb_good"


def test_read_parameter_bundle_registry_or_default_handles_missing_path(tmp_path) -> None:
    registry = read_parameter_bundle_registry_or_default(tmp_path / "missing.json")

    assert isinstance(registry, ParameterSetBundleRegistry)
    assert registry.active_shadow_bundle_id is None
