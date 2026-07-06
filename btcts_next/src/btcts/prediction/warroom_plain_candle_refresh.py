# path: ./btcts_next/src/btcts/prediction/warroom_plain_candle_refresh.py
# desc: Bounded latest-cache refresher for WarRoom plain trade-price candles. No UI/broker/order invocation.

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from btcts.prediction.warroom_plain_candle_cache import (
    WARROOM_PLAIN_CANDLE_CACHE_VERSION,
    WarRoomPlainCandleCacheMeta,
    write_plain_candle_cache_time_range,
)
from btcts.prediction.warroom_plain_candles import (
    DEFAULT_EXCHANGE,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_TRADES,
    DEFAULT_SYMBOL,
    DEFAULT_TIMEFRAME_SECONDS,
    WARROOM_PLAIN_CANDLES_VERSION,
    _last_json_record,
    _record_event_ts,
    market_trade_root,
)

WARROOM_PLAIN_CANDLE_REFRESH_VERSION = "warroom_plain_candle_refresh.2026_07_06.v1_latest_trade_to_cache"
DEFAULT_REFRESH_RANGE_MINUTES = 180
DEFAULT_LATEST_SCAN_DAYS = 7
DEFAULT_LATEST_SCAN_FILES_PER_DAY = 24


@dataclass(frozen=True)
class LatestMarketTradeTsMeta:
    ok: bool
    version: str
    source_root: str
    source_root_reason: str
    exchange: str
    symbol: str
    latest_ts_utc: str
    latest_part_file: str
    scanned_day_count: int
    scanned_file_count: int
    max_days: int
    max_files_per_day: int
    error: str | None = None
    read_only: bool = True
    broker_send_enabled: bool = False
    order_intent_submitted: bool = False
    prediction_invoked: bool = False
    classifier_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "version": self.version,
            "source_root": self.source_root,
            "source_root_reason": self.source_root_reason,
            "exchange": self.exchange,
            "symbol": self.symbol,
            "latest_ts_utc": self.latest_ts_utc,
            "latest_part_file": self.latest_part_file,
            "scanned_day_count": self.scanned_day_count,
            "scanned_file_count": self.scanned_file_count,
            "max_days": self.max_days,
            "max_files_per_day": self.max_files_per_day,
            "error": self.error,
            "read_only": self.read_only,
            "broker_send_enabled": self.broker_send_enabled,
            "order_intent_submitted": self.order_intent_submitted,
            "prediction_invoked": self.prediction_invoked,
            "classifier_invoked": self.classifier_invoked,
        }


@dataclass(frozen=True)
class WarRoomPlainCandleRefreshMeta:
    ok: bool
    version: str
    candle_core_version: str
    cache_version: str
    exchange: str
    symbol: str
    timeframe_sec: int
    range_minutes: int
    start_ts_utc: str
    end_ts_utc: str
    latest_trade_meta: dict[str, Any]
    cache_meta: dict[str, Any]
    error: str | None = None
    read_only: bool = True
    broker_send_enabled: bool = False
    order_intent_submitted: bool = False
    prediction_invoked: bool = False
    classifier_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "version": self.version,
            "candle_core_version": self.candle_core_version,
            "cache_version": self.cache_version,
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timeframe_sec": self.timeframe_sec,
            "range_minutes": self.range_minutes,
            "start_ts_utc": self.start_ts_utc,
            "end_ts_utc": self.end_ts_utc,
            "latest_trade_meta": self.latest_trade_meta,
            "cache_meta": self.cache_meta,
            "error": self.error,
            "read_only": self.read_only,
            "broker_send_enabled": self.broker_send_enabled,
            "order_intent_submitted": self.order_intent_submitted,
            "prediction_invoked": self.prediction_invoked,
            "classifier_invoked": self.classifier_invoked,
        }


def _iso_utc(ts: Any) -> str:
    value = pd.Timestamp(ts)
    if value.tzinfo is None:
        value = value.tz_localize("UTC")
    value = value.tz_convert("UTC")
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_dirs_desc(trade_root: Path, *, max_days: int) -> list[Path]:
    if not trade_root.exists():
        return []
    date_dirs = [path for path in trade_root.glob("date=*") if path.is_dir()]
    return sorted(date_dirs, key=lambda path: path.name, reverse=True)[: max(0, int(max_days))]


def find_latest_market_trade_ts(
    *,
    root: Path | None = None,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    max_days: int = DEFAULT_LATEST_SCAN_DAYS,
    max_files_per_day: int = DEFAULT_LATEST_SCAN_FILES_PER_DAY,
) -> tuple[pd.Timestamp | None, LatestMarketTradeTsMeta]:
    trade_root, root_reason = market_trade_root(root, exchange=exchange, symbol=symbol)
    scanned_days = 0
    scanned_files = 0
    if not trade_root.exists():
        meta = LatestMarketTradeTsMeta(
            ok=False,
            version=WARROOM_PLAIN_CANDLE_REFRESH_VERSION,
            source_root=str(trade_root),
            source_root_reason=root_reason,
            exchange=exchange,
            symbol=symbol,
            latest_ts_utc="",
            latest_part_file="",
            scanned_day_count=0,
            scanned_file_count=0,
            max_days=int(max_days),
            max_files_per_day=int(max_files_per_day),
            error="market_trade_root_missing",
        )
        return None, meta
    for date_dir in _date_dirs_desc(trade_root, max_days=max_days):
        scanned_days += 1
        part_files = sorted(date_dir.glob("part-*.jsonl"), reverse=True)[: max(0, int(max_files_per_day))]
        for part_file in part_files:
            scanned_files += 1
            record = _last_json_record(part_file)
            ts = _record_event_ts(record or {})
            if ts is None:
                continue
            meta = LatestMarketTradeTsMeta(
                ok=True,
                version=WARROOM_PLAIN_CANDLE_REFRESH_VERSION,
                source_root=str(trade_root),
                source_root_reason=root_reason,
                exchange=exchange,
                symbol=symbol,
                latest_ts_utc=_iso_utc(ts),
                latest_part_file=str(part_file),
                scanned_day_count=scanned_days,
                scanned_file_count=scanned_files,
                max_days=int(max_days),
                max_files_per_day=int(max_files_per_day),
                error=None,
            )
            return ts, meta
    meta = LatestMarketTradeTsMeta(
        ok=False,
        version=WARROOM_PLAIN_CANDLE_REFRESH_VERSION,
        source_root=str(trade_root),
        source_root_reason=root_reason,
        exchange=exchange,
        symbol=symbol,
        latest_ts_utc="",
        latest_part_file="",
        scanned_day_count=scanned_days,
        scanned_file_count=scanned_files,
        max_days=int(max_days),
        max_files_per_day=int(max_files_per_day),
        error="latest_market_trade_ts_not_found",
    )
    return None, meta


