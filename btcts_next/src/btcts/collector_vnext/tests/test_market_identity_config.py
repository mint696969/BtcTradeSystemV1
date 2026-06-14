# path: ./btcts_next/src/btcts/collector_vnext/tests/test_market_identity_config.py
# desc: Tests for SR-FX reference/execution market identity config guards.

from __future__ import annotations

import pytest

from btcts.collector_vnext.config import (
    ConfigValidationError,
    MarketIdentity,
    load_config,
    validate_market_identities,
)


def test_default_config_separates_spot_reference_and_fx_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in [
        "BTCTS_REFERENCE_PRODUCT_CODE",
        "BTCTS_REFERENCE_MARKET_UID",
        "BTCTS_EXECUTION_PRODUCT_CODE",
        "BTCTS_BITFLYER_EXECUTION_PRODUCT_CODE",
        "BTCTS_EXECUTION_MARKET_UID",
        "BTCTS_EXECUTION_MARKET_TYPE",
    ]:
        monkeypatch.delenv(name, raising=False)

    cfg = load_config()

    assert cfg.reference_market.role == "reference_signal"
    assert cfg.reference_market.market_type == "spot"
    assert cfg.reference_market.product_code == "BTC_JPY"
    assert cfg.reference_market.market_uid == "bitflyer.spot.BTC_JPY"

    assert cfg.execution_market.role == "execution"
    assert cfg.execution_market.market_type == "fx"
    assert cfg.execution_market.product_code == "FX_BTC_JPY"
    assert cfg.execution_market.market_uid == "bitflyer.fx.FX_BTC_JPY"


def test_legacy_bitflyer_execution_product_env_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BTCTS_BITFLYER_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.delenv("BTCTS_EXECUTION_PRODUCT_CODE", raising=False)
    monkeypatch.delenv("BTCTS_EXECUTION_MARKET_UID", raising=False)

    cfg = load_config()

    assert cfg.execution_market.product_code == "FX_BTC_JPY"
    assert cfg.execution_market.market_uid == "bitflyer.fx.FX_BTC_JPY"


def test_execution_market_cannot_be_spot() -> None:
    ref = MarketIdentity(
        role="reference_signal",
        exchange="bitflyer",
        market_type="spot",
        product_code="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
    )
    exe = MarketIdentity(
        role="execution",
        exchange="bitflyer",
        market_type="spot",
        product_code="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
    )

    with pytest.raises(ConfigValidationError, match="must not be spot"):
        validate_market_identities(ref, exe)


def test_execution_market_uid_must_not_equal_reference_uid() -> None:
    ref = MarketIdentity(
        role="reference_signal",
        exchange="bitflyer",
        market_type="spot",
        product_code="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
    )
    exe = MarketIdentity(
        role="execution",
        exchange="bitflyer",
        market_type="fx",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
    )

    with pytest.raises(ConfigValidationError, match="spot market uid"):
        validate_market_identities(ref, exe)


def test_execution_identity_summary_is_explicit() -> None:
    cfg = load_config()
    summary = cfg.market_identity_summary()

    assert summary["reference_market"]["role"] == "reference_signal"  # type: ignore[index]
    assert summary["execution_market"]["role"] == "execution"  # type: ignore[index]
    assert summary["execution_market"]["market_uid"] != summary["reference_market"]["market_uid"]  # type: ignore[index]



def test_ws_ca_file_env_is_loaded(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    ca_file = tmp_path / "ca.pem"
    ca_file.write_text("unit", encoding="utf-8")
    monkeypatch.setenv("BTCTS_WS_CA_FILE", str(ca_file))

    cfg = load_config()

    assert cfg.ws_ca_file == ca_file
    assert cfg.ws_ssl_verify is True
