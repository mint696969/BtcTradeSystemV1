# path: ./btcts_next/src/btcts/replay/replay_load.py
# desc: Load replay manifest/report and a tail of replay results for UI/research usage.

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


def _read_tail_jsonl(path: Path, lines: int = 100) -> List[Dict]:
    if not path.exists() or not path.is_file():
        return []

    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0 and data.count(b"\n") < lines:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data

    rows: List[Dict] = []

    for line in data.splitlines()[-lines:]:
        try:
            row = json.loads(line)
        except Exception:
            continue

        if isinstance(row, dict):
            rows.append(row)

    return rows


def load_replay_session(session_dir: Path, *, tail_lines: int = 100) -> Dict:
    manifest_path = session_dir / "manifest.json"
    report_path = session_dir / "replay_report.json"
    results_path = session_dir / "replay_results.jsonl"

    return {
        "session_dir": str(session_dir),
        "manifest": _read_json(manifest_path),
        "report": _read_json(report_path),
        "results_tail": _read_tail_jsonl(results_path, lines=tail_lines),
    }