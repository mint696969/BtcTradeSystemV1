# path: ./btcts_next/src/btcts/prediction/market_regime/source_attribution_adapter.py
# desc: Pure/read-only MR-VS4 adapter that expands compact trace source attribution into horizon rows consumable by the source scorecard read model.

from __future__ import annotations

from typing import Any, Iterable, Mapping

MARKET_REGIME_SOURCE_ATTRIBUTION_ADAPTER_VERSION = "prediction.market_regime.source_attribution_adapter.2026_07_10.v1"
_FORBIDDEN_RAW_KEYS = {
    "raw_candles",
    "raw_orderbook",
    "raw_trades",
    "raw_executions",
    "raw_market_payload",
    "raw_source_payload",
    "bids",
    "asks",
    "trades",
    "executions",
}


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key) in _FORBIDDEN_RAW_KEYS or _has_forbidden_raw_keys(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def expand_market_regime_trace_source_attribution_rows(
    trace_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Expand one trace row into one attribution row per horizon, fail-closed on malformed input."""

    rows: list[dict[str, Any]] = []
    rejected: list[str] = []
    seen: set[tuple[str, str, str]] = set()

    for trace_index, trace in enumerate(trace_rows):
        if not isinstance(trace, Mapping):
            rejected.append(f"trace_{trace_index}_not_mapping")
            continue
        if _has_forbidden_raw_keys(trace):
            rejected.append(f"trace_{trace_index}_forbidden_raw_payload")
            continue
        run_id = str(trace.get("run_id") or "").strip()
        active_parameter_set_id = str(trace.get("active_parameter_set_id") or "").strip()
        attribution = trace.get("source_attribution_by_horizon")
        if not run_id:
            rejected.append(f"trace_{trace_index}_run_id_missing")
            continue
        if not active_parameter_set_id:
            rejected.append(f"trace_{trace_index}_active_parameter_set_id_missing")
            continue
        if not isinstance(attribution, Mapping):
            rejected.append(f"trace_{trace_index}_source_attribution_missing")
            continue

        for horizon_key_raw, horizon in attribution.items():
            horizon_key = str(horizon_key_raw or "").strip()
            if not horizon_key:
                rejected.append(f"trace_{trace_index}_horizon_key_missing")
                continue
            if not isinstance(horizon, Mapping):
                rejected.append(f"trace_{trace_index}_{horizon_key}_not_mapping")
                continue
            row_horizon_key = str(horizon.get("horizon_key") or "").strip()
            if row_horizon_key != horizon_key:
                rejected.append(
                    f"trace_{trace_index}_{horizon_key}_horizon_key_mismatch:{row_horizon_key}"
                )
                continue
            parameter_set_id = str(horizon.get("parameter_set_id") or "").strip()
            if not parameter_set_id:
                rejected.append(f"trace_{trace_index}_{horizon_key}_parameter_set_id_missing")
                continue
            if active_parameter_set_id and parameter_set_id != active_parameter_set_id:
                rejected.append(
                    f"trace_{trace_index}_{horizon_key}_parameter_set_id_mismatch:"
                    f"{parameter_set_id}!={active_parameter_set_id}"
                )
                continue
            source_signals = horizon.get("source_signals")
            if not isinstance(source_signals, Mapping) or not source_signals:
                rejected.append(f"trace_{trace_index}_{horizon_key}_source_signals_missing")
                continue
            compact_signals: dict[str, dict[str, Any]] = {}
            signal_invalid = False
            for source_id_raw, signal in source_signals.items():
                source_id = str(source_id_raw or "").strip()
                if not source_id:
                    rejected.append(f"trace_{trace_index}_{horizon_key}_source_id_missing")
                    signal_invalid = True
                    continue
                if not isinstance(signal, Mapping):
                    rejected.append(
                        f"trace_{trace_index}_{horizon_key}_signal_not_mapping:{source_id}"
                    )
                    signal_invalid = True
                    continue
                compact_signals[source_id] = dict(signal)
            if signal_invalid or not compact_signals:
                if not compact_signals and not signal_invalid:
                    rejected.append(f"trace_{trace_index}_{horizon_key}_source_signals_empty")
                continue
            key = (run_id, horizon_key, parameter_set_id)
            if key in seen:
                rejected.append(
                    f"trace_{trace_index}_{horizon_key}_duplicate_join_key:"
                    f"{'|'.join(key)}"
                )
                continue
            seen.add(key)
            rows.append({
                "run_id": run_id,
                "horizon_key": horizon_key,
                "parameter_set_id": parameter_set_id,
                "predicted_regime": str(horizon.get("predicted_regime") or "UNKNOWN"),
                "source_signals": compact_signals,
                "logic_version": str(horizon.get("logic_version") or ""),
                "trace_id": str(trace.get("trace_id") or ""),
                "generated_at": str(trace.get("generated_at") or ""),
            })

    rows.sort(key=lambda row: (row["run_id"], row["horizon_key"], row["parameter_set_id"]))
    result = {
        "schema_version": "market_regime_source_attribution_adapter_result.2026_07_10.v1",
        "source_attribution_adapter_version": MARKET_REGIME_SOURCE_ATTRIBUTION_ADAPTER_VERSION,
        "row_count": len(rows),
        "rejected_row_count": len(rejected),
        "rows": rows,
        "rejected_rows": rejected,
        "ok": not rejected,
        "safety": {
            "read_only": True,
            "writes_dhot": False,
            "producer_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }
    return result
