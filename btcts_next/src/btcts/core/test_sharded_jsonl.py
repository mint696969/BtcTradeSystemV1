# path: ./btcts_next/src/btcts/core/test_sharded_jsonl.py
# desc: Tests for size-bounded JSONL shard append and tolerant read helpers.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.core.sharded_jsonl import append_jsonl_shard, choose_append_path, discover_part_files, iter_jsonl_part_files


def test_append_jsonl_shard_rolls_before_target_limit(tmp_path: Path) -> None:
    base = tmp_path / "date=2026-07-05"
    first = append_jsonl_shard(base, {"i": 1, "payload": "x" * 20}, target_bytes=80, hard_bytes=120)
    second = append_jsonl_shard(base, {"i": 2, "payload": "x" * 20}, target_bytes=80, hard_bytes=120)
    third = append_jsonl_shard(base, {"i": 3, "payload": "x" * 20}, target_bytes=80, hard_bytes=120)

    assert first.name == "part-00001.jsonl"
    assert second.name == "part-00002.jsonl"
    assert third.name == "part-00003.jsonl"
    assert [path.name for path in discover_part_files(base)] == ["part-00001.jsonl", "part-00002.jsonl", "part-00003.jsonl"]
    rows = [json.loads(path.read_text(encoding="utf-8").strip()) for path in discover_part_files(base)]
    assert [row["i"] for row in rows] == [1, 2, 3]


def test_choose_append_path_skips_existing_huge_part(tmp_path: Path) -> None:
    base = tmp_path / "date=2026-07-05"
    base.mkdir(parents=True)
    huge = base / "part-00001.jsonl"
    huge.write_text("x" * 200, encoding="utf-8")

    selected = choose_append_path(base, next_line_bytes=10, target_bytes=80, hard_bytes=120)

    assert selected.name == "part-00002.jsonl"


def test_iter_jsonl_part_files_ignores_missing_parts_and_orders(tmp_path: Path) -> None:
    base = tmp_path / "date=2026-07-05"
    base.mkdir(parents=True)
    (base / "part-00003.jsonl").write_text("{}\n", encoding="utf-8")
    (base / "part-00001.jsonl").write_text("{}\n", encoding="utf-8")
    (base / "notes.txt").write_text("ignore", encoding="utf-8")

    assert [path.name for path in iter_jsonl_part_files(base)] == ["part-00001.jsonl", "part-00003.jsonl"]


def test_read_jsonl_tail_from_parts_combines_latest_and_previous(tmp_path: Path) -> None:
    from btcts.core.sharded_jsonl import read_jsonl_tail_from_parts

    base = tmp_path / "date=2026-07-05"
    base.mkdir(parents=True)
    (base / "part-00001.jsonl").write_text('{"i":1}\n{"i":2}\n', encoding="utf-8")
    (base / "part-00002.jsonl").write_text('{bad-json}\n{"i":3}\n', encoding="utf-8")

    result = read_jsonl_tail_from_parts(base, max_lines=3, max_bytes=4096)

    assert [row["i"] for row in result.rows] == [1, 2, 3]
    assert result.skipped_bad_lines == 1
    assert any("jsonl_bad_lines_skipped" in warning for warning in result.warnings)


def test_read_jsonl_tail_from_parts_reports_missing_part_numbers(tmp_path: Path) -> None:
    from btcts.core.sharded_jsonl import read_jsonl_tail_from_parts

    base = tmp_path / "date=2026-07-05"
    base.mkdir(parents=True)
    (base / "part-00001.jsonl").write_text('{"i":1}\n', encoding="utf-8")
    (base / "part-00003.jsonl").write_text('{"i":3}\n', encoding="utf-8")

    result = read_jsonl_tail_from_parts(base, max_lines=10, max_bytes=4096)

    assert [row["i"] for row in result.rows] == [1, 3]
    assert result.missing_part_numbers == [2]
    assert any("jsonl_missing_part_numbers:2" == warning for warning in result.warnings)


if __name__ == "__main__":
    test_append_jsonl_shard_rolls_before_target_limit(Path("tmp/_sharded_jsonl_test"))
    print("ok")
