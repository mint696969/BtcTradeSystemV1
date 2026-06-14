# path: ./btcts_next/src/btcts/autotrade/ledger/observer_run_status.py
# desc: Append-only observer run ledger and read-only summary helpers.

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.runtime_paths import decision_ledger_path


@dataclass(frozen=True)
class ObserverRunRecord:
    run_id: str
    started_at: str
    finished_at: str
    requested_cycles: int
    completed_cycles: int
    appended_shadow_decision_count: int
    appended_forecast_outcome_count: int
    duplicate_snapshot_skipped_count: int
    skip_duplicate_snapshot: bool
    blocked_by: Tuple[str, ...]
    would_send_to_broker: bool = False
    bounded: bool = True
    source: str = "autotrade.observer_cycle_bounded"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ObserverRunLedgerSummary:
    path: Path
    exists: bool
    total_rows: int
    skipped_rows: int
    latest_run_id: str | None = None
    latest_started_at: str | None = None
    latest_finished_at: str | None = None
    latest_completed_cycles: int | None = None
    latest_appended_shadow_decision_count: int | None = None
    latest_appended_forecast_outcome_count: int | None = None
    latest_duplicate_snapshot_skipped_count: int | None = None
    latest_skip_duplicate_snapshot: bool | None = None
    latest_blocked_by: Tuple[str, ...] = ()
    latest_would_send_to_broker: bool | None = None
    latest_bounded: bool | None = None
    total_completed_cycles: int = 0
    total_appended_shadow_decision_count: int = 0
    total_appended_forecast_outcome_count: int = 0
    total_duplicate_snapshot_skipped_count: int = 0
    blocked_by_counts: Dict[str, int] = field(default_factory=dict)
    error_samples: Tuple[str, ...] = ()
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def default_observer_run_ledger_path(*, ensure: bool = True) -> Path:
    return decision_ledger_path("observer_runs.jsonl", ensure=ensure)


def append_observer_run_record(path: Path, record: ObserverRunRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + chr(10))


def _iter_recent_lines(path: Path, *, max_lines: int | None = None) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    if max_lines is not None and max_lines >= 0:
        return lines[-max_lines:]
    return lines


def read_observer_run_records(path: Path | None = None, *, max_lines: int | None = 1000) -> tuple[ObserverRunRecord, ...]:
    target = path or default_observer_run_ledger_path(ensure=False)
    rows: list[ObserverRunRecord] = []
    fields = ObserverRunRecord.__dataclass_fields__
    for line in _iter_recent_lines(target, max_lines=max_lines):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        try:
            data = {key: obj.get(key) for key in fields}
            data["blocked_by"] = tuple(data.get("blocked_by") or ())
            rows.append(ObserverRunRecord(**data))
        except Exception:
            continue
    return tuple(rows)


def summarize_observer_run_ledger(path: Path | None = None, *, max_lines: int | None = 1000) -> ObserverRunLedgerSummary:
    target = path or default_observer_run_ledger_path(ensure=False)
    rows = read_observer_run_records(target, max_lines=max_lines)
    skipped = 0
    errors: list[str] = []
    for index, line in enumerate(_iter_recent_lines(target, max_lines=max_lines), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            if not isinstance(obj, dict):
                raise ValueError("not_object")
            data = {key: obj.get(key) for key in ObserverRunRecord.__dataclass_fields__}
            data["blocked_by"] = tuple(data.get("blocked_by") or ())
            ObserverRunRecord(**data)
        except Exception as exc:
            skipped += 1
            if len(errors) < 5:
                errors.append(f"line:{index}:{exc.__class__.__name__}")
    latest = rows[-1] if rows else None
    blocked_counter: Counter[str] = Counter()
    for row in rows:
        blocked_counter.update(row.blocked_by)
    return ObserverRunLedgerSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(rows),
        skipped_rows=skipped,
        latest_run_id=latest.run_id if latest is not None else None,
        latest_started_at=latest.started_at if latest is not None else None,
        latest_finished_at=latest.finished_at if latest is not None else None,
        latest_completed_cycles=latest.completed_cycles if latest is not None else None,
        latest_appended_shadow_decision_count=latest.appended_shadow_decision_count if latest is not None else None,
        latest_appended_forecast_outcome_count=latest.appended_forecast_outcome_count if latest is not None else None,
        latest_duplicate_snapshot_skipped_count=latest.duplicate_snapshot_skipped_count if latest is not None else None,
        latest_skip_duplicate_snapshot=latest.skip_duplicate_snapshot if latest is not None else None,
        latest_blocked_by=latest.blocked_by if latest is not None else (),
        latest_would_send_to_broker=latest.would_send_to_broker if latest is not None else None,
        latest_bounded=latest.bounded if latest is not None else None,
        total_completed_cycles=sum(row.completed_cycles for row in rows),
        total_appended_shadow_decision_count=sum(row.appended_shadow_decision_count for row in rows),
        total_appended_forecast_outcome_count=sum(row.appended_forecast_outcome_count for row in rows),
        total_duplicate_snapshot_skipped_count=sum(row.duplicate_snapshot_skipped_count for row in rows),
        blocked_by_counts=dict(blocked_counter),
        error_samples=tuple(errors),
        would_send_to_broker=False,
        read_only=True,
    )
