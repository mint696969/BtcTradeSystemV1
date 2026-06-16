# path: ./btcts_next/src/btcts/collector_vnext/tests/test_fx_public_rest_identity.py
# desc: Tests for SR-FX public REST execution-market identity separation.

from __future__ import annotations

from dataclasses import replace

from btcts.collector_vnext.config import CollectorConfig, MarketIdentity, load_config
from btcts.collector_vnext.fx_public_rest import execution_market_config, market_identity_payload


def test_execution_market_config_projects_legacy_fields_to_fx(monkeypatch) -> None:
    monkeypatch.delenv("BTCTS_EXECUTION_PRODUCT_CODE", raising=False)
    monkeypatch.delenv("BTCTS_EXECUTION_MARKET_UID", raising=False)
    cfg = load_config()

    fx_cfg = execution_market_config(cfg)

    assert cfg.symbol == "BTC_JPY"
    assert cfg.instrument_id == "bitflyer.spot.BTC_JPY"
    assert fx_cfg.market == "fx"
    assert fx_cfg.symbol == "FX_BTC_JPY"
    assert fx_cfg.instrument_id == "bitflyer.fx.FX_BTC_JPY"
    assert fx_cfg.reference_market.product_code == "BTC_JPY"
    assert fx_cfg.execution_market.product_code == "FX_BTC_JPY"


def test_execution_market_config_uses_explicit_execution_env(monkeypatch) -> None:
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    cfg = load_config()

    fx_cfg = execution_market_config(cfg)

    assert fx_cfg.symbol == "FX_BTC_JPY"
    assert fx_cfg.instrument_id == "bitflyer.fx.FX_BTC_JPY"


def test_market_identity_payload_marks_execution_market() -> None:
    market = MarketIdentity(
        role="execution",
        exchange="bitflyer",
        market_type="fx",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
    )

    payload = market_identity_payload(market, source="public_rest", request_class="public_rest_market_data")

    assert payload["exchange"] == "bitflyer"
    assert payload["product_code"] == "FX_BTC_JPY"
    assert payload["market_type"] == "fx"
    assert payload["market_role"] == "execution"
    assert payload["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert payload["source"] == "public_rest"
    assert payload["request_class"] == "public_rest_market_data"


def test_execution_market_projection_does_not_mutate_reference(monkeypatch) -> None:
    cfg = load_config()
    fx_cfg = execution_market_config(cfg)

    assert fx_cfg.reference_market.market_uid == "bitflyer.spot.BTC_JPY"
    assert fx_cfg.execution_market.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert fx_cfg.reference_market.market_uid != fx_cfg.execution_market.market_uid
