# path: ./btcts_next/src/btcts/prediction/market_regime/future_outcome_persistence_diagnostics.py
# desc: MR-F9.8 pure multi-snapshot diagnostics for unresolved persistence, unknown observations, invalidation, abstention, coverage, and resolution delay.

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

MARKET_REGIME_FUTURE_OUTCOME_PERSISTENCE_DIAGNOSTICS_VERSION = (
    "prediction.market_regime.future_outcome_persistence_diagnostics.mr_f9_8.v1"
)

_TERMINAL_STATUSES = {"CORRECT", "PARTIAL", "INCORRECT", "INVALIDATED", "ABSTAINED"}
_ALLOWED_STATUSES = _TERMINAL_STATUSES | {"UNRESOLVED"}


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(error)
    return value


def _parse_utc(value: str, error: str) -> datetime:
    text = str(value or "")
    if not text.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc:
        raise ValueError(error)
    return parsed


def build_future_outcome_persistence_diagnostics(
    *,
    maturation_snapshots: Sequence[Mapping[str, Any]],
    evaluated_at: str,
) -> Mapping[str, Any]:
    snapshots = _sequence(
        maturation_snapshots,
        "future_outcome_persistence_diagnostics_snapshots_invalid",
    )
    if not snapshots:
        raise ValueError("future_outcome_persistence_diagnostics_snapshots_empty")
    evaluated_dt = _parse_utc(
        evaluated_at,
        "future_outcome_persistence_diagnostics_evaluated_at_invalid",
    )

    by_receipt: dict[str, list[tuple[datetime, Mapping[str, Any]]]] = defaultdict(list)
    seen_snapshot_keys: set[tuple[str, str]] = set()
    for index, snapshot in enumerate(snapshots):
        if not isinstance(snapshot, Mapping):
            raise ValueError(f"future_outcome_persistence_diagnostics_snapshot_invalid:{index}")
        if snapshot.get("artifact_kind") != "future_shadow_maturation_snapshot":
            raise ValueError("future_outcome_persistence_diagnostics_snapshot_kind_invalid")
        receipt_id = str(snapshot.get("receipt_id") or "")
        suite_id = str(snapshot.get("suite_id") or "")
        origin = str(snapshot.get("prediction_origin") or "")
        polled_at = str(snapshot.get("polled_at") or "")
        if not receipt_id or not suite_id or not origin or not polled_at:
            raise ValueError("future_outcome_persistence_diagnostics_snapshot_identity_invalid")
        poll_dt = _parse_utc(polled_at, "future_outcome_persistence_diagnostics_polled_at_invalid")
        origin_dt = _parse_utc(origin, "future_outcome_persistence_diagnostics_origin_invalid")
        if poll_dt < origin_dt:
            raise ValueError("future_outcome_persistence_diagnostics_poll_before_origin")
        if poll_dt > evaluated_dt:
            raise ValueError("future_outcome_persistence_diagnostics_snapshot_after_evaluated_at")
        key = (receipt_id, polled_at)
        if key in seen_snapshot_keys:
            raise ValueError("future_outcome_persistence_diagnostics_duplicate_snapshot")
        seen_snapshot_keys.add(key)
        rows = _sequence(snapshot.get("outcome_rows"), "future_outcome_persistence_diagnostics_rows_invalid")
        trace_ids = tuple(str(row.get("trace_id") or "") for row in rows if isinstance(row, Mapping))
        if len(trace_ids) != len(rows) or any(not trace_id for trace_id in trace_ids):
            raise ValueError("future_outcome_persistence_diagnostics_trace_ids_invalid")
        if len(trace_ids) != len(set(trace_ids)):
            raise ValueError("future_outcome_persistence_diagnostics_duplicate_trace_id")
        if tuple(snapshot.get("trace_ids") or ()) != trace_ids:
            raise ValueError("future_outcome_persistence_diagnostics_trace_set_mismatch")
        if int(snapshot.get("trace_count") or 0) != len(rows):
            raise ValueError("future_outcome_persistence_diagnostics_trace_count_mismatch")
        by_receipt[receipt_id].append((poll_dt, snapshot))

    trace_histories: dict[str, list[Mapping[str, Any]]] = {}
    receipt_origins: set[str] = set()
    for receipt_id, entries in by_receipt.items():
        entries.sort(key=lambda item: item[0])
        suite_ids = {str(item[1].get("suite_id") or "") for item in entries}
        origins = {str(item[1].get("prediction_origin") or "") for item in entries}
        trace_sets = {tuple(item[1].get("trace_ids") or ()) for item in entries}
        if len(suite_ids) != 1 or len(origins) != 1 or len(trace_sets) != 1:
            raise ValueError("future_outcome_persistence_diagnostics_receipt_identity_mismatch")
        receipt_origins.update(origins)
        local_histories: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for _, snapshot in entries:
            for row in snapshot["outcome_rows"]:
                if not isinstance(row, Mapping):
                    raise ValueError("future_outcome_persistence_diagnostics_row_invalid")
                trace_id = str(row.get("trace_id") or "")
                row_origin = str(row.get("origin_timestamp") or "")
                row_resolved_at = str(row.get("resolved_at") or "")
                if row_origin != str(snapshot.get("prediction_origin") or ""):
                    raise ValueError("future_outcome_persistence_diagnostics_row_origin_mismatch")
                if row_resolved_at != str(snapshot.get("polled_at") or ""):
                    raise ValueError("future_outcome_persistence_diagnostics_row_polled_at_mismatch")
                local_histories[trace_id].append(row)
        for trace_id, history in local_histories.items():
            if trace_id in trace_histories:
                raise ValueError("future_outcome_persistence_diagnostics_trace_reused_across_receipts")
            identities = {
                (
                    str(row.get("origin_timestamp") or ""),
                    int(row.get("target_horizon_sec") or 0),
                    str(row.get("parameter_set_id") or ""),
                    str(row.get("model_id") or ""),
                    str(row.get("logic_version") or ""),
                    str(row.get("feature_snapshot_ref") or ""),
                )
                for row in history
            }
            if len(identities) != 1:
                raise ValueError("future_outcome_persistence_diagnostics_trace_identity_changed")
            statuses = [str(row.get("outcome_status") or "") for row in history]
            if any(status not in _ALLOWED_STATUSES for status in statuses):
                raise ValueError("future_outcome_persistence_diagnostics_status_invalid")
            terminal_status = ""
            for status in statuses:
                if terminal_status and status == "UNRESOLVED":
                    raise ValueError("future_outcome_persistence_diagnostics_terminal_regression")
                if terminal_status and status != terminal_status:
                    raise ValueError("future_outcome_persistence_diagnostics_terminal_status_changed")
                if status in _TERMINAL_STATUSES and not terminal_status:
                    terminal_status = status
            trace_histories[trace_id] = history

    grouped: dict[tuple[int, str], list[tuple[str, list[Mapping[str, Any]]]]] = defaultdict(list)
    for trace_id, history in trace_histories.items():
        first = history[0]
        grouped[(int(first["target_horizon_sec"]), str(first["parameter_set_id"]))].append((trace_id, history))

    summaries = []
    for (horizon, candidate), items in sorted(grouped.items()):
        latest_counts: Counter[str] = Counter()
        unresolved_poll_counts: list[int] = []
        resolved_delays: list[float] = []
        unknown_observed = 0
        ever_invalidated = 0
        ever_abstained = 0
        for _, history in items:
            latest = history[-1]
            latest_status = str(latest["outcome_status"])
            latest_counts[latest_status] += 1
            unresolved_poll_counts.append(sum(1 for row in history if row["outcome_status"] == "UNRESOLVED"))
            if any(
                str(row.get("outcome_reason") or "") == "observed_future_state_unknown"
                for row in history
            ):
                unknown_observed += 1
            if any(row["outcome_status"] == "INVALIDATED" for row in history):
                ever_invalidated += 1
            if any(row["outcome_status"] == "ABSTAINED" for row in history):
                ever_abstained += 1
            first_terminal = next(
                (row for row in history if str(row.get("outcome_status") or "") in _TERMINAL_STATUSES),
                None,
            )
            if first_terminal is not None:
                expiry = _parse_utc(str(first_terminal.get("expiry_at") or ""), "future_outcome_persistence_diagnostics_expiry_invalid")
                resolved = _parse_utc(str(first_terminal.get("resolved_at") or ""), "future_outcome_persistence_diagnostics_resolved_at_invalid")
                delay = (resolved - expiry).total_seconds()
                if delay < 0:
                    raise ValueError("future_outcome_persistence_diagnostics_negative_resolution_delay")
                resolved_delays.append(delay)

        trace_count = len(items)
        latest_resolved = sum(latest_counts.get(status, 0) for status in _TERMINAL_STATUSES)
        summaries.append(MappingProxyType({
            "target_horizon_sec": horizon,
            "parameter_set_id": candidate,
            "trace_count": trace_count,
            "latest_status_counts": MappingProxyType(dict(sorted(latest_counts.items()))),
            "latest_unresolved_rate": latest_counts.get("UNRESOLVED", 0) / trace_count,
            "latest_terminal_coverage_rate": latest_resolved / trace_count,
            "unknown_observed_rate": unknown_observed / trace_count,
            "ever_invalidated_rate": ever_invalidated / trace_count,
            "ever_abstained_rate": ever_abstained / trace_count,
            "mean_unresolved_poll_count": sum(unresolved_poll_counts) / trace_count,
            "max_unresolved_poll_count": max(unresolved_poll_counts),
            "resolved_trace_count": len(resolved_delays),
            "mean_resolution_delay_sec": (
                sum(resolved_delays) / len(resolved_delays) if resolved_delays else None
            ),
            "max_resolution_delay_sec": max(resolved_delays) if resolved_delays else None,
        }))

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_OUTCOME_PERSISTENCE_DIAGNOSTICS_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_outcome_persistence_diagnostics_report",
        "evaluated_at": evaluated_at,
        "snapshot_count": len(snapshots),
        "receipt_count": len(by_receipt),
        "origin_count": len(receipt_origins),
        "trace_count": len(trace_histories),
        "summaries": tuple(summaries),
        "diagnostic_only": True,
        "probability_metrics_computed": False,
        "proposal_generated": False,
        "would_write": False,
        "safety": MappingProxyType({
            "read_only_inputs": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_outcome_ledger_append": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
