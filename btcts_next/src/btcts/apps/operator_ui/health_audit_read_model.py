# path: ./btcts_next/src/btcts/apps/operator_ui/health_audit_read_model.py
# desc: Bounded health event input boundary for Operator UI Health read services. Backward-compatible name keeps audit callers working while including PS-Q19B telemetry.

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from btcts.core import io
from btcts.core import paths as core_paths
from btcts.core.sharded_jsonl import iter_jsonl_part_files

HEALTH_AUDIT_READ_MODEL_VERSION = "health_audit_read_model.v2.health_event_input"
HEALTH_TELEMETRY_STREAMS = ("collector_vnext",)
HEALTH_TELEMETRY_MAX_BYTES_PER_FILE = 32 * 1024 * 1024
HEALTH_TELEMETRY_MAX_DATE_PARTITIONS = 2


@dataclass(frozen=True)
class HealthAuditInput:
    """Bounded health-event rows plus read metadata for Health service builders.

    The public class name stays ``HealthAuditInput`` for compatibility with
    existing Health builders/tests. Since PS-Q19B, the actual row input is a
    merged health-event view: low-frequency audit rows plus high-frequency
    collector telemetry rows.
    """

    range_key: str
    max_lines: int
    rows: list[dict[str, Any]]
    source_kind: str = "health_audit_read_model"
    version: str = HEALTH_AUDIT_READ_MODEL_VERSION

    def as_dict(self) -> dict[str, Any]:
        source_counts: dict[str, int] = {}
        for row in self.rows:
            source = str(row.get("health_source_kind") or "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        return {
            "source_kind": self.source_kind,
            "version": self.version,
            "range_key": self.range_key,
            "max_lines": self.max_lines,
            "row_count": len(self.rows),
            "rows": list(self.rows),
            "bounded_input_only": True,
            "ps_q19b_health_event_input": True,
            "includes_telemetry": True,
            "source_counts": source_counts,
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


def telemetry_stream_root(stream: str) -> Path:
    safe_stream = str(stream or "collector_vnext").strip().replace("\\", "/").strip("/")
    safe_stream = safe_stream.replace("/", "_").replace(":", "_") or "collector_vnext"
    return core_paths.logs_dir(ensure=False) / "telemetry" / safe_stream


def telemetry_log_paths(
    *,
    stream: str = "collector_vnext",
    max_partitions: int = HEALTH_TELEMETRY_MAX_DATE_PARTITIONS,
) -> list[Path]:
    base = telemetry_stream_root(stream)
    if not base.exists() or not base.is_dir():
        return []

    date_dirs: list[Path] = []
    try:
        for child in base.iterdir():
            if child.is_dir() and child.name.startswith("date="):
                date_dirs.append(child)
    except Exception:
        return []

    date_dirs.sort(key=lambda p: p.name, reverse=True)
    out: list[Path] = []
    for date_dir in date_dirs[: max(1, int(max_partitions))]:
        out.extend(iter_jsonl_part_files(date_dir))
    return out


def _annotate_rows(
    rows: list[dict[str, Any]],
    *,
    source_kind: str,
    source_path: Path,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        item.setdefault("health_source_kind", source_kind)
        item.setdefault("health_source_path", str(source_path))
        out.append(item)
    return out


def _sort_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("ts") or ""), str(row.get("event") or ""))


def read_recent_audit_only_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    path = audit_log_path()
    return _annotate_rows(
        io.read_jsonl_tail(path, max_lines=max_lines),
        source_kind="audit_primary",
        source_path=path,
    )


def read_recent_telemetry_rows(
    *,
    max_lines: int = 4000,
    streams: tuple[str, ...] = HEALTH_TELEMETRY_STREAMS,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for stream in streams:
        for path in telemetry_log_paths(stream=stream):
            rows.extend(
                _annotate_rows(
                    io.read_jsonl_tail(
                        path,
                        max_lines=max_lines,
                        max_bytes=HEALTH_TELEMETRY_MAX_BYTES_PER_FILE,
                    ),
                    source_kind=f"telemetry_{stream}",
                    source_path=path,
                )
            )
    rows.sort(key=_sort_key)
    return rows


def read_recent_health_event_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    """Return bounded rows for Health timelines and continuity rails.

    Since PS-Q19B, high-frequency collector success events live under
    ``logs/telemetry`` instead of ``logs/audit.jsonl``. Health activity charts
    need those telemetry rows, while anomaly feeds still need audit WARN/ERROR
    rows.  This merged input preserves both without scanning full files.
    """
    rows: list[dict[str, Any]] = []
    rows.extend(read_recent_audit_only_rows(max_lines=max_lines))
    rows.extend(read_recent_telemetry_rows(max_lines=max_lines))
    rows.sort(key=_sort_key)
    return rows


def read_recent_audit_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    """Backward-compatible Health input reader.

    Existing callers still use the audit-oriented function name, but the Health
    event input now includes PS-Q19B telemetry rows as well as primary audit rows.
    """
    return read_recent_health_event_rows(max_lines=max_lines)


def build_health_audit_input(
    *,
    range_key: str,
    read_recent_rows: Callable[..., list[dict[str, Any]]] | None = None,
    max_lines_for_range: Callable[[str], int] | None = None,
) -> HealthAuditInput:
    """Build the single bounded health-event input used by a Health snapshot.

    This boundary owns audit/telemetry tail IO and sizing. It intentionally does
    not classify rows, build charts, compose snapshots, call Streamlit, scan data
    roots, or mutate runtime state. Optional callables preserve legacy tests that
    monkeypatch health_data_service._read_recent_audit_rows.
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
