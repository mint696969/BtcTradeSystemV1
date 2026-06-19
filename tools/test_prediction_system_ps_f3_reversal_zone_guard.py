# path: ./tools/test_prediction_system_ps_f3_reversal_zone_guard.py
# desc: Focused guard for PS-F3 reversal_zone deterministic v1 prediction family.

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


def _rows_near_range_high(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    prices = [10_000_000 + idx * 800 for idx in range(30)]
    prices[-1] = max(prices) + 3_000
    return [
        {
            "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
            "price": price,
            "size": 0.2,
        }
        for idx, price in enumerate(prices)
    ]


def _snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_025_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_028_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_026_000, "event_ts": ts, "market_role": "reference"},
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
    assert "PredictionFamily.REVERSAL_ZONE" in RULE.read_text(encoding="utf-8")
    assert "def _reversal_zone" in RULE.read_text(encoding="utf-8")


def test_reversal_zone_outputs_from_rule_based_v0() -> None:
    from btcts.prediction import build_rule_based_v0_outputs
    from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows
    from btcts.prediction.technical import build_human_technical_summary

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    candles, diagnostics = aggregate_ohlcv_from_rows(_rows_near_range_high(now), now=now)
    assert diagnostics.usable
    technical = build_human_technical_summary(candles, timeframe_sec=300)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, horizon_sec=300, now=now)
    by_family = {output.family.value: output for output in outputs}
    assert "reversal_zone" in by_family
    reversal = by_family["reversal_zone"]
    assert reversal.primary_label in {"reaction_zone_watch", "reversal_watch", "low_reversal_signal", "vwap_reversion_watch"}
    assert reversal.parameter_set.parameter_set_id == "reversal_zone_prediction_v0_1_0"
    assert reversal.read_only is True
    assert reversal.non_executing is True
    assert reversal.would_send_to_broker is False
    assert reversal.mode_apply_requested is False


def test_prediction_system_runner_surfaces_reversal_risk() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows_near_range_high(now),
        venue_snapshots=_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert len(data["outputs"]) == 21
    assert data["forecast_batch"]["record_count"] == 21
    assert "reversal_zone" in data["inference_bundle"]["families_present"]
    outlook = data["scenario_core"]["outlooks"][0]
    assert outlook["reversal_risk"] != "not_implemented_ps_g_lite"
    assert data["gpt_review_digest"]["family_count"] == 7
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_static_boundaries_and_family_registration()
    test_reversal_zone_outputs_from_rule_based_v0()
    test_prediction_system_runner_surfaces_reversal_risk()
    print("[OK] Prediction System PS-F3 reversal_zone guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
