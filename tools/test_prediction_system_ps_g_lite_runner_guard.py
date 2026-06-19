# path: ./tools/test_prediction_system_ps_g_lite_runner_guard.py
# desc: Focused guard for PS-G-lite standalone Prediction System multi-horizon runner.

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
    rows: list[dict[str, object]] = []
    for idx in range(30):
        rows.append(
            {
                "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
                "price": 10_000_000 + idx * 500,
                "size": 0.1 + idx * 0.01,
            }
        )
    return rows


def _snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_015_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_025_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_018_000, "event_ts": ts, "market_role": "reference"},
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
        "would_apply_mode: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    assert "build_prediction_system_result" in text
    assert "PS-G-lite" in text


def test_ps_g_lite_runner_builds_prediction_system_result() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result, horizon_by_seconds, timeframe_by_seconds

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    assert horizon_by_seconds(600).label == "10m"
    assert timeframe_by_seconds(600).label == "10m"

    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert data["run_identity"]["system_version"] == "prediction_system.ps_g_lite.v1"
    assert data["system_input"]["requested_horizons_sec"] == [300, 600, 900]
    assert len(data["outputs"]) == 15
    assert data["inference_bundle"]["source_quality_summary"]["horizon_coverage"]["horizons_present_sec"] == [300, 600, 900]
    assert data["forecast_batch"]["record_count"] == 15
    assert data["scenario_core"]["outlooks"][0]["horizon_group"] == "short_horizon"
    assert data["scenario_core"]["outlooks"][0]["display_label_ja"] == "短期"
    assert "短期" in data["human_narrative_ja"]
    assert data["scenario_core"]["outlooks"][0]["trigger_eligibility"]["trigger_eligibility_state"] == "blocked"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_write_collector_state"] is False
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["approval_append_requested"] is False


def test_ps_g_lite_runner_handles_missing_inputs_without_exception() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    assert data["outputs"]
    assert data["forecast_batch"]["record_count"] == 15
    assert data["warnings"]
    assert data["read_only"] is True
    assert data["non_executing"] is True


def main() -> int:
    test_static_boundaries()
    test_ps_g_lite_runner_builds_prediction_system_result()
    test_ps_g_lite_runner_handles_missing_inputs_without_exception()
    print("[OK] Prediction System PS-G-lite runner guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
