# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/chart_timeframe_view.py
# desc: Action-free chart timeframe and rolling viewport helpers for WarRoom v2 bottom chart.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

CHART_TIMEFRAME_VIEW_VERSION = "warroom_v2_chart_timeframe_view.2026_07_05.v1"
CHART_VIEWPORT_OPTIONS: tuple[tuple[str, int], ...] = (("3分", 3), ("15分", 15), ("1時間", 60))
CHART_DEFAULT_VIEWPORT_LABEL = "15分"
CHART_MODE_OPTIONS: tuple[str, ...] = ("Live", "1分足", "1時間足", "日足")
CHART_DEFAULT_MODE = "Live"
CHART_MODE_FREQUENCY: dict[str, str | None] = {"Live": None, "1分足": "1min", "1時間足": "1h", "日足": "1D"}


@dataclass(frozen=True)
class ChartDisplayConfig:
    mode: str
    viewport_label: str
    viewport_minutes: int
    source_scope: str = "retained_live_history"
    historical_cache_required: bool = False
    read_only: bool = True
    broker_send_enabled: bool = False
    prediction_invoked: bool = False
    classifier_invoked: bool = False


def _safe_selectbox(st_api: Any, label: str, options: list[str], *, index: int, key: str, help_text: str) -> str:
    try:
        value = st_api.selectbox(label, options, index=index, key=key, help=help_text)
    except TypeError:
        try:
            value = st_api.selectbox(label, options, index=index)
        except Exception:  # noqa: BLE001
            value = options[index]
    except Exception:  # noqa: BLE001
        value = options[index]
    return str(value) if str(value) in options else options[index]


def _viewport_minutes(label: str) -> int:
    for option_label, minutes in CHART_VIEWPORT_OPTIONS:
        if option_label == label:
            return minutes
    return 15


def select_chart_display_config(st_api: Any) -> ChartDisplayConfig:
    mode_options = list(CHART_MODE_OPTIONS)
    viewport_options = [label for label, _minutes in CHART_VIEWPORT_OPTIONS]
    try:
        mode_col, viewport_col = st_api.columns(2)
    except Exception:  # noqa: BLE001
        mode_col = st_api
        viewport_col = st_api
    mode = _safe_selectbox(
        mode_col,
        "表示モード",
        mode_options,
        index=mode_options.index(CHART_DEFAULT_MODE),
        key="warroom_v2_bottom_chart_mode",
        help_text="Liveは受信履歴そのまま、分足/時足/日足は現在保持している履歴を読み取り専用で集約します。",
    )
    viewport_label = _safe_selectbox(
        viewport_col,
        "表示範囲",
        viewport_options,
        index=viewport_options.index(CHART_DEFAULT_VIEWPORT_LABEL),
        key="warroom_v2_bottom_chart_viewport",
        help_text="表示だけを切り替えます。履歴は保持され、broker/order/predictionには接続しません。",
    )
    historical_cache_required = mode in {"1時間足", "日足"}
    return ChartDisplayConfig(
        mode=mode,
        viewport_label=viewport_label,
        viewport_minutes=_viewport_minutes(viewport_label),
        historical_cache_required=historical_cache_required,
    )


def apply_rolling_viewport(frame: pd.DataFrame, *, minutes: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    latest_ts = frame["ts"].max()
    if pd.isna(latest_ts):
        return frame
    cutoff = latest_ts - pd.Timedelta(minutes=minutes)
    visible = frame[frame["ts"] >= cutoff].copy()
    if visible.empty:
        return frame.tail(12).copy()
    return visible


def aggregate_chart_frame(frame: pd.DataFrame, *, mode: str) -> pd.DataFrame:
    frequency = CHART_MODE_FREQUENCY.get(mode)
    if not frequency or frame.empty:
        return frame
    required_columns = {"ts", "role", "price", "sequence", "freshness_label"}
    if not required_columns.issubset(set(frame.columns)):
        return frame
    work = frame.copy()
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work["price"] = pd.to_numeric(work["price"], errors="coerce")
    work["sequence"] = pd.to_numeric(work["sequence"], errors="coerce").fillna(0).astype(int)
    work = work.dropna(subset=["ts", "price"])
    if work.empty:
        return work
    work["bucket_ts"] = work["ts"].dt.floor(frequency)
    rows: list[dict[str, Any]] = []
    for (bucket_ts, role), group in work.sort_values("ts").groupby(["bucket_ts", "role"], dropna=True):
        if role not in {"bid", "ask", "mid", "last", "price"}:
            continue
        last = group.iloc[-1]
        rows.append(
            {
                "ts": bucket_ts,
                "topic": f"{role}.{mode}",
                "role": str(role),
                "price": float(last["price"]),
                "sequence": int(last.get("sequence", 0)),
                "freshness_label": str(last.get("freshness_label", "")),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(["ts", "role", "topic"])


def prepare_chart_display_frame(history_frame: pd.DataFrame, config: ChartDisplayConfig) -> pd.DataFrame:
    visible = apply_rolling_viewport(history_frame, minutes=config.viewport_minutes)
    return aggregate_chart_frame(visible, mode=config.mode)
