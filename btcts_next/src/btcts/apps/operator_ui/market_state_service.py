# path: ./btcts_next/src/btcts/apps/operator_ui/market_state_service.py
# desc: Load latest market_state records for the operator UI from data/market_state outputs.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from btcts.core import paths as core_paths


def market_state_root() -> Path:
    return core_paths.data_dir(ensure=False) / "market_state"


def _latest_jsonl_line(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return {}

    for line in reversed(lines):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            continue

    return {}


def load_latest_market_state(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
) -> dict[str, Any]:
    root = (
        market_state_root()
        / f"exchange={exchange}"
        / f"symbol={symbol_raw}"
        / f"type={state_type}"
    )

    if not root.exists():
        return {}

    date_dirs = sorted(
        [p for p in root.iterdir() if p.is_dir() and p.name.startswith("date=")],
        key=lambda p: p.name,
    )
    if not date_dirs:
        return {}

    latest_date_dir = date_dirs[-1]

    part_files = sorted(latest_date_dir.glob("part-*.jsonl"))
    if not part_files:
        return {}

    latest_part = part_files[-1]
    return _latest_jsonl_line(latest_part)