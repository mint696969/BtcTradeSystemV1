# path: ./btcts_next/src/btcts/replay/experiment_load.py
# desc: Load saved replay strategy experiment artifacts for research UI.

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _read_json(path: Path) -> Optional[Dict]:
    if not path.exists() or not path.is_file():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_jsonl(path: Path) -> List[Dict]:
    if not path.exists() or not path.is_file():
        return []

    rows: List[Dict] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except Exception:
                continue

            if isinstance(row, dict):
                rows.append(row)

    return rows


def load_experiment_session(session_dir: Path) -> Dict:
    summary_path = session_dir / "experiment_summary.json"
    best_path = session_dir / "best_strategy.json"
    regime_path = session_dir / "regime_report.json"
    reports_path = session_dir / "strategy_reports.jsonl"
    manifest_path = session_dir / "manifest.json"

    return {
        "session_dir": str(session_dir),
        "summary": _read_json(summary_path),
        "best_strategy": _read_json(best_path),
        "regime_report": _read_json(regime_path),
        "strategy_reports": _read_jsonl(reports_path),
        "manifest": _read_json(manifest_path),
    }