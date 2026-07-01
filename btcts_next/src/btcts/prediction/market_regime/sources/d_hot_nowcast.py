# path: ./btcts_next/src/btcts/prediction/market_regime/sources/d_hot_nowcast.py
# desc: Read-only nowcast source snapshot builder from collector state artifacts.

from __future__ import annotations

from pathlib import Path

from ..source_snapshot import JsonSourceArtifact, NowcastSourceSnapshot
from .collector_state_reader import read_collector_state_sources


def _artifact(sources: dict[str, JsonSourceArtifact], key: str) -> JsonSourceArtifact:
    return sources[key]


def load_nowcast_source_snapshot(hot_root: str | Path) -> NowcastSourceSnapshot:
    sources = read_collector_state_sources(hot_root)
    return NowcastSourceSnapshot(
        market_state=_artifact(sources, "market_state"),
        health=_artifact(sources, "health"),
        executions=_artifact(sources, "executions"),
        daemon=_artifact(sources, "daemon"),
    )
