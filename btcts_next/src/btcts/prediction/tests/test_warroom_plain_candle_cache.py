# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_plain_candle_cache.py
# desc: Tests WarRoom plain candle D-hot derived cache writer/reader with tmp roots only.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.warroom_plain_candle_cache import (  # noqa: E402
    WARROOM_PLAIN_CANDLE_CACHE_VERSION,
    latest_cache_paths,
    read_plain_candle_cache,
    write_plain_candle_cache_time_range,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _market_trade_path(root: Path, date: str, part: int = 1) -> Path:
    return root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / f"date={date}" / f"part-{part:05d}.jsonl"


def _record(ts: str, price: float, *, size: float = 0.1, trade_id: str = "") -> dict[str, object]:
    return {
        "event_ts": ts,
        "payload": {
            "trade_ts": ts,
            "price": price,
            "size": size,
            "side": "BUY",
            "trade_id": trade_id or f"tid-{ts}-{price}",
        },
    }


def test_write_and_read_plain_candle_cache_time_range(tmp_path: Path) -> None:
    raw_root = tmp_path / "hot"
    cache_root = tmp_path / "cache_hot"
    _write_jsonl(
        _market_trade_path(raw_root, "2026-07-06", 1),
        [
            _record("2026-07-06T12:00:01Z", 100.0, trade_id="a"),
            _record("2026-07-06T12:00:20Z", 105.0, trade_id="b"),
            _record("2026-07-06T12:01:01Z", 103.0, trade_id="c"),
        ],
    )
    meta = write_plain_candle_cache_time_range(
        raw_root=raw_root,
        cache_root=cache_root,
        start_ts="2026-07-06T12:00:00Z",
        end_ts="2026-07-06T12:02:00Z",
        max_files=1,
        max_trades=10,
    )
    assert meta.ok is True
    assert meta.version == WARROOM_PLAIN_CANDLE_CACHE_VERSION
    assert meta.candles_written == 2
    assert meta.broker_send_enabled is False
    assert meta.order_intent_submitted is False
    cache_path, meta_path = latest_cache_paths(cache_root)
    assert cache_path.exists()
    assert meta_path.exists()
    frame, read_meta = read_plain_candle_cache(cache_root)
    assert read_meta["read_ok"] is True
    assert len(frame) == 2
    assert list(frame["open"]) == [100.0, 103.0]
    assert list(frame["close"]) == [105.0, 103.0]
    assert read_meta["broker_send_enabled"] is False
    assert read_meta["prediction_invoked"] is False


def test_read_plain_candle_cache_can_tail_limit(tmp_path: Path) -> None:
    raw_root = tmp_path / "hot"
    cache_root = tmp_path / "cache_hot"
    _write_jsonl(
        _market_trade_path(raw_root, "2026-07-06", 1),
        [
            _record("2026-07-06T12:00:01Z", 100.0, trade_id="a"),
            _record("2026-07-06T12:01:01Z", 101.0, trade_id="b"),
            _record("2026-07-06T12:02:01Z", 102.0, trade_id="c"),
        ],
    )
    write_plain_candle_cache_time_range(
        raw_root=raw_root,
        cache_root=cache_root,
        start_ts="2026-07-06T12:00:00Z",
        end_ts="2026-07-06T12:03:00Z",
        max_files=1,
        max_trades=10,
    )
    frame, meta = read_plain_candle_cache(cache_root, max_candles=2)
    assert len(frame) == 2
    assert list(frame["time_utc"]) == ["2026-07-06T12:01:00Z", "2026-07-06T12:02:00Z"]
    assert meta["rows_returned"] == 2



def test_write_plain_candle_cache_does_not_clobber_existing_cache_on_empty_source(tmp_path: Path) -> None:
    raw_root = tmp_path / "hot"
    cache_root = tmp_path / "cache_hot"
    _write_jsonl(
        _market_trade_path(raw_root, "2026-07-06", 1),
        [
            _record("2026-07-06T12:00:01Z", 100.0, trade_id="a"),
            _record("2026-07-06T12:01:01Z", 101.0, trade_id="b"),
        ],
    )
    ok_meta = write_plain_candle_cache_time_range(
        raw_root=raw_root,
        cache_root=cache_root,
        start_ts="2026-07-06T12:00:00Z",
        end_ts="2026-07-06T12:02:00Z",
        max_files=1,
        max_trades=10,
    )
    assert ok_meta.ok is True
    before, _before_meta = read_plain_candle_cache(cache_root)
    assert len(before) == 2

    empty_meta = write_plain_candle_cache_time_range(
        raw_root=raw_root,
        cache_root=cache_root,
        start_ts="2026-07-06T13:00:00Z",
        end_ts="2026-07-06T13:02:00Z",
        max_files=1,
        max_trades=10,
    )
    assert empty_meta.ok is False
    after, after_meta = read_plain_candle_cache(cache_root)
    assert len(after) == 2
    assert list(after["time_utc"]) == list(before["time_utc"])
    assert after_meta["read_ok"] is True

def test_read_plain_candle_cache_missing_is_safe(tmp_path: Path) -> None:
    frame, meta = read_plain_candle_cache(tmp_path / "missing")
    assert frame.empty
    assert meta["ok"] is False
    assert meta["error"] == "cache_missing"
    assert meta["read_only"] is True
    assert meta["classifier_invoked"] is False
