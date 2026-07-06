# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/warroom_chart_data_server.py
# desc: L4 read-only localhost chart data server for WarRoom chart engine polling. Serves rolling candle store first, legacy latest cache as fallback only.

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import parse_qs, urlparse

import pandas as pd

from btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store import (
    WARROOM_CANDLE_STORE_VERSION,
    read_candle_store_chart_payload,
)
from btcts.prediction.warroom_plain_candle_cache import read_plain_candle_cache
from btcts.prediction.warroom_plain_candles import DEFAULT_EXCHANGE, DEFAULT_SYMBOL, DEFAULT_TIMEFRAME_SECONDS

WARROOM_CHART_DATA_SERVER_VERSION = "warroom_chart_data_server.2026_07_07.v3_l4_operator_ui_runtime"
WARROOM_CHART_DATA_SERVER_LAYER = "L4_CONSUMER_MODEL_OPERATOR_UI_RUNTIME"
WARROOM_CHART_DATA_SERVER_CANONICAL_MODULE = "btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server"
WARROOM_PLAIN_CANDLE_SERVER_VERSION = WARROOM_CHART_DATA_SERVER_VERSION
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_MAX_CANDLES = 720


def _utc_timestamp(value: object) -> pd.Timestamp | None:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts


def _iso_utc(value: object) -> str | None:
    ts = _utc_timestamp(value)
    if ts is None:
        return None
    return ts.isoformat().replace("+00:00", "Z")


def _iso_jst(value: object) -> str | None:
    ts = _utc_timestamp(value)
    if ts is None:
        return None
    return ts.tz_convert("Asia/Tokyo").isoformat()


def _epoch_seconds(value: object) -> int | None:
    ts = _utc_timestamp(value)
    if ts is None:
        return None
    return int(ts.timestamp())


def _as_float(value: object) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _as_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def cache_frame_to_chart_candles(frame: pd.DataFrame, *, max_candles: int = DEFAULT_MAX_CANDLES) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    required = {"time_utc", "open", "high", "low", "close"}
    if not required.issubset(set(frame.columns)):
        return []
    work = frame.copy().tail(max(0, int(max_candles)))
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(work.to_dict("records")):
        epoch = _epoch_seconds(row.get("time_utc"))
        if epoch is None:
            continue
        rows.append(
            {
                "time": epoch,
                "time_utc": _iso_utc(row.get("time_utc")),
                "time_jst": _iso_jst(row.get("time_utc")),
                "open": round(_as_float(row.get("open")), 6),
                "high": round(_as_float(row.get("high")), 6),
                "low": round(_as_float(row.get("low")), 6),
                "close": round(_as_float(row.get("close")), 6),
                "volume": round(_as_float(row.get("volume")), 8),
                "trade_count": _as_int(row.get("trade_count")),
                "candle_index": index,
                "candle_status": "forming" if index == len(work) - 1 else "closed",
                "source_role": "legacy_plain_trade_ohlc_cache",
            }
        )
    return rows


