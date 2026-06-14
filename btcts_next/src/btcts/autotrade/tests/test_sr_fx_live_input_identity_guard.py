# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_live_input_identity_guard.py
# desc: SR-FX live input identity guard. Prevent silent spot BTC_JPY use when FX execution context is active.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _write_market_state_row(root: Path, *, symbol_raw: str, market_uid: str) -> Path:
    part = (
        root
        / "data"
        / "market_state"
        / "exchange=bitflyer"
        / f"symbol={symbol_raw}"
        / "type=market.overview"
        / "date=2026-06-14"
        / "part-00001.jsonl"
    )
    part.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    row = {
        "market_uid": market_uid,
        "exchange": "bitflyer",
        "symbol_raw": symbol_raw,
        "collector_ts": now,
        "exchange_ts": now,
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "best_bid": 100.0,
        "best_ask": 101.0,
        "spread": 1.0,
        "mid_price": 100.5,
        "source_series_id": "unit:series:1",
    }
    part.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    return part


def test_live_input_identity_guard_blocks_spot_reference_when_fx_execution_env_is_active(monkeypatch, tmp_path) -> None:
    from btcts.autotrade.read_model.live_input_adapter import live_input_adapter_diagnostics

    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    _write_market_state_row(tmp_path, symbol_raw="BTC_JPY", market_uid="bitflyer.spot.BTC_JPY")

    diag = live_input_adapter_diagnostics(exchange="bitflyer", symbol_raw="BTC_JPY", state_type="market.overview")

    assert diag.requested_market_role == "reference"
    assert diag.requested_symbol_raw == "BTC_JPY"
    assert diag.latest_row_symbol_raw == "BTC_JPY"
    assert diag.latest_row_market_uid == "bitflyer.spot.BTC_JPY"
    assert "live_input_symbol_differs_from_execution_product" in diag.blocked_by
    assert "live_input_row_symbol_differs_from_execution_product" in diag.blocked_by
    assert "live_input_row_market_uid_differs_from_execution_market_uid" in diag.blocked_by


def test_live_input_identity_guard_allows_matching_fx_execution_market(monkeypatch, tmp_path) -> None:
    from btcts.autotrade.read_model.live_input_adapter import live_input_adapter_diagnostics

    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    _write_market_state_row(tmp_path, symbol_raw="FX_BTC_JPY", market_uid="bitflyer.fx.FX_BTC_JPY")

    diag = live_input_adapter_diagnostics(exchange="bitflyer", symbol_raw="FX_BTC_JPY", state_type="market.overview")

    assert diag.requested_market_role == "execution"
    assert diag.requested_symbol_raw == "FX_BTC_JPY"
    assert diag.latest_row_symbol_raw == "FX_BTC_JPY"
    assert diag.latest_row_market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert "live_input_symbol_differs_from_execution_product" not in diag.blocked_by
    assert "live_input_row_symbol_differs_from_execution_product" not in diag.blocked_by
    assert "live_input_row_market_uid_differs_from_execution_market_uid" not in diag.blocked_by
