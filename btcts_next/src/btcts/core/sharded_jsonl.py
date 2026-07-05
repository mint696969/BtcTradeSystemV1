# path: ./btcts_next/src/btcts/core/sharded_jsonl.py
# desc: Size-bounded JSONL shard append helpers for hot data files.

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

PART_RE = re.compile(r"^part-(?P<part_no>\d{5})\.jsonl$")
DEFAULT_TARGET_BYTES = 256 * 1024 * 1024
DEFAULT_HARD_BYTES = 512 * 1024 * 1024


def _env_int(name: str, default: int) -> int:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return int(default)
    try:
        value = int(raw)
    except ValueError:
        return int(default)
    return value if value > 0 else int(default)


def target_bytes_from_env() -> int:
    return _env_int("BTCTS_JSONL_PART_TARGET_BYTES", DEFAULT_TARGET_BYTES)


def hard_bytes_from_env() -> int:
    return _env_int("BTCTS_JSONL_PART_HARD_BYTES", DEFAULT_HARD_BYTES)


def part_file_path(base_dir: Path, part_no: int) -> Path:
    return base_dir / f"part-{int(part_no):05d}.jsonl"


def _part_no(path: Path) -> int | None:
    match = PART_RE.match(path.name)
    if not match:
        return None
    return int(match.group("part_no"))


def discover_part_files(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    parts = [path for path in base_dir.iterdir() if path.is_file() and _part_no(path) is not None]
    return sorted(parts, key=lambda path: (_part_no(path) or 0, path.name))


def latest_part_path(base_dir: Path) -> Path | None:
    parts = discover_part_files(base_dir)
    return parts[-1] if parts else None


def choose_append_path(
    base_dir: Path,
    *,
    next_line_bytes: int,
    target_bytes: int | None = None,
    hard_bytes: int | None = None,
) -> Path:
    """Choose a JSONL part path without writing.

    The currently writable part remains a normal `.jsonl` file for backward
    compatibility with existing readers. Rollover happens before append when
    the next line would exceed the target or hard limit.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    target = int(target_bytes or target_bytes_from_env())
    hard = int(hard_bytes or hard_bytes_from_env())
    if hard < target:
        hard = target

    current = latest_part_path(base_dir)
    if current is None:
        return part_file_path(base_dir, 1)

    current_no = _part_no(current) or 1
    try:
        current_size = current.stat().st_size
    except OSError:
        return part_file_path(base_dir, current_no + 1)

    would_size = current_size + int(next_line_bytes)
    if current_size >= hard or would_size > hard or would_size > target:
        return part_file_path(base_dir, current_no + 1)
    return current


def append_jsonl_shard(
    base_dir: Path,
    record: Mapping[str, Any],
    *,
    target_bytes: int | None = None,
    hard_bytes: int | None = None,
) -> Path:
    line = json.dumps(dict(record), ensure_ascii=False, separators=(",", ":")) + "\n"
    encoded = line.encode("utf-8")
    out = choose_append_path(
        base_dir,
        next_line_bytes=len(encoded),
        target_bytes=target_bytes,
        hard_bytes=hard_bytes,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)
    return out


def iter_jsonl_part_files(base_dir: Path, *, include_open_suffix: bool = False) -> list[Path]:
    """Return ordered readable part files for future readers.

    Missing part numbers are not an error. This intentionally only returns
    existing files and lets callers decide how to report gaps or bad lines.
    """
    parts = discover_part_files(base_dir)
    if include_open_suffix and base_dir.exists():
        parts.extend(sorted(base_dir.glob("part-*.open.jsonl")))
    return sorted(parts, key=lambda path: (_part_no(path) or 10**9, path.name))
