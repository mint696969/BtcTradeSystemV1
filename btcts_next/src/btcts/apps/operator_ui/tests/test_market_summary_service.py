# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_service.py
# desc: Verify operator_ui market_state_service can return shared L4 MarketSummary from latest market.overview.

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.market_state_service import load_latest_market_summary
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_ui_market_summary_service_test"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    os.environ["BTC_TS_DATA_DIR"] = str(tmp_root / "data")

    cfg = MarketEngineConfig(
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

    record = MarketStateRecord(
        market_uid="bitflyer.spot.BTC_JPY",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        collector_ts="2026-03-16T13:00:00Z",
        exchange_ts="2026-03-16T13:00:00Z",
        trust_state=TrustState.TRUSTED,
        boundary_reason=BoundaryReason.NONE,
        continuity_state="continuous",
        interpretation_bucket="allow_structural_use",
        interpretation_reason="healthy_continuity",
        interpretation_policy={
            "mode": "continuous_trusted",
            "review_required": False,
        },
        semantic_observer_status="healthy",
        semantic_usage_summary={
            "source_kind": "market_state_semantic_usage_summary",
            "contract_source": "l3_event_usage_policy",
            "meaning_version": "l3_event_usage_policy.v1alpha1",
            "observer_status": "healthy",
            "total_rows": 2,
            "active_event_count": 1,
            "mapped_event_count": 1,
            "unknown_event_count": 0,
            "event_family_distribution": {"wall": 2},
            "trust_bucket_distribution": {"trusted": 2},
            "interpretation_bucket_distribution": {"observe_only": 2},
            "consumer_distribution": {"health": 2},
        },
        semantic_usage_contract_rows=[
            {
                "contract_source": "l3_event_usage_policy",
                "interpretation_bucket": "allow_structural_use",
                "meaning_version": "l3_event_usage_policy.v1alpha1",
                "event_family": "wall",
                "usage_grade": "strong",
            },
            {
                "contract_source": "l3_event_usage_policy",
                "interpretation_bucket": "allow_structural_use",
                "meaning_version": "l3_event_usage_policy.v1alpha1",
                "event_family": "absorption",
                "usage_grade": "strong",
            },
        ],
        orderbook_persistence_observable=True,
        orderbook_semantics_summary={
            "near_wall": {"side": "bid"},
            "support": None,
            "resistance": None,
            "persistence": None,
            "summary_slots_present": ["near_wall"],
            "summary_slots_count": 1,
            "active_event_count": 1,
            "active_event_names": ["near_wall_continued"],
            "active_event_contracts": [
                {
                    "contract_source": "l3_event_usage_policy",
                    "event_name": "near_wall_continued",
                    "event_family": "wall",
                    "usage_grade": "strong",
                    "interpretation_bucket": "allow_structural_use",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "confidence": 0.85,
                    "trust_bucket": "trusted",
                    "consumer_allowed": ["ui", "alert", "ai", "strategy", "execution"],
                    "actionability": "actionable",
                    "forecast_horizon_hint": "short",
                    "half_life_sec": 30,
                    "invalidates_on": ["series_boundary", "reanchor_required"],
                    "evidence_refs": [],
                    "side": "bid",
                }
            ],
        },
        best_bid=100.5,
        best_ask=101.0,
        spread=0.5,
        near_zone_bids=[{"price": 100.5, "size": 0.7}],
        near_zone_asks=[{"price": 101.0, "size": 1.5}],
        mid_price=100.75,
        top_book_summary={"best_bid": 100.5, "best_ask": 101.0, "spread": 0.5},
        near_zone_liquidity_summary={"bid_size_total": 1.7, "ask_size_total": 1.5},
        imbalance_summary={"near_size_imbalance": 0.0625},
        zone_density_metadata={"mode": "hybrid"},
        source_series_id="bf-sess-1:series:100",
        source_stream_session_id="bf-sess-1",
    )

    writer = MarketStateWriter()
    out = writer.write(
        cfg=cfg,
        state_type="market.overview",
        record=record,
        date_str="2026-03-16",
        part_no=1,
    )
    assert out.exists()

    summary = load_latest_market_summary(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert summary.summary_type == "market_summary"
    assert summary.exchange == "bitflyer"
    assert summary.symbol_raw == "BTC_JPY"
    assert summary.market_uid == "bitflyer.spot.BTC_JPY"
    assert summary.source_kind == "market_state_preferred"
    assert summary.source_series_id == "bf-sess-1:series:100"
    assert summary.trust_state == "trusted"
    assert summary.continuity_state == "continuous"
    assert summary.interpretation_bucket == "allow_structural_use"
    assert summary.interpretation_reason == "healthy_continuity"
    assert summary.semantic_summary_source == "market_state_semantic_usage_summary"
    assert summary.semantic_contract_source == "l3_event_usage_policy"
    assert summary.semantic_meaning_version == "l3_event_usage_policy.v1alpha1"
    assert summary.semantic_observer_status == "healthy"
    assert summary.semantic_observer_present is True
    assert summary.semantic_usage_summary_present is True
    assert summary.semantic_contract_rows_present is True
    assert summary.semantic_contract_rows_count == 2
    assert summary.semantic_runtime_wiring_status == "wired"
    assert summary.semantic_total_rows == 2
    assert summary.semantic_active_event_count == 1
    assert summary.semantic_mapped_event_count == 1
    assert summary.semantic_unknown_event_count == 0
    assert summary.semantic_event_family_distribution == {"wall": 2}
    assert summary.semantic_trust_bucket_distribution == {"trusted": 2}
    assert summary.semantic_interpretation_bucket_distribution == {"observe_only": 2}
    assert summary.semantic_consumer_distribution == {"health": 2}
    assert summary.semantic_usage_contract_rows[0]["contract_source"] == "l3_event_usage_policy"
    assert summary.semantic_usage_contract_rows[0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary.semantic_usage_contract_rows[0]["event_family"] == "wall"
    assert summary.semantic_usage_contract_rows[0]["usage_grade"] == "strong"
    assert summary.orderbook_active_event_names == ["near_wall_continued"]
    assert summary.orderbook_active_event_count == 1
    assert summary.orderbook_active_event_contracts[0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary.orderbook_active_event_contracts[0]["contract_source"] == "l3_event_usage_policy"
    assert summary.orderbook_active_event_contracts[0]["trust_bucket"] == "trusted"
    assert summary.orderbook_active_event_contracts[0]["forecast_horizon_hint"] == "short"
    assert summary.orderbook_active_event_contracts[0]["half_life_sec"] == 30
    assert summary.orderbook_summary_slots_present == ["near_wall"]
    assert summary.orderbook_summary_slots_count == 1
    assert summary.orderbook_near_wall_present is True
    assert summary.orderbook_support_present is False
    assert summary.orderbook_resistance_present is False
    assert summary.orderbook_persistence_present is False
    assert summary.orderbook_wiring_status == "partial"
    assert summary.orderbook_contract_status_source == "orderbook_summary_inference"
    assert summary.orderbook_persistence_observable is True
    assert summary.notable_events is not None
    assert summary.alert_candidates is not None

    empty = load_latest_market_summary(exchange="other", symbol_raw="NONE")
    assert empty.summary_type == "market_summary"
    assert empty.source_kind == "unknown"
    assert empty.freshness == "UNKNOWN"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())