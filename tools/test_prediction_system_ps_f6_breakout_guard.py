# path: ./tools/test_prediction_system_ps_f6_breakout_guard.py
# desc: Focused guard for PS-F6 breakout_false_break deterministic v1 prediction family.

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


def _trend_rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    rows: list[dict[str, object]] = []
    for idx in range(30):
        price = 10_000_000 + idx * 1_000
        rows.append({"event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"), "price": price, "size": 0.2})
    rows[-1]["price"] = 10_040_000
    return rows


def _false_break_rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    prices = [10_000_000 + idx * 300 for idx in range(29)]
    prices.append(10_010_000)
    rows: list[dict[str, object]] = []
    for idx, price in enumerate(prices):
        rows.append({"event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"), "price": price, "size": 0.2})
    return rows


def _confirmed_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_040_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_043_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_041_000, "event_ts": ts, "market_role": "reference"},
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
    assert "PredictionFamily.BREAKOUT_FALSE_BREAK" in RULE.read_text(encoding="utf-8")
    assert "def _breakout_false_break" in RULE.read_text(encoding="utf-8")


def test_breakout_output_from_rule_based_v0() -> None:
    from btcts.prediction import build_cross_venue_reference_summary, build_rule_based_v0_outputs
    from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows
    from btcts.prediction.technical import build_human_technical_summary

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    candles, diagnostics = aggregate_ohlcv_from_rows(_trend_rows(now), now=now)
    assert diagnostics.usable
    technical = build_human_technical_summary(candles, timeframe_sec=300)
    cross = build_cross_venue_reference_summary(_confirmed_snapshots(now), now=now)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, cross_venue_summary=cross, horizon_sec=300, now=now)
    by_family = {output.family.value: output for output in outputs}
    assert "breakout_false_break" in by_family
    breakout = by_family["breakout_false_break"]
    assert breakout.primary_label in {"breakout_candidate", "breakout_watch", "false_break_risk", "range_continuation", "no_breakout_signal"}
    assert breakout.parameter_set.parameter_set_id == "breakout_false_break_prediction_v0_1_0"
    assert breakout.values["proxy_kind"] == "technical_cross_venue_breakout_proxy_v1"
    assert breakout.read_only is True
    assert breakout.non_executing is True
    assert breakout.would_send_to_broker is False
    assert breakout.mode_apply_requested is False


def test_false_break_warning_from_wick_or_unconfirmed_structure() -> None:
    from btcts.prediction import build_cross_venue_reference_summary, build_rule_based_v0_outputs
    from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows
    from btcts.prediction.technical import build_human_technical_summary

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    candles, _ = aggregate_ohlcv_from_rows(_false_break_rows(now), now=now)
    technical = build_human_technical_summary(candles, timeframe_sec=300)
    cross = build_cross_venue_reference_summary(_divergent_snapshots(now), now=now)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, cross_venue_summary=cross, horizon_sec=300, now=now)
    breakout = {output.family.value: output for output in outputs}["breakout_false_break"]
    assert breakout.primary_label in {"false_break_risk", "range_continuation", "breakout_watch", "no_breakout_signal"}
    assert breakout.primary_label != "breakout_candidate"
    assert breakout.values["cross_venue_agreement_state"] == "divergent"
    assert breakout.values["range_close_position"] in {"near_range_high", "near_range_low", "mid_range", "flat"}


def test_prediction_system_runner_surfaces_breakout_false_break_risk() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_trend_rows(now),
        venue_snapshots=_confirmed_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert len(data["outputs"]) == 24
    assert data["forecast_batch"]["record_count"] == 24
    assert "breakout_false_break" in data["inference_bundle"]["families_present"]
    outlook = data["scenario_core"]["outlooks"][0]
    assert outlook["breakout_false_break_risk"] != "not_implemented_ps_g_lite"
    assert data["gpt_review_digest"]["family_count"] == 8
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_static_boundaries_and_family_registration()
    test_breakout_output_from_rule_based_v0()
    test_false_break_warning_from_wick_or_unconfirmed_structure()
    test_prediction_system_runner_surfaces_breakout_false_break_risk()
    print("[OK] Prediction System PS-F6 breakout_false_break guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
