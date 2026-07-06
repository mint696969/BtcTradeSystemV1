# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_plain_candle_refresh.py
# desc: Tests WarRoom plain candle latest-cache refresh core with tmp roots only.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.warroom_plain_candle_cache import read_plain_candle_cache  # noqa: E402
from btcts.prediction.warroom_plain_candle_refresh import (  # noqa: E402
    WARROOM_PLAIN_CANDLE_REFRESH_VERSION,
    find_latest_market_trade_ts,
    refresh_latest_plain_candle_cache,
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


def test_find_latest_market_trade_ts_scans_latest_date_and_part_first(tmp_path: Path) -> None:
    root = tmp_path / "hot"
    _write_jsonl(
        _market_trade_path(root, "2026-07-05", 1),
        [_record("2026-07-05T23:59:00Z", 90.0, trade_id="old")],
    )
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 1),
        [_record("2026-07-06T12:00:00Z", 100.0, trade_id="a")],
    )
    _write_jsonl(
        _market_trade_path(root, "2026-07-06", 2),
        [_record("2026-07-06T12:05:00Z", 105.0, trade_id="b")],
    )
    latest_ts, meta = find_latest_market_trade_ts(root=root, max_days=3, max_files_per_day=4)
    assert meta.ok is True
    assert meta.version == WARROOM_PLAIN_CANDLE_REFRESH_VERSION
    assert str(latest_ts) == "2026-07-06 12:05:00+00:00"
    assert meta.scanned_day_count == 1
    assert meta.scanned_file_count == 1
    assert meta.broker_send_enabled is False
    assert meta.prediction_invoked is False


def test_refresh_latest_plain_candle_cache_writes_latest_cache(tmp_path: Path) -> None:
    raw_root = tmp_path / "hot"
    cache_root = tmp_path / "cache_hot"
    _write_jsonl(
        _market_trade_path(raw_root, "2026-07-06", 1),
        [
            _record("2026-07-06T11:58:00Z", 98.0, trade_id="before"),
            _record("2026-07-06T12:00:01Z", 100.0, trade_id="a"),
            _record("2026-07-06T12:00:20Z", 105.0, trade_id="b"),
            _record("2026-07-06T12:01:01Z", 103.0, trade_id="c"),
            _record("2026-07-06T12:02:00Z", 104.0, trade_id="latest"),
        ],
    )
    meta = refresh_latest_plain_candle_cache(
        raw_root=raw_root,
        cache_root=cache_root,
        range_minutes=3,
        max_files=1,
        max_trades=20,
        latest_scan_days=2,
        latest_scan_files_per_day=3,
    )
    assert meta.ok is True
    assert meta.start_ts_utc == "2026-07-06T11:59:00Z"
    assert meta.end_ts_utc == "2026-07-06T12:02:00Z"
    assert meta.broker_send_enabled is False
    assert meta.order_intent_submitted is False
    frame, read_meta = read_plain_candle_cache(cache_root)
    assert read_meta["read_ok"] is True
    assert list(frame["time_utc"]) == ["2026-07-06T12:00:00Z", "2026-07-06T12:01:00Z", "2026-07-06T12:02:00Z"]
    assert list(frame["open"]) == [100.0, 103.0, 104.0]


def test_refresh_latest_plain_candle_cache_missing_source_is_safe(tmp_path: Path) -> None:
    meta = refresh_latest_plain_candle_cache(raw_root=tmp_path / "missing", cache_root=tmp_path / "cache_hot")
    assert meta.ok is False
    assert meta.error == "market_trade_root_missing"
    assert meta.read_only is True
    assert meta.classifier_invoked is False
