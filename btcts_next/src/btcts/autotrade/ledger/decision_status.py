# path: ./btcts_next/src/btcts/autotrade/ledger/decision_status.py
# desc: Read-only status/read-model helpers for AutoTrade shadow decision ledger.

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.runtime_paths import decision_ledger_path


@dataclass(frozen=True)
class ShadowDecisionLedgerReadResult:
    path: Path
    rows: Tuple[Dict[str, Any], ...]
    skipped_count: int = 0
    error_samples: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


@dataclass(frozen=True)
class ShadowDecisionLedgerSummary:
    path: Path
    exists: bool
    total_rows: int
    skipped_rows: int
    latest_decision_id: str | None = None
    latest_snapshot_id: str | None = None
    latest_forecast_id: str | None = None
    latest_action: str | None = None
    latest_forecast_direction: str | None = None
    latest_forecast_confidence: str | None = None
    latest_risk_allowed: bool | None = None
    latest_executable: bool | None = None
    action_counts: Dict[str, int] = field(default_factory=dict)
    forecast_confidence_counts: Dict[str, int] = field(default_factory=dict)
    blocked_by_counts: Dict[str, int] = field(default_factory=dict)
    reason_code_counts: Dict[str, int] = field(default_factory=dict)
    error_samples: Tuple[str, ...] = ()
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def default_shadow_decision_status_path(*, ensure: bool = False) -> Path:
    return decision_ledger_path("shadow_decisions.jsonl", ensure=ensure)


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


def read_shadow_decision_rows(path: Path | None = None, *, max_lines: int | None = 1000) -> ShadowDecisionLedgerReadResult:
    target = path or default_shadow_decision_status_path(ensure=False)
    rows: list[Dict[str, Any]] = []
    skipped = 0
    errors: list[str] = []
    for index, line in enumerate(_iter_recent_lines(target, max_lines=max_lines), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except Exception as exc:
            skipped += 1
            if len(errors) < 5:
                errors.append(f"line:{index}:{exc.__class__.__name__}")
            continue
        if isinstance(obj, dict):
            rows.append(obj)
        else:
            skipped += 1
            if len(errors) < 5:
                errors.append(f"line:{index}:not_object")
    return ShadowDecisionLedgerReadResult(
        path=target,
        rows=tuple(rows),
        skipped_count=skipped,
        error_samples=tuple(errors),
    )


def _count_list_values(rows: Tuple[Dict[str, Any], ...], key: str) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = row.get(key)
        if isinstance(value, list):
            counter.update(str(item) for item in value)
    return dict(counter)


def _action_counts(rows: Tuple[Dict[str, Any], ...]) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        action = row.get("final_action") or (row.get("candidate") or {}).get("action")
        if action:
            counter[str(action)] += 1
    return dict(counter)


def _forecast_confidence_counts(rows: Tuple[Dict[str, Any], ...]) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        forecast = row.get("forecast_5m") or {}
        confidence = forecast.get("confidence")
        if confidence:
            counter[str(confidence)] += 1
    return dict(counter)


def summarize_shadow_decision_ledger(path: Path | None = None, *, max_lines: int | None = 1000) -> ShadowDecisionLedgerSummary:
    read = read_shadow_decision_rows(path, max_lines=max_lines)
    rows = read.rows
    latest = rows[-1] if rows else {}
    latest_forecast = latest.get("forecast_5m") or {}
    latest_risk = latest.get("risk_gate") or {}
    return ShadowDecisionLedgerSummary(
        path=read.path,
        exists=read.path.exists(),
        total_rows=len(rows),
        skipped_rows=read.skipped_count,
        latest_decision_id=latest.get("decision_id"),
        latest_snapshot_id=latest.get("snapshot_id"),
        latest_forecast_id=latest.get("forecast_id"),
        latest_action=latest.get("final_action") or (latest.get("candidate") or {}).get("action"),
        latest_forecast_direction=latest_forecast.get("forecast_direction"),
        latest_forecast_confidence=latest_forecast.get("confidence"),
        latest_risk_allowed=latest_risk.get("allowed") if "allowed" in latest_risk else None,
        latest_executable=latest_risk.get("executable") if "executable" in latest_risk else None,
        action_counts=_action_counts(rows),
        forecast_confidence_counts=_forecast_confidence_counts(rows),
        blocked_by_counts=_count_list_values(rows, "blocked_by"),
        reason_code_counts=_count_list_values(rows, "reason_codes"),
        error_samples=read.error_samples,
        would_send_to_broker=False,
        read_only=True,
    )
