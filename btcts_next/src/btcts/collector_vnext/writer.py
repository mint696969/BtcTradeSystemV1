# path: ./btcts_next/src/btcts/collector_vnext/writer.py
# desc: JSONL append writers for raw, canonical, and state outputs in Collector vNext.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .config import CollectorConfig
from .paths import build_layer_paths, ensure_dir, part_file_path


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


def write_raw(cfg: CollectorConfig, *, exchange: str, symbol: str, channel: str, record_type: str, record: Dict[str, Any]) -> Path:
    lp = build_layer_paths(cfg, exchange=exchange, symbol=symbol, channel=channel, record_type=record_type)
    out = part_file_path(lp.raw_dir, part_no=1)
    _append_jsonl(out, record)
    return out


def write_canonical(cfg: CollectorConfig, *, exchange: str, symbol: str, channel: str, record_type: str, record: Dict[str, Any]) -> Path:
    lp = build_layer_paths(cfg, exchange=exchange, symbol=symbol, channel=channel, record_type=record_type)
    out = part_file_path(lp.canonical_dir, part_no=1)
    _append_jsonl(out, record)
    return out


def write_status(cfg: CollectorConfig, status: Dict[str, Any]) -> Path:
    state_dir = cfg.roots()["state"]
    ensure_dir(state_dir)
    out = state_dir / "status.json"
    out.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    return out