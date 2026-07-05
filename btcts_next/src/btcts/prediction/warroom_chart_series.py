# path: ./btcts_next/src/btcts/prediction/warroom_chart_series.py
# desc: Deterministic WarRoom chart series builder. Non-UI, read-only, no broker/order/prediction invocation.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

from btcts.prediction.ohlcv import LOGIC_VERSION as BASE_OHLCV_LOGIC_VERSION
from btcts.prediction.ohlcv import aggregate_ohlcv_from_rows

WARROOM_CHART_SERIES_VERSION = "warroom_chart_series.2026_07_05.v1"
WARROOM_CHART_SOURCE_FAMILY = "warroom_market_state_mid_rows"
WARROOM_CHART_TIMEFRAME_SECONDS: dict[str, int] = {
    "Live": 60,
    "1分足": 60,
    "1時間足": 3600,
    "日足": 86400,
}


@dataclass(frozen=True)
class WarRoomChartSeriesMeta:
    version: str
    base_ohlcv_logic_version: str
    source_family: str
    mode: str
    timeframe_sec: int
    input_row_count: int
    usable_row_count: int
    candle_count: int
    latest_candle_forming: bool
    provisional: bool = True
    source_notice: str = "暫定market-state mid由来。D-hot履歴bootstrapと正式約定OHLCは未接続。"
    read_only: bool = True
    broker_send_enabled: bool = False
    prediction_invoked: bool = False
    classifier_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "base_ohlcv_logic_version": self.base_ohlcv_logic_version,
            "source_family": self.source_family,
            "mode": self.mode,
            "timeframe_sec": self.timeframe_sec,
            "input_row_count": self.input_row_count,
            "usable_row_count": self.usable_row_count,
            "candle_count": self.candle_count,
            "latest_candle_forming": self.latest_candle_forming,
            "provisional": self.provisional,
            "source_notice": self.source_notice,
            "read_only": self.read_only,
            "broker_send_enabled": self.broker_send_enabled,
            "prediction_invoked": self.prediction_invoked,
            "classifier_invoked": self.classifier_invoked,
        }


def _normalized_history_frame(history_frame: pd.DataFrame) -> pd.DataFrame:
    if history_frame.empty:
        return pd.DataFrame(columns=["ts", "role", "price", "sequence", "freshness_label"])
    required = {"ts", "role", "price"}
    if not required.issubset(set(history_frame.columns)):
        return pd.DataFrame(columns=["ts", "role", "price", "sequence", "freshness_label"])
    work = history_frame.copy()
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work["price"] = pd.to_numeric(work["price"], errors="coerce")
    if "sequence" not in work.columns:
        work["sequence"] = 0
    if "freshness_label" not in work.columns:
        work["freshness_label"] = ""
    work = work.dropna(subset=["ts", "price"])
    if work.empty:
        return pd.DataFrame(columns=["ts", "role", "price", "sequence", "freshness_label"])
    return work[["ts", "role", "price", "sequence", "freshness_label"]].copy()


def market_state_mid_rows(history_frame: pd.DataFrame) -> list[dict[str, Any]]:
    work = _normalized_history_frame(history_frame)
    if work.empty:
        return []
    rows: list[dict[str, Any]] = []
    quote_frame = work[work["role"].isin(["bid", "ask"])].copy()
    if not quote_frame.empty:
        pivot = quote_frame.pivot_table(index="ts", columns="role", values="price", aggfunc="last").sort_index()
        if "bid" in pivot.columns and "ask" in pivot.columns:
            pivot = pivot.dropna(subset=["bid", "ask"])
            for ts, row in pivot.iterrows():
                mid = float((row["bid"] + row["ask"]) / 2.0)
                rows.append(
                    {
                        "ts": ts.isoformat(),
                        "event_ts": ts.isoformat(),
                        "price": mid,
                        "mid_price": mid,
                        "size": 0.0,
                        "source_family": WARROOM_CHART_SOURCE_FAMILY,
                        "source_role": "mid_from_bid_ask",
                    }
                )
    direct_frame = work[work["role"].isin(["last", "price", "mid"])].sort_values("ts")
    for row in direct_frame.to_dict("records"):
        ts = row.get("ts")
        price = float(row.get("price") or 0.0)
        rows.append(
            {
                "ts": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                "event_ts": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                "price": price,
                "mid_price": price,
                "size": 0.0,
                "source_family": WARROOM_CHART_SOURCE_FAMILY,
                "source_role": str(row.get("role") or "price"),
            }
        )
    rows.sort(key=lambda item: str(item.get("event_ts") or item.get("ts") or ""))
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, float, str]] = set()
    for row in rows:
        key = (str(row.get("event_ts") or row.get("ts") or ""), float(row.get("price") or 0.0), str(row.get("source_role") or ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _direction(open_price: float, close_price: float) -> str:
    return "up" if close_price >= open_price else "down"


def build_warroom_chart_candles(history_frame: pd.DataFrame, *, mode: str, x_domain: tuple[pd.Timestamp, pd.Timestamp] | None = None) -> tuple[pd.DataFrame, WarRoomChartSeriesMeta]:
    timeframe_sec = WARROOM_CHART_TIMEFRAME_SECONDS.get(mode, 60)
    rows = market_state_mid_rows(history_frame)
    candles, diagnostics = aggregate_ohlcv_from_rows(
        rows,
        timeframes_sec=(timeframe_sec,),
        source_family=WARROOM_CHART_SOURCE_FAMILY,
        source_symbol="FX_BTC_JPY",
        source_venue="bitflyer",
    )
    out: list[dict[str, Any]] = []
    for candle in candles:
        start_ts = pd.to_datetime(candle.start_ts, utc=True, errors="coerce")
        if pd.isna(start_ts):
            continue
        out.append(
            {
                "ts": start_ts,
                "open": float(candle.open),
                "high": float(candle.high),
                "low": float(candle.low),
                "close": float(candle.close),
                "direction": _direction(float(candle.open), float(candle.close)),
                "count": int(candle.row_count),
                "volume": float(candle.volume),
                "trade_count": int(candle.trade_count),
                "source_role": WARROOM_CHART_SOURCE_FAMILY,
                "timeframe_sec": int(timeframe_sec),
                "timeframe_label": candle.timeframe.label,
                "gap": bool(candle.gap),
                "stale": bool(candle.stale),
                "warnings": ",".join(candle.warnings),
                "candle_status": "closed",
                "is_closed": True,
            }
        )
    frame = pd.DataFrame(out)
    if not frame.empty:
        frame = frame.sort_values("ts").reset_index(drop=True)
        frame.loc[frame.index == frame.index.max(), "candle_status"] = "forming"
        frame["is_closed"] = frame["candle_status"] == "closed"
        if x_domain is not None:
            start, end = x_domain
            visible = frame[(frame["ts"] >= start) & (frame["ts"] <= end)].copy()
            frame = visible if not visible.empty else frame.tail(12).copy()
    meta = WarRoomChartSeriesMeta(
        version=WARROOM_CHART_SERIES_VERSION,
        base_ohlcv_logic_version=BASE_OHLCV_LOGIC_VERSION,
        source_family=WARROOM_CHART_SOURCE_FAMILY,
        mode=mode,
        timeframe_sec=timeframe_sec,
        input_row_count=len(rows),
        usable_row_count=diagnostics.usable_row_count,
        candle_count=len(frame),
        latest_candle_forming=not frame.empty,
    )
    return frame, meta
