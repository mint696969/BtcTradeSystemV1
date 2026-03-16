# path: ./btcts_next/src/btcts/apps/operator_ui/decision_log_store.py
# desc: AI Operator Decision Log を JSONL に永続化し、直近履歴を読み戻す。

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from btcts.core import io, paths


def decision_log_jsonl_path() -> Path:
    return paths.data_dir() / "operator_ui" / "ai_operator_decisions.jsonl"


def _normalize_row(item: Dict[str, object]) -> Dict[str, object]:
    return {
        "ts": str(item.get("ts") or ""),
        "regime": str(item.get("regime") or ""),
        "spread_state": str(item.get("spread_state") or ""),
        "imbalance_state": str(item.get("imbalance_state") or ""),
        "delta_state": str(item.get("delta_state") or ""),
        "wall_state": str(item.get("wall_state") or ""),
        "action": str(item.get("action") or ""),
        "risk": str(item.get("risk") or ""),
        "runtime_source": str(item.get("runtime_source") or ""),
    }


def _same_row(a: Dict[str, object], b: Dict[str, object]) -> bool:
    return (
        str(a.get("ts") or "") == str(b.get("ts") or "")
        and str(a.get("regime") or "") == str(b.get("regime") or "")
        and str(a.get("spread_state") or "") == str(b.get("spread_state") or "")
        and str(a.get("imbalance_state") or "") == str(b.get("imbalance_state") or "")
        and str(a.get("delta_state") or "") == str(b.get("delta_state") or "")
        and str(a.get("wall_state") or "") == str(b.get("wall_state") or "")
        and str(a.get("action") or "") == str(b.get("action") or "")
        and str(a.get("risk") or "") == str(b.get("risk") or "")
        and str(a.get("runtime_source") or "") == str(b.get("runtime_source") or "")
    )


def load_recent_decisions(*, max_items: int = 20) -> List[Dict[str, object]]:
    rows = io.read_jsonl_tail(decision_log_jsonl_path(), max_lines=max_items)
    out: List[Dict[str, object]] = []

    for row in reversed(rows):
        try:
            out.append(_normalize_row(row))
        except Exception:
            continue

    out.reverse()
    return out[:max_items]


def append_decision(item: Dict[str, object], *, max_items_hint: int = 20) -> tuple[List[Dict[str, object]], bool]:
    normalized = _normalize_row(item)

    recent_before = load_recent_decisions(max_items=max_items_hint)
    if recent_before and _same_row(normalized, recent_before[0]):
        return recent_before[:max_items_hint], True

    row = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        **normalized,
    }

    try:
        io.append_jsonl(decision_log_jsonl_path(), row, fsync_each=True)
    except Exception:
        return [normalized] + recent_before[: max_items_hint - 1], False

    recent_after = load_recent_decisions(max_items=max_items_hint)
    if not recent_after:
        return [normalized], True

    merged = [normalized]
    for old in recent_after:
        if _same_row(normalized, old):
            continue
        merged.append(old)
        if len(merged) >= max_items_hint:
            break

    return merged[:max_items_hint], True


def overwrite_decisions(items: List[Dict[str, object]]) -> bool:
    path = decision_log_jsonl_path()
    normalized_items = [_normalize_row(x) for x in items]

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