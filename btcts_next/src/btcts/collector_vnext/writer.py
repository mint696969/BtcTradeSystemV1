# path: ./btcts_next/src/btcts/collector_vnext/writer.py
# desc: Size-bounded JSONL append writers for raw, canonical, and state outputs in Collector vNext.

from __future__ import annotations

import json
from typing import Any, Dict

from btcts.core.sharded_jsonl import append_jsonl_shard

from .config import CollectorConfig
from .paths import build_layer_paths, ensure_dir


def write_raw(cfg: CollectorConfig, *, exchange: str, symbol: str, channel: str, record_type: str, record: Dict[str, Any]):
    lp = build_layer_paths(cfg, exchange=exchange, symbol=symbol, channel=channel, record_type=record_type)
    return append_jsonl_shard(lp.raw_dir, record)


def write_canonical(cfg: CollectorConfig, *, exchange: str, symbol: str, channel: str, record_type: str, record: Dict[str, Any]):
    lp = build_layer_paths(cfg, exchange=exchange, symbol=symbol, channel=channel, record_type=record_type)
    return append_jsonl_shard(lp.canonical_dir, record)


def write_status(cfg: CollectorConfig, status: Dict[str, Any]):
    state_dir = cfg.roots()["state"]
    ensure_dir(state_dir)
    out = state_dir / "status.json"
    out.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
