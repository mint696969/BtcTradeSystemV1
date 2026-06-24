# path: ./btcts_next/src/btcts/collector_vnext/archive/audit.py
# desc: Archive worker audit writer. Routes high-frequency INFO progress to telemetry while keeping WARN/ERROR/control events in archive_audit.jsonl.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from btcts.collector_vnext.events import now_iso_utc
from btcts.core import telemetry

from .config import ArchiveConfig


ARCHIVE_INFO_TELEMETRY_EVENTS = frozenset(
    {
        "archive.copy.begin",
        "archive.copy.completed",
        "archive.gc.begin",
        "archive.gc.completed",
        "archive.transfer_health_summary.updated",
    }
)


def archive_audit_path(cfg: ArchiveConfig) -> Path:
    return cfg.hot_root / "logs" / "collector_vnext" / "archive_audit.jsonl"


def _should_route_archive_telemetry(event: str, *, level: str) -> bool:
    return (str(level or "INFO").upper() == "INFO") and (str(event or "") in ARCHIVE_INFO_TELEMETRY_EVENTS)


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

    if _should_route_archive_telemetry(event, level=level):
        telemetry_payload = dict(payload)
        telemetry_payload.setdefault("audit_routed", False)
        telemetry_payload.setdefault("telemetry_routed", True)
        telemetry_payload.setdefault("ps_q19b_audit_telemetry_split", True)
        telemetry.emit(
            event,
            level=level,
            feature="collector_vnext_archive",
            stream="collector_vnext_archive",
            actor="collector_vnext.archive.worker",
            site="collector_vnext.archive.audit.append_archive_audit",
            payload=telemetry_payload,
            logs_root=cfg.hot_root / "logs",
        )
        return

    path = archive_audit_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
