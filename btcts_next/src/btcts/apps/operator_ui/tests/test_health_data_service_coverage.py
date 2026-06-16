# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_coverage.py
# desc: Verify health audit-backed series exposes coverage metadata when audit tail does not cover the requested window.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.health_data_service as svc  # noqa: E402


def main() -> int:
    original_range_config = svc.range_config
    original_time_buckets = svc.time_buckets
    original_display_buckets = svc.display_buckets
    original_read_recent_audit_rows = svc._read_recent_audit_rows

    try:
        svc.range_config = lambda range_key: {
            "window_minutes": 60,
            "bucket_minutes": 1,
        }
        buckets = [
            svc.parse_ts("2026-04-15T01:00:00Z"),
            svc.parse_ts("2026-04-15T01:01:00Z"),
            svc.parse_ts("2026-04-15T01:02:00Z"),
        ]
        svc.time_buckets = lambda window_minutes, bucket_minutes: list(buckets)
        svc.display_buckets = lambda items, include_in_progress=False: list(items[:-1])

        svc._read_recent_audit_rows = lambda max_lines=4000: [
            {
                "ts": "2026-04-15T01:01:10Z",
                "event": "collector_vnext.unified.ws_board.message",
                "payload": {},
            },
            {
                "ts": "2026-04-15T01:01:20Z",
                "event": "collector_vnext.unified.ws_executions.message",
                "payload": {},
            },
        ]

        rows = svc.build_recent_api_ws_series(range_key="1h")
        assert len(rows) == 2
        assert rows[-1]["coverage_complete"] is False
        assert rows[-1]["coverage_warning"] == "audit_tail_did_not_cover_full_window"
        assert rows[-1]["coverage_window_start_ts"] == "2026-04-15T01:00:00Z"
        assert rows[-1]["coverage_oldest_available_ts"] == "2026-04-15T01:01:10Z"

        rail = svc.build_ws_continuity_rail(range_key="1h")
        assert rail
        first_cell = rail[0]["cells"][0]
        assert first_cell["coverage_complete"] is False
        assert first_cell["coverage_warning"] == "audit_tail_did_not_cover_full_window"
        assert first_cell["coverage_window_start_ts"] == "2026-04-15T01:00:00Z"
        assert first_cell["coverage_oldest_available_ts"] == "2026-04-15T01:01:10Z"
    finally:
        svc.range_config = original_range_config
        svc.time_buckets = original_time_buckets
        svc.display_buckets = original_display_buckets
        svc._read_recent_audit_rows = original_read_recent_audit_rows

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())