# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_ledger_observation.py
# desc: MR-F8.11 pure canonical point-observation resolver from append-only MarketRegime trace-ledger rows.

from __future__ import annotations

from collections.abc import Mapping as MappingABC, Sequence
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import MarketRegimeCode
from .future_shadow_runtime_outcome_intake import FutureShadowPointObservation
from .future_target_definition import future_target_definitions_by_horizon

MARKET_REGIME_FUTURE_SHADOW_LEDGER_OBSERVATION_VERSION = (
    "prediction.market_regime.future_shadow_ledger_observation.mr_f8_11.v1"
)


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"ledger_observation_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"ledger_observation_timestamp_timezone_missing:{field}")
    return parsed.astimezone(timezone.utc)


def _canonical(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _current_regime(row: Mapping[str, Any]) -> MarketRegimeCode:
    summary = row.get("prediction_summary")
    if not isinstance(summary, MappingABC):
        raise ValueError("ledger_observation_prediction_summary_missing")
    horizons = summary.get("horizons")
    if not isinstance(horizons, Sequence) or isinstance(horizons, (str, bytes)):
        raise ValueError("ledger_observation_horizons_invalid")
    current_rows = [
        item
        for item in horizons
        if isinstance(item, MappingABC)
        and item.get("horizon_sec") is not None
        and int(item["horizon_sec"]) == 0
    ]
    if len(current_rows) != 1:
        raise ValueError(f"ledger_observation_current_row_count_invalid:{len(current_rows)}")
    return MarketRegimeCode(str(current_rows[0].get("regime_code") or "UNKNOWN"))


def resolve_point_observation_from_ledger_rows(
    *,
    target_horizon_sec: int,
    expiry_at: str,
    ledger_rows: Sequence[Mapping[str, Any]],
    source_ref: str,
) -> FutureShadowPointObservation | None:
    horizon = int(target_horizon_sec)
    definition = future_target_definitions_by_horizon().get(horizon)
    if definition is None:
        raise ValueError(f"ledger_observation_horizon_invalid:{horizon}")
    expiry = _parse_utc(expiry_at, "expiry_at")
    latest_allowed = expiry.timestamp() + int(definition.observation_tolerance_sec)

    candidates: list[tuple[datetime, Mapping[str, Any]]] = []
    for row in ledger_rows:
        if not isinstance(row, MappingABC):
            raise ValueError("ledger_observation_row_invalid")
        if row.get("artifact_kind") != "trace_row" or row.get("event_type") != "market_regime_prediction_trace":
            continue
        generated = _parse_utc(row.get("generated_at"), "generated_at")
        if generated.timestamp() < expiry.timestamp() or generated.timestamp() > latest_allowed:
            continue
        safety = row.get("safety")
        if not isinstance(safety, MappingABC) or safety.get("read_only_sources") is not True:
            raise ValueError("ledger_observation_safety_invalid")
        candidates.append((generated, row))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    observed_at, selected = candidates[0]
    state = _current_regime(selected)
    if state is MarketRegimeCode.UNKNOWN:
        return None
    return FutureShadowPointObservation(
        target_horizon_sec=horizon,
        observed_at=_canonical(observed_at),
        observed_future_state=state,
        observation_source_ref=f"{source_ref}#{selected.get('trace_id')}",
    )


def build_ledger_observation_report(
    *,
    runtime_preflight_result: Mapping[str, Any],
    ledger_rows_by_horizon: Mapping[int, Sequence[Mapping[str, Any]]],
    source_refs_by_horizon: Mapping[int, str],
) -> Mapping[str, Any]:
    preflight = runtime_preflight_result.get("preflight_report")
    if not isinstance(preflight, MappingABC):
        raise ValueError("ledger_observation_preflight_invalid")
    pairs = preflight.get("pairs")
    if not isinstance(pairs, Sequence) or isinstance(pairs, (str, bytes)) or len(pairs) != 7:
        raise ValueError("ledger_observation_pairs_invalid")

    observations: dict[int, FutureShadowPointObservation] = {}
    unresolved: list[int] = []
    for pair in pairs:
        if not isinstance(pair, MappingABC):
            raise ValueError("ledger_observation_pair_invalid")
        slot = pair.get("slot_identity")
        if not isinstance(slot, MappingABC):
            raise ValueError("ledger_observation_slot_invalid")
        horizon = int(slot.get("target_horizon_sec") or 0)
        forecasts = pair.get("forecasts")
        if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)) or len(forecasts) != 2:
            raise ValueError("ledger_observation_forecasts_invalid")
        expiries = {str(item.get("expiry_at") or "") for item in forecasts if isinstance(item, MappingABC)}
        if len(expiries) != 1:
            raise ValueError("ledger_observation_expiry_mismatch")
        observation = resolve_point_observation_from_ledger_rows(
            target_horizon_sec=horizon,
            expiry_at=next(iter(expiries)),
            ledger_rows=ledger_rows_by_horizon.get(horizon, ()),
            source_ref=str(source_refs_by_horizon.get(horizon) or ""),
        )
        if observation is None:
            unresolved.append(horizon)
        else:
            observations[horizon] = observation

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_LEDGER_OBSERVATION_VERSION,
        "artifact_kind": "future_shadow_ledger_observation_report",
        "observation_count": len(observations),
        "unresolved_count": len(unresolved),
        "observed_horizons": tuple(sorted(observations)),
        "unresolved_horizons": tuple(sorted(unresolved)),
        "observations_by_horizon": MappingProxyType(dict(observations)),
        "safety": MappingProxyType({
            "canonical_current_state_only": True,
            "first_row_at_or_after_expiry": True,
            "target_tolerance_enforced": True,
            "historical_state_inference_forbidden": True,
            "read_only_inputs": True,
            "writes_dhot": False,
            "scheduler_enabled": False,
        }),
    })
