# path: ./tools/test_prediction_system_ps_h2_scenario_trace_detail_guard.py
# desc: Focused guard for PS-H2 Scenario trace detail and evidence refs lite.

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
            "price": 10_000_000 + idx * 1200,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _divergent_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_280_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 9_760_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_static_boundaries_and_ps_h2_markers() -> None:
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
    assert "PredictionEvidenceRef" in text
    assert "_scenario_evidence_refs" in text
    assert "_scenario_trace_detail" in text
    assert "ps_h2.v1" in text


def test_scenario_trace_detail_and_evidence_refs_are_emitted() -> None:
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
    outlook = scenario["outlooks"][0]
    trace = outlook["gpt_review_digest"]["scenario_trace_detail"]

    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert outlook["evidence_refs"]
    assert len(outlook["evidence_refs"]) >= 8
    assert {item["family"] for item in outlook["evidence_refs"]} >= {"trend_bias", "market_regime", "cross_venue_confirmation", "liquidity_execution_quality"}
    assert all(item["evidence_ref_id"] for item in outlook["evidence_refs"])
    assert all(item["evidence_kind"] for item in outlook["evidence_refs"])
    assert trace["trace_version"] == "ps_h2.v1"
    assert trace["evidence_ref_ids"]
    assert trace["horizon_group"] == "short_horizon"
    assert trace["what_to_watch_next"]
    assert scenario["scenario_trace"]["outlook_traces"]
    assert scenario["scenario_trace"]["evidence_ref_count"] == len(outlook["evidence_refs"])
    assert scenario["gpt_review_digest"]["scenario_trace_detail_version"] == "ps_h2.v1"

    assert outlook["trigger_eligibility"]["trigger_eligibility_state"] == "blocked"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def test_scenario_trace_detail_handles_missing_inputs_without_exception() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    scenario = data["scenario_core"]
    outlook = scenario["outlooks"][0]
    assert outlook["evidence_refs"]
    assert scenario["scenario_trace"]["outlook_traces"]
    assert scenario["scenario_trace"]["what_to_watch_next"]
    assert data["warnings"]
    assert data["read_only"] is True
    assert data["non_executing"] is True


def main() -> int:
    test_static_boundaries_and_ps_h2_markers()
    test_scenario_trace_detail_and_evidence_refs_are_emitted()
    test_scenario_trace_detail_handles_missing_inputs_without_exception()
    print("[OK] Prediction System PS-H2 scenario trace detail guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
