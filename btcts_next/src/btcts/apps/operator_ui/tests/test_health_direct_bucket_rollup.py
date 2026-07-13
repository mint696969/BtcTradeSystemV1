# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_direct_bucket_rollup.py
# desc: Verifies direct telemetry bucket aggregation for Health ranges.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from btcts.apps.operator_ui.health_telemetry_rollup import build_health_telemetry_rows


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _activity_rows(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in rows
        if str(row.get("event") or "").startswith("collector_vnext.unified.")
    ]


def test_one_week_rollup_aggregates_directly_to_three_hour_buckets(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    _write_rows(
        path,
        [
            {
                "ts": "2026-07-14T00:01:00Z",
                "event": "collector_vnext.unified.rest_trades.completed",
            },
            {
                "ts": "2026-07-14T01:59:00Z",
                "event": "collector_vnext.unified.rest_trades.completed",
            },
            {
                "ts": "2026-07-14T02:30:00Z",
                "event": "collector_vnext.unified.ws_board.message.received",
            },
        ],
    )

    rows = build_health_telemetry_rows(
        range_key="1w",
        logs_root=logs_root,
        cache_root=cache_root,
        now=datetime(2026, 7, 14, 3, 0, tzinfo=timezone.utc),
    )
    activity = _activity_rows(rows)

    assert len(activity) == 2
    rest = next(row for row in activity if row["event"].endswith("rest_trades.completed"))
    ws = next(row for row in activity if row["event"].endswith("ws_board.message.received"))
    assert rest["ts"] == "2026-07-14T00:00:00Z"
    assert rest["payload"]["health_event_count"] == 2
    assert rest["payload"]["telemetry_rollup_bucket_minutes"] == 180
    assert rest["payload"]["telemetry_rollup_direct_bucket"] is True
    assert ws["ts"] == "2026-07-14T00:00:00Z"


def test_24h_rollup_uses_thirty_minute_buckets(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    _write_rows(
        path,
        [
            {
                "ts": "2026-07-14T00:01:00Z",
                "event": "collector_vnext.unified.board_snapshot.completed",
            },
            {
                "ts": "2026-07-14T00:29:59Z",
                "event": "collector_vnext.unified.board_snapshot.completed",
            },
            {
                "ts": "2026-07-14T00:30:00Z",
                "event": "collector_vnext.unified.board_snapshot.completed",
            },
        ],
    )

    rows = build_health_telemetry_rows(
        range_key="24h",
        logs_root=logs_root,
        cache_root=cache_root,
        now=datetime(2026, 7, 14, 1, 0, tzinfo=timezone.utc),
    )
    activity = _activity_rows(rows)

    assert len(activity) == 2
    assert [row["ts"] for row in activity] == [
        "2026-07-14T00:00:00Z",
        "2026-07-14T00:30:00Z",
    ]
    assert [row["payload"]["health_event_count"] for row in activity] == [2, 1]


def test_direct_bucket_rollup_preserves_total_event_count(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs"
    cache_root = tmp_path / "cache"
    path = logs_root / "telemetry/collector_vnext/date=2026-07-14/part-00001.jsonl"
    source_rows = [
        {
            "ts": f"2026-07-14T00:{minute:02d}:00Z",
            "event": "collector_vnext.unified.ws_executions.message.received",
        }
        for minute in range(60)
    ]
    _write_rows(path, source_rows)

    rows = build_health_telemetry_rows(
        range_key="1w",
        logs_root=logs_root,
        cache_root=cache_root,
        now=datetime(2026, 7, 14, 3, 0, tzinfo=timezone.utc),
    )
    activity = _activity_rows(rows)

    assert len(activity) == 1
    assert activity[0]["payload"]["health_event_count"] == 60
