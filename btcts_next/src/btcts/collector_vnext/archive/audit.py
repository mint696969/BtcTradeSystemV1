# path: ./btcts_next/src/btcts/collector_vnext/archive/audit.py
# desc: Archive worker audit writer.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from btcts.collector_vnext.events import now_iso_utc

from .config import ArchiveConfig


def archive_audit_path(cfg: ArchiveConfig) -> Path:
    return cfg.hot_root / "logs" / "collector_vnext" / "archive_audit.jsonl"


def append_archive_audit(
    cfg: ArchiveConfig,
    event: str,
    *,
    level: str = "INFO",
    extra: dict[str, Any] | None = None,
) -> None:
    payload = {
        "ts": now_iso_utc(),
        "level": level,
        "event": event,
    }
    if extra:
        payload.update(extra)

    path = archive_audit_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")