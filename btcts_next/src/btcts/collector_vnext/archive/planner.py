# path: ./btcts_next/src/btcts/collector_vnext/archive/planner.py
# desc: Safe copy planner for hot/cold archive.

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .config import ArchiveConfig


@dataclass(frozen=True)
class CopyItem:
    src: Path
    dst: Path
    kind: str  # file | dir
    size_bytes: int


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _today_date_dir_name() -> str:
    return f"date={_utc_now().strftime('%Y-%m-%d')}"


def _copy_cutoff_name(days: int) -> str:
    target = (_utc_now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return f"date={target}"


def _iter_target_roots(hot_root: Path, relative_prefixes: list[str]) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for rel in relative_prefixes:
        p = hot_root / rel
        if p.exists():
            out.append((rel, p))
    return out


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


def build_copy_plan(cfg: ArchiveConfig) -> list[CopyItem]:
    items: list[CopyItem] = []
    today_name = _today_date_dir_name()
    copy_cutoff = _copy_cutoff_name(cfg.copy_min_age_days)

    for rel_prefix, root in _iter_target_roots(cfg.hot_root, cfg.relative_prefixes):
        if rel_prefix.startswith("data/"):
            for date_dir in _iter_date_dirs(root):
                if date_dir.name >= today_name:
                    continue
                if date_dir.name > copy_cutoff:
                    continue

                rel = date_dir.relative_to(cfg.hot_root)
                dst_dir = cfg.cold_root / rel

                if not dst_dir.exists():
                    for src_file in sorted([p for p in date_dir.rglob("*") if p.is_file()]):
                        if not _is_stable_file(src_file, stable_age_sec=cfg.stable_age_sec):
                            continue

                        rel_file = src_file.relative_to(cfg.hot_root)
                        dst_file = cfg.cold_root / rel_file

                        try:
                            src_size = src_file.stat().st_size
                        except Exception:
                            continue

                        items.append(CopyItem(src=src_file, dst=dst_file, kind="file", size_bytes=src_size))
                    continue

                for src_file in sorted([p for p in date_dir.rglob("*") if p.is_file()]):
                    if not _is_stable_file(src_file, stable_age_sec=cfg.stable_age_sec):
                        continue

                    rel_file = src_file.relative_to(cfg.hot_root)
                    dst_file = cfg.cold_root / rel_file

                    try:
                        src_size = src_file.stat().st_size
                    except Exception:
                        continue

                    if not dst_file.exists():
                        items.append(CopyItem(src=src_file, dst=dst_file, kind="file", size_bytes=src_size))
                        continue

                    try:
                        dst_size = dst_file.stat().st_size
                    except Exception:
                        dst_size = -1

                    if dst_size < src_size:
                        items.append(CopyItem(src=src_file, dst=dst_file, kind="file", size_bytes=src_size))
            continue

        for src_file in sorted([p for p in root.rglob("*") if p.is_file()]):
            if not _is_stable_file(src_file, stable_age_sec=cfg.stable_age_sec):
                continue

            rel_file = src_file.relative_to(cfg.hot_root)
            dst_file = cfg.cold_root / rel_file

            try:
                src_size = src_file.stat().st_size
            except Exception:
                continue

            if not dst_file.exists():
                items.append(CopyItem(src=src_file, dst=dst_file, kind="file", size_bytes=src_size))
                continue

            try:
                dst_size = dst_file.stat().st_size
            except Exception:
                dst_size = -1

            if dst_size < src_size:
                items.append(CopyItem(src=src_file, dst=dst_file, kind="file", size_bytes=src_size))

    planned: list[CopyItem] = []
    bytes_so_far = 0

    for item in items:
        if len(planned) >= cfg.max_files_per_cycle:
            break
        if planned and bytes_so_far + item.size_bytes > cfg.max_bytes_per_cycle:
            break
        planned.append(item)
        bytes_so_far += item.size_bytes

    return planned


def execute_copy_plan(items: list[CopyItem]) -> dict[str, int | list[dict[str, str]]]:
    copied_dirs = 0
    copied_files = 0
    copied_bytes = 0
    errors: list[dict[str, str]] = []

    for item in items:
        try:
            item.dst.parent.mkdir(parents=True, exist_ok=True)
            if item.kind == "dir":
                shutil.copytree(item.src, item.dst, dirs_exist_ok=True)
                copied_dirs += 1
            else:
                shutil.copy2(item.src, item.dst)
                copied_files += 1
            copied_bytes += int(item.size_bytes)
        except Exception as exc:
            errors.append(
                {
                    "src": str(item.src),
                    "dst": str(item.dst),
                    "kind": item.kind,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    return {
        "copied_dirs": copied_dirs,
        "copied_files": copied_files,
        "copied_bytes": copied_bytes,
        "error_count": len(errors),
        "errors_sample": errors[:20],
    }