# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_sr_fx_operator_ui_execution_market_bridge.py
# desc: Operator UI / WorkRoom bridge can read configured SR-FX execution market as first-class service input.

from __future__ import annotations

from datetime import datetime, timezone
import os

from btcts.apps.operator_ui.components.market_state_bridge import (
    execution_market_context,
    load_execution_market_overview,
    load_execution_market_prediction_summary_status_payload,
    load_execution_market_summary_status_payload,
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
        continuity_state="continuous",
        interpretation_bucket="allow_structural_use",
        interpretation_reason="sr_fx_execution_market_service_input",
        interpretation_policy={"execution_market_input": True, "review_required": False},
        semantic_observer_status="healthy",
        semantic_usage_summary={
            "source_kind": "sr_fx_execution_market_service_input",
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
            "consumer_distribution": {"workroom": 1, "operator_ui": 1, "autotrade": 1},
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
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        mid_price=100.5,
        price=100.5,
        imbalance=0.25,
        trade_delta=-0.5,
        near_zone_bids=[{"price": 100.0, "size": 2.0}],
        near_zone_asks=[{"price": 101.0, "size": 1.2}],
        top_book_summary={"best_bid": 100.0, "best_ask": 101.0, "spread": 1.0, "mid_price": 100.5},
        near_zone_liquidity_summary={"bid_size_total": 2.0, "ask_size_total": 1.2},
        imbalance_summary={"near_size_imbalance": 0.25},
        zone_density_metadata={"mode": "unit"},
        source_series_id="unit:fx:series:1",
        source_stream_session_id="unit:fx",
    )
    MarketStateWriter().write(cfg=cfg, state_type="market.overview", record=record, date_str="2026-06-14", part_no=1)


def _write_fx_rest_baseline_market_state() -> None:
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
        best_bid=200.0,
        best_ask=201.0,
        spread=1.0,
        mid_price=200.5,
        price=200.5,
        imbalance=0.35,
        trade_delta=0.75,
        near_zone_bids=[{"price": 200.0, "size": 3.0}],
        near_zone_asks=[{"price": 201.0, "size": 2.0}],
        top_book_summary={"best_bid": 200.0, "best_ask": 201.0, "spread": 1.0, "mid_price": 200.5},
        near_zone_liquidity_summary={"bid_size_total": 3.0, "ask_size_total": 2.0},
        imbalance_summary={"near_size_imbalance": 0.35},
        zone_density_metadata={"mode": "unit_rest_baseline"},
        source_series_id="unit:fx:rest:series:2",
        source_stream_session_id="unit:fx:rest",
    )
    MarketStateWriter().write(cfg=cfg, state_type="market.overview", record=record, date_str="2026-06-14", part_no=1)


def test_operator_ui_execution_market_bridge_reads_configured_sr_fx_market(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")
    assert str(tmp_path / "data") in os.environ.get("BTC_TS_DATA_DIR", "")
    _write_fx_market_state()

    ctx = execution_market_context()
    overview = load_execution_market_overview()
    summary_payload = load_execution_market_summary_status_payload()
    prediction_payload = load_execution_market_prediction_summary_status_payload(include_health_caution=False)

    assert ctx["symbol_raw"] == "FX_BTC_JPY"
    assert ctx["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert ctx["read_only"] is True
    assert ctx["would_send_to_broker"] is False

    assert overview["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert overview["symbol_raw"] == "FX_BTC_JPY"
    assert overview["service_input_role"] == "execution_market"
    assert overview["trade_delta"] == -0.5
    assert overview["imbalance"] == 0.25

    assert summary_payload["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert summary_payload["symbol_raw"] == "FX_BTC_JPY"
    assert summary_payload["service_input_role"] == "execution_market"
    assert summary_payload["execution_product_code"] == "FX_BTC_JPY"
    assert summary_payload["execution_market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert summary_payload["read_only"] is True
    assert summary_payload["would_send_to_broker"] is False

    assert prediction_payload["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert prediction_payload["service_input_role"] == "execution_market"
    assert prediction_payload["execution_product_code"] == "FX_BTC_JPY"
    assert prediction_payload["execution_market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert prediction_payload["read_only"] is True
    assert prediction_payload["would_send_to_broker"] is False



def test_operator_ui_execution_market_bridge_prefers_newer_rest_baseline_over_older_continuous(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")

    _write_fx_market_state()
    _write_fx_rest_baseline_market_state()

    overview = load_execution_market_overview()
    summary_payload = load_execution_market_summary_status_payload()

    assert overview["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert overview["symbol_raw"] == "FX_BTC_JPY"
    assert overview["continuity_state"] == "rest_baseline_snapshot"
    assert overview["source_series_id"] == "unit:fx:rest:series:2"
    assert overview["best_bid"] == 200.0
    assert overview["trade_delta"] == 0.75
    assert summary_payload["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert summary_payload["source_series_id"] == "unit:fx:rest:series:2"
    assert summary_payload["service_input_role"] == "execution_market"
