# path: ./btcts_next/src/btcts/apps/operator_ui/health_telemetry_rollup.py
# desc: Read-only D-hot collector telemetry to compact per-minute Operator UI Health rollups cached under repo tmp.

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from btcts.apps.operator_ui.health_ranges import bucket_floor, range_config
from btcts.core import paths as core_paths
from btcts.core.sharded_jsonl import iter_jsonl_part_files

HEALTH_TELEMETRY_ROLLUP_VERSION = "health_telemetry_rollup.v3.d_hot_priority"
HOT_LOGS_ROOT = Path(r"D:\btc_ts_hot\logs")
HEALTH_TELEMETRY_STREAM = "collector_vnext"
HEALTH_TELEMETRY_EVENTS = frozenset(
    {
        "collector_vnext.unified.board_snapshot.completed",
        "collector_vnext.unified.rest_trades.completed",
        "collector_vnext.unified.ws_board.message.received",
        "collector_vnext.unified.ws_executions.message.received",
        "collector_vnext.unified.ws_executions.trade.written",
    }
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _minute_key(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")


def project_root() -> Path:
    # core_paths.repo_root() resolves to the btcts_next package root here.
    return core_paths.repo_root().parent


def default_cache_root() -> Path:
    return project_root() / "tmp" / "operator_ui" / "health_rollup"


def resolve_logs_root(logs_root: Path | None = None) -> Path:
    if logs_root is not None:
        return Path(logs_root)

    hot_telemetry = HOT_LOGS_ROOT / "telemetry" / HEALTH_TELEMETRY_STREAM
    if hot_telemetry.exists():
        return HOT_LOGS_ROOT

    configured = core_paths.logs_dir(ensure=False)
    configured_telemetry = configured / "telemetry" / HEALTH_TELEMETRY_STREAM
    if configured_telemetry.exists():
        return configured

    return HOT_LOGS_ROOT


def telemetry_date_dir(*, date_key: str, logs_root: Path | None = None) -> Path:
    root = resolve_logs_root(logs_root)
    return root / "telemetry" / HEALTH_TELEMETRY_STREAM / f"date={date_key}"


def telemetry_paths_for_date(*, date_key: str, logs_root: Path | None = None) -> list[Path]:
    date_dir = telemetry_date_dir(date_key=date_key, logs_root=logs_root)
    if not date_dir.exists() or not date_dir.is_dir():
        return []
    return list(iter_jsonl_part_files(date_dir))


def _empty_cache(date_key: str, *, source_logs_root: Path | None = None) -> dict[str, Any]:
    return {
        "version": HEALTH_TELEMETRY_ROLLUP_VERSION,
        "date_key": date_key,
        "source_logs_root": str(source_logs_root) if source_logs_root is not None else None,
        "offsets": {},
        "source_sizes": {},
        "source_mtimes_ns": {},
        "minutes": {},
    }


def _load_cache(path: Path, *, date_key: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _empty_cache(date_key)
    if payload.get("version") != HEALTH_TELEMETRY_ROLLUP_VERSION:
        return _empty_cache(date_key)
    if payload.get("date_key") != date_key:
        return _empty_cache(date_key)
    return payload


def _write_cache(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def _add_event(payload: dict[str, Any], *, minute: str, event: str) -> None:
    minutes = payload.setdefault("minutes", {})
    row = minutes.setdefault(minute, {})
    row[event] = int(row.get(event) or 0) + 1


def _scan_path(payload: dict[str, Any], path: Path) -> bool:
    key = str(path)
    stat = path.stat()
    offsets = payload.setdefault("offsets", {})
    source_sizes = payload.setdefault("source_sizes", {})
    source_mtimes = payload.setdefault("source_mtimes_ns", {})
    offset = int(offsets.get(key) or 0)
    stored_size = int(source_sizes.get(key) or -1)
    stored_mtime_ns = int(source_mtimes.get(key) or -1)

    if stat.st_size < offset:
        payload["minutes"] = {}
        payload["offsets"] = {}
        payload["source_sizes"] = {}
        payload["source_mtimes_ns"] = {}
        offset = 0
        offsets = payload["offsets"]
        source_sizes = payload["source_sizes"]
        source_mtimes = payload["source_mtimes_ns"]
        stored_size = -1
        stored_mtime_ns = -1

    if stored_size == stat.st_size and stored_mtime_ns == stat.st_mtime_ns:
        return False

    committed_offset = offset
    with path.open("rb") as handle:
        handle.seek(offset)
        while True:
            line_start = handle.tell()
            raw = handle.readline()
            if not raw:
                break
            if not raw.endswith(b"\n"):
                handle.seek(line_start)
                break
            committed_offset = handle.tell()
            try:
                row = json.loads(raw.decode("utf-8"))
            except Exception:
                continue
            event = str(row.get("event") or "")
            if event not in HEALTH_TELEMETRY_EVENTS:
                continue
            dt = _parse_ts(row.get("ts"))
            if dt is None:
                continue
            _add_event(payload, minute=_minute_key(dt), event=event)

    offsets[key] = committed_offset
    source_sizes[key] = stat.st_size
    source_mtimes[key] = stat.st_mtime_ns
    return True


def update_daily_rollup(
    *,
    date_key: str,
    logs_root: Path | None = None,
    cache_root: Path | None = None,
) -> dict[str, Any]:
    resolved_cache_root = Path(cache_root) if cache_root is not None else default_cache_root()
    cache_path = resolved_cache_root / f"date={date_key}.json"
    resolved_logs_root = resolve_logs_root(logs_root)
    payload = _load_cache(cache_path, date_key=date_key)
    if payload.get("source_logs_root") != str(resolved_logs_root):
        payload = _empty_cache(date_key, source_logs_root=resolved_logs_root)
    paths = telemetry_paths_for_date(date_key=date_key, logs_root=resolved_logs_root)
    changed = not cache_path.exists() or not payload.get("updated_at")

    known = set(payload.get("offsets") or {})
    current = {str(path) for path in paths}
    if known - current:
        payload = _empty_cache(date_key, source_logs_root=resolved_logs_root)
        changed = True

    for path in paths:
        changed = _scan_path(payload, path) or changed

    if int(payload.get("source_file_count") or 0) != len(paths):
        changed = True

    if changed:
        payload["updated_at"] = _utc_now().isoformat().replace("+00:00", "Z")
        payload["source_file_count"] = len(paths)
        _write_cache(cache_path, payload)

    return payload


def _date_keys(start: datetime, end: datetime) -> list[str]:
    cursor = start.astimezone(timezone.utc).date()
    end_date = end.astimezone(timezone.utc).date()
    out: list[str] = []
    while cursor <= end_date:
        out.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return out


def build_health_telemetry_rows(
    *,
    range_key: str,
    logs_root: Path | None = None,
    cache_root: Path | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    resolved_now = (now or _utc_now()).astimezone(timezone.utc)
    cfg = range_config(range_key)
    window_minutes = int(cfg["window_minutes"])
    bucket_minutes = int(cfg["bucket_minutes"])
    start = resolved_now - timedelta(minutes=window_minutes)

    # Aggregate directly from cached one-minute counts into the selected
    # display bucket. This keeps the durable cache fine-grained while avoiding
    # expansion to tens of thousands of synthetic event rows for 24h/1w views.
    bucketed: dict[tuple[str, str], int] = {}
    bucket_sources: dict[tuple[str, str], str] = {}

    for date_key in _date_keys(start, resolved_now):
        payload = update_daily_rollup(
            date_key=date_key,
            logs_root=logs_root,
            cache_root=cache_root,
        )
        source_path = str(telemetry_date_dir(date_key=date_key, logs_root=logs_root))
        minutes = payload.get("minutes") or {}
        for minute, counts in minutes.items():
            dt = _parse_ts(minute)
            if dt is None or dt < start or dt > resolved_now:
                continue
            bucket_dt = bucket_floor(dt, bucket_minutes)
            bucket_ts = bucket_dt.isoformat().replace("+00:00", "Z")
            for event, count in dict(counts).items():
                count_value = int(count or 0)
                if count_value <= 0:
                    continue
                key = (bucket_ts, str(event))
                bucketed[key] = bucketed.get(key, 0) + count_value
                bucket_sources.setdefault(key, source_path)

    rows: list[dict[str, Any]] = []
    for (bucket_ts, event), count in bucketed.items():
        rows.append(
            {
                "ts": bucket_ts,
                "event": event,
                "level": "INFO",
                "feature": "collector_vnext",
                "payload": {
                    "health_event_count": count,
                    "telemetry_rollup": True,
                    "telemetry_rollup_bucket_minutes": bucket_minutes,
                    "telemetry_rollup_direct_bucket": True,
                },
                "health_source_kind": "telemetry_collector_vnext_rollup",
                "health_source_path": bucket_sources.get((bucket_ts, event)),
            }
        )

    rows.extend(
        [
            {
                "ts": start.isoformat().replace("+00:00", "Z"),
                "event": "health.telemetry.rollup.coverage.start",
                "payload": {
                    "telemetry_rollup": True,
                    "telemetry_rollup_bucket_minutes": bucket_minutes,
                },
                "health_source_kind": "telemetry_collector_vnext_rollup",
            },
            {
                "ts": resolved_now.isoformat().replace("+00:00", "Z"),
                "event": "health.telemetry.rollup.coverage.end",
                "payload": {
                    "telemetry_rollup": True,
                    "telemetry_rollup_bucket_minutes": bucket_minutes,
                },
                "health_source_kind": "telemetry_collector_vnext_rollup",
            },
        ]
    )
    rows.sort(key=lambda row: (str(row.get("ts") or ""), str(row.get("event") or "")))
    return rows
