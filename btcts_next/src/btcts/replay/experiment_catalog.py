# path: ./btcts_next/src/btcts/replay/experiment_catalog.py
# desc: Discover saved replay strategy experiment sessions under the research artifact root.

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def list_experiment_sessions(root: Path) -> List[Dict]:
    if not root.exists() or not root.is_dir():
        return []

    rows: List[Dict] = []

    for child in root.iterdir():
        if not child.is_dir():
            continue

        summary_path = child / "experiment_summary.json"
        best_path = child / "best_strategy.json"
        regime_path = child / "regime_report.json"
        manifest_path = child / "manifest.json"
        reports_path = child / "strategy_reports.jsonl"

        rows.append(
            {
                "session_dir": str(child),
                "session_name": child.name,
                "summary_path": str(summary_path),
                "best_strategy_path": str(best_path),
                "regime_report_path": str(regime_path),
                "manifest_path": str(manifest_path),
                "strategy_reports_path": str(reports_path),
                "has_summary": summary_path.exists(),
                "has_best_strategy": best_path.exists(),
                "has_regime_report": regime_path.exists(),
                "has_manifest": manifest_path.exists(),
                "has_strategy_reports": reports_path.exists(),
                "mtime": child.stat().st_mtime,
            }
        )

    rows.sort(key=lambda row: row["mtime"], reverse=True)
    return rows