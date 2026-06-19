# path: ./tools/test_prediction_system_ps_h1_scenario_core_lite_guard.py
# desc: Focused guard for PS-H1 Scenario Core lite deterministic integration.

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"


def _rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    return [
        {
            "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
            "price": 10_000_000 + idx * 900,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _divergent_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_250_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 9_800_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_static_boundaries() -> None:
    text = SYSTEM.read_text(encoding="utf-8")
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
    assert "deterministic_family_label_weighting_v1" in text
    assert "_scenario_signal_summary" in text


def test_scenario_core_lite_replaces_placeholders_and_preserves_trigger_block() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_divergent_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    scenario = data["scenario_core"]
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert scenario["continuation_vs_reversal_balance"]["state"] in {"continuation_bias", "reversal_risk_bias", "mixed_or_transition"}
    assert scenario["turning_point_risk"] in {"low", "medium", "high"}
    assert scenario["invalidation_state"] != "not_evaluated_ps_g_lite"
    assert scenario["rewrite_state"] != "not_evaluated_ps_g_lite"
    assert scenario["scenario_switch_hint"] != "not_evaluated_ps_g_lite"
    assert scenario["evidence_weighting_summary"]["state"] == "deterministic_family_label_weighting_v1"
    assert scenario["evidence_conflict_state"] != "basic_bundle_only_ps_g_lite"
    assert scenario["scenario_trace"]["what_to_watch_next"]
    assert scenario["gpt_review_digest"]["scenario_core_lite_version"] == "ps_h1.v1"

    outlook = scenario["outlooks"][0]
    assert outlook["invalidation_state"] != "not_evaluated_ps_g_lite"
    assert outlook["scenario_switch_hint"] != "not_evaluated_ps_g_lite"
    assert outlook["gpt_review_digest"]["scenario_lite"]["what_to_watch_next"]
    assert outlook["trigger_eligibility"]["trigger_eligibility_state"] == "blocked"
    assert outlook["trigger_eligibility"]["machine_fields"]["scenario_switch_hint"] == outlook["scenario_switch_hint"]
    assert outlook["trigger_eligibility"]["machine_fields"]["invalidation_state"] == outlook["invalidation_state"]

    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def test_scenario_core_lite_handles_missing_inputs_without_exception() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    scenario = data["scenario_core"]
    assert data["outputs"]
    assert scenario["evidence_weighting_summary"]["state"] == "deterministic_family_label_weighting_v1"
    assert scenario["scenario_trace"]["what_to_watch_next"]
    assert data["warnings"]
    assert data["read_only"] is True
    assert data["non_executing"] is True


def main() -> int:
    test_static_boundaries()
    test_scenario_core_lite_replaces_placeholders_and_preserves_trigger_block()
    test_scenario_core_lite_handles_missing_inputs_without_exception()
    print("[OK] Prediction System PS-H1 Scenario Core lite guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
