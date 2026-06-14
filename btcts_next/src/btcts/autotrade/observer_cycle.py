# path: ./btcts_next/src/btcts/autotrade/observer_cycle.py
# desc: Bounded AutoTrade observer cycle runner. Shadow decision + forecast outcome resolution only.

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from btcts.autotrade.mode_runtime_gate import ModeRuntimeGate, build_mode_runtime_gate
from btcts.autotrade.ledger import (
    ForecastOutcomeResolutionResult,
    ObserverRunRecord,
    append_observer_run_record,
    default_forecast_outcome_ledger_path,
    default_observer_run_ledger_path,
    resolve_due_shadow_forecast_outcomes,
)
from btcts.autotrade.live_shadow import default_shadow_decision_ledger_path
from btcts.autotrade.shadow_cycle import MAX_BOUNDED_SHADOW_CYCLES, ShadowCycleOnceResult, run_shadow_cycle_once


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return f"obs_run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class ObserverCycleOnceResult:
    cycle_kind: str
    shadow: ShadowCycleOnceResult
    forecast_resolution: ForecastOutcomeResolutionResult
    mode_runtime_gate: ModeRuntimeGate | None = None
    would_send_to_broker: bool = False
    loop_started: bool = False

    @property
    def appended_shadow_decision(self) -> bool:
        return self.shadow.appended

    @property
    def appended_forecast_outcomes(self) -> int:
        return int(self.forecast_resolution.appended_count)

    @property
    def snapshot_id(self) -> str | None:
        return self.shadow.result.snapshot_id

    @property
    def blocked_by(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tuple(self.shadow.blocked_by) + tuple(self.forecast_resolution.blocked_by)))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["shadow"] = self.shadow.to_dict()
        data["forecast_resolution"] = self.forecast_resolution.to_dict()
        data["mode_runtime_gate"] = self.mode_runtime_gate.to_dict() if self.mode_runtime_gate is not None else None
        data["snapshot_id"] = self.snapshot_id
        data["appended_shadow_decision"] = self.appended_shadow_decision
        data["appended_forecast_outcomes"] = self.appended_forecast_outcomes
        data["blocked_by"] = list(self.blocked_by)
        return data


@dataclass(frozen=True)
class ObserverCycleBoundedResult:
    cycle_kind: str
    requested_cycles: int
    completed_cycles: int
    appended_shadow_decision_count: int
    appended_forecast_outcome_count: int
    duplicate_snapshot_skipped_count: int
    results: Tuple[ObserverCycleOnceResult, ...]
    run_id: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    observer_run_record_appended: bool = False
    observer_run_ledger_path: str | None = None
    would_send_to_broker: bool = False
    loop_started: bool = True
    bounded: bool = True
    skip_duplicate_snapshot: bool = True

    @property
    def blocked_by(self) -> tuple[str, ...]:
        blocked: list[str] = []
        for item in self.results:
            blocked.extend(item.blocked_by)
        return tuple(dict.fromkeys(blocked))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["results"] = [item.to_dict() for item in self.results]
        data["blocked_by"] = list(self.blocked_by)
        return data


def _validate_observer_cycle_args(*, max_cycles: int, interval_sec: float) -> None:
    if max_cycles < 1:
        raise ValueError("max_cycles must be >= 1")
    if max_cycles > MAX_BOUNDED_SHADOW_CYCLES:
        raise ValueError(f"max_cycles must be <= {MAX_BOUNDED_SHADOW_CYCLES}")
    if interval_sec < 0:
        raise ValueError("interval_sec must be >= 0")



def _blocked_forecast_resolution(gate: ModeRuntimeGate) -> ForecastOutcomeResolutionResult:
    blocked = tuple(dict.fromkeys(tuple(gate.blocked_by) + ("mode_runtime_gate_blocked_forecast_outcome_resolution",)))
    return ForecastOutcomeResolutionResult(
        shadow_decision_path=default_shadow_decision_ledger_path(ensure=False),
        outcome_ledger_path=default_forecast_outcome_ledger_path(ensure=False),
        actual_snapshot_id=None,
        actual_ground_direction=None,
        due_count=0,
        appended_count=0,
        duplicate_skipped_count=0,
        unresolved_count=0,
        blocked_by=blocked,
        records=(),
        would_send_to_broker=False,
        read_only_inputs=True,
    )

