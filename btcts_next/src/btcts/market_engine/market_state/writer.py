# path: ./btcts_next/src/btcts/market_engine/market_state/writer.py
# desc: JSONL writer for stable market_state outputs under data/market_state.

from __future__ import annotations

import json
from pathlib import Path

from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.storage_paths import market_state_part_path


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        fh.write("\n")


class MarketStateWriter:
    def write(
        self,
        *,
        cfg: MarketEngineConfig,
        state_type: str,
        record: MarketStateRecord,
        date_str: str | None = None,
        part_no: int = 1,
    ) -> Path:
        out = market_state_part_path(
            cfg,
            state_type=state_type,
            date_str=date_str,
            part_no=part_no,
        )
        _append_jsonl(out, record.to_dict())
        return out