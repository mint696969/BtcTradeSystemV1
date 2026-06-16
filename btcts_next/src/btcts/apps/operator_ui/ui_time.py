# path: ./btcts_next/src/btcts/apps/operator_ui/ui_time.py
# desc: Format UTC timestamps for Operator UI display. en shows UTC, ja shows JST.

from __future__ import annotations

from datetime import datetime, timezone, timedelta


_JST = timezone(timedelta(hours=9))


def _parse_ts(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def format_ui_ts(value: str | None, lang: str = "en") -> str:
    dt = _parse_ts(value)
    if dt is None:
        return str(value or "-")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    if lang == "ja":
        local_dt = dt.astimezone(_JST)
        return local_dt.strftime("%Y-%m-%d %H:%M:%S JST")

    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC")