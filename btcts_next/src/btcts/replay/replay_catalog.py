# path: ./btcts_next/src/btcts/replay/replay_catalog.py
# desc: Discover replay export sessions under the replay artifact root.

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def list_replay_sessions(root: Path) -> List[Dict]:
    if not root.exists() or not root.is_dir():
        return []

    rows: List[Dict] = []

    for child in root.iterdir():
        if not child.is_dir():
            continue

        manifest = child / "manifest.json"
        report = child / "replay_report.json"
        results = child / "replay_results.jsonl"

        rows.append(
            {
                "session_dir": str(child),
                "session_name": child.name,
                "manifest_path": str(manifest),
                "report_path": str(report),
                "results_path": str(results),
                "has_manifest": manifest.exists(),
                "has_report": report.exists(),
                "has_results": results.exists(),
                "mtime": child.stat().st_mtime,
            }
        )

    rows.sort(key=lambda row: row["mtime"], reverse=True)
    return rows