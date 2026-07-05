# path: ./btcts_next/src/btcts/collector_vnext/archive/file_policy.py
# desc: Completed-file filters for hot/cold archive copy and GC planners.

from __future__ import annotations

from pathlib import Path

INCOMPLETE_SUFFIX_MARKERS: tuple[str, ...] = (
    ".open",
    ".tmp",
    ".partial",
    ".inprogress",
    ".writing",
    ".lock",
)
COMPLETED_SUFFIXES: tuple[str, ...] = (
    ".jsonl",
    ".json",
    ".parquet",
)
DATA_COMPLETED_SUFFIXES: tuple[str, ...] = (
    ".jsonl",
    ".parquet",
)


def is_incomplete_archive_file(path: Path | str) -> bool:
    name = Path(path).name.lower()
    return any(marker in name for marker in INCOMPLETE_SUFFIX_MARKERS)


def is_completed_archive_file(path: Path | str, *, data_file: bool = False) -> bool:
    if is_incomplete_archive_file(path):
        return False
    name = Path(path).name.lower()
    suffixes = DATA_COMPLETED_SUFFIXES if data_file else COMPLETED_SUFFIXES
    return any(name.endswith(suffix) for suffix in suffixes)


def is_archive_copy_candidate(path: Path, *, data_file: bool) -> bool:
    if not path.is_file():
        return False
    return is_completed_archive_file(path, data_file=data_file)


def is_archive_gc_candidate(path: Path) -> bool:
    if not path.is_file():
        return False
    # GC only runs over data prefixes, so data suffix rules are intentionally strict.
    return is_completed_archive_file(path, data_file=True)
