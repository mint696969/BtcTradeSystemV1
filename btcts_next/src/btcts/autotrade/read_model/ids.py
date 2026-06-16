# path: ./btcts_next/src/btcts/autotrade/read_model/ids.py
# desc: Stable id builders for AutoTrade snapshots and 5-minute forecasts.

from __future__ import annotations

import hashlib


def _digest(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def build_snapshot_id(*, market_uid: str, created_at: str, parameter_set_id: str, effective_event_ts: str | None) -> str:
    return "snap_" + _digest(market_uid, created_at, parameter_set_id, effective_event_ts or "none")


def build_forecast_id(*, snapshot_id: str, target_ts: str, parameter_set_id: str, logic_version: str) -> str:
    return "fcst_" + _digest(snapshot_id, target_ts, parameter_set_id, logic_version)
