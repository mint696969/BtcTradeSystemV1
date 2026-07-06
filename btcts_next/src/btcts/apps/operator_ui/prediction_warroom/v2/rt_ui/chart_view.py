# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/chart_view.py
# desc: WarRoom v2 realtime bottom chart renderer. Candlestick-like price context with bid/ask board layers and read-only overlays.

from __future__ import annotations

import os
import re
from typing import Any, Mapping

import pandas as pd

from btcts.prediction.warroom_chart_history_bootstrap import WARROOM_CHART_DHOT_BOOTSTRAP_VERSION
from btcts.prediction.warroom_plain_candle_cache import (
    WARROOM_PLAIN_CANDLE_CACHE_VERSION,
    read_plain_candle_cache,
)
from btcts.prediction.warroom_chart_series import (
    WARROOM_CHART_SERIES_VERSION,
    build_warroom_chart_candles,
)
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.chart_timeframe_view import (
    CHART_TIMEFRAME_VIEW_VERSION,
    ChartDisplayConfig,
    chart_x_domain,
    prepare_chart_display_frame,
    select_chart_display_config,
)
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.interactive_chart import (
    INTERACTIVE_CHART_COMPONENT_VERSION,
    render_interactive_candle_chart,
)

BOTTOM_CHART_POLISH_VERSION = "warroom_v2_bottom_chart_polish.2026_07_06.v15_base_candle_freshness"
_PRICE_RE = re.compile(r"(?:best_ask|best_bid|last_price|spread)=([0-9]+(?:\.[0-9]+)?)")
_NAMED_PRICE_RE = re.compile(r"(best_ask|best_bid|last_price|spread)=([0-9]+(?:\.[0-9]+)?)")
CHART_HISTORY_SESSION_STATE_KEY = "warroom_v2_bottom_chart_history_rows"
CHART_DHOT_BOOTSTRAP_SESSION_STATE_KEY = "warroom_v2_bottom_chart_dhot_bootstrap"
CHART_HISTORY_LIMIT = 1440
PLAIN_CANDLE_CACHE_MAX_CANDLES = 720
PLAIN_CANDLE_CACHE_MODES = {"Live", "1分足"}
DEFAULT_CHART_DATA_ENDPOINT = "http://127.0.0.1:8765/warroom/plain-candles/latest"
CHART_DATA_ENDPOINT_ENV = "WARROOM_PLAIN_CANDLE_CHART_ENDPOINT"
CHART_DATA_POLL_INTERVAL_MS = 3000


def _as_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        if isinstance(value, str) and value.strip():
            return float(value)
    except ValueError:
        return None
    return None


def _series_role(topic: str) -> str:
    topic_l = topic.lower()
    if "best_ask" in topic_l or topic_l.endswith("ask"):
        return "ask"
    if "best_bid" in topic_l or topic_l.endswith("bid"):
        return "bid"
    if "last_price" in topic_l or "trades" in topic_l:
        return "last"
    if "mid" in topic_l:
        return "mid"
    return "price"


def _append_price(rows: list[dict[str, Any]], *, updated_at_ms: int, topic: str, price: float, sequence: int, freshness: str) -> None:
    if updated_at_ms <= 0:
        return
    rows.append(
        {
            "ts": pd.to_datetime(updated_at_ms, unit="ms", utc=True),
            "topic": topic,
            "role": _series_role(topic),
            "price": float(price),
            "sequence": int(sequence),
            "freshness_label": freshness,
        }
    )


