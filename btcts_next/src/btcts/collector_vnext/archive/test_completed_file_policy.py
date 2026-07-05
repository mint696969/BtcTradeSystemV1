# path: ./btcts_next/src/btcts/collector_vnext/archive/test_completed_file_policy.py
# desc: Tests for archive copy/GC completed-file filtering. No real D/E mutation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.collector_vnext.archive.config import ArchiveConfig  # noqa: E402
from btcts.collector_vnext.archive.file_policy import (  # noqa: E402
    is_archive_copy_candidate,
    is_archive_gc_candidate,
    is_completed_archive_file,
    is_incomplete_archive_file,
)
from btcts.collector_vnext.archive.gc_job import build_gc_plan  # noqa: E402
from btcts.collector_vnext.archive.planner import build_copy_plan  # noqa: E402


def _cfg(root: Path) -> ArchiveConfig:
    return ArchiveConfig(
        hot_root=root / "hot",
        cold_root=root / "cold",
        copy_prefixes=["data/market_data", "state/collector_vnext"],
        gc_prefixes=["data/market_data"],
        stable_age_sec=0,
        copy_min_age_days=1,
        gc_min_age_days=10,
        max_files_per_cycle=100,
        max_bytes_per_cycle=10 * 1024 * 1024,
        max_delete_files_per_cycle=100,
        max_delete_bytes_per_cycle=10 * 1024 * 1024,
    )


def _write(path: Path, text: str = "{}\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_archive_file_policy_marks_incomplete_names() -> None:
    assert is_incomplete_archive_file(Path("part-00001.open.jsonl")) is True
    assert is_incomplete_archive_file(Path("part-00001.jsonl.tmp")) is True
    assert is_incomplete_archive_file(Path("state.json.lock")) is True
    assert is_completed_archive_file(Path("part-00001.jsonl"), data_file=True) is True
    assert is_completed_archive_file(Path("state.json"), data_file=False) is True
    assert is_completed_archive_file(Path("state.json"), data_file=True) is False


def test_copy_plan_excludes_incomplete_data_files_but_keeps_completed_state(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    date_dir = cfg.hot_root / "data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.trade/date=2026-06-01"
    _write(date_dir / "part-00001.jsonl")
    _write(date_dir / "part-00002.open.jsonl")
    _write(date_dir / "part-00003.jsonl.tmp")
    _write(cfg.hot_root / "state/collector_vnext/archive_copy_state.json", "{}")
    _write(cfg.hot_root / "state/collector_vnext/archive_worker.lock.json", "{}")

    plan = build_copy_plan(cfg)
    rels = sorted(item.src.relative_to(cfg.hot_root).as_posix() for item in plan)

    assert "data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.trade/date=2026-06-01/part-00001.jsonl" in rels
    assert "state/collector_vnext/archive_copy_state.json" in rels
    assert all(".open" not in rel for rel in rels)
    assert all(".tmp" not in rel for rel in rels)
    assert all(".lock" not in rel for rel in rels)
    assert is_archive_copy_candidate(date_dir / "part-00001.jsonl", data_file=True) is True


def test_gc_plan_excludes_incomplete_files_and_requires_cold_size_match(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    date_dir = cfg.hot_root / "data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.trade/date=2026-06-01"
    complete = date_dir / "part-00001.jsonl"
    open_file = date_dir / "part-00002.open.jsonl"
    tmp_file = date_dir / "part-00003.jsonl.tmp"
    _write(complete, '{"i":1}\n')
    _write(open_file, '{"i":2}\n')
    _write(tmp_file, '{"i":3}\n')
    cold_complete = cfg.cold_root / complete.relative_to(cfg.hot_root)
    _write(cold_complete, '{"i":1}\n')
    _write(cfg.cold_root / open_file.relative_to(cfg.hot_root), '{"i":2}\n')
    _write(cfg.cold_root / tmp_file.relative_to(cfg.hot_root), '{"i":3}\n')

    plan = build_gc_plan(cfg)
    rels = [item.relative_path for item in plan]

    assert rels == ["data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.trade/date=2026-06-01/part-00001.jsonl"]
    assert is_archive_gc_candidate(complete) is True
    assert is_archive_gc_candidate(open_file) is False
    assert is_archive_gc_candidate(tmp_file) is False


def test_gc_plan_skips_completed_file_when_cold_size_mismatch(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    hot = cfg.hot_root / "data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.trade/date=2026-06-01/part-00001.jsonl"
    cold = cfg.cold_root / hot.relative_to(cfg.hot_root)
    _write(hot, '{"i":1}\n')
    _write(cold, '{"i":1}\nextra\n')

    assert build_gc_plan(cfg) == []


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory(prefix="btcts_archive_policy_") as td:
        root = Path(td)
        test_archive_file_policy_marks_incomplete_names()
        test_copy_plan_excludes_incomplete_data_files_but_keeps_completed_state(root)
        test_gc_plan_excludes_incomplete_files_and_requires_cold_size_match(root)
        test_gc_plan_skips_completed_file_when_cold_size_mismatch(root)
    print("ok")
