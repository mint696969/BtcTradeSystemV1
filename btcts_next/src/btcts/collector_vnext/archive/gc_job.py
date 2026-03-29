# path: ./btcts_next/src/btcts/collector_vnext/archive/gc_job.py
# desc: Verified GC for hot archive files after safe copy to cold.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .config import ArchiveConfig


@dataclass(frozen=True)
class DeleteItem:
    hot_path: Path
    cold_path: Path
    size_bytes: int


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _gc_cutoff_name(days: int) -> str:
    target = (_utc_now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return f"date={target}"


def _is_stable_file(path: Path, *, stable_age_sec: int) -> bool:
    try:
        age_sec = (_utc_now() - datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)).total_seconds()
        return age_sec >= stable_age_sec
    except Exception:
        return False


def _iter_date_dirs(base: Path) -> list[Path]:
    out: list[Path] = []
    if not base.exists():
        return out
    for p in base.rglob("*"):
        if p.is_dir() and p.name.startswith("date="):
            out.append(p)
    out.sort()
    return out


def build_gc_plan(cfg: ArchiveConfig) -> list[DeleteItem]:
    items: list[DeleteItem] = []
    cutoff = _gc_cutoff_name(cfg.gc_min_age_days)

    for rel_prefix in cfg.relative_prefixes:
        if not rel_prefix.startswith("data/"):
            continue

        root = cfg.hot_root / rel_prefix
        if not root.exists():
            continue

        for date_dir in _iter_date_dirs(root):
            if date_dir.name > cutoff:
                continue

            for hot_file in sorted([p for p in date_dir.rglob("*") if p.is_file()]):
                if not _is_stable_file(hot_file, stable_age_sec=cfg.stable_age_sec):
                    continue

                rel_file = hot_file.relative_to(cfg.hot_root)
                cold_file = cfg.cold_root / rel_file
                if not cold_file.exists():
                    continue

                try:
                    hot_size = hot_file.stat().st_size
                    cold_size = cold_file.stat().st_size
                except Exception:
                    continue

                if cold_size < hot_size:
                    continue

                items.append(DeleteItem(hot_path=hot_file, cold_path=cold_file, size_bytes=hot_size))

    return items[: cfg.max_delete_files_per_cycle]


def execute_gc_plan(items: list[DeleteItem], *, dry_run: bool) -> dict[str, int | list[dict[str, str]]]:
    deleted_files = 0
    deleted_bytes = 0
    errors: list[dict[str, str]] = []

    for item in items:
        try:
            if not dry_run:
                item.hot_path.unlink(missing_ok=False)
            deleted_files += 1
            deleted_bytes += int(item.size_bytes)
        except Exception as exc:
            errors.append(
                {
                    "hot_path": str(item.hot_path),
                    "cold_path": str(item.cold_path),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    return {
        "deleted_files": deleted_files,
        "deleted_bytes": deleted_bytes,
        "error_count": len(errors),
        "errors_sample": errors[:20],
    }