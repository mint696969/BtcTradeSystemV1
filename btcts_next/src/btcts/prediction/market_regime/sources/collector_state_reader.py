# path: ./btcts_next/src/btcts/prediction/market_regime/sources/collector_state_reader.py
# desc: Read-only collector state source reader for market-regime nowcast inputs.

from __future__ import annotations

from pathlib import Path
from typing import Dict

from ..source_snapshot import JsonSourceArtifact
from .json_io import read_json_artifact

COLLECTOR_STATE_RELATIVE_PATHS = {
    "market_state": "state/collector_vnext/unified_market_state_status.json",
    "health": "state/collector_vnext/unified_health.json",
    "executions": "state/collector_vnext/unified_executions_status.json",
    "daemon": "state/collector_vnext/unified_daemon_status.json",
}


def read_collector_state_sources(hot_root: str | Path) -> Dict[str, JsonSourceArtifact]:
    return {
        name: read_json_artifact(hot_root, relative_path)
        for name, relative_path in COLLECTOR_STATE_RELATIVE_PATHS.items()
    }
