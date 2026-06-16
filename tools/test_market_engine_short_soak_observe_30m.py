# path: ./tools/test_market_engine_short_soak_observe_30m.py
# desc: Observe market_state outputs for 30 minutes and summarize the minimum short-soak gate signals.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_overview,
    market_monitor_metrics,
    market_state_status_caption,
)
from btcts.core import paths as core_paths


MAX_SECONDS = float(os.getenv("BTCTS_MARKET_ENGINE_SOAK_SECONDS", "1800").strip() or "1800")
POLL_INTERVAL_SEC = float(os.getenv("BTCTS_MARKET_ENGINE_SOAK_POLL_SEC", "5").strip() or "5")
EXCHANGE = os.getenv("BTCTS_MARKET_ENGINE_EXCHANGE", "bitflyer").strip() or "bitflyer"
SYMBOL_RAW = os.getenv("BTCTS_MARKET_ENGINE_SYMBOL", "BTC_JPY").strip() or "BTC_JPY"
STATE_TYPE = os.getenv("BTCTS_MARKET_ENGINE_STATE_TYPE", "market.overview").strip() or "market.overview"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def market_state_root() -> Path:
    return (
        core_paths.data_dir(ensure=False)
        / "market_state"
        / f"exchange={EXCHANGE}"
        / f"symbol={SYMBOL_RAW}"
        / f"type={STATE_TYPE}"
    )


def _latest_part_file(root: Path) -> Path | None:
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


def _read_all_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
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


@dataclass
class ObserveSummary:
    started_at: str
    finished_at: str
    observed_seconds: float
    poll_interval_sec: float
    output_path: str | None
    record_count: int
    trust_counts: dict[str, int]
    boundary_counts: dict[str, int]
    continuity_counts: dict[str, int]
    latest_trust_state: str | None
    latest_boundary_reason: str | None
    latest_continuity_state: str | None
    latest_best_bid: float | None
    latest_best_ask: float | None
    latest_spread: float | None
    latest_mid_price: float | None
    ui_caption: str
    ui_metrics_visible: bool
    gate_checks: dict[str, bool]
    ok: bool


def observe() -> ObserveSummary:
    started_at = utc_now_iso()
    started_monotonic = time.monotonic()

    root = market_state_root()
    seen_count = 0
    stable_polls = 0

    while True:
        elapsed = time.monotonic() - started_monotonic
        if elapsed >= MAX_SECONDS:
            break

        latest_part = _latest_part_file(root)
        rows = _read_all_rows(latest_part)
        current_count = len(rows)

        if current_count > seen_count:
            seen_count = current_count
            stable_polls = 0
        else:
            stable_polls += 1

        time.sleep(POLL_INTERVAL_SEC)

    latest_part = _latest_part_file(root)
    rows = _read_all_rows(latest_part)

    trust_counts = Counter()
    boundary_counts = Counter()
    continuity_counts = Counter()

    for row in rows:
        trust_counts[str(row.get("trust_state") or "missing")] += 1
        boundary_counts[str(row.get("boundary_reason") or "missing")] += 1
        continuity_counts[str(row.get("continuity_state") or "missing")] += 1

    latest = load_market_overview(exchange=EXCHANGE, symbol_raw=SYMBOL_RAW)
    metrics = market_monitor_metrics(latest)
    caption = market_state_status_caption(latest)

    latest_best_bid = latest.get("best_bid")
    latest_best_ask = latest.get("best_ask")
    latest_spread = latest.get("spread")
    latest_mid_price = latest.get("mid_price")

    gate_checks = {
        "market_state_records_exist": len(rows) > 0,
        "market_state_records_multiple": len(rows) >= 2,
        "ui_can_read_latest_state": bool(latest),
        "ui_can_show_trust_boundary_series": (
            "trust=" in caption and "boundary=" in caption and "series=" in caption
        ),
        "top_of_book_visible": (
            latest_best_bid is not None and latest_best_ask is not None and latest_spread is not None
        ),
        "mid_price_visible": latest_mid_price is not None,
        "continuity_state_visible": bool(latest.get("continuity_state")),
        "near_zone_visible": (
            isinstance(latest.get("near_zone_bids"), list)
            and isinstance(latest.get("near_zone_asks"), list)
        ),
        "ui_metrics_visible": (
            metrics.get("best_bid") is not None
            and metrics.get("best_ask") is not None
            and metrics.get("spread") is not None
        ),
        "boundary_not_silent": any(key != "missing" for key in boundary_counts.keys()),
        "trust_not_silent": any(key != "missing" for key in trust_counts.keys()),
    }

    ok = all(gate_checks.values())

    return ObserveSummary(
        started_at=started_at,
        finished_at=utc_now_iso(),
        observed_seconds=round(time.monotonic() - started_monotonic, 1),
        poll_interval_sec=POLL_INTERVAL_SEC,
        output_path=str(latest_part) if latest_part else None,
        record_count=len(rows),
        trust_counts=dict(trust_counts),
        boundary_counts=dict(boundary_counts),
        continuity_counts=dict(continuity_counts),
        latest_trust_state=latest.get("trust_state"),
        latest_boundary_reason=latest.get("boundary_reason"),
        latest_continuity_state=latest.get("continuity_state"),
        latest_best_bid=latest_best_bid,
        latest_best_ask=latest_best_ask,
        latest_spread=latest_spread,
        latest_mid_price=latest_mid_price,
        ui_caption=caption,
        ui_metrics_visible=gate_checks["ui_metrics_visible"],
        gate_checks=gate_checks,
        ok=ok,
    )


def main() -> None:
    summary = observe()
    print(
        json.dumps(
            {
                "started_at": summary.started_at,
                "finished_at": summary.finished_at,
                "observed_seconds": summary.observed_seconds,
                "poll_interval_sec": summary.poll_interval_sec,
                "exchange": EXCHANGE,
                "symbol_raw": SYMBOL_RAW,
                "state_type": STATE_TYPE,
                "output_path": summary.output_path,
                "record_count": summary.record_count,
                "trust_counts": summary.trust_counts,
                "boundary_counts": summary.boundary_counts,
                "continuity_counts": summary.continuity_counts,
                "latest_trust_state": summary.latest_trust_state,
                "latest_boundary_reason": summary.latest_boundary_reason,
                "latest_continuity_state": summary.latest_continuity_state,
                "latest_best_bid": summary.latest_best_bid,
                "latest_best_ask": summary.latest_best_ask,
                "latest_spread": summary.latest_spread,
                "latest_mid_price": summary.latest_mid_price,
                "ui_caption": summary.ui_caption,
                "ui_metrics_visible": summary.ui_metrics_visible,
                "gate_checks": summary.gate_checks,
                "ok": summary.ok,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()