# path: ./btcts_next/src/btcts/apps/operator_ui/ai_memory_store.py
# desc: Operator UI の市場状態メモリを JSONL へ永続化し、直近履歴を読み戻す。競合時は session memory を優先して継続する。

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from btcts.core import io, paths


def memory_jsonl_path() -> Path:
    return paths.data_dir() / "operator_ui" / "ai_market_memory.jsonl"


def _normalize_entry(entry: Dict[str, float]) -> Dict[str, float]:
    return {
        "spread": float(entry["spread"]),
        "imbalance": float(entry["imbalance"]),
        "delta": float(entry["delta"]),
        "wall_ratio": float(entry["wall_ratio"]),
    }


def _same_entry(a: Dict[str, float], b: Dict[str, float]) -> bool:
    return (
        abs(float(a["spread"]) - float(b["spread"])) <= 1e-9
        and abs(float(a["imbalance"]) - float(b["imbalance"])) <= 1e-9
        and abs(float(a["delta"]) - float(b["delta"])) <= 1e-9
        and abs(float(a["wall_ratio"]) - float(b["wall_ratio"])) <= 1e-9
    )


def _merge_front(entry: Dict[str, float], rows: List[Dict[str, float]], *, max_items: int) -> List[Dict[str, float]]:
    merged = [entry]

    for row in rows:
        try:
            normalized = _normalize_entry(row)
        except Exception:
            continue

        if _same_entry(entry, normalized):
            continue

        merged.append(normalized)

        if len(merged) >= max_items:
            break

    return merged[:max_items]


def load_recent_memory(*, max_items: int = 8) -> List[Dict[str, float]]:
    rows = io.read_jsonl_tail(memory_jsonl_path(), max_lines=max_items)
    out: List[Dict[str, float]] = []

    for row in reversed(rows):
        try:
            out.append(
                {
                    "spread": float(row["spread"]),
                    "imbalance": float(row["imbalance"]),
                    "delta": float(row["delta"]),
                    "wall_ratio": float(row["wall_ratio"]),
                }
            )
        except Exception:
            continue

    out.reverse()
    return out[:max_items]


def _append_row_with_retry(row: Dict[str, float], *, attempts: int = 3) -> bool:
    path = memory_jsonl_path()

    for i in range(attempts):
        try:
            with io.file_lock(path, timeout_sec=0.5, stale_sec=5.0):
                io.append_jsonl(path, row, fsync_each=True)
            return True

        except (PermissionError, TimeoutError):
            if i == attempts - 1:
                return False
            time.sleep(0.08 * (i + 1))

    return False


def append_memory(entry: Dict[str, float], *, max_items_hint: int = 8) -> List[Dict[str, float]]:
    normalized = _normalize_entry(entry)

    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **normalized,
    }

    recent_before = load_recent_memory(max_items=max_items_hint)

    persisted = _append_row_with_retry(row, attempts=3)

    if not persisted:
        return _merge_front(normalized, recent_before, max_items=max_items_hint)

    recent_after = load_recent_memory(max_items=max_items_hint)

    if not recent_after:
        return [normalized]

    return _merge_front(normalized, recent_after, max_items=max_items_hint)