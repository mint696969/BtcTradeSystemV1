# path: ./btcts_next/src/btcts/market_engine/tests/test_market_state_flow.py
# desc: Small end-to-end market_state flow test for Market Engine profile, realtime path, projector, and writer.

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.execution.execution_facade import ExecutionFacade
from btcts.market_engine.profiles import BitflyerProfile
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.projector import MarketStateProjector
from btcts.market_engine.market_state.writer import MarketStateWriter


def _cfg(tmp_root: Path) -> MarketEngineConfig:
    return MarketEngineConfig(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        instrument_id="bitflyer.spot.BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        profile_name="bitflyer",
        near_zone_levels=2,
        far_zone_levels=2,
        replay_batch_size=1000,
        write_market_state=True,
    )


def _snapshot_event() -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "bf-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 100,
        "source_event_id": "bf-snap-1",
        "collector_ts": "2026-03-16T12:00:00Z",
        "exchange_ts": "2026-03-16T12:00:00Z",
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "resynced",
            "stream_event_no": 1,
            "bids": [
                {"price": 100.0, "size": 1.0},
                {"price": 99.5, "size": 2.0},
                {"price": 99.0, "size": 3.0},
            ],
            "asks": [
                {"price": 101.0, "size": 1.5},
                {"price": 101.5, "size": 2.5},
                {"price": 102.0, "size": 3.5},
            ],
        },
    }


def _diff_event() -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "bf-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 101,
        "source_event_id": "bf-diff-1",
        "collector_ts": "2026-03-16T12:00:01Z",
        "exchange_ts": "2026-03-16T12:00:01Z",
        "payload": {
            "event_type": "delta",
            "continuity_state": "continuous",
            "stream_event_no": 2,
            "bids": [
                {"price": 100.5, "size": 0.7},
            ],
            "asks": [],
        },
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_market_state_flow_test"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    profile = BitflyerProfile()
    engine = ExecutionFacade(profile)
    projector = MarketStateProjector()
    writer = MarketStateWriter()
    cfg = _cfg(tmp_root)

    import os
    os.environ["BTC_TS_DATA_DIR"] = str(tmp_root / "data")

    current_series = None
    current_book = None

    step1 = engine.run_realtime_step(
        current_series=current_series,
        current_book=current_book,
        normalized_event=_snapshot_event(),
    )
    current_series = step1.series_state
    current_book = step1.book_state

    step2 = engine.run_realtime_step(
        current_series=current_series,
        current_book=current_book,
        normalized_event=_diff_event(),
    )

    record = projector.project(
        cfg=cfg,
        book_state=step2.book_state,
        series_state=step2.series_state,
        zone_metadata=step2.zone_metadata,
        orderbook_semantics_contract_status=step2.orderbook_semantics_contract_status,
        orderbook_semantics_summary=step2.orderbook_semantics_summary,
        orderbook_persistence_observable=step2.orderbook_persistence_observable,
    )

    assert record.continuity_state in {"continuous", "resynced", None}
    assert record.mid_price == 100.75
    assert len(record.near_zone_bids) >= 1
    assert len(record.near_zone_asks) >= 1

    assert record.market_uid == "bitflyer.spot.BTC_JPY"
    assert record.exchange == "bitflyer"
    assert record.symbol_raw == "BTC_JPY"
    assert record.best_bid == 100.5
    assert record.best_ask == 101.0
    assert record.spread == 0.5
    assert record.trust_state.value in {"trusted", "provisional"}
    assert record.interpretation_bucket in {
        "allow_structural_use",
        "observe_only",
        "reanchor_required",
        None,
    }
    assert record.semantic_observer_status in {
        "healthy",
        "caution",
        "broken",
        "unknown",
    }
    assert isinstance(record.semantic_usage_summary, dict)
    assert "observer_status" in record.semantic_usage_summary
    assert "total_rows" in record.semantic_usage_summary
    assert "contract_source" in record.semantic_usage_summary
    assert "active_event_count" in record.semantic_usage_summary
    assert "mapped_event_count" in record.semantic_usage_summary
    assert "unknown_event_count" in record.semantic_usage_summary
    assert "event_family_distribution" in record.semantic_usage_summary
    assert "trust_bucket_distribution" in record.semantic_usage_summary
    assert "interpretation_bucket_distribution" in record.semantic_usage_summary
    assert "consumer_distribution" in record.semantic_usage_summary
    assert isinstance(record.semantic_usage_contract_rows, list)
    assert len(record.semantic_usage_contract_rows) == record.semantic_usage_summary["total_rows"]
    assert all(
        row["contract_source"] == "l3_event_usage_policy"
        for row in record.semantic_usage_contract_rows
    )
    assert all(
        row["meaning_version"] == "l3_event_usage_policy.v1alpha1"
        for row in record.semantic_usage_contract_rows
    )
    assert record.orderbook_semantics_contract_status in {"partial", "wired"}
    assert isinstance(record.orderbook_semantics_summary, dict)
    assert set(record.orderbook_semantics_summary.keys()) == {
        "near_wall",
        "support",
        "resistance",
        "persistence",
        "summary_slots_present",
        "summary_slots_count",
        "active_event_count",
        "active_event_names",
        "active_event_contracts",
    }
    assert record.orderbook_persistence_observable is True
    assert record.zone_density_metadata["mode"] == "hybrid"

    out = writer.write(
        cfg=cfg,
        state_type="market.overview",
        record=record,
        date_str="2026-03-16",
        part_no=1,
    )

    assert out.exists()

    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    saved = json.loads(lines[0])
    assert saved["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert saved["best_bid"] == 100.5
    assert saved["best_ask"] == 101.0
    assert saved["spread"] == 0.5
    assert saved["semantic_observer_status"] in {
        "healthy",
        "caution",
        "broken",
        "unknown",
    }
    assert isinstance(saved["semantic_usage_summary"], dict)
    assert "observer_status" in saved["semantic_usage_summary"]
    assert "contract_source" in saved["semantic_usage_summary"]
    assert "active_event_count" in saved["semantic_usage_summary"]
    assert "mapped_event_count" in saved["semantic_usage_summary"]
    assert "unknown_event_count" in saved["semantic_usage_summary"]
    assert "event_family_distribution" in saved["semantic_usage_summary"]
    assert "trust_bucket_distribution" in saved["semantic_usage_summary"]
    assert "interpretation_bucket_distribution" in saved["semantic_usage_summary"]
    assert "consumer_distribution" in saved["semantic_usage_summary"]
    assert isinstance(saved["semantic_usage_contract_rows"], list)
    assert len(saved["semantic_usage_contract_rows"]) == saved["semantic_usage_summary"]["total_rows"]
    assert all(
        row["contract_source"] == "l3_event_usage_policy"
        for row in saved["semantic_usage_contract_rows"]
    )
    assert all(
        row["meaning_version"] == "l3_event_usage_policy.v1alpha1"
        for row in saved["semantic_usage_contract_rows"]
    )
    assert saved["orderbook_semantics_contract_status"] in {"partial", "wired"}
    assert isinstance(saved["orderbook_semantics_summary"], dict)
    assert set(saved["orderbook_semantics_summary"].keys()) == {
        "near_wall",
        "support",
        "resistance",
        "persistence",
        "summary_slots_present",
        "summary_slots_count",
        "active_event_count",
        "active_event_names",
        "active_event_contracts",
    }
    assert saved["orderbook_persistence_observable"] is True
    assert saved["zone_density_metadata"]["mode"] == "hybrid"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())