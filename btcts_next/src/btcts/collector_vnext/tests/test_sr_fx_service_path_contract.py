# path: ./btcts_next/src/btcts/collector_vnext/tests/test_sr_fx_service_path_contract.py
# desc: SR-FX hot/cold/service path contract diagnostics tests. No broker calls.

from __future__ import annotations


def test_sr_fx_service_path_contract_separates_hot_runtime_from_service_data_root(monkeypatch, tmp_path) -> None:
    from btcts.collector_vnext.service_path_contract import build_sr_fx_service_path_contract

    service_root = tmp_path / "btc_ts"
    hot_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(service_root / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(service_root / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(service_root / "state"))
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(hot_root))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")

    contract = build_sr_fx_service_path_contract()
    data = contract.to_dict()

    assert contract.execution_product_code == "FX_BTC_JPY"
    assert contract.execution_market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert "symbol=FX_BTC_JPY" in data["execution_market_state_dir"]
    assert data["service_readable_market_state_root"].endswith("data\\market_state") or data["service_readable_market_state_root"].endswith("data/market_state")
    assert str(hot_root) in data["autotrade_runtime_root"]
    assert contract.read_only is True
    assert contract.would_send_to_broker is False
    assert "collector_data_root_points_to_autotrade_hot_runtime" not in contract.warnings