def run_observer_cycle_once(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
    persist: bool = True,
    max_decision_lines: int | None = 1000,
    max_actual_match_age_sec: float = 45.0,
) -> ObserverCycleOnceResult:
    gate = build_mode_runtime_gate()
    shadow = run_shadow_cycle_once(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
        persist=bool(persist and gate.allow_shadow_decision_append),
    )
    if gate.allow_forecast_outcome_resolution:
        forecast_resolution = resolve_due_shadow_forecast_outcomes(
            exchange=exchange,
            symbol_raw=symbol_raw,
            state_type=state_type,
            persist=persist,
            max_decision_lines=max_decision_lines,
            max_actual_match_age_sec=max_actual_match_age_sec,
        )
    else:
        forecast_resolution = _blocked_forecast_resolution(gate)
    return ObserverCycleOnceResult(
        cycle_kind="autotrade.observer_cycle_once",
        shadow=shadow,
        forecast_resolution=forecast_resolution,
        mode_runtime_gate=gate,
        would_send_to_broker=False,
        loop_started=False,
    )


def run_observer_cycle_bounded(
    *,
    max_cycles: int,
    interval_sec: float = 0.0,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
    persist: bool = True,
    max_decision_lines: int | None = 1000,
    max_actual_match_age_sec: float = 45.0,
    skip_duplicate_snapshot: bool = True,
    persist_run_record: bool = True,
) -> ObserverCycleBoundedResult:
    _validate_observer_cycle_args(max_cycles=max_cycles, interval_sec=interval_sec)
    started_at = _utc_now()
    run_id = _run_id()
    results: list[ObserverCycleOnceResult] = []
    last_snapshot_id: str | None = None
    duplicate_snapshot_skipped = 0

    for index in range(max_cycles):
        probe = run_shadow_cycle_once(
            exchange=exchange,
            symbol_raw=symbol_raw,
            state_type=state_type,
            persist=False,
        )
        snapshot_id = probe.result.snapshot_id
        duplicate = bool(skip_duplicate_snapshot and snapshot_id is not None and snapshot_id == last_snapshot_id)
        should_persist_shadow_and_outcomes = bool(persist and not duplicate)
        if persist and duplicate:
            duplicate_snapshot_skipped += 1

        item = run_observer_cycle_once(
            exchange=exchange,
            symbol_raw=symbol_raw,
            state_type=state_type,
            persist=should_persist_shadow_and_outcomes,
            max_decision_lines=max_decision_lines,
            max_actual_match_age_sec=max_actual_match_age_sec,
        )
        results.append(item)
        if snapshot_id is not None:
            last_snapshot_id = snapshot_id
        if index + 1 < max_cycles and interval_sec > 0:
            time.sleep(interval_sec)

    finished_at = _utc_now()
    appended_shadow = sum(1 for item in results if item.appended_shadow_decision)
    appended_outcomes = sum(item.appended_forecast_outcomes for item in results)
    partial = ObserverCycleBoundedResult(
        cycle_kind="autotrade.observer_cycle_bounded",
        requested_cycles=max_cycles,
        completed_cycles=len(results),
        appended_shadow_decision_count=appended_shadow,
        appended_forecast_outcome_count=appended_outcomes,
        duplicate_snapshot_skipped_count=duplicate_snapshot_skipped,
        results=tuple(results),
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        observer_run_record_appended=False,
        observer_run_ledger_path=str(default_observer_run_ledger_path(ensure=False)),
        would_send_to_broker=False,
        loop_started=True,
        bounded=True,
        skip_duplicate_snapshot=skip_duplicate_snapshot,
    )
    observer_run_record_appended = False
    ledger_path = default_observer_run_ledger_path(ensure=persist_run_record)
    if persist_run_record:
        record = ObserverRunRecord(
            run_id=run_id,
            started_at=started_at,
            finished_at=finished_at,
            requested_cycles=max_cycles,
            completed_cycles=len(results),
            appended_shadow_decision_count=appended_shadow,
            appended_forecast_outcome_count=appended_outcomes,
            duplicate_snapshot_skipped_count=duplicate_snapshot_skipped,
            skip_duplicate_snapshot=skip_duplicate_snapshot,
            blocked_by=partial.blocked_by,
            would_send_to_broker=False,
            bounded=True,
        )
        append_observer_run_record(ledger_path, record)
        observer_run_record_appended = True
    return ObserverCycleBoundedResult(
        cycle_kind=partial.cycle_kind,
        requested_cycles=partial.requested_cycles,
        completed_cycles=partial.completed_cycles,
        appended_shadow_decision_count=partial.appended_shadow_decision_count,
        appended_forecast_outcome_count=partial.appended_forecast_outcome_count,
        duplicate_snapshot_skipped_count=partial.duplicate_snapshot_skipped_count,
        results=partial.results,
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        observer_run_record_appended=observer_run_record_appended,
        observer_run_ledger_path=str(ledger_path),
        would_send_to_broker=False,
        loop_started=True,
        bounded=True,
        skip_duplicate_snapshot=skip_duplicate_snapshot,
    )
