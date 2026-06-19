# path: ./tools/test_prediction_system_ps_i1_revision_lifetime_guard.py
# desc: Focused guard for PS-I1 revision and lifetime refresh-lite.

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
            "price": 10_000_000 + idx * 1500,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _divergent_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_300_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 9_740_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_static_boundaries_and_ps_i1_markers() -> None:
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
    assert "_refresh_decision_from_scenario_lite" in text
    assert "_build_revision_summary" in text
    assert "ps_i1.v1" in text


def test_lifetime_refresh_required_on_conflict_or_invalidation() -> None:
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
    lifetime = outlook["lifetime"]

    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert scenario["gpt_review_digest"]["lifetime_refresh_version"] == "ps_i1.v1"
    assert outlook["gpt_review_digest"]["lifetime_refresh"]["state"].startswith("refresh_required")
    assert lifetime["refresh_required"] is True
    assert lifetime["refresh_reason"] in {"blocked_prediction_inputs", "active_invalidation_watch", "scenario_switch_watch", "conflicting_evidence_watch", "high_turning_point_risk"}
    assert lifetime["refresh_trigger"]
    assert outlook["trigger_eligibility"]["trigger_eligibility_state"] == "blocked"
    assert outlook["trigger_eligibility"]["machine_fields"]["lifetime_refresh_required"] is True
    assert data["gpt_review_digest"]["prediction_lifetime_state"] in {"refresh_required", "current_until_stale_after"}
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def test_revision_lite_when_previous_prediction_run_id_supplied() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_divergent_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        previous_prediction_run_id="previous-run-001",
        now=now,
    )
    data = result.to_dict()
    revision = data["revision_summary"]
    assert revision["has_revision"] is True
    assert revision["previous_prediction_run_id"] == "previous-run-001"
    assert revision["revision_reason"] == "previous_run_supplied_revision_lite_no_previous_snapshot"
    assert revision["new_primary_label"]
    assert revision["new_invalidation_state"] == data["scenario_core"]["invalidation_state"]
    assert revision["change_summary_for_gpt"]["revision_lite_version"] == "ps_i1.v1"
    assert revision["change_summary_for_gpt"]["full_previous_run_diff_available"] is False
    assert revision["changed_horizons_sec"] == [300, 600, 900]
    assert data["gpt_review_digest"]["revision_lite_version"] == "ps_i1.v1"
    assert data["gpt_review_digest"]["has_revision"] is True


def main() -> int:
    test_static_boundaries_and_ps_i1_markers()
    test_lifetime_refresh_required_on_conflict_or_invalidation()
    test_revision_lite_when_previous_prediction_run_id_supplied()
    print("[OK] Prediction System PS-I1 revision lifetime guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
