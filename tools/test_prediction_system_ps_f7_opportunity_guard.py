# path: ./tools/test_prediction_system_ps_f7_opportunity_guard.py
# desc: Focused guard for PS-F7 opportunity_participation deterministic v1 prediction family.

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"


def _rows(now: datetime, step: int = 900) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    return [
        {
            "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
            "price": 10_000_000 + idx * step,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _confirmed_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_030_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_031_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_032_000, "event_ts": ts, "market_role": "reference"},
    ]


def _divergent_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_180_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 9_850_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_static_boundaries_and_family_registration() -> None:
    text = RULE.read_text(encoding="utf-8") + "\n" + SYSTEM.read_text(encoding="utf-8")
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "would_apply_mode: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    assert "PredictionFamily.OPPORTUNITY_PARTICIPATION" in RULE.read_text(encoding="utf-8")
    assert "def _opportunity_participation" in RULE.read_text(encoding="utf-8")


def test_opportunity_output_from_rule_based_v0() -> None:
    from btcts.prediction import build_cross_venue_reference_summary, build_rule_based_v0_outputs
    from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows
    from btcts.prediction.technical import build_human_technical_summary

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    candles, diagnostics = aggregate_ohlcv_from_rows(_rows(now), now=now)
    assert diagnostics.usable
    technical = build_human_technical_summary(candles, timeframe_sec=300)
    cross = build_cross_venue_reference_summary(_confirmed_snapshots(now), now=now)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, cross_venue_summary=cross, horizon_sec=300, now=now)
    by_family = {output.family.value: output for output in outputs}
    assert "opportunity_participation" in by_family
    opportunity = by_family["opportunity_participation"]
    assert opportunity.primary_label in {"participation_candidate", "opportunity_watch", "wait_for_confirmation", "no_edge", "opportunity_blocked"}
    assert opportunity.parameter_set.parameter_set_id == "opportunity_participation_prediction_v0_1_0"
    assert opportunity.values["proxy_kind"] == "summary_based_opportunity_proxy_v1"
    assert opportunity.read_only is True
    assert opportunity.non_executing is True
    assert opportunity.would_send_to_broker is False
    assert opportunity.mode_apply_requested is False


def test_opportunity_blocks_on_divergent_or_bad_context() -> None:
    from btcts.prediction import build_cross_venue_reference_summary, build_rule_based_v0_outputs
    from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows
    from btcts.prediction.technical import build_human_technical_summary

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    candles, _ = aggregate_ohlcv_from_rows(_rows(now), now=now)
    technical = build_human_technical_summary(candles, timeframe_sec=300)
    cross = build_cross_venue_reference_summary(_divergent_snapshots(now), now=now)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, cross_venue_summary=cross, horizon_sec=300, now=now)
    opportunity = {output.family.value: output for output in outputs}["opportunity_participation"]
    assert opportunity.primary_label in {"opportunity_blocked", "wait_for_confirmation"}
    assert opportunity.warnings


def test_prediction_system_runner_surfaces_opportunity_in_digest() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_confirmed_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert "opportunity_participation" in data["inference_bundle"]["families_present"]
    outlook = data["scenario_core"]["outlooks"][0]
    assert "opportunity_participation" in outlook["gpt_review_digest"]["family_labels"]
    assert outlook["trigger_eligibility"]["machine_fields"]["opportunity_participation"] in {"participation_candidate", "opportunity_watch", "wait_for_confirmation", "no_edge", "opportunity_blocked", "unknown"}
    assert data["gpt_review_digest"]["family_count"] == 11
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_static_boundaries_and_family_registration()
    test_opportunity_output_from_rule_based_v0()
    test_opportunity_blocks_on_divergent_or_bad_context()
    test_prediction_system_runner_surfaces_opportunity_in_digest()
    print("[OK] Prediction System PS-F7 opportunity_participation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
