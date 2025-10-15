# path: ./btc_trade_system/features/collector/status.py
# desc: collector 健全性ステータスの更新/保存。data/collector/status.json を原子的に生成/上書き。

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- optional audit import (soft dependency)
try:
    from common.audit import audit  # type: ignore
except Exception:  # pragma: no cover
    audit = None  # type: ignore

ISO = "%Y-%m-%dT%H:%M:%SZ"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime(ISO)


def _to_data_root(explicit: Optional[Path] = None) -> Path:
    """
    data ルートの解決。優先順位: 引数 > ENV:BTC_TS_DATA_DIR > ./data
    common.paths が存在する場合はそれを優先的に利用（存在しない場合はフォールバック）。
    """
    if explicit:
        return Path(explicit)
    try:
        from common.paths import data_dir  # type: ignore
        return Path(data_dir())
    except Exception:
        pass
    env = os.environ.get("BTC_TS_DATA_DIR")
    if env:
        return Path(env)
    return Path("data")


@dataclass
class StatusItem:
    exchange: str
    topic: str
    last_iso: Optional[str] = None
    status: str = "OK"
    retries: Optional[int] = None
    cause: Optional[str] = None
    notes: Optional[str] = None
    source: str = "status"

@dataclass
class LeaderMeta:
    host: str
    pid: int
    started_ms: int
    heartbeat_ms: int

@dataclass
class StorageMeta:
    logs_root: str
    data_root: str
    primary_ok: bool

class StatusWriter:
    def __init__(self, data_root: Optional[Path] = None) -> None:
        self.root = _to_data_root(data_root)
        self.path = self.root / "collector" / "status.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._items: Dict[tuple[str, str], StatusItem] = {}
        self._leader: Optional[LeaderMeta] = None
        self._storage: Optional[StorageMeta] = None
        self._load_if_exists()

    def update(
        self,
        exchange: str,
        topic: str,
        *,
        ok: Optional[bool] = None,
        last_iso: Optional[str] = None,
        retries: Optional[int] = None,
        cause: Optional[str] = None,
        notes: Optional[str] = None,
        source: str = "status",
    ) -> None:
        key = (exchange, topic)
        item = self._items.get(key) or StatusItem(exchange=exchange, topic=topic)
        if last_iso is not None:
            item.last_iso = last_iso
        if ok is not None:
            item.status = "OK" if ok else "CRIT"
        if cause:
            item.cause = cause
            if item.status == "OK":
                item.status = "WARN"
        if retries is not None:
            item.retries = retries
        if notes is not None:
            item.notes = notes
        item.source = source or item.source
        self._items[key] = item

    def set_storage(self, *, logs_root: str, data_root: str, primary_ok: bool) -> None:
        self._storage = StorageMeta(logs_root=logs_root, data_root=data_root, primary_ok=primary_ok)

    def set_leader(self, host: str, pid: int, started_ms: int, heartbeat_ms: int) -> None:
        self._leader = LeaderMeta(host=host, pid=pid, started_ms=started_ms, heartbeat_ms=heartbeat_ms)

    def flush(self) -> Path:
        payload = {
            "items": [asdict(v) for v in self._items.values()],
            "updated_at": _utc_now_iso(),
        }
        if getattr(self, "_leader", None) is not None:
            payload["leader"] = asdict(self._leader)  # type: ignore[arg-type]
        if getattr(self, "_storage", None) is not None:
            payload["storage"] = asdict(self._storage)  # type: ignore[arg-type]

        tmp = self.path.with_suffix(".tmp")
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

        # audit: write event (soft)
        if audit:
            try:
                audit(
                    event="collector.status.update",
                    level="INFO",
                    feature="collector",
                    payload={"items": len(self._items), "path": str(self.path)},
                )
            except Exception:
                pass

        return self.path

    def _load_if_exists(self) -> None:
        try:
            if not self.path.exists():
                return
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            items = raw.get("items", [])
            for it in items:
                key = (it.get("exchange"), it.get("topic"))
                self._items[key] = StatusItem(
                    exchange=it.get("exchange"),
                    topic=it.get("topic"),
                    last_iso=it.get("last_iso"),
                    status=it.get("status", "OK"),
                    retries=it.get("retries"),
                    cause=it.get("cause"),
                    notes=it.get("notes"),
                    source=it.get("source", "status"),
                )

            # optional: storage meta の読み戻し
            storage = raw.get("storage")
            if storage:
                try:
                    self._storage = StorageMeta(
                        logs_root=str(storage.get("logs_root", "")),
                        data_root=str(storage.get("data_root", "")),
                        primary_ok=bool(storage.get("primary_ok", False)),
                    )
                except Exception:
                    self._storage = None

            # optional: leader meta の読み戻し
            leader = raw.get("leader")
            if leader:
                try:
                    self._leader = LeaderMeta(
                        host=leader.get("host"),
                        pid=int(leader.get("pid")),
                        started_ms=int(leader.get("started_ms")),
                        heartbeat_ms=int(leader.get("heartbeat_ms")),
                    )
                except Exception:
                    self._leader = None

        except Exception:
            self._items = {}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Update collector status.json")
    ap.add_argument("exchange")
    ap.add_argument("topic")
    ap.add_argument("--ok", dest="ok", action="store_true")
    ap.add_argument("--ng", dest="ng", action="store_true")
    ap.add_argument("--last-iso")
    ap.add_argument("--retries", type=int)
    ap.add_argument("--cause")
    ap.add_argument("--notes")
    ns = ap.parse_args()

    writer = StatusWriter()
    ok_val = True if ns.ok else (False if ns.ng else None)
    writer.update(
        ns.exchange,
        ns.topic,
        ok=ok_val,
        last_iso=ns.last_iso,
        retries=ns.retries,
        cause=ns.cause,
        notes=ns.notes,
    )
    out = writer.flush()
    print(str(out))
