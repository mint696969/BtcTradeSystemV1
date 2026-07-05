# path: ./btcts_next/src/btcts/collector_vnext/archive/test_copy_throttle.py
# desc: Tests for archive copy throttling configuration and metadata-preserving copy.

from __future__ import annotations

import os
from pathlib import Path

from btcts.collector_vnext.archive.planner import CopyItem, execute_copy_plan


def test_execute_copy_plan_preserves_file_size_and_mtime_with_throttle(tmp_path: Path) -> None:
    src = tmp_path / "hot" / "data" / "sample.jsonl"
    dst = tmp_path / "cold" / "data" / "sample.jsonl"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes((b"abc123\n" * 4096))
    os.utime(src, (1_700_000_000, 1_700_000_000))

    result = execute_copy_plan(
        [CopyItem(src=src, dst=dst, kind="file", size_bytes=src.stat().st_size)],
        throttle_mib_per_sec=512,
    )

    assert result["copied_files"] == 1
    assert result["copied_bytes"] == src.stat().st_size
    assert result["error_count"] == 0
    assert dst.read_bytes() == src.read_bytes()
    assert int(dst.stat().st_mtime) == int(src.stat().st_mtime)


def test_execute_copy_plan_accepts_unlimited_copy_mode(tmp_path: Path) -> None:
    src = tmp_path / "hot" / "data" / "sample.jsonl"
    dst = tmp_path / "cold" / "data" / "sample.jsonl"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("{}\n", encoding="utf-8")

    result = execute_copy_plan(
        [CopyItem(src=src, dst=dst, kind="file", size_bytes=src.stat().st_size)],
        throttle_mib_per_sec=0,
    )

    assert result["copied_files"] == 1
    assert result["error_count"] == 0
    assert dst.read_text(encoding="utf-8") == "{}\n"
