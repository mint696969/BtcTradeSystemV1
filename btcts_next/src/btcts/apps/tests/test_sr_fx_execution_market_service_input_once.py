# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_execution_market_service_input_once.py
# desc: App-level read-only SR-FX execution-market service input contract test.

from __future__ import annotations

from datetime import datetime, timezone

from btcts.apps.sr_fx_execution_market_service_input_once import (
    build_sr_fx_execution_market_service_input_payload,
)
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState


def _write_fx_market_state() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    cfg = MarketEngineConfig(
        exchange="bitflyer",
        symbol_raw="FX_BTC_JPY",
        instrument_id="bitflyer.fx.FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        profile_name="bitflyer",
        near_zone_levels=2,
        far_zone_levels=2,
        replay_batch_size=1000,
        write_market_state=True,
    )
    record = MarketStateRecord(
        market_uid="bitflyer.fx.FX_BTC_JPY",
        exchange="bitflyer",
        symbol_raw="FX_BTC_JPY",
        collector_ts=now,
        exchange_ts=now,
        trust_state=TrustState.TRUSTED,
        boundary_reason=BoundaryReason.NONE,
        continuity_state="rest_baseline_snapshot",
        interpretation_bucket="allow_structural_use",
        interpretation_reason="fx_public_rest_board_snapshot_baseline",
        interpretation_policy={"execution_market_input": True, "review_required": False},
        semantic_observer_status="healthy",
        semantic_usage_summary={
            "source_kind": "sr_fx_execution_market_service_input_app_test",
            "contract_source": "sr_fx_service_path_contract",
            "meaning_version": "sr_fx_execution_market_service_input.v1",
            "observer_status": "healthy",
            "total_rows": 1,
            "active_event_count": 0,
            "mapped_event_count": 0,
            "unknown_event_count": 0,
            "event_family_distribution": {},
            "trust_bucket_distribution": {"trusted": 1},
            "interpretation_bucket_distribution": {"allow_structural_use": 1},
            "consumer_distribution": {"workroom": 1, "operator_ui": 1, "autotrade": 1, "l4_consumer": 1},
        },
        semantic_usage_contract_rows=[],
        orderbook_persistence_observable=False,
        orderbook_semantics_summary={
            "near_wall": None,
            "support": None,
            "resistance": None,
            "persistence": None,
            "summary_slots_present": [],
            "summary_slots_count": 0,
            "active_event_count": 0,
            "active_event_names": [],
            "active_event_contracts": [],
        },
        best_bid=300.0,
        best_ask=301.0,
        spread=1.0,
        mid_price=300.5,
        price=300.5,
        imbalance=0.15,
        trade_delta=0.25,
        near_zone_bids=[{"price": 300.0, "size": 2.0}],
        near_zone_asks=[{"price": 301.0, "size": 1.2}],
        top_book_summary={"best_bid": 300.0, "best_ask": 301.0, "spread": 1.0, "mid_price": 300.5},
        near_zone_liquidity_summary={"bid_size_total": 2.0, "ask_size_total": 1.2},
        imbalance_summary={"near_size_imbalance": 0.15},
        zone_density_metadata={"mode": "unit"},
        source_series_id="unit:fx:app:series:1",
        source_stream_session_id="unit:fx:app",
    )
    MarketStateWriter().write(cfg=cfg, state_type="market.overview", record=record, date_str="2026-06-14", part_no=1)


def test_sr_fx_execution_market_service_input_once_payload_is_read_only(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")
    _write_fx_market_state()

    payload = build_sr_fx_execution_market_service_input_payload()
    contract = payload["contract"]

    assert payload["ok"] is True
    assert payload["stage"] == "sr_fx_execution_market_service_input_once"
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False
    assert payload["context"]["symbol_raw"] == "FX_BTC_JPY"
    assert payload["context"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert contract["contract_type"] == "execution_market_service_input"
    assert contract["service_input_role"] == "execution_market"
    assert contract["symbol_raw"] == "FX_BTC_JPY"
    assert contract["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert contract["blocked_by"] == []
    assert contract["read_only"] is True
    assert contract["would_send_to_broker"] is False
    assert "workroom" in contract["consumer_allowed"]
    assert "operator_ui" in contract["consumer_allowed"]
    assert "autotrade" in contract["consumer_allowed"]
    assert contract["diagnostics"]["entrypoint"] == "sr_fx_execution_market_service_input_once"