def _legacy_cache_payload(*, cache_root: Path | None, exchange: str, symbol: str, timeframe_sec: int, max_candles: int) -> dict[str, Any]:
    frame, meta = read_plain_candle_cache(cache_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec, max_candles=max_candles)
    candles = cache_frame_to_chart_candles(frame, max_candles=max_candles)
    return {
        "ok": bool(candles),
        "version": WARROOM_CHART_DATA_SERVER_VERSION,
        "server_role": "read_only_chart_engine_data_endpoint",
        "endpoint_family": "warroom_plain_candles_legacy_latest_fallback",
        "exchange": exchange,
        "symbol": symbol,
        "timeframe_sec": int(timeframe_sec),
        "candles": candles,
        "candle_count": len(candles),
        "meta": {**dict(meta), "server_poll_ok": bool(candles), "server_version": WARROOM_CHART_DATA_SERVER_VERSION, "server_source": "legacy_plain_candle_cache", "gap_policy": "absent_candles_no_synthetic_null"},
        "gap_policy": "absent_candles_no_synthetic_null",
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def build_plain_candle_server_payload(
    *,
    cache_root: Path | None = None,
    exchange: str = DEFAULT_EXCHANGE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS,
    max_candles: int = DEFAULT_MAX_CANDLES,
) -> dict[str, Any]:
    store_payload = read_candle_store_chart_payload(store_root=cache_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec, max_candles=max_candles)
    if store_payload.get("ok"):
        store_payload["server_version"] = WARROOM_CHART_DATA_SERVER_VERSION
        return store_payload
    legacy = _legacy_cache_payload(cache_root=cache_root, exchange=exchange, symbol=symbol, timeframe_sec=timeframe_sec, max_candles=max_candles)
    legacy["meta"]["store_fallback_reason"] = "candle_store_empty_or_missing"
    legacy["meta"]["candle_store_version"] = WARROOM_CANDLE_STORE_VERSION
    return legacy


class _Handler(BaseHTTPRequestHandler):
    cache_root: Path | None = None
    exchange: str = DEFAULT_EXCHANGE
    symbol: str = DEFAULT_SYMBOL
    timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS
    max_candles: int = DEFAULT_MAX_CANDLES

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def _send_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json({"ok": True, "options": True})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json({"ok": True, "version": WARROOM_CHART_DATA_SERVER_VERSION, "candle_store_version": WARROOM_CANDLE_STORE_VERSION, "read_only": True})
            return
        if parsed.path != "/warroom/plain-candles/latest":
            self._send_json({"ok": False, "error": "not_found", "read_only": True}, status=404)
            return
        params = parse_qs(parsed.query)
        max_candles = _as_int(params.get("max_candles", [self.max_candles])[0]) or self.max_candles
        timeframe_sec = _as_int(params.get("timeframe_sec", [self.timeframe_sec])[0]) or self.timeframe_sec
        payload = build_plain_candle_server_payload(cache_root=self.cache_root, exchange=self.exchange, symbol=self.symbol, timeframe_sec=timeframe_sec, max_candles=max_candles)
        self._send_json(payload, status=200 if payload.get("ok") else 503)


def run_server(*, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, cache_root: Path | None = None, exchange: str = DEFAULT_EXCHANGE, symbol: str = DEFAULT_SYMBOL, timeframe_sec: int = DEFAULT_TIMEFRAME_SECONDS, max_candles: int = DEFAULT_MAX_CANDLES) -> None:
    _Handler.cache_root = cache_root
    _Handler.exchange = exchange
    _Handler.symbol = symbol
    _Handler.timeframe_sec = int(timeframe_sec)
    _Handler.max_candles = int(max_candles)
    server = ThreadingHTTPServer((host, int(port)), _Handler)
    print(json.dumps({"ok": True, "version": WARROOM_CHART_DATA_SERVER_VERSION, "candle_store_version": WARROOM_CANDLE_STORE_VERSION, "serving": f"http://{host}:{int(port)}/warroom/plain-candles/latest", "cache_root": str(cache_root) if cache_root is not None else None, "read_only": True, "broker_send_enabled": False, "order_intent_submitted": False, "prediction_invoked": False, "classifier_invoked": False}, ensure_ascii=False))
    server.serve_forever()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve WarRoom rolling candle store as a read-only localhost chart endpoint.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--cache-root", default=None)
    parser.add_argument("--exchange", default=DEFAULT_EXCHANGE)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--timeframe-sec", type=int, default=DEFAULT_TIMEFRAME_SECONDS)
    parser.add_argument("--max-candles", type=int, default=DEFAULT_MAX_CANDLES)
    args = parser.parse_args(argv)
    run_server(host=args.host, port=args.port, cache_root=Path(args.cache_root) if args.cache_root else None, exchange=args.exchange, symbol=args.symbol, timeframe_sec=args.timeframe_sec, max_candles=args.max_candles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
