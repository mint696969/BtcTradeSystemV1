# path: ./btcts_next/src/btcts/autotrade/shadow_cycle.py
# desc: AutoTrade one-shot and bounded shadow cycle runners. Writes shadow ledger only.

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from btcts.autotrade.config import initial_parameter_set_v0_1
from btcts.autotrade.config.models import ParameterSet
from btcts.autotrade.live_shadow import ShadowDecisionVerticalResult, default_shadow_decision_ledger_path, run_latest_market_state_shadow_decision
from btcts.autotrade.mode_runtime_gate import ModeRuntimeGate, build_mode_runtime_gate
from btcts.autotrade.runtime_paths import AutoTradeRuntimePathDiagnostics, autotrade_runtime_path_diagnostics

MAX_BOUNDED_SHADOW_CYCLES = 1000


@dataclass(frozen=True)
class ShadowCycleOnceResult:
    cycle_kind: str
    result: ShadowDecisionVerticalResult
    runtime_diagnostics: AutoTradeRuntimePathDiagnostics
    mode_runtime_gate: ModeRuntimeGate | None = None
    would_send_to_broker: bool = False
    loop_started: bool = False

    @property
    def appended(self) -> bool:
        return self.result.appended

    @property
    def blocked_by(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tuple(self.runtime_diagnostics.blocked_by) + tuple(self.result.blocked_by)))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["result"] = self.result.to_dict()
        data["runtime_diagnostics"] = self.runtime_diagnostics.to_dict()
        data["mode_runtime_gate"] = self.mode_runtime_gate.to_dict() if self.mode_runtime_gate is not None else None
        data["appended"] = self.appended
        data["blocked_by"] = list(self.blocked_by)
        return data


@dataclass(frozen=True)
class ShadowCycleBoundedResult:
    cycle_kind: str
    requested_cycles: int
    completed_cycles: int
    appended_count: int
    duplicate_skipped_count: int
    results: Tuple[ShadowCycleOnceResult, ...]
    would_send_to_broker: bool = False
    loop_started: bool = True
    bounded: bool = True

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


def run_shadow_cycle_once(
    *,
    parameter_set: ParameterSet | None = None,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
    persist: bool = True,
) -> ShadowCycleOnceResult:
    ps = parameter_set or initial_parameter_set_v0_1()
    runtime_diag = autotrade_runtime_path_diagnostics()
    gate = build_mode_runtime_gate()
    if not gate.allow_shadow_decision_append:
        blocked = tuple(dict.fromkeys(tuple(gate.blocked_by) + ("mode_runtime_gate_blocked_shadow_decision_append",)))
        result = ShadowDecisionVerticalResult(
            snapshot_id=None,
            forecast_id=None,
            decision_id=None,
            candidate_action=None,
            risk_allowed=False,
            appended=False,
            ledger_path=default_shadow_decision_ledger_path(ensure=False),
            blocked_by=blocked,
            would_send_to_broker=False,
            decision=None,
            diagnostics=None,
        )
        return ShadowCycleOnceResult(
            cycle_kind="autotrade.shadow_cycle_once",
            result=result,
            runtime_diagnostics=runtime_diag,
            mode_runtime_gate=gate,
            would_send_to_broker=False,
            loop_started=False,
        )
    result = run_latest_market_state_shadow_decision(
        parameter_set=ps,
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
        persist=persist,
    )
    return ShadowCycleOnceResult(
        cycle_kind="autotrade.shadow_cycle_once",
        result=result,
        runtime_diagnostics=runtime_diag,
        mode_runtime_gate=gate,
        would_send_to_broker=False,
        loop_started=False,
    )


def _validate_bounded_cycle_args(*, max_cycles: int, interval_sec: float) -> None:
    if max_cycles < 1:
        raise ValueError("max_cycles must be >= 1")
    if max_cycles > MAX_BOUNDED_SHADOW_CYCLES:
        raise ValueError(f"max_cycles must be <= {MAX_BOUNDED_SHADOW_CYCLES}")
    if interval_sec < 0:
        raise ValueError("interval_sec must be >= 0")


def run_shadow_cycle_bounded(
    *,
    max_cycles: int,
    interval_sec: float = 0.0,
    parameter_set: ParameterSet | None = None,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
    persist: bool = True,
    skip_duplicate_snapshot: bool = True,
) -> ShadowCycleBoundedResult:
    _validate_bounded_cycle_args(max_cycles=max_cycles, interval_sec=interval_sec)
    ps = parameter_set or initial_parameter_set_v0_1()
    results: list[ShadowCycleOnceResult] = []
    last_snapshot_id: str | None = None
    duplicate_skipped = 0

    for index in range(max_cycles):
        probe = run_shadow_cycle_once(
            parameter_set=ps,
            exchange=exchange,
            symbol_raw=symbol_raw,
            state_type=state_type,
            persist=False,
        )
        snapshot_id = probe.result.snapshot_id
        duplicate = bool(skip_duplicate_snapshot and snapshot_id is not None and snapshot_id == last_snapshot_id)
        should_persist = bool(persist and not duplicate and snapshot_id is not None)
        if duplicate:
            duplicate_skipped += 1

        item = run_shadow_cycle_once(
            parameter_set=ps,
            exchange=exchange,
            symbol_raw=symbol_raw,
            state_type=state_type,
            persist=should_persist,
        )
        results.append(item)
        if snapshot_id is not None:
            last_snapshot_id = snapshot_id
        if index + 1 < max_cycles and interval_sec > 0:
            time.sleep(interval_sec)

    return ShadowCycleBoundedResult(
        cycle_kind="autotrade.shadow_cycle_bounded",
        requested_cycles=max_cycles,
        completed_cycles=len(results),
        appended_count=sum(1 for item in results if item.appended),
        duplicate_skipped_count=duplicate_skipped,
        results=tuple(results),
        would_send_to_broker=False,
        loop_started=True,
        bounded=True,
    )
