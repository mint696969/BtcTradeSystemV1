# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_audit_read_model.py
# desc: Verify Health audit read-model boundary owns bounded audit input metadata and preserves injectable readers.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.health_audit_read_model import (  # noqa: E402
    HEALTH_AUDIT_READ_MODEL_VERSION,
    HealthAuditInput,
    audit_max_lines_for_range,
    build_health_audit_input,
)


def main() -> int:
    assert audit_max_lines_for_range("1h") == 12000
    assert audit_max_lines_for_range("24h") == 36000
    assert audit_max_lines_for_range("1w") == 72000
    assert audit_max_lines_for_range("unknown") == 12000

    calls: list[int] = []

    def fake_reader(*, max_lines: int = 4000) -> list[dict[str, object]]:
        calls.append(max_lines)
        return [
            {"ts": "2026-06-03T00:00:00Z", "event": "collector_vnext.unified.ws_board.message"},
            {"ts": "2026-06-03T00:00:01Z", "event": "collector_vnext.unified.rest.ok"},
        ]

    audit_input = build_health_audit_input(
        range_key="24h",
        read_recent_rows=fake_reader,
    )

    assert isinstance(audit_input, HealthAuditInput)
    assert calls == [36000]
    assert audit_input.range_key == "24h"
    assert audit_input.max_lines == 36000
    assert len(audit_input.rows) == 2

    payload = audit_input.as_dict()
    assert payload["source_kind"] == "health_audit_read_model"
    assert payload["version"] == HEALTH_AUDIT_READ_MODEL_VERSION
    assert payload["range_key"] == "24h"
    assert payload["max_lines"] == 36000
    assert payload["row_count"] == 2
    assert payload["bounded_input_only"] is True
    assert payload["rows"] == audit_input.rows
    assert payload["rows"] is not audit_input.rows

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
