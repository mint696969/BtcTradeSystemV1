# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_telemetry_rollup.py
# desc: Verifies D-hot Health telemetry rollup, caching, and incremental updates.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from btcts.apps.operator_ui.health_telemetry_rollup import (
    build_health_telemetry_rows,
    update_daily_rollup,
)


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_rollup_reads_all_required_ranges_and_preserves_counts(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    _write_rows(
        path,
        [
            {
                "ts": "2026-07-14T00:10:01Z",
                "event": "collector_vnext.unified.board_snapshot.completed",
            },
            {
                "ts": "2026-07-14T00:10:20Z",
                "event": "collector_vnext.unified.board_snapshot.completed",
            },
            {
                "ts": "2026-07-14T00:11:00Z",
                "event": "collector_vnext.unified.ws_board.message.received",
            },
        ],
    )

    rows = build_health_telemetry_rows(
        range_key="24h",
        logs_root=logs_root,
        cache_root=cache_root,
        now=datetime(2026, 7, 14, 1, 0, tzinfo=timezone.utc),
    )

    board = [row for row in rows if row.get("event") == "collector_vnext.unified.board_snapshot.completed"]
    assert len(board) == 1
    assert board[0]["payload"]["health_event_count"] == 2
    assert any(row.get("event") == "collector_vnext.unified.ws_board.message.received" for row in rows)


def test_rollup_updates_incrementally_without_double_count(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    first = {
        "ts": "2026-07-14T00:10:01Z",
        "event": "collector_vnext.unified.rest_trades.completed",
    }
    _write_rows(path, [first])
    update_daily_rollup(date_key="2026-07-14", logs_root=logs_root, cache_root=cache_root)
    update_daily_rollup(date_key="2026-07-14", logs_root=logs_root, cache_root=cache_root)

    second = {
        "ts": "2026-07-14T00:10:30Z",
        "event": "collector_vnext.unified.rest_trades.completed",
    }
    _write_rows(path, [second])
    payload = update_daily_rollup(
        date_key="2026-07-14",
        logs_root=logs_root,
        cache_root=cache_root,
    )

    minute = payload["minutes"]["2026-07-14T00:10:00Z"]
    assert minute["collector_vnext.unified.rest_trades.completed"] == 2


def test_one_week_reads_eight_utc_date_partitions_when_window_crosses_dates(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    for day in range(7, 15):
        path = logs_root / f"telemetry/collector_vnext/date=2026-07-{day:02d}/part-00001.jsonl"
        _write_rows(
            path,
            [
                {
                    "ts": f"2026-07-{day:02d}T12:00:00Z",
                    "event": "collector_vnext.unified.ws_executions.message.received",
                }
            ],
        )

    rows = build_health_telemetry_rows(
        range_key="1w",
        logs_root=logs_root,
        cache_root=cache_root,
        now=datetime(2026, 7, 14, 13, 0, tzinfo=timezone.utc),
    )
    execution_rows = [
        row
        for row in rows
        if row.get("event") == "collector_vnext.unified.ws_executions.message.received"
    ]
    assert len(execution_rows) == 7


def test_default_cache_root_is_project_tmp_not_btcts_next_tmp() -> None:
    from btcts.apps.operator_ui.health_telemetry_rollup import default_cache_root

    root = default_cache_root()
    assert root.parts[-3:] == ("tmp", "operator_ui", "health_rollup")
    assert root.parent.parent.parent.name == "BtcTradeSystem"


def test_explicit_logs_root_is_used_without_fallback(tmp_path: Path) -> None:
    from btcts.apps.operator_ui.health_telemetry_rollup import resolve_logs_root

    explicit = tmp_path / "logs"
    assert resolve_logs_root(explicit) == explicit

def test_unchanged_rollup_does_not_rewrite_cache(
    monkeypatch, tmp_path: Path
) -> None:
    from btcts.apps.operator_ui import health_telemetry_rollup as rollup

    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    _write_rows(
        path,
        [
            {
                "ts": "2026-07-14T00:10:01Z",
                "event": "collector_vnext.unified.rest_trades.completed",
            }
        ],
    )

    rollup.update_daily_rollup(
        date_key="2026-07-14",
        logs_root=logs_root,
        cache_root=cache_root,
    )

    writes: list[Path] = []
    original_write = rollup._write_cache

    def spy_write(path: Path, payload: dict) -> None:
        writes.append(path)
        original_write(path, payload)

    monkeypatch.setattr(rollup, "_write_cache", spy_write)

    rollup.update_daily_rollup(
        date_key="2026-07-14",
        logs_root=logs_root,
        cache_root=cache_root,
    )

    assert writes == []


def test_appended_telemetry_rewrites_cache_once(
    monkeypatch, tmp_path: Path
) -> None:
    from btcts.apps.operator_ui import health_telemetry_rollup as rollup

    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    _write_rows(
        path,
        [
            {
                "ts": "2026-07-14T00:10:01Z",
                "event": "collector_vnext.unified.rest_trades.completed",
            }
        ],
    )
    rollup.update_daily_rollup(
        date_key="2026-07-14",
        logs_root=logs_root,
        cache_root=cache_root,
    )

    writes: list[Path] = []
    original_write = rollup._write_cache

    def spy_write(path: Path, payload: dict) -> None:
        writes.append(path)
        original_write(path, payload)

    monkeypatch.setattr(rollup, "_write_cache", spy_write)
    _write_rows(
        path,
        [
            {
                "ts": "2026-07-14T00:10:30Z",
                "event": "collector_vnext.unified.rest_trades.completed",
            }
        ],
    )

    payload = rollup.update_daily_rollup(
        date_key="2026-07-14",
        logs_root=logs_root,
        cache_root=cache_root,
    )

    assert len(writes) == 1
    minute = payload["minutes"]["2026-07-14T00:10:00Z"]
    assert minute["collector_vnext.unified.rest_trades.completed"] == 2

def test_resolve_logs_root_prefers_d_hot_over_configured_cold(
    monkeypatch, tmp_path: Path
) -> None:
    from btcts.apps.operator_ui import health_telemetry_rollup as rollup

    hot_logs = tmp_path / "hot_logs"
    cold_logs = tmp_path / "cold_logs"
    (hot_logs / "telemetry/collector_vnext").mkdir(parents=True)
    (cold_logs / "telemetry/collector_vnext").mkdir(parents=True)

    monkeypatch.setattr(rollup, "HOT_LOGS_ROOT", hot_logs)
    monkeypatch.setattr(rollup.core_paths, "logs_dir", lambda ensure=False: cold_logs)

    assert rollup.resolve_logs_root() == hot_logs


def test_explicit_logs_root_still_wins_over_d_hot(
    monkeypatch, tmp_path: Path
) -> None:
    from btcts.apps.operator_ui import health_telemetry_rollup as rollup

    explicit = tmp_path / "explicit"
    hot_logs = tmp_path / "hot_logs"
    (hot_logs / "telemetry/collector_vnext").mkdir(parents=True)
    monkeypatch.setattr(rollup, "HOT_LOGS_ROOT", hot_logs)

    assert rollup.resolve_logs_root(explicit) == explicit


def test_cache_is_rebuilt_when_source_logs_root_changes(tmp_path: Path) -> None:
    from btcts.apps.operator_ui.health_telemetry_rollup import update_daily_rollup

    first_logs = tmp_path / "first_logs"
    second_logs = tmp_path / "second_logs"
    cache_root = tmp_path / "cache"

    first_path = first_logs / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    second_path = second_logs / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"

    _write_rows(
        first_path,
        [{
            "ts": "2026-07-14T00:10:01Z",
            "event": "collector_vnext.unified.rest_trades.completed",
        }],
    )
    _write_rows(
        second_path,
        [{
            "ts": "2026-07-14T00:20:01Z",
            "event": "collector_vnext.unified.ws_board.message.received",
        }],
    )

    update_daily_rollup(
        date_key="2026-07-14",
        logs_root=first_logs,
        cache_root=cache_root,
    )
    payload = update_daily_rollup(
        date_key="2026-07-14",
        logs_root=second_logs,
        cache_root=cache_root,
    )

    assert payload["source_logs_root"] == str(second_logs)
    assert "2026-07-14T00:10:00Z" not in payload["minutes"]
    assert payload["minutes"]["2026-07-14T00:20:00Z"][
        "collector_vnext.unified.ws_board.message.received"
    ] == 1
