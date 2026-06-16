# path: ./btcts_next/src/btcts/collector_vnext/paths.py
# desc: Path builders for Collector vNext raw, canonical, log, and state outputs.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import CollectorConfig


def _utc_date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


@dataclass(frozen=True)
class LayerPaths:
    raw_dir: Path
    canonical_dir: Path
    state_dir: Path
    logs_dir: Path


def build_layer_paths(
    cfg: CollectorConfig,
    *,
    exchange: str,
    symbol: str,
    channel: str,
    record_type: str,
) -> LayerPaths:
    roots = cfg.roots()
    date_str = _utc_date_str()

    raw_dir = roots["raw"] / f"exchange={exchange}" / f"symbol={symbol}" / f"channel={channel}" / f"date={date_str}"
    canonical_dir = roots["canonical"] / f"exchange={exchange}" / f"symbol={symbol}" / f"type={record_type}" / f"date={date_str}"
    state_dir = roots["state"]
    logs_dir = roots["logs"]

    return LayerPaths(
        raw_dir=raw_dir,
        canonical_dir=canonical_dir,
        state_dir=state_dir,
        logs_dir=logs_dir,
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def part_file_path(base_dir: Path, part_no: int = 1) -> Path:
    ensure_dir(base_dir)
    return base_dir / f"part-{part_no:05d}.jsonl"