# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge_prediction_tactic.py
# desc: Verify market_state_bridge can materialize shared tactic proposal payloads safely for operator UI consumers.

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_state_bridge import (  # noqa: E402
    load_prediction_tactic_proposal_payload,
)
from btcts.market_engine.config import MarketEngineConfig  # noqa: E402
from btcts.market_engine.market_state.schema import MarketStateRecord  # noqa: E402
from btcts.market_engine.market_state.writer import MarketStateWriter  # noqa: E402
from btcts.market_engine.types import BoundaryReason, TrustState  # noqa: E402


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_ui_market_state_bridge_prediction_tactic_test"
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
            "total_rows": 1,
            "active_event_count": 1,
            "mapped_event_count": 1,
            "unknown_event_count": 0,
            "event_family_distribution": {"wall": 1},
            "trust_bucket_distribution": {"trusted": 1},
            "interpretation_bucket_distribution": {"observe_only": 1},
            "consumer_distribution": {"health": 1},
        },
        semantic_usage_contract_rows=[
            {
                "contract_source": "l3_event_usage_policy",
                "interpretation_bucket": "allow_structural_use",
                "meaning_version": "l3_event_usage_policy.v1alpha1",
                "event_family": "wall",
                "usage_grade": "strong",
            }
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
                    "consumer_allowed": [
                        "ui",
                        "alert",
                        "ai",
                        "strategy",
                        "execution",
                    ],
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

    payload = load_prediction_tactic_proposal_payload(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
    )
    assert payload["proposal_type"] == "scenario_tactic_proposal_output"
    assert payload["source_kind"] == "prediction_scenario_output"
    assert payload["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert payload["scenario_regime"] != ""
    assert payload["primary_tactic_key"] in {
        "observe_only",
        "tighten_entry_gate",
        "cautious_probe",
        "continuation_follow",
        "reversal_prepare",
        "defensive_reduce_risk",
        "maintain_no_trade",
    }
    assert isinstance(payload["candidate_tactics"], tuple)
    assert len(payload["candidate_tactics"]) >= 1
    assert isinstance(payload["candidate_tactics"][0], dict)
    assert payload["diagnostics"]["builder_type"] == (
        "operator_ui_market_state_bridge"
    )
    assert payload["diagnostics"]["bridge_type"] == (
        "prediction_tactic_proposal_payload"
    )
    assert payload["diagnostics"]["parameter_trace"]["active_set_id"].endswith(
        "_phase4a_default"
    )
    assert payload["explanation_trace"]["trace_type"] == (
        "scenario_tactic_explanation_trace"
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())