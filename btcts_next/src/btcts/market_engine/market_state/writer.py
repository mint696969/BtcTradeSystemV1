# path: ./btcts_next/src/btcts/market_engine/market_state/writer.py
# desc: Size-bounded JSONL writer for stable market_state outputs under data/market_state.

from __future__ import annotations

import json
from pathlib import Path

from btcts.core.sharded_jsonl import append_jsonl_shard, hard_bytes_from_env, target_bytes_from_env
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.storage_paths import build_market_state_paths, market_state_part_path


def _append_jsonl(base_dir: Path, record: dict) -> Path:
    return append_jsonl_shard(base_dir, record)


def _append_explicit(path: Path, record: dict) -> Path:
    # Compatibility path for one-shot callers/tests that request a specific
    # part number. Even explicit part writes must not keep growing an already
    # oversized file; if the requested file is at/over the configured shard
    # target or hard limit, fall back to size-bounded sharding in the same
    # date directory.
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    line_bytes = len(line.encode("utf-8"))
    if path.exists():
        try:
            current_size = path.stat().st_size
        except OSError:
            current_size = hard_bytes_from_env()
        target = target_bytes_from_env()
        hard = max(target, hard_bytes_from_env())
        if current_size >= hard or current_size + line_bytes > hard or current_size + line_bytes > target:
            return append_jsonl_shard(path.parent, record)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)
    return path


class MarketStateWriter:
    def write(
        self,
        *,
        cfg: MarketEngineConfig,
        state_type: str,
        record: MarketStateRecord,
        date_str: str | None = None,
        part_no: int | None = None,
    ) -> Path:
        if part_no is not None:
            # Compatibility path for tests/one-shot callers that explicitly ask
            # for a part. Normal runtime calls leave part_no unset and use
            # size-bounded sharding.
            out = market_state_part_path(
                cfg,
                state_type=state_type,
                date_str=date_str,
                part_no=part_no,
            )
            return _append_explicit(out, record.to_dict())

        paths = build_market_state_paths(cfg, state_type=state_type, date_str=date_str)
        return _append_jsonl(paths.date_dir, record.to_dict())
