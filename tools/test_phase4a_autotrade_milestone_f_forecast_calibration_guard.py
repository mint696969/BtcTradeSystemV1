# path: ./tools/test_phase4a_autotrade_milestone_f_forecast_calibration_guard.py
# desc: Guard AutoTrade milestone F forecast outcome linking and calibration summaries.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.ledger import (  # noqa: E402
    count_divergence_reasons,
    group_forecast_by_confidence,
    group_forecast_by_driver,
    group_forecast_by_parameter_set,
    link_forecast_outcome,
    summarize_forecast_links,
)
from btcts.autotrade.read_model import build_rule_based_forecast_5m, build_snapshot_id, score_forecast_outcome  # noqa: E402
from btcts.autotrade.read_model.models import (  # noqa: E402
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    ForecastDirection,
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


def make_forecast(direction: GroundDirection):
    ps = initial_parameter_set_v0_1()
    created_at = "2026-06-12T12:00:00Z"
    sid = build_snapshot_id(market_uid="bitflyer:BTC_JPY_FX", created_at=created_at, parameter_set_id=ps.parameter_set_id, effective_event_ts="2026-06-12T11:59:59Z")
    snap = AutoTradeSnapshot(
        snapshot_id=sid,
        created_at=created_at,
        market_uid="bitflyer:BTC_JPY_FX",
        parameter_set_id=ps.parameter_set_id,
        logic_version=ps.logic_version,
        effective_event_ts="2026-06-12T11:59:59Z",
        ground=GroundState(direction=direction, confidence=Confidence.MEDIUM),
        usability=SnapshotUsability(regime=True, liquidity=True, trade=True, l4=True, temporal=True),
        inputs=CurrentMarketInputs(spread=4500.0, mid_price=10000000.0),
        temporal_flow=TemporalFlowFeatures(
            windows_sec=ps.temporal_flow.windows_sec,
            generated_at=created_at,
            usable=True,
            temporal_pressure_flow={"pressure_acceleration": "sell" if direction == GroundDirection.SELL_LEANING else "buy"},
            temporal_price_flow={"mid_return_300s": -0.001 if direction == GroundDirection.SELL_LEANING else 0.001},
            temporal_pattern_flags={"liquidity_vacuum_candidate": False},
        ),
    )
    return build_rule_based_forecast_5m(snap, ps)


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()

    f_hit = make_forecast(GroundDirection.SELL_LEANING)
    o_hit = score_forecast_outcome(f_hit, GroundDirection.SELL_LEANING, actual_snapshot_id="actual_hit", resolved_at="2026-06-12T12:05:00Z")
    l_hit = link_forecast_outcome(f_hit, o_hit)

    f_miss = make_forecast(GroundDirection.BUY_LEANING)
    o_miss = score_forecast_outcome(f_miss, GroundDirection.SELL_LEANING, actual_snapshot_id="actual_miss", resolved_at="2026-06-12T12:05:00Z")
    l_miss = link_forecast_outcome(f_miss, o_miss)

    f_un = make_forecast(GroundDirection.SELL_LEANING)
    o_un = score_forecast_outcome(f_un, GroundDirection.UNKNOWN, actual_snapshot_id=None, resolved_at="2026-06-12T12:05:00Z")
    l_un = link_forecast_outcome(f_un, o_un)

    links = [l_hit, l_miss, l_un]
    summary = summarize_forecast_links(links)
    by_param = group_forecast_by_parameter_set(links)
    by_conf = group_forecast_by_confidence(links)
    by_driver = group_forecast_by_driver(links)
    divergence = count_divergence_reasons(links)

    checks = {
        "link_has_forecast_id": l_hit.forecast_id == f_hit.forecast_id,
        "link_has_parameter_set": l_hit.parameter_set_id == ps.parameter_set_id,
        "link_has_driver": bool(l_hit.drivers),
        "summary_total": summary.total_forecast_count == 3,
        "summary_scorable": summary.scorable_forecast_count == 2,
        "summary_hit_rate": summary.hit_rate == 0.5,
        "summary_miss_rate": summary.miss_rate == 0.5,
        "summary_unscorable_rate": summary.unscorable_rate == 1 / 3,
        "group_by_parameter_set": ps.parameter_set_id in by_param,
        "group_by_confidence": "medium" in by_conf,
        "group_by_driver": any(key in by_driver for key in ("sell_pressure_or_ground", "buy_pressure_or_ground")),
        "divergence_reasons_present": divergence.get("direction_mismatch", 0) >= 1,
        "json_safe_link": json.loads(json.dumps(l_hit.to_dict(), ensure_ascii=False))["forecast_id"] == f_hit.forecast_id,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["hit_count"] == 1,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone F: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_f_forecast_calibration_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "forecast_outcome_link_present": checks["link_has_forecast_id"] and checks["link_has_parameter_set"],
            "calibration_summary_present": checks["summary_total"] and checks["summary_scorable"] and checks["summary_hit_rate"],
            "confidence_driver_grouping_present": checks["group_by_confidence"] and checks["group_by_driver"],
            "divergence_reason_summary_present": checks["divergence_reasons_present"],
            "parameter_set_grouping_present": checks["group_by_parameter_set"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary.to_dict(),
        "by_confidence_keys": sorted(by_conf.keys()),
        "by_driver_keys": sorted(by_driver.keys()),
        "divergence_reasons": divergence,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
