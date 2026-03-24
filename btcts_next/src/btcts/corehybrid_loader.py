# path: ./btcts_next/src/btcts/core/hybrid_loader.py
# desc: Resolve hybrid data sources with cold-first and hot-tail strategy.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class HybridSourcePlan:
    cold_root: Path
    hot_root: Path
    relative_prefix: str
    dates: list[str]
    cold_files: list[Path]
    hot_tail_files: list[Path]

    @property
    def ordered_files(self) -> list[Path]:
        return [*self.cold_files, *self.hot_tail_files]


def _date_dir_name(date_str: str) -> str:
    return f"date={date_str}"


def _collect_files_in_date_dir(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    return sorted([p for p in base_dir.rglob("*") if p.is_file()])


def _relative_file_key(path: Path, base_dir: Path) -> str:
    return str(path.relative_to(base_dir)).replace("\\", "/")


def _resolve_date_files(root: Path, relative_prefix: str, date_str: str) -> list[Path]:
    date_dir = root / relative_prefix / _date_dir_name(date_str)
    return _collect_files_in_date_dir(date_dir)


def _build_hot_tail_files(
    *,
    cold_root: Path,
    hot_root: Path,
    relative_prefix: str,
    date_str: str,
) -> list[Path]:
    hot_date_dir = hot_root / relative_prefix / _date_dir_name(date_str)
    cold_date_dir = cold_root / relative_prefix / _date_dir_name(date_str)

    hot_files = _collect_files_in_date_dir(hot_date_dir)
    if not hot_files:
        return []

    cold_files = _collect_files_in_date_dir(cold_date_dir)
    cold_key_map = {
        _relative_file_key(p, cold_date_dir): p
        for p in cold_files
    }

    tail_files: list[Path] = []
    for hot_file in hot_files:
        rel_key = _relative_file_key(hot_file, hot_date_dir)
        cold_file = cold_key_map.get(rel_key)

        if cold_file is None:
            tail_files.append(hot_file)
            continue

        hot_size = hot_file.stat().st_size
        cold_size = cold_file.stat().st_size

        if hot_size > cold_size:
            tail_files.append(hot_file)

    return sorted(tail_files)


def resolve_hybrid_sources(
    *,
    cold_root: Path,
    hot_root: Path,
    relative_prefix: str,
    dates: Iterable[str],
) -> HybridSourcePlan:
    normalized_dates = list(dict.fromkeys(dates))

    cold_files: list[Path] = []
    hot_tail_files: list[Path] = []

    for date_str in normalized_dates:
        cold_files.extend(
            _resolve_date_files(
                cold_root,
                relative_prefix,
                date_str,
            )
        )
        hot_tail_files.extend(
            _build_hot_tail_files(
                cold_root=cold_root,
                hot_root=hot_root,
                relative_prefix=relative_prefix,
                date_str=date_str,
            )
        )

    return HybridSourcePlan(
        cold_root=cold_root,
        hot_root=hot_root,
        relative_prefix=relative_prefix,
        dates=normalized_dates,
        cold_files=sorted(cold_files),
        hot_tail_files=sorted(hot_tail_files),
    )


def resolve_single_date_hybrid_sources(
    *,
    cold_root: Path,
    hot_root: Path,
    relative_prefix: str,
    date_str: str,
) -> HybridSourcePlan:
    return resolve_hybrid_sources(
        cold_root=cold_root,
        hot_root=hot_root,
        relative_prefix=relative_prefix,
        dates=[date_str],
    )