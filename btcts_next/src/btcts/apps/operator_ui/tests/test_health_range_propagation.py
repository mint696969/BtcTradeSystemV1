# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_range_propagation.py
# desc: Verifies selected Health ranges propagate through data and view layers.

from __future__ import annotations

from btcts.apps.operator_ui import health_data_service


def test_health_audit_wrapper_propagates_selected_range(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_reader(*, max_lines: int, range_key: str):
        captured["max_lines"] = max_lines
        captured["range_key"] = range_key
        return []

    monkeypatch.setattr(
        health_data_service,
        "_read_recent_audit_rows_impl",
        fake_reader,
    )

    rows = health_data_service._read_recent_audit_rows(
        max_lines=72000,
        range_key="1w",
    )

    assert rows == []
    assert captured == {"max_lines": 72000, "range_key": "1w"}


def test_load_health_audit_input_does_not_fall_back_to_one_hour(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_reader(*, max_lines: int, range_key: str):
        captured["max_lines"] = max_lines
        captured["range_key"] = range_key
        return [
            {
                "ts": "2026-07-10T00:00:00Z",
                "event": "collector_vnext.unified.rest_trades.completed",
                "payload": {"health_event_count": 1},
            }
        ]

    monkeypatch.setattr(
        health_data_service,
        "_read_recent_audit_rows_impl",
        fake_reader,
    )

    result = health_data_service.load_health_audit_input(range_key="24h")

    assert result.range_key == "24h"
    assert captured["range_key"] == "24h"
    assert captured["max_lines"] == 36000
    assert len(result.rows) == 1