def refresh_latest_plain_candle_cache(
    *,
    raw_root: Path | None = None,
    cache_root: Path | None = None,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    range_minutes: int = DEFAULT_REFRESH_RANGE_MINUTES,
    max_files: int = DEFAULT_MAX_FILES,
    max_trades: int = DEFAULT_MAX_TRADES,
    latest_scan_days: int = DEFAULT_LATEST_SCAN_DAYS,
    latest_scan_files_per_day: int = DEFAULT_LATEST_SCAN_FILES_PER_DAY,
) -> WarRoomPlainCandleRefreshMeta:
    latest_ts, latest_meta = find_latest_market_trade_ts(
        root=raw_root,
        exchange=exchange,
        symbol=symbol,
        max_days=latest_scan_days,
        max_files_per_day=latest_scan_files_per_day,
    )
    if latest_ts is None:
        return WarRoomPlainCandleRefreshMeta(
            ok=False,
            version=WARROOM_PLAIN_CANDLE_REFRESH_VERSION,
            candle_core_version=WARROOM_PLAIN_CANDLES_VERSION,
            cache_version=WARROOM_PLAIN_CANDLE_CACHE_VERSION,
            exchange=exchange,
            symbol=symbol,
            timeframe_sec=int(timeframe_sec),
            range_minutes=int(range_minutes),
            start_ts_utc="",
            end_ts_utc="",
            latest_trade_meta=latest_meta.to_dict(),
            cache_meta={},
            error=latest_meta.error or "latest_ts_missing",
        )
    end_ts = pd.Timestamp(latest_ts).tz_convert("UTC")
    start_ts = end_ts - pd.Timedelta(minutes=max(1, int(range_minutes)))
    cache_meta: WarRoomPlainCandleCacheMeta = write_plain_candle_cache_time_range(
        raw_root=raw_root,
        cache_root=cache_root,
        start_ts=start_ts,
        end_ts=end_ts,
        exchange=exchange,
        symbol=symbol,
        timeframe_sec=timeframe_sec,
        max_range_minutes=max(1, int(range_minutes)),
        max_files=max_files,
        max_trades=max_trades,
    )
    return WarRoomPlainCandleRefreshMeta(
        ok=bool(cache_meta.ok),
        version=WARROOM_PLAIN_CANDLE_REFRESH_VERSION,
        candle_core_version=WARROOM_PLAIN_CANDLES_VERSION,
        cache_version=WARROOM_PLAIN_CANDLE_CACHE_VERSION,
        exchange=exchange,
        symbol=symbol,
        timeframe_sec=int(timeframe_sec),
        range_minutes=int(range_minutes),
        start_ts_utc=_iso_utc(start_ts),
        end_ts_utc=_iso_utc(end_ts),
        latest_trade_meta=latest_meta.to_dict(),
        cache_meta=cache_meta.to_dict(),
        error=None if cache_meta.ok else cache_meta.error or "cache_refresh_failed",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh WarRoom plain candle latest cache from D-hot market.trade.")
    parser.add_argument("--raw-root", default=None)
    parser.add_argument("--cache-root", default=None)
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--timeframe-sec", type=int, default=DEFAULT_TIMEFRAME_SECONDS)
    parser.add_argument("--range-minutes", type=int, default=DEFAULT_REFRESH_RANGE_MINUTES)
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--max-trades", type=int, default=DEFAULT_MAX_TRADES)
    parser.add_argument("--latest-scan-days", type=int, default=DEFAULT_LATEST_SCAN_DAYS)
    parser.add_argument("--latest-scan-files-per-day", type=int, default=DEFAULT_LATEST_SCAN_FILES_PER_DAY)
    args = parser.parse_args(argv)
    meta = refresh_latest_plain_candle_cache(
        raw_root=Path(args.raw_root) if args.raw_root else None,
        cache_root=Path(args.cache_root) if args.cache_root else None,
        exchange=args.exchange,
        symbol=args.symbol,
        timeframe_sec=args.timeframe_sec,
        range_minutes=args.range_minutes,
        max_files=args.max_files,
        max_trades=args.max_trades,
        latest_scan_days=args.latest_scan_days,
        latest_scan_files_per_day=args.latest_scan_files_per_day,
    )
    print(json.dumps(meta.to_dict(), ensure_ascii=False, indent=2))
    return 0 if meta.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
