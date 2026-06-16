# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_runtime_cli.py
# desc: Guards one-shot parameter bundle runtime CLI. No broker execution.

from __future__ import annotations

import json

from btcts.apps.autotrade_parameter_bundle_runtime_once import main
from btcts.autotrade.config.bundle_events import read_parameter_bundle_events_jsonl


def _read_stdout_json(capsys):
    captured = capsys.readouterr()
    return json.loads(captured.out)


def test_cli_init_default_writes_bundle_registry_and_event(tmp_path, capsys) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    event_path = tmp_path / "parameter_sets" / "parameter_bundle_events.jsonl"

    exit_code = main(
        [
            "init-default",
            "--event-ts",
            "2026-06-16T17:00:00+09:00",
            "--reason",
            "Initialize from CLI.",
            "--created-by",
            "human_gpt",
            "--registry-path",
            str(registry_path),
            "--event-ledger-path",
            str(event_path),
            "--source-decision-ids",
            "dec_cli_init_001,dec_cli_init_002",
            "--gpt-review-ids",
            "gpt_cli_init_001",
            "--human-approval-id",
            "approval_cli_init_001",
        ]
    )

    data = _read_stdout_json(capsys)
    events = read_parameter_bundle_events_jsonl(event_path)

    assert exit_code == 0
    assert data["ok"] is True
    assert data["would_send_to_broker"] is False
    assert data["bundle_written"] is True
    assert data["registry_written"] is True
    assert data["event_appended"] is True
    assert registry_path.exists()
    assert event_path.exists()
    assert events[0].event_type.value == "bundle_created"
    assert events[0].source_decision_ids == ("dec_cli_init_001", "dec_cli_init_002")
    assert events[0].gpt_review_ids == ("gpt_cli_init_001",)
    assert events[0].human_approval_id == "approval_cli_init_001"


def test_cli_activate_shadow_reads_existing_registry_and_appends_event(tmp_path, capsys) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    event_path = tmp_path / "parameter_sets" / "parameter_bundle_events.jsonl"

    assert main(
        [
            "init-default",
            "--event-ts",
            "2026-06-16T17:00:00+09:00",
            "--reason",
            "Initialize from CLI.",
            "--created-by",
            "human_gpt",
            "--registry-path",
            str(registry_path),
            "--event-ledger-path",
            str(event_path),
        ]
    ) == 0
    capsys.readouterr()

    exit_code = main(
        [
            "activate-shadow",
            "--event-ts",
            "2026-06-16T17:30:00+09:00",
            "--bundle-id",
            "pb_cli_shadow_candidate",
            "--reason",
            "Activate shadow candidate from CLI.",
            "--approved-by",
            "human",
            "--registry-path",
            str(registry_path),
            "--event-ledger-path",
            str(event_path),
            "--source-decision-ids",
            "dec_cli_shadow",
        ]
    )

    data = _read_stdout_json(capsys)
    events = read_parameter_bundle_events_jsonl(event_path)

    assert exit_code == 0
    assert data["registry"]["active_shadow_bundle_id"] == "pb_cli_shadow_candidate"
    assert events[-1].event_type.value == "bundle_activated_shadow"
    assert events[-1].new_bundle_id == "pb_cli_shadow_candidate"
    assert events[-1].source_decision_ids == ("dec_cli_shadow",)


def test_cli_activate_live_sets_last_known_good(tmp_path, capsys) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    event_path = tmp_path / "parameter_sets" / "parameter_bundle_events.jsonl"

    exit_code = main(
        [
            "activate-live",
            "--event-ts",
            "2026-06-16T18:00:00+09:00",
            "--bundle-id",
            "pb_cli_live",
            "--reason",
            "Activate live candidate from CLI.",
            "--approved-by",
            "human",
            "--registry-path",
            str(registry_path),
            "--event-ledger-path",
            str(event_path),
        ]
    )

    data = _read_stdout_json(capsys)

    assert exit_code == 0
    assert data["registry"]["active_live_bundle_id"] == "pb_cli_live"
    assert data["registry"]["last_known_good_bundle_id"] == "pb_cli_live"
    assert data["event"]["event_type"] == "bundle_activated_live"


def test_cli_rollback_live_restores_target_bundle(tmp_path, capsys) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    event_path = tmp_path / "parameter_sets" / "parameter_bundle_events.jsonl"

    assert main(
        [
            "activate-live",
            "--event-ts",
            "2026-06-16T18:00:00+09:00",
            "--bundle-id",
            "pb_bad",
            "--reason",
            "Activate bad live candidate.",
            "--approved-by",
            "human",
            "--registry-path",
            str(registry_path),
            "--event-ledger-path",
            str(event_path),
        ]
    ) == 0
    capsys.readouterr()

    exit_code = main(
        [
            "rollback",
            "--event-ts",
            "2026-06-16T18:30:00+09:00",
            "--rollback-bundle-id",
            "pb_good",
            "--target-stage",
            "live",
            "--reason",
            "Rollback via CLI.",
            "--approved-by",
            "human",
            "--registry-path",
            str(registry_path),
            "--event-ledger-path",
            str(event_path),
            "--source-decision-ids",
            "dec_bad_cli",
        ]
    )

    data = _read_stdout_json(capsys)
    events = read_parameter_bundle_events_jsonl(event_path)

    assert exit_code == 0
    assert data["registry"]["active_live_bundle_id"] == "pb_good"
    assert data["registry"]["rollback_bundle_id"] == "pb_bad"
    assert events[-1].event_type.value == "bundle_rollback"
    assert events[-1].previous_bundle_id == "pb_bad"
    assert events[-1].new_bundle_id == "pb_good"
    assert events[-1].source_decision_ids == ("dec_bad_cli",)
