# path: ./btcts_next/src/btcts/apps/operator_ui/health_audit_read_model.py
# desc: Bounded audit input boundary for Operator UI Health read services.

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from btcts.core import io
from btcts.core import paths as core_paths

HEALTH_AUDIT_READ_MODEL_VERSION = "health_audit_read_model.v1"


@dataclass(frozen=True)
class HealthAuditInput:
    """Bounded audit rows plus read metadata for Health service builders."""

    range_key: str
    max_lines: int
    rows: list[dict[str, Any]]
    source_kind: str = "health_audit_read_model"
    version: str = HEALTH_AUDIT_READ_MODEL_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_kind": self.source_kind,
            "version": self.version,
            "range_key": self.range_key,
            "max_lines": self.max_lines,
            "row_count": len(self.rows),
            "rows": list(self.rows),
            "bounded_input_only": True,
        }


def audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


HEALTH_AUDIT_MAX_LINES_BY_RANGE = {
    "1h": 12000,
    "24h": 36000,
    "1w": 72000,
}
HEALTH_AUDIT_DEFAULT_MAX_LINES = HEALTH_AUDIT_MAX_LINES_BY_RANGE["1h"]


def audit_max_lines_for_range(range_key: str) -> int:
    return int(
        HEALTH_AUDIT_MAX_LINES_BY_RANGE.get(
            str(range_key or "").strip(),
            HEALTH_AUDIT_DEFAULT_MAX_LINES,
        )
    )


def read_recent_audit_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    return io.read_jsonl_tail(audit_log_path(), max_lines=max_lines)


def build_health_audit_input(
    *,
    range_key: str,
    read_recent_rows: Callable[..., list[dict[str, Any]]] | None = None,
    max_lines_for_range: Callable[[str], int] | None = None,
) -> HealthAuditInput:
    """Build the single bounded audit input used by a Health snapshot.

    This boundary owns audit-tail IO and sizing. It intentionally does not
    classify rows, build charts, compose snapshots, call Streamlit, scan data
    roots, or mutate runtime state.  Optional callables preserve legacy tests
    that monkeypatch health_data_service._read_recent_audit_rows.
    """
    resolved_max_lines_for_range = max_lines_for_range or audit_max_lines_for_range
    resolved_read_recent_rows = read_recent_rows or read_recent_audit_rows
    max_lines = int(resolved_max_lines_for_range(range_key))
    rows = list(resolved_read_recent_rows(max_lines=max_lines))
    return HealthAuditInput(
        range_key=range_key,
        max_lines=max_lines,
        rows=rows,
    )
