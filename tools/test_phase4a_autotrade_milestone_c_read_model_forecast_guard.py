# path: ./tools/test_phase4a_autotrade_milestone_c_read_model_forecast_guard.py
# desc: Guard AutoTrade milestone C read model, temporal flow, and 5m forecast lifecycle.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.read_model import (  # noqa: E402
    build_rule_based_forecast_5m,
    build_snapshot_id,
    score_forecast_outcome,
)
from btcts.autotrade.read_model.models import (  # noqa: E402
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    ForecastOutcomeResult,
    GroundDirection,
    GroundState,
    SnapshotUsability,
    TemporalFlowFeatures,
)

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def make_snapshot(*, temporal: bool, trade: bool, stale_reasons: tuple[str, ...] = ()) -> AutoTradeSnapshot:
    ps = initial_parameter_set_v0_1()
    created_at = "2026-06-12T12:00:00Z"
    snapshot_id = build_snapshot_id(
        market_uid="bitflyer:BTC_JPY_FX",
        created_at=created_at,
        parameter_set_id=ps.parameter_set_id,
        effective_event_ts="2026-06-12T11:59:59Z",
    )
    return AutoTradeSnapshot(
        snapshot_id=snapshot_id,
        created_at=created_at,
        market_uid="bitflyer:BTC_JPY_FX",
        parameter_set_id=ps.parameter_set_id,
        logic_version=ps.logic_version,
        effective_event_ts="2026-06-12T11:59:59Z",
        ground=GroundState(direction=GroundDirection.SELL_LEANING, confidence=Confidence.MEDIUM),
        usability=SnapshotUsability(regime=True, liquidity=True, trade=trade, l4=True, temporal=temporal),
        inputs=CurrentMarketInputs(spread=4500.0, imbalance=-0.1, wall_ratio=-0.12, wall_side="ask", trade_delta=-2.0, mid_price=10000000.0),
        temporal_flow=TemporalFlowFeatures(
            windows_sec=ps.temporal_flow.windows_sec,
            generated_at=created_at,
            source_snapshot_ids=("snap_a", "snap_b"),
            max_feature_age_sec=4.0 if temporal else 30.0,
            usable=temporal,
            blocked_by=() if temporal else ("temporal_stale",),
            temporal_pressure_flow={"pressure_acceleration": "sell", "trade_delta_change": -2.0},
            temporal_price_flow={"mid_return_300s": -0.001},
            temporal_pattern_flags={"liquidity_vacuum_candidate": False},
        ),
        stale_reasons=stale_reasons,
    )


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    fresh = make_snapshot(temporal=True, trade=True)
    stale = make_snapshot(temporal=False, trade=False, stale_reasons=("trade_stale",))

    forecast = build_rule_based_forecast_5m(fresh, ps)
    stale_forecast = build_rule_based_forecast_5m(stale, ps)
    outcome_hit = score_forecast_outcome(forecast, GroundDirection.SELL_LEANING, actual_snapshot_id="snap_actual", resolved_at="2026-06-12T12:05:00Z")
    outcome_miss = score_forecast_outcome(forecast, GroundDirection.BUY_LEANING, actual_snapshot_id="snap_actual_2", resolved_at="2026-06-12T12:05:00Z")
    outcome_unscorable = score_forecast_outcome(forecast, GroundDirection.UNKNOWN, actual_snapshot_id=None, resolved_at="2026-06-12T12:05:00Z")

    checks = {
        "snapshot_id_stable_prefix": fresh.snapshot_id.startswith("snap_"),
        "temporal_windows_present": fresh.temporal_flow.windows_sec == (15, 30, 60, 180, 300),
        "temporal_flow_usable_flag": fresh.temporal_flow.usable is True,
        "forecast_id_present": forecast.forecast_id.startswith("fcst_"),
        "forecast_target_5m": forecast.target_ts == "2026-06-12T12:05:00Z",
        "forecast_source_snapshot_linked": forecast.source_snapshot_id == fresh.snapshot_id,
        "forecast_parameter_set_linked": forecast.parameter_set_id == ps.parameter_set_id,
        "forecast_direction_from_temporal_pressure": forecast.forecast_direction.value == "down",
        "forecast_drivers_present": "sell_pressure_or_ground" in forecast.drivers,
        "stale_forecast_low_confidence": stale_forecast.confidence == Confidence.LOW,
        "stale_forecast_blocked_by_trade": "trade_stale" in stale_forecast.blocked_by,
        "stale_forecast_blocked_by_temporal": "temporal_flow_unusable" in stale_forecast.blocked_by,
        "outcome_hit": outcome_hit.score.result == ForecastOutcomeResult.HIT,
        "outcome_miss": outcome_miss.score.result == ForecastOutcomeResult.MISS,
        "outcome_unscorable": outcome_unscorable.score.result == ForecastOutcomeResult.UNSCORABLE,
        "forecast_to_dict_json_safe": json.loads(json.dumps(forecast.to_dict(), ensure_ascii=False))["forecast_id"] == forecast.forecast_id,
        "snapshot_to_dict_has_temporal": "temporal_flow" in fresh.to_dict(),
        "outcome_to_dict_has_score": outcome_hit.to_dict()["score"]["result"] == "hit",
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone C: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_c_read_model_forecast_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "snapshot_contract_present": checks["snapshot_id_stable_prefix"] and checks["snapshot_to_dict_has_temporal"],
            "temporal_flow_core_input_present": checks["temporal_windows_present"] and checks["temporal_flow_usable_flag"],
            "forecast_lifecycle_present": checks["forecast_id_present"] and checks["forecast_target_5m"] and checks["forecast_source_snapshot_linked"],
            "stale_inputs_do_not_raise_confidence": checks["stale_forecast_low_confidence"] and checks["stale_forecast_blocked_by_temporal"],
            "forecast_outcome_scoring_present": checks["outcome_hit"] and checks["outcome_miss"] and checks["outcome_unscorable"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "forecast_id": forecast.forecast_id,
        "snapshot_id": fresh.snapshot_id,
        "target_ts": forecast.target_ts,
        "stale_blocked_by": list(stale_forecast.blocked_by),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
