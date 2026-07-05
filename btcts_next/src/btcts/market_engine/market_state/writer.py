# path: ./btcts_next/src/btcts/market_engine/market_state/writer.py
# desc: Size-bounded JSONL writer for stable market_state outputs under data/market_state.

from __future__ import annotations

import json
from pathlib import Path

from btcts.core.sharded_jsonl import append_jsonl_shard
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.storage_paths import build_market_state_paths, market_state_part_path


def _append_jsonl(base_dir: Path, record: dict) -> Path:
    return append_jsonl_shard(base_dir, record)


def _append_explicit(path: Path, record: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        fh.write("\n")
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
