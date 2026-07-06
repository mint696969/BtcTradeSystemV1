# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_plain_candles.py
# desc: Tests bounded WarRoom plain trade-price candle core without reading real D-hot files.

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.warroom_plain_candles import (  # noqa: E402
    WARROOM_PLAIN_CANDLES_VERSION,
    build_trade_ohlc,
    candle_records,
    load_market_trade_rows_time_range,
    load_plain_trade_candles_time_range,
    market_trade_record_to_trade_row,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _market_trade_path(root: Path, date: str, part: int = 1) -> Path:
    return root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / f"date={date}" / f"part-{part:05d}.jsonl"


def _record(ts: str, price: float, *, size: float = 0.1, side: str = "BUY", trade_id: str = "") -> dict[str, object]:
    return {
        "event_ts": ts,
        "payload": {
            "trade_ts": ts,
            "price": price,
            "size": size,
            "side": side,
            "trade_id": trade_id or f"tid-{ts}-{price}",
        },
    }


def test_market_trade_record_to_trade_row_uses_payload_price_only() -> None:
    row = market_trade_record_to_trade_row(_record("2026-07-06T12:00:01Z", 100.0, size=0.2, side="SELL"), source_file="sample.jsonl")
    assert row is not None
    assert row["ts"] == pd.Timestamp("2026-07-06T12:00:01Z")
    assert row["price"] == 100.0
    assert row["size"] == 0.2
    assert row["side"] == "SELL"
    assert row["source_file"] == "sample.jsonl"


def test_build_trade_ohlc_is_plain_trade_price_only() -> None:
    trades = pd.DataFrame(
        [
            {"ts": "2026-07-06T12:00:01Z", "price": 100.0, "size": 0.1},
            {"ts": "2026-07-06T12:00:20Z", "price": 105.0, "size": 0.2},
            {"ts": "2026-07-06T12:00:59Z", "price": 99.0, "size": 0.3},
            {"ts": "2026-07-06T12:01:01Z", "price": 102.0, "size": 0.4},
        ]
    )
    candles = build_trade_ohlc(trades, timeframe_sec=60)
    assert len(candles) == 2
    first = candles.iloc[0]
    assert first["open"] == 100.0
    assert first["high"] == 105.0
    assert first["low"] == 99.0
    assert first["close"] == 99.0
    assert round(float(first["volume"]), 6) == 0.6
    assert first["trade_count"] == 3
    assert first["source_family"] == "warroom_market_trade_plain_ohlc"


def test_load_plain_trade_candles_time_range_is_bounded_and_read_only(tmp_path: Path) -> None:
    root = tmp_path / "hot"
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 1),
        [
            _record("2026-07-06T10:00:00Z", 90.0),
            _record("2026-07-06T12:00:01Z", 100.0, trade_id="a"),
            _record("2026-07-06T12:00:30Z", 102.0, trade_id="b"),
            _record("2026-07-06T12:01:01Z", 101.0, trade_id="c"),
            _record("2026-07-06T12:02:01Z", 103.0, trade_id="d"),
        ],
    )
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 2),
        [
            _record("2026-07-06T12:03:01Z", 104.0, trade_id="e"),
        ],
    )
    candles, meta = load_plain_trade_candles_time_range(
        root=root,
        start_ts="2026-07-06T11:00:00Z",
        end_ts="2026-07-06T12:04:00Z",
        max_range_minutes=10,
        max_files=1,
        max_trades=10,
    )
    assert meta.version == WARROOM_PLAIN_CANDLES_VERSION
    assert meta.range_clamped is True
    assert meta.scanned_file_count == 1
    assert meta.candidate_file_count == 2
    assert meta.max_files == 1
    assert meta.broker_send_enabled is False
    assert meta.order_intent_submitted is False
    assert meta.prediction_invoked is False
    assert meta.classifier_invoked is False
    assert list(candles["ts"].dt.strftime("%H:%M")) == ["12:00", "12:01", "12:02"]
    assert candles.iloc[0]["open"] == 100.0
    assert candles.iloc[0]["high"] == 102.0
    assert candles.iloc[0]["close"] == 102.0
    assert meta.candles_returned == 3


def test_load_market_trade_rows_time_range_respects_max_trades(tmp_path: Path) -> None:
    root = tmp_path / "hot"
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 1),
        [
            _record("2026-07-06T12:00:00Z", 100.0, trade_id="a"),
            _record("2026-07-06T12:00:01Z", 101.0, trade_id="b"),
            _record("2026-07-06T12:00:02Z", 102.0, trade_id="c"),
        ],
    )
    trades, meta = load_market_trade_rows_time_range(
        root=root,
        start_ts="2026-07-06T12:00:00Z",
        end_ts="2026-07-06T12:01:00Z",
        max_files=1,
        max_trades=2,
    )
    assert len(trades) == 2
    assert meta.trades_read == 2
    assert meta.read_only is True



def test_load_plain_trade_candles_time_range_filters_part_files_by_event_span_before_max_files(tmp_path: Path) -> None:
    root = tmp_path / "hot"
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 1),
        [
            _record("2026-07-06T09:00:00Z", 90.0, trade_id="old-a"),
            _record("2026-07-06T09:01:00Z", 91.0, trade_id="old-b"),
        ],
    )
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 2),
        [
            _record("2026-07-06T12:00:00Z", 100.0, trade_id="new-a"),
            _record("2026-07-06T12:01:00Z", 101.0, trade_id="new-b"),
        ],
    )
    candles, meta = load_plain_trade_candles_time_range(
        root=root,
        start_ts="2026-07-06T11:59:00Z",
        end_ts="2026-07-06T12:02:00Z",
        max_files=1,
        max_trades=10,
    )
    assert meta.candidate_file_count == 1
    assert meta.scanned_file_count == 1
    assert list(candles["ts"].dt.strftime("%H:%M")) == ["12:00", "12:01"]
    assert candles.iloc[0]["open"] == 100.0

def test_candle_records_are_lightweight_chart_ready() -> None:
    candles = pd.DataFrame(
        [
            {"ts": pd.Timestamp("2026-07-06T12:00:00Z"), "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 3.0, "trade_count": 4, "timeframe_sec": 60, "source_family": "warroom_market_trade_plain_ohlc"}
        ]
    )
    records = candle_records(candles)
    assert records == [
        {
            "time": int(pd.Timestamp("2026-07-06T12:00:00Z").timestamp()),
            "time_utc": "2026-07-06T12:00:00Z",
            "candle_index": 0,
            "open": 1.0,
            "high": 2.0,
            "low": 0.5,
            "close": 1.5,
            "volume": 3.0,
            "trade_count": 4,
            "timeframe_sec": 60,
            "source_family": "warroom_market_trade_plain_ohlc",
        }
    ]
