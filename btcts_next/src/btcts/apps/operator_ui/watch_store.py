# path: ./btcts_next/src/btcts/apps/operator_ui/watch_store.py
# desc: Operator UI の Watch List を JSONL に永続化し、直近履歴を読み戻す。

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from btcts.core import io, paths


def watch_jsonl_path() -> Path:
    return paths.data_dir() / "operator_ui" / "watch_list.jsonl"


def _normalize_watch(item: Dict[str, object]) -> Dict[str, object]:
    tactic_summary_lines = tuple(
        str(line).strip()
        for line in (item.get("tactic_summary_lines") or ())
        if str(line).strip()
    )

    return {
        "ts": str(item.get("ts") or ""),
        "regime": str(item.get("regime") or ""),
        "action": str(item.get("action") or ""),
        "risk": str(item.get("risk") or ""),
        "tactic_summary_lines": tactic_summary_lines,
    }


def _same_watch(a: Dict[str, object], b: Dict[str, object]) -> bool:
    return (
        str(a.get("ts") or "") == str(b.get("ts") or "")
        and str(a.get("regime") or "") == str(b.get("regime") or "")
        and str(a.get("action") or "") == str(b.get("action") or "")
        and str(a.get("risk") or "") == str(b.get("risk") or "")
        and tuple(a.get("tactic_summary_lines") or ())
        == tuple(b.get("tactic_summary_lines") or ())
    )


def load_recent_watch_list(*, max_items: int = 12) -> List[Dict[str, object]]:
    rows = io.read_jsonl_tail(watch_jsonl_path(), max_lines=max_items)
    out: List[Dict[str, object]] = []

    for row in reversed(rows):
        try:
            out.append(_normalize_watch(row))
        except Exception:
            continue

    return out[:max_items]


def _append_row(row: Dict[str, object]) -> bool:
    path = watch_jsonl_path()

    try:
        io.append_jsonl(path, row, fsync_each=True)
        return True
    except Exception:
        return False


def append_watch(item: Dict[str, object], *, max_items_hint: int = 12) -> tuple[List[Dict[str, object]], bool]:
    normalized = _normalize_watch(item)

    recent_before = load_recent_watch_list(max_items=max_items_hint)
    if recent_before and _same_watch(normalized, recent_before[0]):
        return recent_before[:max_items_hint], True

    row = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        **normalized,
    }

    persisted = _append_row(row)
    if not persisted:
        return [normalized] + recent_before[: max_items_hint - 1], False

    recent_after = load_recent_watch_list(max_items=max_items_hint)
    if not recent_after:
        return [normalized], True

    merged = [normalized]
    for old in recent_after:
        if _same_watch(normalized, old):
            continue
        merged.append(old)
        if len(merged) >= max_items_hint:
            break

    return merged[:max_items_hint], True


def overwrite_watch_list(items: List[Dict[str, object]]) -> bool:
    path = watch_jsonl_path()
    normalized_items = [_normalize_watch(x) for x in items]

    try:
        if path.exists():
            path.unlink()

        for item in normalized_items:
            row = {
                "saved_at": datetime.now(timezone.utc).isoformat(),
                **item,
            }
            io.append_jsonl(path, row, fsync_each=True)

        return True
    except Exception:
        return False