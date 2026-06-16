# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_events.py
# desc: Guards parameter bundle event JSONL history for replayable parameter switching.

from __future__ import annotations

from btcts.autotrade.config import initial_parameter_bundle_v0_1
from btcts.autotrade.config.bundle_events import (
    ParameterBundleEventType,
    append_parameter_bundle_event_jsonl,
    build_bundle_activation_event,
    build_bundle_created_event,
    build_bundle_rollback_event,
    read_parameter_bundle_events_jsonl,
)
from btcts.autotrade.runtime_paths import parameter_bundle_event_ledger_path


def test_bundle_created_event_records_split_parameter_identity(tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    event = build_bundle_created_event(
        bundle=bundle,
        event_ts="2026-06-16T12:00:00+09:00",
        reason="Initial split regime/trade bundle.",
        created_by="human_gpt",
        source_decision_ids=("dec_001",),
        gpt_review_ids=("gpt_review_001",),
        human_approval_id="approval_001",
    )

    data = event.to_dict()
    assert data["schema_version"] == "autotrade_parameter_bundle_event.v1"
    assert data["event_type"] == "bundle_created"
    assert data["parameter_bundle_id"] == bundle.parameter_bundle_id
    assert data["regime_parameter_set_id"] == bundle.regime_parameter_set_id
    assert data["trade_parameter_set_id"] == bundle.trade_parameter_set_id
    assert data["source_decision_ids"] == ["dec_001"]
    assert data["gpt_review_ids"] == ["gpt_review_001"]
    assert data["human_approval_id"] == "approval_001"

    path = tmp_path / "parameter_bundle_events.jsonl"
    append_parameter_bundle_event_jsonl(path, event)
    rows = read_parameter_bundle_events_jsonl(path)

    assert len(rows) == 1
    assert rows[0].event_id == event.event_id
    assert rows[0].parameter_bundle_id == bundle.parameter_bundle_id
    assert rows[0].regime_parameter_set_id == bundle.regime_parameter_set_id
    assert rows[0].trade_parameter_set_id == bundle.trade_parameter_set_id


def test_activation_and_rollback_events_keep_previous_and_new_bundle_ids() -> None:
    activation = build_bundle_activation_event(
        event_type=ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW,
        event_ts="2026-06-16T12:30:00+09:00",
        previous_bundle_id="pb_old",
        new_bundle_id="pb_new",
        reason="Shadow evaluation approved.",
        approved_by="human",
    )

    assert activation.event_type == ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW
    assert activation.previous_bundle_id == "pb_old"
    assert activation.new_bundle_id == "pb_new"
    assert activation.parameter_bundle_id == "pb_new"

    rollback = build_bundle_rollback_event(
        event_ts="2026-06-16T13:00:00+09:00",
        previous_bundle_id="pb_new",
        rollback_bundle_id="pb_old",
        reason="Rollback after review.",
        approved_by="human",
    )

    assert rollback.event_type == ParameterBundleEventType.BUNDLE_ROLLBACK
    assert rollback.previous_bundle_id == "pb_new"
    assert rollback.new_bundle_id == "pb_old"
    assert rollback.parameter_bundle_id == "pb_old"


def test_parameter_bundle_event_ledger_path_uses_parameter_set_runtime_dir(monkeypatch, tmp_path) -> None:
    runtime_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(runtime_root))

    path = parameter_bundle_event_ledger_path(ensure=False)

    assert path.name == "parameter_bundle_events.jsonl"
    assert path.parent.name == "parameter_sets"
    assert str(runtime_root) in str(path)
