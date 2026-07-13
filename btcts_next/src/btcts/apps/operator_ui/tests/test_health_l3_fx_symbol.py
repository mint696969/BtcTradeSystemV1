# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_l3_fx_symbol.py
# desc: Verifies Layer3 Health reads the FX_BTC_JPY symbol.

from __future__ import annotations

from pathlib import Path

SERVICE = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui/health_data_service.py"
MARKET_STATE_SERVICE = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui/market_state_service.py"


def test_health_layer3_reads_current_fx_market_explicitly() -> None:
    text = SERVICE.read_text(encoding="utf-8-sig")

    assert 'HEALTH_MARKET_SYMBOL_RAW = "FX_BTC_JPY"' in text
    assert text.count("load_latest_market_state(symbol_raw=HEALTH_MARKET_SYMBOL_RAW)") == 2
    assert text.count("market_state_diagnostics(symbol_raw=HEALTH_MARKET_SYMBOL_RAW)") == 2
    assert "load_latest_market_state()" not in text
    assert "market_state_diagnostics()" not in text


def test_generic_market_state_service_defaults_remain_unchanged() -> None:
    text = MARKET_STATE_SERVICE.read_text(encoding="utf-8-sig")

    assert 'symbol_raw: str = "BTC_JPY"' in text
    assert 'symbol_raw: str = "FX_BTC_JPY"' not in text
