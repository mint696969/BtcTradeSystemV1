# path: ./btcts_next/src/btcts/core/telemetry.py
# desc: High-frequency operational telemetry writer. Keeps audit.jsonl for low-frequency safety/audit events while routing collector success telemetry to date-partitioned JSONL.

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from . import env
from . import io
from . import paths


@dataclass(frozen=True)
class TelemetryConfig:
    enabled: bool
    mode: str
    logs_root: Path
    stream: str
    date_key: str
    path: Path
    fsync_each: bool
    file_lock: bool


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso() -> str:
    return _utc_now().isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _date_key() -> str:
    return _utc_now().strftime("%Y-%m-%d")


def _safe_stream(value: str) -> str:
    text = str(value or "collector_vnext").strip().replace("\\", "/")
    parts = [p for p in text.split("/") if p and p not in {".", ".."}]
    safe = "_".join(parts).replace(":", "_")
    return safe or "collector_vnext"


def _env_bool(name: str, default: bool) -> bool:
    raw = str(os.getenv(name, "") or "").strip().lower()
    if not raw:
        return bool(default)
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return bool(default)


def _base_meta() -> Dict[str, Any]:
    return {
        "pid": os.getpid(),
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "",
    }


def telemetry_path(*, logs_root: Path | None = None, stream: str = "collector_vnext", date_key: str | None = None) -> Path:
    root = Path(logs_root) if logs_root is not None else paths.logs_dir()
    safe_stream = _safe_stream(stream)
    date_text = str(date_key or _date_key())
    return root / "telemetry" / safe_stream / f"date={date_text}" / "part-00001.jsonl"


def get_config(*, stream: str = "collector_vnext", logs_root: Path | None = None) -> TelemetryConfig:
    date_text = _date_key()
    root = Path(logs_root) if logs_root is not None else paths.logs_dir()
    safe_stream = _safe_stream(stream)
    return TelemetryConfig(
        enabled=_env_bool("BTCTS_TELEMETRY_ENABLED", True),
        mode=env.mode(),
        logs_root=root,
        stream=safe_stream,
        date_key=date_text,
        path=telemetry_path(logs_root=root, stream=safe_stream, date_key=date_text),
        fsync_each=_env_bool("BTCTS_TELEMETRY_FSYNC_EACH", False),
        file_lock=_env_bool("BTCTS_TELEMETRY_FILE_LOCK", False),
    )


def emit(
    event: str,
    *,
    level: str = "INFO",
    feature: str = "",
    stream: str = "collector_vnext",
    payload: Optional[Dict[str, Any]] = None,
    actor: str = "",
    site: str = "",
    trace_id: Optional[str] = None,
    logs_root: Path | None = None,
) -> None:
    """Append one high-frequency telemetry row.

    Telemetry is intentionally separate from ``audit.jsonl``. It is partitioned by
    stream and UTC date and defaults to no fsync and no cross-process lock, so it
    can absorb collector success chatter without turning the primary audit stream
    into a giant operational data file.
    """

    cfg = get_config(stream=stream, logs_root=logs_root)
    if not cfg.enabled:
        return

    row: Dict[str, Any] = {
        "ts": _utc_iso(),
        "mode": cfg.mode,
        "event": event,
        "feature": feature,
        "stream": cfg.stream,
        "level": (level or "INFO").upper(),
        "actor": actor,
        "site": site,
        "trace_id": trace_id or uuid.uuid4().hex,
        "payload": payload or {},
        "meta": _base_meta(),
    }

    if cfg.file_lock:
        with io.file_lock(cfg.path, timeout_sec=1.0):
            io.append_jsonl(cfg.path, row, fsync_each=cfg.fsync_each)
        return

    io.append_jsonl(cfg.path, row, fsync_each=cfg.fsync_each)


def flush_marker(event: str = "telemetry.flush") -> None:
    emit(event, level="INFO", feature="telemetry", payload={"ok": True, "t": time.time()})
