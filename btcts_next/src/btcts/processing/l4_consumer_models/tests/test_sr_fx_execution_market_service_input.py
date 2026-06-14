# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_sr_fx_execution_market_service_input.py
# desc: Shared L4 execution-market service input contract tests for SR-FX consumers.

from __future__ import annotations

from btcts.processing.l4_consumer_models.shared import (
    MarketSummary,
    build_execution_market_service_input,
)


def _summary(**overrides):
    data = dict(
        summary_type="market_summary",
        exchange="bitflyer",
        symbol_raw="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        source_kind="market_state_preferred",
        source_series_id="unit:fx:rest:series:1",
        event_ts="2026-06-14T00:00:00Z",
        age_sec=2.0,
        freshness="LIVE",
        is_stale=False,
        trust_state="trusted",
        continuity_state="rest_baseline_snapshot",
        interpretation_bucket="allow_structural_use",
        interpretation_reason="fx_public_rest_board_snapshot_baseline",
        market_state_label=None,
        participation_state=None,
        liquidity_bias=None,
        semantic_runtime_wiring_status="partial",
        orderbook_wiring_status="missing",
    )
    data.update(overrides)
    return MarketSummary(**data)


def test_execution_market_service_input_is_read_only_fx_contract() -> None:
    contract = build_execution_market_service_input(_summary())
    data = contract.to_dict()

    assert data["contract_type"] == "execution_market_service_input"
    assert data["service_input_role"] == "execution_market"
    assert data["exchange"] == "bitflyer"
    assert data["symbol_raw"] == "FX_BTC_JPY"
    assert data["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
    assert data["blocked_by"] == []
    assert "workroom" in data["consumer_allowed"]
    assert "operator_ui" in data["consumer_allowed"]
    assert "autotrade" in data["consumer_allowed"]
    assert "freshness_usable" in data["capabilities"]
    assert "trusted_market_state" in data["capabilities"]
    assert "structural_use_allowed" in data["capabilities"]
    assert "semantic_context_available" in data["capabilities"]
    assert "execution_market_rest_baseline_not_continuous_ws_series" in data["warnings"]
    assert "orderbook_context_missing" in data["warnings"]


def test_execution_market_service_input_blocks_stale_or_untrusted_summary() -> None:
    contract = build_execution_market_service_input(
        _summary(
            freshness="STALE",
            is_stale=True,
            trust_state="provisional",
            interpretation_bucket="observe_only",
        )
    )

    assert contract.blocked_by == (
        "market_summary_stale",
        "market_summary_not_trusted",
        "market_summary_not_structural_use",
    )
    assert contract.read_only is True
    assert contract.would_send_to_broker is False
