# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py
# desc: Small UI bridge test for reading latest market_state records into operator UI helpers.

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_overview,
    load_market_summary_bundle,
    load_market_summary_status_payload,
    load_market_summary_ui_bundle,
    load_market_summary_widget_model,
    load_prediction_summary_bundle,
    load_prediction_summary_status_payload,
    load_prediction_summary_ui_bundle,
    load_prediction_summary_widget_model,
    market_monitor_metrics,
    market_state_status_caption,
    market_summary_status_caption,
)
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_ui_market_state_bridge_test"
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

    loaded = load_market_overview(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert loaded["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert loaded["best_bid"] == 100.5
    assert loaded["best_ask"] == 101.0
    assert loaded["spread"] == 0.5

    metrics = market_monitor_metrics(loaded)
    assert metrics["best_bid"] == 100.5
    assert metrics["best_ask"] == 101.0
    assert metrics["spread"] == 0.5
    assert metrics["bid_depth"] == 1.7
    assert metrics["ask_depth"] == 1.5
    assert metrics["imbalance"] == 0.0625

    caption = market_state_status_caption(loaded)
    assert "trust=trusted" in caption
    assert "boundary=none" in caption
    assert "series=bf-sess-1:series:100" in caption

    summary = load_market_summary_bundle(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert summary.summary_type == "market_summary"
    assert summary.market_uid == "bitflyer.spot.BTC_JPY"
    assert summary.trust_state == "trusted"
    assert summary.continuity_state == "continuous"
    assert summary.interpretation_bucket == "allow_structural_use"

    summary_caption = market_summary_status_caption(summary)
    assert "freshness=" in summary_caption
    assert "trust=trusted" in summary_caption
    assert "semantic_wiring=wired" in summary_caption
    assert "semantic_contract=l3_event_usage_policy" in summary_caption
    assert "semantic_version=l3_event_usage_policy.v1alpha1" in summary_caption
    assert "orderbook_wiring=partial" in summary_caption
    assert "persistence_present=False" in summary_caption
    assert "persistence_observable=True" in summary_caption
    assert "family_rows=2" in summary_caption
    assert "semantic_active_events=1" in summary_caption
    assert "mapped_events=1" in summary_caption
    assert "unknown_events=0" in summary_caption
    assert "family_dist_keys=1" in summary_caption
    assert "trust_dist_keys=1" in summary_caption
    assert "interpretation_dist_keys=1" in summary_caption
    assert "consumer_dist_keys=1" in summary_caption
    assert "summary_slots=1" in summary_caption
    assert "active_events=1" in summary_caption
    assert "active_event_rows=1" in summary_caption
    assert "series=bf-sess-1:series:100" in summary_caption

    summary_payload = load_market_summary_status_payload(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert summary_payload["summary_type"] == "market_summary"
    assert summary_payload["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert summary_payload["trust_state"] == "trusted"
    assert summary_payload["continuity_state"] == "continuous"
    assert summary_payload["interpretation_bucket"] == "allow_structural_use"

    summary_ui_bundle = load_market_summary_ui_bundle(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert summary_ui_bundle["summary"].summary_type == "market_summary"
    assert summary_ui_bundle["summary"].market_uid == "bitflyer.spot.BTC_JPY"
    assert summary_ui_bundle["status_payload"]["semantic_runtime_wiring_status"] == "wired"
    assert summary_ui_bundle["widget_model"].semantic_wiring_key == "wired"
    assert summary_payload["semantic_summary_source"] == "market_state_semantic_usage_summary"
    assert summary_payload["semantic_contract_source"] == "l3_event_usage_policy"
    assert summary_payload["semantic_meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary_payload["semantic_observer_status"] == "healthy"
    assert summary_payload["semantic_observer_present"] is True
    assert summary_payload["semantic_usage_summary_present"] is True
    assert summary_payload["semantic_contract_rows_present"] is True
    assert summary_payload["semantic_contract_rows_count"] == 2
    assert summary_payload["semantic_runtime_wiring_status"] == "wired"
    assert summary_payload["semantic_total_rows"] == 2
    assert summary_payload["semantic_active_event_count"] == 1
    assert summary_payload["semantic_mapped_event_count"] == 1
    assert summary_payload["semantic_unknown_event_count"] == 0
    assert summary_payload["semantic_event_family_distribution"] == {"wall": 2}
    assert summary_payload["semantic_trust_bucket_distribution"] == {"trusted": 2}
    assert summary_payload["semantic_interpretation_bucket_distribution"] == {"observe_only": 2}
    assert summary_payload["semantic_consumer_distribution"] == {"health": 2}
    assert summary_payload["semantic_usage_contract_rows_kind"] == "event_family_contract_rows"
    assert summary_payload["semantic_usage_contract_rows_count"] == 2
    assert summary_payload["semantic_usage_contract_rows"][0]["contract_source"] == "l3_event_usage_policy"
    assert summary_payload["semantic_usage_contract_rows"][0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary_payload["orderbook_summary_slots_kind"] == "summary_slot_names"
    assert summary_payload["orderbook_summary_slots_count"] == 1
    assert summary_payload["orderbook_wiring_status"] == "partial"
    assert summary_payload["orderbook_contract_status_source"] == "orderbook_summary_inference"
    assert summary_payload["orderbook_persistence_observable"] is True
    assert summary_payload["orderbook_near_wall_present"] is True
    assert summary_payload["orderbook_support_present"] is False
    assert summary_payload["orderbook_resistance_present"] is False
    assert summary_payload["orderbook_persistence_present"] is False
    assert summary_payload["orderbook_summary_slots_present"] == ["near_wall"]
    assert summary_payload["orderbook_active_event_names"] == ["near_wall_continued"]
    assert summary_payload["orderbook_active_event_count"] == 1
    assert summary_payload["orderbook_active_event_compact_rows_kind"] == "active_event_stable_subset_rows"
    assert summary_payload["orderbook_active_event_compact_rows_count"] == 1
    assert summary_payload["orderbook_active_event_compact_rows"][0] == {
        "contract_source": "l3_event_usage_policy",
        "event_name": "near_wall_continued",
        "event_family": "wall",
        "meaning_version": "l3_event_usage_policy.v1alpha1",
        "usage_grade": "strong",
        "interpretation_bucket": "allow_structural_use",
        "trust_bucket": "trusted",
        "actionability": "actionable",
        "forecast_horizon_hint": "short",
        "half_life_sec": 30,
        "side": "bid",
    }
    assert summary_payload["orderbook_active_event_contracts_kind"] == "active_event_contract_rows"
    assert summary_payload["orderbook_active_event_contracts_count"] == 1
    assert summary_payload["orderbook_active_event_contracts"][0]["contract_source"] == "l3_event_usage_policy"
    assert summary_payload["orderbook_active_event_contracts"][0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert isinstance(summary_payload["notable_events"], list)
    assert isinstance(summary_payload["alert_candidates"], list)

    widget_model = load_market_summary_widget_model(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert widget_model.widget_kind == "market_summary"
    assert widget_model.freshness_key in {"LIVE", "QUIET", "STALE", "UNKNOWN"}
    assert widget_model.trust_key == "trusted"
    assert widget_model.continuity_key == "continuous"
    assert widget_model.interpretation_key == "allow_structural_use"
    assert widget_model.semantic_wiring_key == "wired"
    assert widget_model.semantic_observer_status_key == "healthy"
    assert widget_model.semantic_observer_present_key == "true"
    assert widget_model.semantic_usage_summary_present_key == "true"
    assert widget_model.semantic_contract_rows_present_key == "true"
    assert widget_model.semantic_summary_source_key == "market_state_semantic_usage_summary"
    assert widget_model.semantic_contract_source_key == "l3_event_usage_policy"
    assert widget_model.semantic_meaning_version_key == "l3_event_usage_policy.v1alpha1"
    assert widget_model.orderbook_wiring_key == "partial"
    assert widget_model.orderbook_contract_status_source_key == "orderbook_summary_inference"
    assert widget_model.semantic_rows_count == 2
    assert widget_model.semantic_total_rows == 2
    assert widget_model.semantic_active_event_count == 1
    assert widget_model.semantic_mapped_event_count == 1
    assert widget_model.semantic_unknown_event_count == 0
    assert widget_model.semantic_event_family_distribution == {"wall": 2}
    assert widget_model.semantic_trust_bucket_distribution == {"trusted": 2}
    assert widget_model.semantic_interpretation_bucket_distribution == {"observe_only": 2}
    assert widget_model.semantic_consumer_distribution == {"health": 2}
    assert widget_model.summary_slots_count == 1
    assert widget_model.orderbook_summary_slots_present == ["near_wall"]
    assert widget_model.orderbook_near_wall_present_key == "true"
    assert widget_model.orderbook_support_present_key == "false"
    assert widget_model.orderbook_resistance_present_key == "false"
    assert widget_model.active_event_count == 1
    assert widget_model.orderbook_active_event_names == ["near_wall_continued"]
    assert widget_model.persistence_present_key == "false"
    assert widget_model.persistence_observable_key == "true"
    assert widget_model.source_kind == "market_state_preferred"
    assert isinstance(widget_model.notable_tags, list)
    assert isinstance(widget_model.alert_tags, list)

    prediction_summary = load_prediction_summary_bundle(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
    )
    assert prediction_summary.prediction_type == "shared_prediction_summary"
    assert prediction_summary.market_uid == "bitflyer.spot.BTC_JPY"
    assert prediction_summary.horizon == "short"

    prediction_payload = load_prediction_summary_status_payload(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
    )
    assert prediction_payload["prediction_type"] == "shared_prediction_summary"
    assert prediction_payload["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert prediction_payload["horizon"] == "short"
    assert "confidence" in prediction_payload

    prediction_ui_bundle = load_prediction_summary_ui_bundle(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
    )
    assert prediction_ui_bundle["summary"].prediction_type == "shared_prediction_summary"
    assert prediction_ui_bundle["status_payload"]["prediction_type"] == "shared_prediction_summary"
    assert prediction_ui_bundle["widget_model"].widget_kind == "shared_prediction_summary"

    prediction_widget = load_prediction_summary_widget_model(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
    )
    assert prediction_widget.widget_kind == "shared_prediction_summary"
    assert prediction_widget.horizon_key == "short"
    assert prediction_widget.freshness_key in {"LIVE", "QUIET", "STALE", "UNKNOWN"}

    saved = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert saved["market_uid"] == "bitflyer.spot.BTC_JPY"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())