# path: ./btcts_next/src/btcts/apps/operator_ui/market_state_service.py
# desc: Load latest market_state records for the operator UI from data/market_state outputs.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.core import paths as core_paths
from btcts.processing.l4_consumer_models.shared import (
    MarketSummary,
    MarketSummaryBuildInput,
    build_market_summary,
)


def market_state_root() -> Path:
    return core_paths.data_dir(ensure=False) / "market_state"


def _latest_jsonl_line(path: Path) -> dict[str, Any]:
    rows = _read_jsonl_rows(path)
    return rows[-1] if rows else {}


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    rows: list[dict[str, Any]] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)

    return rows


def _latest_market_state_part_file(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
) -> Path | None:
    root = (
        market_state_root()
        / f"exchange={exchange}"
        / f"symbol={symbol_raw}"
        / f"type={state_type}"
    )

    if not root.exists():
        return None

    date_dirs = sorted(
        [p for p in root.iterdir() if p.is_dir() and p.name.startswith("date=")],
        key=lambda p: p.name,
    )
    if not date_dirs:
        return None

    latest_date_dir = date_dirs[-1]

    part_files = sorted(latest_date_dir.glob("part-*.jsonl"))
    if not part_files:
        return None

    return part_files[-1]


def _preferred_market_state_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}

    preferred: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("trust_state") or "") != "trusted":
            continue
        if str(row.get("interpretation_bucket") or "") != "allow_structural_use":
            continue
        continuity = str(row.get("continuity_state") or "")
        if continuity not in {"continuous", "rest_baseline_snapshot"}:
            continue
        preferred.append(row)

    if preferred:
        # Preserve append order as the time ordering contract for part files.  This
        # prevents an older continuous row from masking a newer FX REST baseline
        # service input in the same part file.
        return preferred[-1]

    return rows[-1]


def _row_age_seconds(row: dict[str, Any]) -> float | None:
    ts = row.get("collector_ts") or row.get("exchange_ts")
    if not isinstance(ts, str) or not ts:
        return None

    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None

    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def _row_freshness_label(
    row: dict[str, Any],
    *,
    live_sec: float = 30.0,
    stale_sec: float = 120.0,
) -> str:
    age = _row_age_seconds(row)
    if age is None:
        return "UNKNOWN"
    if age <= live_sec:
        return "LIVE"
    if age <= stale_sec:
        return "QUIET"
    return "STALE"


def market_state_diagnostics(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
) -> dict[str, Any]:
    latest_part = _latest_market_state_part_file(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
    )

    info: dict[str, Any] = {
        "data_root": str(core_paths.data_dir(ensure=False)),
        "market_state_root": str(market_state_root()),
        "latest_part_path": str(latest_part) if latest_part else None,
        "latest_part_exists": bool(latest_part and latest_part.exists()),
        "latest_part_mtime_utc": None,
        "latest_part_age_sec": None,
        "preferred_row_trust_state": None,
        "preferred_row_continuity_state": None,
        "preferred_row_interpretation_bucket": None,
        "preferred_row_source_series_id": None,
        "preferred_row_age_sec": None,
        "preferred_row_freshness": None,
        "preferred_row_is_stale": None,
    }

    if latest_part and latest_part.exists():
        try:
            mtime = datetime.fromtimestamp(latest_part.stat().st_mtime, tz=timezone.utc)
            info["latest_part_mtime_utc"] = mtime.isoformat().replace("+00:00", "Z")
            info["latest_part_age_sec"] = max(
                (datetime.now(timezone.utc) - mtime).total_seconds(),
                0.0,
            )
        except Exception:
            pass

        rows = _read_jsonl_rows(latest_part)
        preferred = _preferred_market_state_row(rows)
        if preferred:
            preferred_age = _row_age_seconds(preferred)
            preferred_freshness = _row_freshness_label(preferred)

            info["preferred_row_trust_state"] = preferred.get("trust_state")
            info["preferred_row_continuity_state"] = preferred.get("continuity_state")
            info["preferred_row_interpretation_bucket"] = preferred.get("interpretation_bucket")
            info["preferred_row_source_series_id"] = preferred.get("source_series_id")
            info["preferred_row_age_sec"] = preferred_age
            info["preferred_row_freshness"] = preferred_freshness
            info["preferred_row_is_stale"] = preferred_freshness == "STALE"

    return info


def load_latest_market_state(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
) -> dict[str, Any]:
    latest_part = _latest_market_state_part_file(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
    )
    if latest_part is None:
        return {}

    rows = _read_jsonl_rows(latest_part)
    return _preferred_market_state_row(rows)


def load_latest_market_summary(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
) -> MarketSummary:
    row = load_latest_market_state(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
    )
    diagnostics = market_state_diagnostics(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
    )
    source_kind = "market_state_preferred" if row else None

    return build_market_summary(
        MarketSummaryBuildInput(
            market_state_row=row,
            diagnostics=diagnostics,
            source_kind=source_kind,
        )
    )