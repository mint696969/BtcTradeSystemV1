# path: ./btcts_next/src/btcts/core/sharded_jsonl.py
# desc: Size-bounded JSONL shard append and tolerant read helpers for hot data files.

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

PART_RE = re.compile(r"^part-(?P<part_no>\d{5})\.jsonl$")
DEFAULT_TARGET_BYTES = 256 * 1024 * 1024
DEFAULT_HARD_BYTES = 512 * 1024 * 1024


@dataclass(frozen=True)
class JsonlTailReadResult:
    rows: list[dict[str, Any]]
    source_paths: list[str]
    warnings: list[str]
    skipped_bad_lines: int = 0
    missing_part_numbers: list[int] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": list(self.rows),
            "row_count": len(self.rows),
            "source_paths": list(self.source_paths),
            "warnings": list(self.warnings),
            "skipped_bad_lines": int(self.skipped_bad_lines),
            "missing_part_numbers": list(self.missing_part_numbers or []),
            "tolerant_jsonl_reader": True,
        }


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


def missing_part_numbers(base_dir: Path) -> list[int]:
    part_numbers = [_part_no(path) for path in discover_part_files(base_dir)]
    numbers = sorted(n for n in part_numbers if n is not None)
    if not numbers:
        return []
    expected = set(range(numbers[0], numbers[-1] + 1))
    return sorted(expected.difference(numbers))


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


def _tail_text_lines(path: Path, *, max_lines: int, max_bytes: int) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        return [], [f"jsonl_part_missing:{path}"]
    try:
        size = path.stat().st_size
    except Exception as exc:
        return [], [f"jsonl_part_stat_failed:{path}:{type(exc).__name__}"]
    if size <= 0:
        return [], []
    read_size = min(int(size), max(1024, int(max_bytes)))
    try:
        with path.open("rb") as handle:
            handle.seek(max(0, int(size) - read_size))
            data = handle.read(read_size)
    except Exception as exc:
        return [], [f"jsonl_part_read_failed:{path}:{type(exc).__name__}"]
    if read_size < size:
        first_newline = data.find(bytes((10,)))
        if first_newline >= 0:
            data = data[first_newline + 1 :]
        else:
            warnings.append(f"jsonl_tail_started_mid_line_no_newline:{path}")
    try:
        lines = data.decode("utf-8", errors="replace").splitlines()
    except Exception as exc:
        return [], [*warnings, f"jsonl_part_decode_failed:{path}:{type(exc).__name__}"]
    return lines[-max(1, int(max_lines)) :], warnings


def read_jsonl_tail_file(path: Path, *, max_lines: int = 200, max_bytes: int = 8 * 1024 * 1024) -> JsonlTailReadResult:
    lines, warnings = _tail_text_lines(path, max_lines=max_lines, max_bytes=max_bytes)
    rows: list[dict[str, Any]] = []
    skipped = 0
    for line in lines:
        text = str(line or "").strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except Exception:
            skipped += 1
            continue
        if isinstance(value, dict):
            rows.append(value)
        else:
            skipped += 1
    if skipped:
        warnings.append(f"jsonl_bad_lines_skipped:{path}:{skipped}")
    return JsonlTailReadResult(rows=rows[-max(1, int(max_lines)) :], source_paths=[str(path)], warnings=warnings, skipped_bad_lines=skipped, missing_part_numbers=[])


def read_jsonl_tail_from_parts(base_dir: Path, *, max_lines: int = 200, max_bytes: int = 8 * 1024 * 1024) -> JsonlTailReadResult:
    parts = iter_jsonl_part_files(base_dir)
    missing = missing_part_numbers(base_dir)
    warnings: list[str] = []
    if not parts:
        return JsonlTailReadResult(rows=[], source_paths=[], warnings=[f"jsonl_parts_missing:{base_dir}"], skipped_bad_lines=0, missing_part_numbers=[])
    if missing:
        warnings.append("jsonl_missing_part_numbers:" + ",".join(str(n) for n in missing))

    rows_reversed: list[dict[str, Any]] = []
    source_paths: list[str] = []
    skipped = 0
    # Tail from newest parts backward so a newly rolled small latest part can be
    # combined with the previous part without full-scanning old multi-GB files.
    per_part_lines = max(1, int(max_lines))
    per_part_bytes = max(1024, int(max_bytes))
    for part in reversed(parts):
        if len(rows_reversed) >= max(1, int(max_lines)):
            break
        result = read_jsonl_tail_file(part, max_lines=per_part_lines, max_bytes=per_part_bytes)
        source_paths.append(str(part))
        warnings.extend(result.warnings)
        skipped += int(result.skipped_bad_lines)
        rows_reversed.extend(reversed(result.rows))
    rows = list(reversed(rows_reversed))[-max(1, int(max_lines)) :]
    return JsonlTailReadResult(rows=rows, source_paths=list(reversed(source_paths)), warnings=warnings, skipped_bad_lines=skipped, missing_part_numbers=missing)
