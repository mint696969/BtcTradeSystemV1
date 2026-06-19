# path: ./tools/test_prediction_system_ps_f9_macro_guard.py
# desc: Focused guard for PS-F9 macro_risk_context deterministic v1 prediction family.

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


def _rows(now: datetime, step: int = 400) -> list[dict[str, object]]:
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
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_012_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_013_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_014_000, "event_ts": ts, "market_role": "reference"},
    ]


def _divergent_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_220_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 9_820_000, "event_ts": ts, "market_role": "reference"},
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
        "requests.get",
        "urllib.request",
        "would_apply_mode: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    assert "PredictionFamily.MACRO_RISK_CONTEXT" in RULE.read_text(encoding="utf-8")
    assert "def _macro_risk_context" in RULE.read_text(encoding="utf-8")


def test_macro_output_from_rule_based_v0() -> None:
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
    assert "macro_risk_context" in by_family
    macro = by_family["macro_risk_context"]
    assert macro.primary_label in {"macro_context_neutral", "macro_risk_watch", "macro_context_unavailable"}
    assert macro.parameter_set.parameter_set_id == "macro_risk_context_prediction_v0_1_0"
    assert macro.values["proxy_kind"] == "summary_based_macro_risk_proxy_v1"
    assert macro.values["primary_direction_owner"] is False
    assert macro.read_only is True
    assert macro.non_executing is True
    assert macro.would_send_to_broker is False
    assert macro.mode_apply_requested is False


def test_macro_watch_on_divergent_context() -> None:
    from btcts.prediction import build_cross_venue_reference_summary, build_rule_based_v0_outputs
    from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows
    from btcts.prediction.technical import build_human_technical_summary

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    candles, _ = aggregate_ohlcv_from_rows(_rows(now), now=now)
    technical = build_human_technical_summary(candles, timeframe_sec=300)
    cross = build_cross_venue_reference_summary(_divergent_snapshots(now), now=now)
    outputs = build_rule_based_v0_outputs(technical_summary=technical, cross_venue_summary=cross, horizon_sec=300, now=now)
    macro = {output.family.value: output for output in outputs}["macro_risk_context"]
    assert macro.primary_label == "macro_risk_watch"
    assert macro.warnings
    assert macro.values["cross_venue_agreement_state"] == "divergent"


def test_prediction_system_runner_surfaces_macro_context_without_direction_ownership() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_confirmed_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert len(data["outputs"]) == 30
    assert data["forecast_batch"]["record_count"] == 30
    assert "macro_risk_context" in data["inference_bundle"]["families_present"]
    outlook = data["scenario_core"]["outlooks"][0]
    assert "macro_risk_context" in outlook["gpt_review_digest"]["family_labels"]
    assert outlook["trigger_eligibility"]["machine_fields"]["macro_risk_context"] in {"macro_context_neutral", "macro_risk_watch", "macro_context_unavailable", "unknown"}
    assert outlook["primary_label"] in {"long_bias", "short_bias", "trend_candidate", "range_candidate", "volatile_or_divergent", "unclear", "no_edge", "unknown"}
    assert outlook["primary_label"] not in {"macro_context_neutral", "macro_risk_watch", "macro_context_unavailable"}
    assert data["gpt_review_digest"]["family_count"] == 10
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_static_boundaries_and_family_registration()
    test_macro_output_from_rule_based_v0()
    test_macro_watch_on_divergent_context()
    test_prediction_system_runner_surfaces_macro_context_without_direction_ownership()
    print("[OK] Prediction System PS-F9 macro_risk_context guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
