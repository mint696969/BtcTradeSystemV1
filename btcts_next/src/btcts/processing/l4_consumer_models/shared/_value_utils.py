# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/_value_utils.py
# desc: Internal shared value normalization helpers for L4 consumer shared modules.

from __future__ import annotations

from typing import Any


def safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None