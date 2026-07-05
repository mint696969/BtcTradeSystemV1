# path: ./btcts_next/src/btcts/collector_vnext/archive/gc_job.py
# desc: Verified GC for hot archive files after safe copy to cold.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from .config import ArchiveConfig
from .file_policy import is_archive_gc_candidate


def _same_resolved_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve(strict=False) == right.resolve(strict=False)
    except Exception:
        return str(left.absolute()).casefold() == str(right.absolute()).casefold()


@dataclass(frozen=True)
class DeleteItem:
    hot_path: Path
    cold_path: Path
    size_bytes: int
    relative_path: str
    cold_size_bytes: int


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


def _plan_limit_reached(
    *,
    planned_count: int,
    planned_bytes: int,
    next_size: int,
    max_files: int,
    max_bytes: int,
) -> bool:
    if planned_count >= max_files:
        return True
    if planned_count > 0 and planned_bytes + next_size > max_bytes:
        return True
    return False


def build_gc_plan(cfg: ArchiveConfig) -> list[DeleteItem]:
    if _same_resolved_path(cfg.hot_root, cfg.cold_root):
        return []

    items: list[DeleteItem] = []
    cutoff = _gc_cutoff_name(cfg.gc_min_age_days)
    planned_bytes = 0

    for rel_prefix in cfg.resolved_gc_prefixes():
        if not rel_prefix.startswith("data/"):
            continue

        root = cfg.hot_root / rel_prefix
        if not root.exists():
            continue

        for date_dir in _iter_date_dirs(root):
            if date_dir.name > cutoff:
                continue

            for hot_file in sorted(p for p in date_dir.rglob("*") if is_archive_gc_candidate(p)):
                if not _is_stable_file(hot_file, stable_age_sec=cfg.stable_age_sec):
                    continue

                rel_file = hot_file.relative_to(cfg.hot_root)
                cold_file = cfg.cold_root / rel_file
                if _same_resolved_path(hot_file, cold_file):
                    continue
                if not cold_file.exists():
                    continue

                try:
                    hot_size = hot_file.stat().st_size
                    cold_size = cold_file.stat().st_size
                except Exception:
                    continue

                # Automatic GC must require exact D/E size equality. A larger
                # cold file is not treated as safe because it can indicate an
                # unexpected path collision, append, or schema/rotation issue.
                if cold_size != hot_size:
                    continue

                if _plan_limit_reached(
                    planned_count=len(items),
                    planned_bytes=planned_bytes,
                    next_size=hot_size,
                    max_files=cfg.max_delete_files_per_cycle,
                    max_bytes=cfg.max_delete_bytes_per_cycle,
                ):
                    return items

                items.append(
                    DeleteItem(
                        hot_path=hot_file,
                        cold_path=cold_file,
                        size_bytes=hot_size,
                        relative_path=rel_file.as_posix(),
                        cold_size_bytes=cold_size,
                    )
                )
                planned_bytes += int(hot_size)

    return items


def _verify_before_delete(item: DeleteItem) -> tuple[bool, dict[str, Any]]:
    details: dict[str, Any] = {
        "hot_path": str(item.hot_path),
        "cold_path": str(item.cold_path),
        "relative_path": item.relative_path,
        "expected_size_bytes": int(item.size_bytes),
    }
    if _same_resolved_path(item.hot_path, item.cold_path):
        details["error"] = "hot_cold_path_same_before_delete"
        return False, details

    try:
        hot_stat = item.hot_path.stat()
        cold_stat = item.cold_path.stat()
    except Exception as exc:
        details["error"] = f"pre_delete_stat_failed: {type(exc).__name__}: {exc}"
        return False, details

    details["hot_size_bytes"] = int(hot_stat.st_size)
    details["cold_size_bytes"] = int(cold_stat.st_size)
    details["cold_present_before_delete"] = True

    if int(hot_stat.st_size) != int(item.size_bytes):
        details["error"] = "hot_size_changed_before_delete"
        return False, details
    if int(cold_stat.st_size) != int(item.size_bytes):
        details["error"] = "cold_size_mismatch_before_delete"
        return False, details
    return True, details


def _verify_after_delete(item: DeleteItem) -> tuple[bool, dict[str, Any]]:
    details: dict[str, Any] = {
        "hot_path": str(item.hot_path),
        "cold_path": str(item.cold_path),
        "relative_path": item.relative_path,
        "expected_size_bytes": int(item.size_bytes),
    }
    hot_exists = item.hot_path.exists()
    cold_exists = item.cold_path.exists()
    details["hot_missing_after_delete"] = not hot_exists
    details["cold_present_after_delete"] = cold_exists

    if hot_exists:
        details["error"] = "hot_file_still_present_after_delete"
        return False, details
    if not cold_exists:
        details["error"] = "cold_file_missing_after_delete"
        return False, details

    try:
        cold_size = item.cold_path.stat().st_size
    except Exception as exc:
        details["error"] = f"post_delete_cold_stat_failed: {type(exc).__name__}: {exc}"
        return False, details

    details["cold_size_bytes_after_delete"] = int(cold_size)
    if int(cold_size) != int(item.size_bytes):
        details["error"] = "cold_size_changed_after_delete"
        return False, details
    return True, details


def execute_gc_plan(items: list[DeleteItem], *, dry_run: bool) -> dict[str, Any]:
    deleted_files = 0
    deleted_bytes = 0
    planned_deleted_files = len(items)
    planned_deleted_bytes = sum(int(item.size_bytes) for item in items)
    verified_before_files = 0
    verified_after_files = 0
    errors: list[dict[str, Any]] = []
    audit_sample: list[dict[str, Any]] = []

    for item in items:
        ok_before, before_details = _verify_before_delete(item)
        if not ok_before:
            errors.append(before_details)
            continue
        verified_before_files += 1

        if dry_run:
            if len(audit_sample) < 20:
                audit_sample.append({**before_details, "dry_run": True})
            continue

        try:
            item.hot_path.unlink(missing_ok=False)
        except Exception as exc:
            errors.append(
                {
                    **before_details,
                    "error": f"delete_failed: {type(exc).__name__}: {exc}",
                }
            )
            continue

        ok_after, after_details = _verify_after_delete(item)
        if not ok_after:
            errors.append(after_details)
            continue

        verified_after_files += 1
        deleted_files += 1
        deleted_bytes += int(item.size_bytes)
        if len(audit_sample) < 20:
            audit_sample.append({**after_details, "dry_run": False})

    return {
        "deleted_files": deleted_files,
        "deleted_bytes": deleted_bytes,
        "planned_deleted_files": planned_deleted_files,
        "planned_deleted_bytes": planned_deleted_bytes,
        "verified_before_files": verified_before_files,
        "verified_after_files": verified_after_files,
        "dry_run": dry_run,
        "error_count": len(errors),
        "errors_sample": errors[:20],
        "audit_sample": audit_sample,
    }
