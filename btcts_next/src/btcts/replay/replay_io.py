# path: ./btcts_next/src/btcts/replay/replay_io.py
# desc: Basic file output helpers for replay artifacts.

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Dict) -> Path:
    ensure_dir(path.parent)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def write_jsonl(path: Path, rows: Iterable[Dict]) -> Path:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path