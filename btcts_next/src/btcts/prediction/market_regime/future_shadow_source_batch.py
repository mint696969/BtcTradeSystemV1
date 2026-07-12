# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_source_batch.py
# desc: Pure MR-F5.14 exact future-shadow source batch producer and observation-window contract. No reads or writes.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_shadow_outcome import (
    FutureShadowOutcomeEvidence,
    FutureShadowOutcomeStatus,
    resolve_market_regime_future_shadow_outcome,
)
from .future_trace_identity import MarketRegimeFutureTraceIdentity

MARKET_REGIME_FUTURE_SHADOW_SOURCE_BATCH_VERSION = "prediction.market_regime.future_shadow_source_batch.mr_f5_14.v1"
ELIGIBLE_STATUSES = {
    FutureShadowOutcomeStatus.CORRECT,
    FutureShadowOutcomeStatus.PARTIAL,
    FutureShadowOutcomeStatus.INCORRECT,
}


def _parse_canonical_utc(value: str, error: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise ValueError(error)
    return parsed


@dataclass(frozen=True)
class FutureShadowObservationWindow:
    window_id: str
    opened_at: str
    evaluated_at: str
    source_role: str
    source_refs: tuple[str, ...]
    minimum_resolved_rows: int

    def __post_init__(self) -> None:
        if not self.window_id.strip():
            raise ValueError("future_shadow_source_window_id_missing")
        opened = _parse_canonical_utc(self.opened_at, "future_shadow_source_window_opened_at_invalid")
        evaluated = _parse_canonical_utc(self.evaluated_at, "future_shadow_source_window_evaluated_at_invalid")
        if evaluated < opened:
            raise ValueError("future_shadow_source_window_time_order_invalid")
        if self.source_role != "hot_data_root":
            raise ValueError("future_shadow_source_window_role_invalid")
        refs = tuple(dict.fromkeys(str(item).strip() for item in self.source_refs))
        if not refs or any(not item for item in refs):
            raise ValueError("future_shadow_source_window_refs_missing")
        object.__setattr__(self, "source_refs", refs)
        if isinstance(self.minimum_resolved_rows, bool) or not isinstance(self.minimum_resolved_rows, int) or self.minimum_resolved_rows <= 0:
            raise ValueError("future_shadow_source_window_minimum_rows_invalid")


def build_market_regime_future_shadow_source_batch(
    *,
    traces: Sequence[MarketRegimeFutureTraceIdentity],
    evidence_by_trace_id: Mapping[str, FutureShadowOutcomeEvidence],
    observation_window: FutureShadowObservationWindow,
) -> Mapping[str, Any]:
    trace_rows = tuple(traces)
    if not trace_rows:
        raise ValueError("future_shadow_source_batch_traces_missing")
    if any(not isinstance(item, MarketRegimeFutureTraceIdentity) for item in trace_rows):
        raise ValueError("future_shadow_source_batch_trace_invalid")
    trace_ids = tuple(item.trace_id for item in trace_rows)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_source_batch_trace_duplicate")
    unknown_evidence = tuple(sorted(set(evidence_by_trace_id) - set(trace_ids)))
    if unknown_evidence:
        raise ValueError("future_shadow_source_batch_unknown_evidence_trace")

    window_opened = _parse_canonical_utc(
        observation_window.opened_at, "future_shadow_source_window_opened_at_invalid"
    )
    window_evaluated = _parse_canonical_utc(
        observation_window.evaluated_at, "future_shadow_source_window_evaluated_at_invalid"
    )

    resolved_rows: list[Mapping[str, Any]] = []
    status_counts = {status.value: 0 for status in FutureShadowOutcomeStatus}
    missing_evidence_trace_ids: list[str] = []
    unresolved_trace_ids: list[str] = []
    excluded_trace_ids: list[str] = []

    for trace in sorted(trace_rows, key=lambda item: item.trace_id):
        trace_origin = _parse_canonical_utc(
            trace.origin_timestamp, "future_shadow_source_trace_origin_invalid"
        )
        if trace_origin < window_opened or trace_origin > window_evaluated:
            raise ValueError("future_shadow_source_trace_outside_window")
        evidence = evidence_by_trace_id.get(trace.trace_id)
        if evidence is None:
            missing_evidence_trace_ids.append(trace.trace_id)
            continue
        if not isinstance(evidence, FutureShadowOutcomeEvidence):
            raise ValueError("future_shadow_source_batch_evidence_invalid")
        resolved_at = _parse_canonical_utc(
            evidence.resolved_at, "future_shadow_source_evidence_resolved_at_invalid"
        )
        if resolved_at > window_evaluated:
            raise ValueError("future_shadow_source_evidence_after_window")
        if evidence.observation_available:
            observed_at = _parse_canonical_utc(
                evidence.observed_at, "future_shadow_source_evidence_observed_at_invalid"
            )
            if observed_at > window_evaluated:
                raise ValueError("future_shadow_source_observation_after_window")
        outcome = resolve_market_regime_future_shadow_outcome(trace=trace, evidence=evidence)
        status_counts[outcome.status.value] += 1
        if outcome.status in ELIGIBLE_STATUSES:
            resolved_rows.append(outcome.to_evaluation_row())
        elif outcome.status is FutureShadowOutcomeStatus.UNRESOLVED:
            unresolved_trace_ids.append(trace.trace_id)
        else:
            excluded_trace_ids.append(trace.trace_id)

    exact_rows = tuple(MappingProxyType(dict(row)) for row in resolved_rows)
    ready = len(exact_rows) >= observation_window.minimum_resolved_rows
    blockers: list[str] = []
    if missing_evidence_trace_ids:
        blockers.append("trace_evidence_missing")
    if unresolved_trace_ids:
        blockers.append("target_or_observation_unresolved")
    if len(exact_rows) < observation_window.minimum_resolved_rows:
        blockers.append("minimum_resolved_rows_not_met")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_SOURCE_BATCH_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_source_batch",
        "window_id": observation_window.window_id,
        "opened_at": observation_window.opened_at,
        "evaluated_at": observation_window.evaluated_at,
        "source_role": observation_window.source_role,
        "source_refs": observation_window.source_refs,
        "trace_count": len(trace_rows),
        "evidence_count": len(evidence_by_trace_id),
        "exact_row_count": len(exact_rows),
        "minimum_resolved_rows": observation_window.minimum_resolved_rows,
        "observation_window_ready": ready,
        "write_approval_candidate": ready and not blockers,
        "status_counts": MappingProxyType(status_counts),
        "missing_evidence_trace_ids": tuple(missing_evidence_trace_ids),
        "unresolved_trace_ids": tuple(unresolved_trace_ids),
        "excluded_trace_ids": tuple(excluded_trace_ids),
        "blockers": tuple(blockers),
        "rows": exact_rows,
        "safety": MappingProxyType({
            "pure_projection": True,
            "reads_dhot": False,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "legacy_rows_accepted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
        }),
    })
