# path: ./btcts_next/src/btcts/market_engine/storage_paths.py
# desc: Output path helpers for Market Engine state files under data/market_state.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from btcts.core.paths import data_dir

from .config import MarketEngineConfig


def _utc_date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass(frozen=True)
class MarketStatePaths:
    root_dir: Path
    exchange_dir: Path
    symbol_dir: Path
    state_type_dir: Path
    date_dir: Path


def market_state_root(*, ensure: bool = True) -> Path:
    path = data_dir(ensure=ensure) / "market_state"
    return _ensure_dir(path) if ensure else path


def build_market_state_paths(
    cfg: MarketEngineConfig,
    *,
    state_type: str,
    date_str: str | None = None,
) -> MarketStatePaths:
    date_value = date_str or _utc_date_str()

    root_dir = market_state_root(ensure=True)
    exchange_dir = root_dir / f"exchange={cfg.exchange}"
    symbol_dir = exchange_dir / f"symbol={cfg.symbol_raw}"
    state_type_dir = symbol_dir / f"type={state_type}"
    date_dir = state_type_dir / f"date={date_value}"

    _ensure_dir(date_dir)

    return MarketStatePaths(
        root_dir=root_dir,
        exchange_dir=exchange_dir,
        symbol_dir=symbol_dir,
        state_type_dir=state_type_dir,
        date_dir=date_dir,
    )


def market_state_part_path(
    cfg: MarketEngineConfig,
    *,
    state_type: str,
    date_str: str | None = None,
    part_no: int = 1,
) -> Path:
    paths = build_market_state_paths(cfg, state_type=state_type, date_str=date_str)
    return paths.date_dir / f"part-{part_no:05d}.jsonl"