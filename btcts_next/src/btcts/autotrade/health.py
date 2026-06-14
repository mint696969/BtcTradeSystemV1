# path: ./btcts_next/src/btcts/autotrade/health.py
# desc: Read-only AutoTrade runtime health snapshot across runtime paths and ledgers.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from btcts.autotrade.ledger import (
    ForecastOutcomeLedgerSummary,
    ObserverRunLedgerSummary,
    ShadowDecisionLedgerSummary,
    summarize_forecast_outcome_ledger,
    summarize_observer_run_ledger,
    summarize_shadow_decision_ledger,
)
from btcts.autotrade.runtime_paths import AutoTradeRuntimePathDiagnostics, autotrade_runtime_path_diagnostics

DEFAULT_MAX_OBSERVER_RUN_AGE_SEC = 120.0


@dataclass(frozen=True)
class AutoTradeRuntimeHealthSnapshot:
    health_state: str
    generated_at: str
    runtime: AutoTradeRuntimePathDiagnostics
    observer_runs: ObserverRunLedgerSummary
    shadow_decisions: ShadowDecisionLedgerSummary
    forecast_outcomes: ForecastOutcomeLedgerSummary
    observer_run_age_sec: float | None
    observer_run_fresh: bool
    max_observer_run_age_sec: float
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["runtime"] = self.runtime.to_dict()
        data["observer_runs"] = self.observer_runs.to_dict()
        data["shadow_decisions"] = self.shadow_decisions.to_dict()
        data["forecast_outcomes"] = self.forecast_outcomes.to_dict()
        return data


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_ts(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_ts(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _age_seconds(value: str | None, *, now: datetime) -> float | None:
    dt = _parse_ts(value)
    if dt is None:
        return None
    return max(0.0, (now - dt).total_seconds())


def _health_state(*, blocked_by: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    if blocked_by:
        return "blocked"
    if warnings:
        return "warn"
    return "ok"


def build_autotrade_runtime_health_snapshot(
    *,
    max_observer_run_age_sec: float = DEFAULT_MAX_OBSERVER_RUN_AGE_SEC,
    max_lines: int | None = 1000,
    now: datetime | None = None,
) -> AutoTradeRuntimeHealthSnapshot:
    anchor = now or _utc_now()
    runtime = autotrade_runtime_path_diagnostics()
    observer_runs = summarize_observer_run_ledger(max_lines=max_lines)
    shadow_decisions = summarize_shadow_decision_ledger(max_lines=max_lines)
    forecast_outcomes = summarize_forecast_outcome_ledger(max_lines=max_lines)

    blocked: list[str] = list(runtime.blocked_by)
    warnings: list[str] = list(runtime.warnings)

    observer_age = _age_seconds(observer_runs.latest_finished_at, now=anchor)
    observer_fresh = bool(observer_age is not None and observer_age <= max_observer_run_age_sec)
    if observer_runs.total_rows <= 0:
        blocked.append("observer_run_missing")
    elif not observer_fresh:
        blocked.append("observer_run_stale")

    if shadow_decisions.total_rows <= 0:
        warnings.append("shadow_decision_ledger_empty")
    if forecast_outcomes.total_rows <= 0:
        warnings.append("forecast_outcome_ledger_empty")
    if observer_runs.skipped_rows > 0:
        warnings.append("observer_run_ledger_has_skipped_rows")
    if shadow_decisions.skipped_rows > 0:
        warnings.append("shadow_decision_ledger_has_skipped_rows")

    blocked_tuple = tuple(dict.fromkeys(blocked))
    warnings_tuple = tuple(dict.fromkeys(warnings))
    return AutoTradeRuntimeHealthSnapshot(
        health_state=_health_state(blocked_by=blocked_tuple, warnings=warnings_tuple),
        generated_at=_format_ts(anchor),
        runtime=runtime,
        observer_runs=observer_runs,
        shadow_decisions=shadow_decisions,
        forecast_outcomes=forecast_outcomes,
        observer_run_age_sec=observer_age,
        observer_run_fresh=observer_fresh,
        max_observer_run_age_sec=float(max_observer_run_age_sec),
        blocked_by=blocked_tuple,
        warnings=warnings_tuple,
        would_send_to_broker=False,
        read_only=True,
    )
