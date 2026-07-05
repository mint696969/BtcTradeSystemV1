# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/chart_view.py
# desc: WarRoom v2 realtime bottom chart renderer. Candlestick-like price context with bid/ask board layers and read-only overlays.

from __future__ import annotations

import re
from typing import Any, Mapping

import pandas as pd

BOTTOM_CHART_POLISH_VERSION = "warroom_v2_bottom_chart_polish.2026_07_05.v2_history"
_PRICE_RE = re.compile(r"(?:best_ask|best_bid|last_price|spread)=([0-9]+(?:\.[0-9]+)?)")
_NAMED_PRICE_RE = re.compile(r"(best_ask|best_bid|last_price|spread)=([0-9]+(?:\.[0-9]+)?)")
CHART_HISTORY_SESSION_STATE_KEY = "warroom_v2_bottom_chart_history_rows"
CHART_HISTORY_LIMIT = 240


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


def _render_price_chart(frame: pd.DataFrame, band_frame: pd.DataFrame, st_api: Any) -> bool:
    if frame.empty:
        return False
    try:
        import altair as alt  # type: ignore

        base = alt.Chart(frame).encode(x=alt.X("ts:T", title="time"))
        layers: list[Any] = []
        if not band_frame.empty:
            band = alt.Chart(band_frame).mark_area(opacity=0.16, color="#7dd3fc").encode(
                x=alt.X("ts:T", title="time"),
                y=alt.Y("bid:Q", title="price", scale=alt.Scale(zero=False)),
                y2="ask:Q",
                tooltip=["ts:T", "bid:Q", "ask:Q", "mid:Q", "spread:Q"],
            )
            mid = alt.Chart(band_frame).mark_line(color="#64748b", strokeDash=[4, 4], strokeWidth=1.4).encode(
                x="ts:T",
                y=alt.Y("mid:Q", title="price", scale=alt.Scale(zero=False)),
                tooltip=["ts:T", "mid:Q", "spread:Q"],
            )
            layers.extend([band, mid])
        quote_lines = base.transform_filter("datum.role == 'bid' || datum.role == 'ask'").mark_line(point=True, strokeWidth=2).encode(
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "role:N",
                title="series",
                scale=alt.Scale(domain=["ask", "bid", "last", "price"], range=["#ef4444", "#2563eb", "#16a34a", "#94a3b8"]),
            ),
            tooltip=["ts:T", "topic:N", "role:N", "price:Q", "sequence:Q", "freshness_label:N"],
        )
        trades = base.transform_filter("datum.role == 'last'").mark_circle(size=90, color="#16a34a", opacity=0.9).encode(
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            tooltip=["ts:T", "topic:N", "price:Q", "sequence:Q", "freshness_label:N"],
        )
        other = base.transform_filter("datum.role != 'bid' && datum.role != 'ask' && datum.role != 'last'").mark_point(size=60, color="#94a3b8").encode(
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            tooltip=["ts:T", "topic:N", "role:N", "price:Q", "sequence:Q", "freshness_label:N"],
        )
        layers.extend([quote_lines, trades, other])
        chart = alt.layer(*layers).resolve_scale(y="shared").properties(height=380)
        st_api.altair_chart(chart, use_container_width=True)
        return True
    except Exception:  # noqa: BLE001
        pivot = frame.pivot_table(index="ts", columns="topic", values="price", aggfunc="last").sort_index()
        st_api.line_chart(pivot, height=340, width="stretch")
        return True


def render_rt_bottom_chart_graph(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("チャート: 買気配/売気配の板レイヤー + 中心線 + 約定点 / 短期履歴保持 / 読み取り専用")
    current_frame = chart_rows_to_frame(packet)
    frame = _retain_chart_history(current_frame, st_api)
    band_frame = _board_band_frame(frame)
    overlay_rows = _overlay_rows(packet)
    live_rows = sum(1 for row in packet.get("chart_rows", []) if isinstance(row, Mapping) and row.get("freshness_label") == "live")
    latest = frame.sort_values("ts").iloc[-1] if not frame.empty else None
    latest_band = band_frame.sort_values("ts").iloc[-1] if not band_frame.empty else None

    c1, c2, c3, c4, c5, c6 = st_api.columns(6)
    c1.metric("履歴点", len(frame))
    c2.metric("最新行", live_rows)
    c3.metric("買気配", _fmt_price(None if latest_band is None else latest_band.get("bid")))
    c4.metric("売気配", _fmt_price(None if latest_band is None else latest_band.get("ask")))
    c5.metric("スプレッド", _fmt_spread(None if latest_band is None else latest_band.get("spread")))
    c6.metric("レイヤー", len(overlay_rows))

    if not frame.empty:
        rendered = _render_price_chart(frame, band_frame, st_api)
        assert latest is not None
        st_api.caption(
            f"latest={_fmt_price(latest['price'])} / topic={latest['topic']} / role={latest['role']} / freshness={latest['freshness_label']} / version={BOTTOM_CHART_POLISH_VERSION}"
        )
    else:
        rendered = False
        st_api.info("価格行がまだありません。market.depth または market.trades の到着を待っています。")

    if overlay_rows:
        st_api.caption("overlays: " + " / ".join(f"{row['overlay']}={row['state']}" for row in overlay_rows[:4]))
    with st_api.expander("チャート行・板帯・レイヤー詳細", expanded=False):
        st_api.dataframe(frame, width="stretch")
        st_api.dataframe(band_frame, width="stretch")
        st_api.dataframe(overlay_rows, width="stretch")
    return {
        "ok": True,
        "bottom_chart_polish_version": BOTTOM_CHART_POLISH_VERSION,
        "chart_graph_rendered": rendered,
        "history_retention_ready": True,
        "history_session_state_key": CHART_HISTORY_SESSION_STATE_KEY,
        "current_frame_rows": len(current_frame),
        "frame_rows": len(frame),
        "board_band_rows": len(band_frame),
        "overlay_rows": len(overlay_rows),
        "bid_ask_layer_ready": True,
        "mid_reference_ready": True,
        "trade_points_ready": True,
        "zero_free_scale_ready": True,
        "read_only": True,
        "controls_added": False,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
