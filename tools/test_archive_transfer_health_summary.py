# path: ./tools/test_archive_transfer_health_summary.py
# desc: Unit tests for bounded D/E archive transfer health summary producer.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import tempfile
from pathlib import Path

from btcts.collector_vnext.archive.config import ArchiveConfig
from btcts.collector_vnext.archive.gc_job import DeleteItem
from btcts.collector_vnext.archive.health_summary import build_archive_transfer_health_summary
from btcts.collector_vnext.archive.planner import CopyItem


def _cfg(root: Path) -> ArchiveConfig:
    return ArchiveConfig(
        hot_root=root / "D_hot",
        cold_root=root / "E_cold",
        stable_age_sec=1800,
        gc_min_age_days=10,
    )


def test_ok_when_copy_and_delete_candidates_hash_match() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cfg = _cfg(root)
        hot = cfg.hot_root / "data" / "market_data" / "date=2026-05-30" / "a.jsonl"
        cold = cfg.cold_root / "data" / "market_data" / "date=2026-05-30" / "a.jsonl"
        hot.parent.mkdir(parents=True, exist_ok=True)
        cold.parent.mkdir(parents=True, exist_ok=True)
        hot.write_text("same\n", encoding="utf-8")
        cold.write_text("same\n", encoding="utf-8")

        copy_item = CopyItem(src=hot, dst=cold, kind="file", size_bytes=hot.stat().st_size)
        delete_item = DeleteItem(
            hot_path=hot,
            cold_path=cold,
            size_bytes=hot.stat().st_size,
            relative_path=hot.relative_to(cfg.hot_root).as_posix(),
            cold_size_bytes=cold.stat().st_size,
        )
        payload = build_archive_transfer_health_summary(
            cfg,
            copy_items=[copy_item],
            copy_result={"copied_files": 1, "copied_bytes": hot.stat().st_size, "error_count": 0},
            gc_items=[delete_item],
            gc_result={"planned_deleted_files": 1, "deleted_files": 0, "deleted_bytes": 0, "error_count": 0, "dry_run": True},
        )
        assert payload["status"] == "ok"
        assert payload["integrity"]["hash_mismatch_count"] == 0
        assert payload["last_delete"]["delete_basis"] == "verified_on_e_drive_by_size_and_sha256"
        assert payload["bad_files"] == []


def test_crit_when_same_size_hash_mismatch_before_delete() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cfg = _cfg(root)
        hot = cfg.hot_root / "data" / "collector_raw" / "date=2026-05-30" / "b.jsonl"
        cold = cfg.cold_root / "data" / "collector_raw" / "date=2026-05-30" / "b.jsonl"
        hot.parent.mkdir(parents=True, exist_ok=True)
        cold.parent.mkdir(parents=True, exist_ok=True)
        hot.write_text("aaaa\n", encoding="utf-8")
        cold.write_text("bbbb\n", encoding="utf-8")

        delete_item = DeleteItem(
            hot_path=hot,
            cold_path=cold,
            size_bytes=hot.stat().st_size,
            relative_path=hot.relative_to(cfg.hot_root).as_posix(),
            cold_size_bytes=cold.stat().st_size,
        )
        payload = build_archive_transfer_health_summary(
            cfg,
            gc_items=[delete_item],
            gc_result={"planned_deleted_files": 1, "deleted_files": 0, "deleted_bytes": 0, "error_count": 0, "dry_run": True},
        )
        assert payload["status"] == "crit"
        assert payload["integrity"]["hash_mismatch_count"] == 1
        assert payload["last_delete"]["unverified_delete_candidate_count"] == 1
        assert payload["bad_files"][0]["reason"] == "delete_candidate_hash_mismatch"
        assert "d_hash" in payload["bad_files"][0]
        assert "e_hash" in payload["bad_files"][0]


def test_crit_when_cold_file_missing_for_copy_pair() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cfg = _cfg(root)
        hot = cfg.hot_root / "data" / "market_data" / "date=2026-05-30" / "c.jsonl"
        cold = cfg.cold_root / "data" / "market_data" / "date=2026-05-30" / "c.jsonl"
        hot.parent.mkdir(parents=True, exist_ok=True)
        hot.write_text("payload\n", encoding="utf-8")
        copy_item = CopyItem(src=hot, dst=cold, kind="file", size_bytes=hot.stat().st_size)
        payload = build_archive_transfer_health_summary(
            cfg,
            copy_items=[copy_item],
            copy_result={"copied_files": 1, "copied_bytes": hot.stat().st_size, "error_count": 0},
        )
        assert payload["status"] == "crit"
        assert payload["last_copy"]["missing_count"] == 1
        assert payload["bad_files"][0]["reason"] == "copy_missing_on_e"


if __name__ == "__main__":
    test_ok_when_copy_and_delete_candidates_hash_match()
    test_crit_when_same_size_hash_mismatch_before_delete()
    test_crit_when_cold_file_missing_for_copy_pair()
    print("ok")