def chart_rows_to_frame(packet: Mapping[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in packet.get("chart_rows", []):
        if not isinstance(row, Mapping):
            continue
        price = _as_float(row.get("price"))
        topic = str(row.get("topic_key") or "")
        updated_at_ms = int(row.get("updated_at_ms") or 0)
        sequence = int(row.get("sequence") or 0)
        freshness = str(row.get("freshness_label") or "")
        if price is not None:
            _append_price(rows, updated_at_ms=updated_at_ms, topic=topic, price=price, sequence=sequence, freshness=freshness)
        label = str(row.get("value_label") or "")
        for name, raw_price in _NAMED_PRICE_RE.findall(label):
            if name == "spread":
                continue
            _append_price(rows, updated_at_ms=updated_at_ms, topic=f"{topic}.{name}", price=float(raw_price), sequence=sequence, freshness=freshness)
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.drop_duplicates(subset=["ts", "topic", "price", "sequence"]).sort_values(["ts", "role", "topic"])
    return frame


def _board_band_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["ts", "bid", "ask", "mid", "spread"])
    role_frame = frame[frame["role"].isin(["bid", "ask"])].copy()
    if role_frame.empty:
        return pd.DataFrame(columns=["ts", "bid", "ask", "mid", "spread"])
    pivot = role_frame.pivot_table(index="ts", columns="role", values="price", aggfunc="last").sort_index()
    if "bid" not in pivot.columns or "ask" not in pivot.columns:
        return pd.DataFrame(columns=["ts", "bid", "ask", "mid", "spread"])
    pivot = pivot.dropna(subset=["bid", "ask"]).reset_index()
    if pivot.empty:
        return pd.DataFrame(columns=["ts", "bid", "ask", "mid", "spread"])
    pivot["mid"] = (pivot["bid"] + pivot["ask"]) / 2.0
    pivot["spread"] = pivot["ask"] - pivot["bid"]
    return pivot



def _plain_cache_to_candle_frame(cache_frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "ts",
        "open",
        "high",
        "low",
        "close",
        "direction",
        "count",
        "volume",
        "trade_count",
        "source_role",
        "timeframe_sec",
        "candle_status",
        "is_closed",
    ]
    if cache_frame.empty:
        return pd.DataFrame(columns=columns)
    required = {"time_utc", "open", "high", "low", "close"}
    if not required.issubset(set(cache_frame.columns)):
        return pd.DataFrame(columns=columns)
    work = cache_frame.copy()
    work["ts"] = pd.to_datetime(work["time_utc"], utc=True, errors="coerce")
    for column in ("open", "high", "low", "close", "volume"):
        if column in work.columns:
            work[column] = pd.to_numeric(work[column], errors="coerce")
    if "trade_count" not in work.columns:
        work["trade_count"] = 0
    work["trade_count"] = pd.to_numeric(work["trade_count"], errors="coerce").fillna(0).astype(int)
    if "timeframe_sec" not in work.columns:
        work["timeframe_sec"] = 60
    work["timeframe_sec"] = pd.to_numeric(work["timeframe_sec"], errors="coerce").fillna(60).astype(int)
    work = work.dropna(subset=["ts", "open", "high", "low", "close"]).sort_values("ts").reset_index(drop=True)
    if work.empty:
        return pd.DataFrame(columns=columns)
    if "volume" not in work.columns:
        work["volume"] = 0.0
    work["volume"] = pd.to_numeric(work["volume"], errors="coerce").fillna(0.0)
    work["direction"] = work.apply(lambda row: "up" if float(row["close"]) >= float(row["open"]) else "down", axis=1)
    work["count"] = work["trade_count"]
    work["source_role"] = "plain_trade_ohlc_cache"
    work["candle_status"] = "closed"
    work.loc[work.index == work.index.max(), "candle_status"] = "forming"
    work["is_closed"] = work["candle_status"] == "closed"
    return work[columns]


def _filter_candles_to_domain(candles: pd.DataFrame, x_domain: tuple[pd.Timestamp, pd.Timestamp] | None) -> pd.DataFrame:
    if candles.empty or x_domain is None:
        return candles
    start, end = x_domain
    visible = candles[(candles["ts"] >= start) & (candles["ts"] <= end)].copy()
    return visible if not visible.empty else candles.tail(12).copy()


def _candle_x_domain(candles: pd.DataFrame, *, minutes: int) -> tuple[pd.Timestamp, pd.Timestamp] | None:
    if candles.empty or "ts" not in candles.columns:
        return None
    ts = pd.to_datetime(candles["ts"], utc=True, errors="coerce").dropna()
    if ts.empty:
        return None
    end = ts.max()
    start = end - pd.Timedelta(minutes=minutes)
    return start, end


def _cache_candles_to_display_points(candles: pd.DataFrame) -> pd.DataFrame:
    columns = ["ts", "topic", "role", "price", "sequence", "freshness_label"]
    if candles.empty:
        return pd.DataFrame(columns=columns)
    rows = [
        {
            "ts": row["ts"],
            "topic": "plain_trade_ohlc_cache.close",
            "role": "last",
            "price": float(row["close"]),
            "sequence": int(index),
            "freshness_label": "plain_trade_cache",
        }
        for index, row in enumerate(candles.sort_values("ts").reset_index(drop=True).to_dict("records"))
        if row.get("ts") is not None and row.get("close") is not None
    ]
    return pd.DataFrame(rows, columns=columns)


def _plain_cache_chart_series_meta(*, cache_frame: pd.DataFrame, candle_frame: pd.DataFrame, mode: str) -> dict[str, Any]:
    return {
        "version": WARROOM_PLAIN_CANDLE_CACHE_VERSION,
        "source_family": "warroom_plain_trade_ohlc_cache",
        "mode": mode,
        "timeframe_sec": 60,
        "input_row_count": len(cache_frame),
        "usable_row_count": len(candle_frame),
        "candle_count": len(candle_frame),
        "latest_candle_forming": not candle_frame.empty,
        "provisional": False,
        "source_notice": "D-hot derived plain trade OHLC cache. Base candle uses market.trade payload.price only.",
        "read_only": True,
        "broker_send_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def _meta_to_dict(meta: Any) -> dict[str, Any]:
    if hasattr(meta, "to_dict"):
        return meta.to_dict()
    if isinstance(meta, Mapping):
        return dict(meta)
    return {}

def _build_board_band_overlay_layers(band_frame: pd.DataFrame, *, limit: int = 240) -> list[dict[str, Any]]:
    if band_frame.empty:
        return []
    required = {"ts", "bid", "ask"}
    if not required.issubset(set(band_frame.columns)):
        return []
    compact = band_frame.tail(limit).copy()
    points: list[dict[str, Any]] = []
    for row in compact.to_dict("records"):
        ts = row.get("ts")
        if not hasattr(ts, "isoformat"):
            continue
        bid = _as_float(row.get("bid"))
        ask = _as_float(row.get("ask"))
        if bid is None or ask is None:
            continue
        mid = _as_float(row.get("mid"))
        spread = _as_float(row.get("spread"))
        points.append(
            {
                "ts": ts.isoformat(),
                "bid": round(bid, 6),
                "ask": round(ask, 6),
                "mid": round(float(mid if mid is not None else (bid + ask) / 2.0), 6),
                "spread": round(float(spread if spread is not None else ask - bid), 6),
            }
        )
    if len(points) < 2:
        return []
    return [
        {
            "layer_id": "warroom_board_bid_ask_band",
            "label": "板気配 bid/ask/mid",
            "kind": "board_band",
            "points": points,
            "read_only": True,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "ledger_append_allowed": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        }
    ]

def _overlay_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for overlay in packet.get("overlays", []):
        if not isinstance(overlay, Mapping):
            continue
        rows.append(
            {
                "priority": int(overlay.get("priority") or 99),
                "overlay": str(overlay.get("overlay_id") or ""),
                "state": str(overlay.get("state") or "unknown"),
                "label": str(overlay.get("label") or ""),
                "read_only": bool(overlay.get("read_only", True)),
            }
        )
    return sorted(rows, key=lambda row: row["priority"])


def _compact_frame_records(frame: pd.DataFrame, *, limit: int, columns: list[str]) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    available = [column for column in columns if column in frame.columns]
    compact = frame[available].tail(limit).copy()
    rows: list[dict[str, Any]] = []
    for row in compact.to_dict("records"):
        normalized: dict[str, Any] = {}
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                normalized[key] = value.isoformat()
            elif isinstance(value, float):
                normalized[key] = round(value, 6)
            elif pd.isna(value):
                normalized[key] = None
            else:
                normalized[key] = value
        rows.append(normalized)
    return rows


def _build_gpt_review_chart_snapshot(
    *,
    display_frame: pd.DataFrame,
    candle_frame: pd.DataFrame,
    band_frame: pd.DataFrame,
    overlay_rows: list[dict[str, Any]],
    chart_config: ChartDisplayConfig,
    chart_series_meta: Any,
    dhot_bootstrap_meta: Mapping[str, Any],
    x_domain: tuple[pd.Timestamp, pd.Timestamp] | None,
) -> dict[str, Any]:
    latest_display = display_frame.sort_values("ts").iloc[-1].to_dict() if not display_frame.empty else {}
    latest_band = band_frame.sort_values("ts").iloc[-1].to_dict() if not band_frame.empty else {}
    return {
        "schema_version": "warroom_chart_gpt_review_snapshot.v2_light_pointer",
        "purpose": "identify selected WarRoom chart context and source pointers for GPT Actions analysis",
        "display_mode": chart_config.mode,
        "viewport_label": chart_config.viewport_label,
        "viewport_minutes": chart_config.viewport_minutes,
        "source_label": chart_config.source_label,
        "source_notice": chart_config.source_notice,
        "history_rows": len(display_frame),
        "visible_rows": len(display_frame),
        "latest": {
            "ts": latest_display.get("ts").isoformat() if hasattr(latest_display.get("ts"), "isoformat") else latest_display.get("ts"),
            "topic": latest_display.get("topic"),
            "role": latest_display.get("role"),
            "price": latest_display.get("price"),
            "freshness_label": latest_display.get("freshness_label"),
            "bid": latest_band.get("bid"),
            "ask": latest_band.get("ask"),
            "mid": latest_band.get("mid"),
            "spread": latest_band.get("spread"),
        },
        "x_domain": {
            "start": x_domain[0].isoformat() if x_domain is not None else None,
            "end": x_domain[1].isoformat() if x_domain is not None else None,
            "latest_anchored": x_domain is not None,
        },
        "candle_summary": {
            "rows": len(candle_frame),
            "closed": int((candle_frame.get("candle_status") == "closed").sum()) if not candle_frame.empty and "candle_status" in candle_frame.columns else 0,
            "forming": int((candle_frame.get("candle_status") == "forming").sum()) if not candle_frame.empty and "candle_status" in candle_frame.columns else 0,
            "source": "dhot_derived_plain_trade_ohlc_cache" if _meta_to_dict(chart_series_meta).get("source_family") == "warroom_plain_trade_ohlc_cache" else "non_ui_warroom_chart_series",
            "true_trade_ohlcv_connected": _meta_to_dict(chart_series_meta).get("source_family") == "warroom_plain_trade_ohlc_cache",
        },
        "chart_series_meta": _meta_to_dict(chart_series_meta),
        "dhot_bootstrap": dict(dhot_bootstrap_meta),
        "sample_preview": {
            "visible_price_tail_count": min(len(display_frame), 12),
            "candle_tail_count": min(len(candle_frame), 6),
            "board_band_tail_count": min(len(band_frame), 6),
            "visible_price_rows_tail": _compact_frame_records(display_frame, limit=12, columns=["ts", "topic", "role", "price", "freshness_label"]),
            "candles_tail": _compact_frame_records(candle_frame, limit=6, columns=["ts", "open", "high", "low", "close", "candle_status", "is_closed"]),
            "board_band_tail": _compact_frame_records(band_frame, limit=6, columns=["ts", "bid", "ask", "mid", "spread"]),
        },
        "overlays_summary": overlay_rows[:4],
        "trust_boundary": {
            "chart_logic_owner": "btcts.prediction.warroom_plain_candle_cache",
            "ui_role": "render_only",
            "input_source": "dhot_derived_plain_trade_ohlc_cache_plus_retained_market_state_overlay" if _meta_to_dict(chart_series_meta).get("source_family") == "warroom_plain_trade_ohlc_cache" else "retained_market_state_rows",
            "latest_candle_may_change": True,
            "closed_candles_should_not_change_in_session": True,
            "official_exchange_ohlc_connected": _meta_to_dict(chart_series_meta).get("source_family") == "warroom_plain_trade_ohlc_cache",
            "manual_review_only": True,
        },
        "safety": {
            "read_only": True,
            "websocket_send_enabled": False,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        },
    }


def _fmt_price(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "--"
    return f"{numeric:,.0f}"


def _fmt_spread(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "--"
    return f"{numeric:,.0f}"


def _fmt_time_minute(value: object) -> str:
    if value is None:
        return "--"
    try:
        ts = pd.Timestamp(value)
    except Exception:  # noqa: BLE001
        return "--"
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    ts = ts.tz_convert("UTC")
    return ts.strftime("%H:%MZ")


def _latest_candle_row(candles: pd.DataFrame) -> dict[str, Any]:
    if candles.empty or "ts" not in candles.columns:
        return {}
    ordered = candles.sort_values("ts")
    return ordered.iloc[-1].to_dict()


def _cache_lag_label(*, cache_ts: object, live_ts: object) -> str:
    if cache_ts is None or live_ts is None:
        return "--"
    try:
        cache_value = pd.Timestamp(cache_ts)
        live_value = pd.Timestamp(live_ts)
    except Exception:  # noqa: BLE001
        return "--"
    if cache_value.tzinfo is None:
        cache_value = cache_value.tz_localize("UTC")
    if live_value.tzinfo is None:
        live_value = live_value.tz_localize("UTC")
    delta_sec = max(0.0, (live_value.tz_convert("UTC") - cache_value.tz_convert("UTC")).total_seconds())
    if delta_sec < 90:
        return "live相当"
    return f"{int(round(delta_sec / 60.0))}分"


def _session_state(st_api: Any) -> Any | None:
    state = getattr(st_api, "session_state", None)
    if hasattr(state, "get") and hasattr(state, "__setitem__"):
        return state
    return None


def _frame_to_history_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if frame.empty:
        return records
    for row in frame.to_dict("records"):
        ts = row.get("ts")
        records.append(
            {
                "ts": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                "topic": str(row.get("topic") or ""),
                "role": str(row.get("role") or "price"),
                "price": float(row.get("price") or 0.0),
                "sequence": int(row.get("sequence") or 0),
                "freshness_label": str(row.get("freshness_label") or ""),
            }
        )
    return records


def _history_records_to_frame(records: object) -> pd.DataFrame:
    if not isinstance(records, list):
        return pd.DataFrame(columns=["ts", "topic", "role", "price", "sequence", "freshness_label"])
    rows = [row for row in records if isinstance(row, Mapping)]
    if not rows:
        return pd.DataFrame(columns=["ts", "topic", "role", "price", "sequence", "freshness_label"])
    frame = pd.DataFrame(rows)
    frame["ts"] = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    frame["sequence"] = pd.to_numeric(frame["sequence"], errors="coerce").fillna(0).astype(int)
    frame = frame.dropna(subset=["ts", "price"])
    if frame.empty:
        return pd.DataFrame(columns=["ts", "topic", "role", "price", "sequence", "freshness_label"])
    return frame[["ts", "topic", "role", "price", "sequence", "freshness_label"]]


def _retain_chart_history(current_frame: pd.DataFrame, st_api: Any) -> pd.DataFrame:
    state = _session_state(st_api)
    if state is None:
        return current_frame
    previous = _history_records_to_frame(state.get(CHART_HISTORY_SESSION_STATE_KEY, []))
    if current_frame.empty:
        history = previous
    elif previous.empty:
        history = current_frame
    else:
        history = pd.concat([previous, current_frame], ignore_index=True)
    if history.empty:
        state[CHART_HISTORY_SESSION_STATE_KEY] = []
        return history
    history = history.drop_duplicates(subset=["ts", "topic", "role", "price", "sequence"]).sort_values(["ts", "role", "topic"]).tail(CHART_HISTORY_LIMIT)
    state[CHART_HISTORY_SESSION_STATE_KEY] = _frame_to_history_records(history)
    return history

def _bootstrap_dhot_chart_history(current_frame: pd.DataFrame, st_api: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    return current_frame, {
        "ok": False,
        "version": WARROOM_CHART_DHOT_BOOTSTRAP_VERSION,
        "reason": "disabled_after_plain_trade_candle_cache_connected",
        "raw_trade_read_from_ui_enabled": False,
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }

def _render_price_chart(frame: pd.DataFrame, band_frame: pd.DataFrame, candle_frame: pd.DataFrame, st_api: Any, *, x_domain: tuple[pd.Timestamp, pd.Timestamp] | None = None) -> bool:
    if frame.empty:
        return False
    try:
        import altair as alt  # type: ignore

        x_scale = alt.Scale(domain=[x_domain[0].to_pydatetime(), x_domain[1].to_pydatetime()]) if x_domain is not None else alt.Undefined
        x_encoding = alt.X("ts:T", title="time", scale=x_scale)
        base = alt.Chart(frame).encode(x=x_encoding)
        layers: list[Any] = []
        if not band_frame.empty:
            band = alt.Chart(band_frame).mark_area(opacity=0.08, color="#38bdf8").encode(
                x=x_encoding,
                y=alt.Y("bid:Q", title="price", scale=alt.Scale(zero=False)),
                y2="ask:Q",
                tooltip=["ts:T", "bid:Q", "ask:Q", "mid:Q", "spread:Q"],
            )
            mid = alt.Chart(band_frame).mark_line(color="#64748b", strokeDash=[4, 4], strokeWidth=1.1, opacity=0.82).encode(
                x=x_encoding,
                y=alt.Y("mid:Q", title="price", scale=alt.Scale(zero=False)),
                tooltip=["ts:T", "mid:Q", "spread:Q"],
            )
            layers.extend([band, mid])
        if not candle_frame.empty:
            candle_rule = alt.Chart(candle_frame).mark_rule(strokeWidth=1.4, opacity=0.9).encode(
                x=x_encoding,
                y=alt.Y("low:Q", title="price", scale=alt.Scale(zero=False)),
                y2="high:Q",
                color=alt.Color("direction:N", title="ローソク", scale=alt.Scale(domain=["up", "down"], range=["#f59e0b", "#ef4444"]), legend=None),
                tooltip=["ts:T", "open:Q", "high:Q", "low:Q", "close:Q", "count:Q", "candle_status:N", "source_role:N"],
            )
            candle_body = alt.Chart(candle_frame).mark_bar(size=7, opacity=0.88).encode(
                x=x_encoding,
                y=alt.Y("open:Q", title="price", scale=alt.Scale(zero=False)),
                y2="close:Q",
                color=alt.Color("direction:N", title="ローソク", scale=alt.Scale(domain=["up", "down"], range=["#f59e0b", "#ef4444"]), legend=None),
                tooltip=["ts:T", "open:Q", "high:Q", "low:Q", "close:Q", "count:Q", "source_role:N"],
            )
            layers.extend([candle_rule, candle_body])
        quote_lines = base.transform_filter("datum.role == 'bid' || datum.role == 'ask'").mark_line(point=False, strokeWidth=1.15, opacity=0.58).encode(
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "role:N",
                title="補助線",
                scale=alt.Scale(domain=["ask", "bid", "last", "price"], range=["#fb7185", "#60a5fa", "#16a34a", "#94a3b8"]),
                legend=alt.Legend(orient="right"),
            ),
            tooltip=["ts:T", "topic:N", "role:N", "price:Q", "sequence:Q", "freshness_label:N"],
        )
        trades = base.transform_filter("datum.role == 'last'").mark_circle(size=72, color="#16a34a", opacity=0.74).encode(
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            tooltip=["ts:T", "topic:N", "price:Q", "sequence:Q", "freshness_label:N"],
        )
        other = base.transform_filter("datum.role != 'bid' && datum.role != 'ask' && datum.role != 'last'").mark_point(size=42, color="#94a3b8", opacity=0.55).encode(
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            tooltip=["ts:T", "topic:N", "role:N", "price:Q", "sequence:Q", "freshness_label:N"],
        )
        layers.extend([quote_lines, trades, other])
        chart = alt.layer(*layers).resolve_scale(y="shared").properties(height=400)
        st_api.altair_chart(chart, use_container_width=True)
        return True
    except Exception:  # noqa: BLE001
        pivot = frame.pivot_table(index="ts", columns="topic", values="price", aggfunc="last").sort_index()
        st_api.line_chart(pivot, height=340, width="stretch")
        return True


def render_rt_bottom_chart_graph(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("チャート: Live/分足/時足/日足モード + rolling表示窓 / 読み取り専用")
    current_frame = chart_rows_to_frame(packet)
    dhot_bootstrap_meta = {
        "ok": False,
        "version": WARROOM_CHART_DHOT_BOOTSTRAP_VERSION,
        "reason": "disabled_after_plain_trade_candle_cache_connected",
        "raw_trade_read_from_ui_enabled": False,
    }
    frame = _retain_chart_history(current_frame, st_api)
    chart_config: ChartDisplayConfig = select_chart_display_config(st_api)
    display_frame = prepare_chart_display_frame(frame, chart_config)
    plain_cache_frame, plain_cache_meta = read_plain_candle_cache(max_candles=PLAIN_CANDLE_CACHE_MAX_CANDLES)
    plain_cache_all_candles = _plain_cache_to_candle_frame(plain_cache_frame)
    plain_cache_connected = (chart_config.mode in PLAIN_CANDLE_CACHE_MODES) and not plain_cache_all_candles.empty
    x_domain = _candle_x_domain(plain_cache_all_candles, minutes=chart_config.viewport_minutes) if plain_cache_connected else chart_x_domain(frame, minutes=chart_config.viewport_minutes)
    interactive_candle_frame = pd.DataFrame()
    initial_visible_candle_count = 0
    if plain_cache_connected:
        visible_candle_frame = _filter_candles_to_domain(plain_cache_all_candles, x_domain)
        candle_frame = visible_candle_frame
        interactive_candle_frame = plain_cache_all_candles
        initial_visible_candle_count = max(1, len(visible_candle_frame)) if not visible_candle_frame.empty else 0
        chart_series_meta = _plain_cache_chart_series_meta(cache_frame=plain_cache_frame, candle_frame=candle_frame, mode=chart_config.mode)
        if display_frame.empty:
            display_frame = _cache_candles_to_display_points(candle_frame)
    else:
        candle_frame, chart_series_meta = build_warroom_chart_candles(frame, mode=chart_config.mode, x_domain=x_domain)
    raw_candle_frame = candle_frame
    closed_candle_count = int((candle_frame.get("candle_status") == "closed").sum()) if not candle_frame.empty and "candle_status" in candle_frame.columns else 0
    forming_candle_count = int((candle_frame.get("candle_status") == "forming").sum()) if not candle_frame.empty and "candle_status" in candle_frame.columns else 0
    band_frame = _board_band_frame(display_frame)
    overlay_rows = _overlay_rows(packet)
    live_rows = sum(1 for row in packet.get("chart_rows", []) if isinstance(row, Mapping) and row.get("freshness_label") == "live")
    latest = display_frame.sort_values("ts").iloc[-1] if not display_frame.empty else None
    latest_band = band_frame.sort_values("ts").iloc[-1] if not band_frame.empty else None
    base_latest = _latest_candle_row(plain_cache_all_candles if plain_cache_connected else candle_frame)
    base_latest_ts = base_latest.get("ts")
    live_overlay_ts = None if latest is None else latest.get("ts")
    cache_lag = _cache_lag_label(cache_ts=base_latest_ts, live_ts=live_overlay_ts)

    c1, c2, c3, c4, c5, c6, c7 = st_api.columns(7)
    c1.metric("足終値", _fmt_price(base_latest.get("close")))
    c2.metric("cache遅延", cache_lag)
    c3.metric("表示モード", chart_config.mode)
    c4.metric("表示窓", chart_config.viewport_label)
    c5.metric("買気配", _fmt_price(None if latest_band is None else latest_band.get("bid")))
    c6.metric("売気配", _fmt_price(None if latest_band is None else latest_band.get("ask")))
    c7.metric("スプレッド", _fmt_spread(None if latest_band is None else latest_band.get("spread")))

    cache_rows = int(plain_cache_meta.get("rows_returned") or 0) if isinstance(plain_cache_meta, Mapping) else 0
    st_api.caption(f"データ範囲={chart_config.source_label} / 注意={chart_config.source_notice}")
    st_api.caption(f"ベース足=plain trade OHLC cache / latest_close={_fmt_price(base_latest.get('close'))} / cache_end={_fmt_time_minute(base_latest_ts)} / cache_lag_vs_live={cache_lag}")
    st_api.caption(f"チャート信頼境界=plain trade OHLC cache優先 / cache={cache_rows}行 / UI raw market.trade bootstrap=disabled / 最新足のみ未確定 / bid-ask線は現在気配overlayで予測線ではありません")
    if chart_config.historical_cache_required:
        st_api.info("1時間足/日足は現在のLive保持履歴からの暫定表示です。10日超やcold archive統合は、後続の集約キャッシュ接続で扱います。")

    interactive_chart_summary: dict[str, Any] = {"interactive_chart_rendered": False}
    if not display_frame.empty:
        render_candle_frame = interactive_candle_frame if plain_cache_connected and not interactive_candle_frame.empty else candle_frame
        interactive_chart_summary = render_interactive_candle_chart(
            render_candle_frame,
            mode=chart_config.mode,
            chart_context={
                "display_mode": chart_config.mode,
                "viewport_label": chart_config.viewport_label,
                "viewport_minutes": chart_config.viewport_minutes,
                "initial_visible_candle_count": initial_visible_candle_count,
                "interactive_candle_count": len(render_candle_frame),
                "base_candle_pan_history_enabled": bool(plain_cache_connected and len(render_candle_frame) > len(candle_frame)),
                "base_latest_close": base_latest.get("close"),
                "base_latest_ts_utc": base_latest_ts.isoformat() if hasattr(base_latest_ts, "isoformat") else base_latest_ts,
                "cache_lag_vs_live": cache_lag,
                "cache_rows": cache_rows,
                "plain_cache_connected": bool(plain_cache_connected),
                "chart_data_endpoint": os.environ.get(CHART_DATA_ENDPOINT_ENV, DEFAULT_CHART_DATA_ENDPOINT),
                "chart_data_poll_interval_ms": CHART_DATA_POLL_INTERVAL_MS,
                "chart_engine_polling_enabled": True,
                "streamlit_fragment_rerender_required_for_candles": False,
                "primary_market_trade_path": dict(plain_cache_meta).get("cache_path") if plain_cache_connected and isinstance(plain_cache_meta, Mapping) else None,
                "dhot_bootstrap": dict(dhot_bootstrap_meta) if isinstance(dhot_bootstrap_meta, Mapping) else {},
                "plain_candle_cache": dict(plain_cache_meta) if isinstance(plain_cache_meta, Mapping) else {},
                "input_source": "dhot_derived_plain_trade_ohlc_cache_plus_retained_market_state_overlay" if plain_cache_connected else "retained_market_state_rows",
                "overlay_layers": _build_board_band_overlay_layers(band_frame),
            },
            st_api=st_api,
        )
        rendered = bool(interactive_chart_summary.get("interactive_chart_rendered"))
        if not rendered:
            rendered = _render_price_chart(display_frame, band_frame, candle_frame, st_api, x_domain=x_domain)
        assert latest is not None
        st_api.caption(
            f"base_close={_fmt_price(base_latest.get('close'))} / base_end={_fmt_time_minute(base_latest_ts)} / live_overlay_price={_fmt_price(latest['price'])} / live_topic={latest['topic']} / freshness={latest['freshness_label']} / 表示モード={chart_config.mode} / 表示窓={chart_config.viewport_label} / history={len(frame)} / visible={len(display_frame)} / candles={len(candle_frame)} / closed={closed_candle_count} / forming={forming_candle_count} / helper={CHART_TIMEFRAME_VIEW_VERSION} / version={BOTTOM_CHART_POLISH_VERSION}"
        )
    else:
        rendered = False
        st_api.info("価格行がまだありません。market.depth または market.trades の到着を待っています。")

    chart_review_snapshot = _build_gpt_review_chart_snapshot(
        display_frame=display_frame,
        candle_frame=candle_frame,
        band_frame=band_frame,
        overlay_rows=overlay_rows,
        chart_config=chart_config,
        chart_series_meta=chart_series_meta,
        dhot_bootstrap_meta=dhot_bootstrap_meta if isinstance(dhot_bootstrap_meta, Mapping) else {},
        x_domain=x_domain,
    )
    if overlay_rows:
        st_api.caption("overlays: " + " / ".join(f"{row['overlay']}={row['state']}" for row in overlay_rows[:4]))
    with st_api.expander("チャート行・板帯・レイヤー詳細", expanded=False):
        st_api.dataframe(display_frame, width="stretch")
        st_api.dataframe(candle_frame, width="stretch")
        st_api.dataframe(frame, width="stretch")
        st_api.dataframe(band_frame, width="stretch")
        st_api.dataframe(overlay_rows, width="stretch")
    return {
        "ok": True,
        "bottom_chart_polish_version": BOTTOM_CHART_POLISH_VERSION,
        "chart_graph_rendered": rendered,
        "interactive_chart_component_version": INTERACTIVE_CHART_COMPONENT_VERSION,
        "interactive_chart_rendered": bool(interactive_chart_summary.get("interactive_chart_rendered")),
        "interactive_chart_selection_copy_ready": bool(interactive_chart_summary.get("selection_copy_ready", False)),
        "history_retention_ready": True,
        "rolling_viewport_ready": True,
        "timeframe_modes_ready": True,
        "timeframe_mode": chart_config.mode,
        "viewport_label": chart_config.viewport_label,
        "viewport_minutes": chart_config.viewport_minutes,
        "historical_cache_required": chart_config.historical_cache_required,
        "chart_source_label": chart_config.source_label,
        "chart_source_notice": chart_config.source_notice,
        "historical_cache_connected": bool(plain_cache_connected),
        "plain_candle_cache_connected": bool(plain_cache_connected),
        "plain_candle_cache_version": WARROOM_PLAIN_CANDLE_CACHE_VERSION,
        "plain_candle_cache_meta": dict(plain_cache_meta) if isinstance(plain_cache_meta, Mapping) else {},
        "cold_archive_direct_read_enabled": False,
        "timeframe_helper_version": CHART_TIMEFRAME_VIEW_VERSION,
        "chart_series_version": WARROOM_CHART_SERIES_VERSION,
        "dhot_bootstrap_version": WARROOM_CHART_DHOT_BOOTSTRAP_VERSION,
        "dhot_history_bootstrap_connected": bool(dhot_bootstrap_meta.get("ok")) if isinstance(dhot_bootstrap_meta, Mapping) else False,
        "dhot_history_bootstrap_meta": dict(dhot_bootstrap_meta) if isinstance(dhot_bootstrap_meta, Mapping) else {},
        "history_session_state_key": CHART_HISTORY_SESSION_STATE_KEY,
        "dhot_bootstrap_session_state_key": CHART_DHOT_BOOTSTRAP_SESSION_STATE_KEY,
        "current_frame_rows": len(current_frame),
        "display_frame_rows": len(display_frame),
        "frame_rows": len(frame),
        "fixed_x_domain_ready": x_domain is not None,
        "x_domain_start": x_domain[0].isoformat() if x_domain is not None else None,
        "x_domain_end": x_domain[1].isoformat() if x_domain is not None else None,
        "ohlc_overlay_ready": True,
        "ohlc_visual_polish_ready": True,
        "stable_candles_ready": True,
        "sealed_candles_ready": False,
        "chart_series_logic_split_ready": True,
        "chart_series_meta": _meta_to_dict(chart_series_meta),
        "gpt_review_chart_snapshot_ready": True,
        "gpt_review_chart_snapshot": chart_review_snapshot,
        "chart_trust_level": "plain_trade_ohlc_cache" if plain_cache_connected else "deterministic_provisional_market_state_mid_ohlcv",
        "true_trade_ohlcv_connected": bool(plain_cache_connected),
        "chart_engine_polling_enabled": True,
        "chart_data_endpoint": os.environ.get(CHART_DATA_ENDPOINT_ENV, DEFAULT_CHART_DATA_ENDPOINT),
        "streamlit_fragment_rerender_required_for_candles": False,
        "raw_candle_frame_rows": len(raw_candle_frame),
        "candle_frame_rows": len(candle_frame),
        "closed_candle_count": closed_candle_count,
        "forming_candle_count": forming_candle_count,
        "candle_source": "dhot_derived_plain_trade_ohlc_cache" if plain_cache_connected else "retained_market_state_mid_rows",
        "board_band_rows": len(band_frame),
        "overlay_rows": len(overlay_rows),
        "bid_ask_layer_ready": True,
        "mid_reference_ready": True,
        "trade_points_ready": True,
        "zero_free_scale_ready": True,
        "read_only": True,
        "controls_added": True,
        "display_control_action_free": True,
        "timeframe_control_action_free": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
