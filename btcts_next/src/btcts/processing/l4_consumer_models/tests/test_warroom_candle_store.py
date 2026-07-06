# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_warroom_candle_store.py
# desc: Verify rolling WarRoom candle store closed/forming and gap policy.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui import warroom_candle_store as candle_store_module  # noqa: E402
from btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store import (  # noqa: E402
    DEFAULT_TIMEFRAMES_SEC,
    WARROOM_CANDLE_STORE_VERSION,
    _merge_record,
    read_candle_store_chart_payload,
    update_candle_store_from_latest_part,
)


def test_timeframes_include_manual_trade_chart_set() -> None:
    assert DEFAULT_TIMEFRAMES_SEC == (60, 300, 900, 1800, 3600, 86400)


def test_merge_record_keeps_open_and_updates_ohlcv_for_forming_candle() -> None:
    base = {"time": 100, "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5, "volume": 1.0, "trade_count": 2}
    incoming = {"time": 100, "open": 10.5, "high": 12.0, "low": 8.5, "close": 11.5, "volume": 2.0, "trade_count": 3}
    merged = _merge_record(base, incoming, timeframe_sec=60, status="forming")
    assert merged is not None
    assert merged["open"] == 10.0
    assert merged["high"] == 12.0
    assert merged["low"] == 8.5
    assert merged["close"] == 11.5
    assert merged["volume"] == 3.0
    assert merged["trade_count"] == 5
    assert merged["candle_status"] == "forming"


def test_empty_store_returns_no_candles_without_gap_error(tmp_path: Path) -> None:
    payload = read_candle_store_chart_payload(store_root=tmp_path, max_candles=10)
    assert payload["ok"] is False
    assert payload["candles"] == []
    assert payload["gap_policy"] == "absent_candles_no_synthetic_null"
    assert payload["meta"]["missing_periods_error"] is False


def test_update_missing_raw_root_is_safe_error_payload(tmp_path: Path) -> None:
    payload = update_candle_store_from_latest_part(raw_root=tmp_path / "missing", store_root=tmp_path)
    assert payload["ok"] is False
    assert payload["read_only_source"] is True
    assert payload["broker_send_enabled"] is False
    assert payload["prediction_invoked"] is False


def test_version_declared() -> None:
    assert WARROOM_CANDLE_STORE_VERSION.startswith("warroom_candle_store.")


def test_candle_store_is_canonical_l4_operator_ui_module() -> None:
    import btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store as module

    assert module.WARROOM_CANDLE_STORE_LAYER == "L4_CONSUMER_MODEL_OPERATOR_UI"
    assert module.WARROOM_CANDLE_STORE_CANONICAL_MODULE == "btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store"


def test_read_trade_rows_from_stored_offset_keeps_first_appended_line(tmp_path: Path, monkeypatch) -> None:
    part = tmp_path / "part-00001.jsonl"
    first = b"{\"id\":1}\n"
    second = b"{\"id\":2}\n"
    part.write_bytes(first + second)

    monkeypatch.setattr(candle_store_module, "_json_record_from_line", lambda line: {"raw": line.decode("utf-8").strip()})
    monkeypatch.setattr(
        candle_store_module,
        "market_trade_record_to_trade_row",
        lambda record, source_file: {"record": record["raw"], "source_file": source_file},
    )

    rows, new_offset, lines_read, tail_bootstrap = candle_store_module._read_trade_rows_from_offset(
        part,
        offset=len(first),
        max_bootstrap_bytes=1024,
    )

    assert tail_bootstrap is False
    assert lines_read == 1
    assert rows == [{"record": '{"id":2}', "source_file": str(part)}]
    assert new_offset == len(first + second)

