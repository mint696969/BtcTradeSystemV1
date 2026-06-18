# path: ./tools/test_archive_dry_run_gc_health_summary_cold_load_guard.py
# desc: Guard archive transfer health summary does not hash-read cold delete candidates during GC dry-run cycles.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import btcts.collector_vnext.archive.health_summary as health_summary
from btcts.collector_vnext.archive.config import ArchiveConfig
from btcts.collector_vnext.archive.health_summary import build_archive_transfer_health_summary


@dataclass(frozen=True)
class DummyDeleteItem:
    hot_path: Path
    cold_path: Path
    size_bytes: int
    relative_path: str
    cold_size_bytes: int


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    failures: list[str] = []
    called_paths: list[str] = []

    tmp_root = repo_root / "tmp" / "archive_dry_run_gc_health_summary_cold_load_guard"
    hot_root = tmp_root / "hot"
    cold_root = tmp_root / "cold"
    rel = Path("data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.orderbook.diff/date=2026-05-26/part-00001.jsonl")
    hot_path = hot_root / rel
    cold_path = cold_root / rel
    hot_path.parent.mkdir(parents=True, exist_ok=True)
    cold_path.parent.mkdir(parents=True, exist_ok=True)
    hot_path.write_text("hot payload", encoding="utf-8")
    cold_path.write_text("cold payload deliberately different but same size"[: len("hot payload")], encoding="utf-8")

    cfg = ArchiveConfig(hot_root=hot_root, cold_root=cold_root)
    item = DummyDeleteItem(
        hot_path=hot_path,
        cold_path=cold_path,
        size_bytes=hot_path.stat().st_size,
        relative_path=rel.as_posix(),
        cold_size_bytes=cold_path.stat().st_size,
    )

    original_sha = health_summary._sha256_file

    def _blocked_sha(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
        called_paths.append(str(path))
        raise AssertionError(f"unexpected dry-run hash read: {path}")

    try:
        health_summary._sha256_file = _blocked_sha
        payload = build_archive_transfer_health_summary(
            cfg,
            copy_items=(),
            copy_result={"error_count": 0, "copied_files": 0, "copied_bytes": 0},
            gc_items=(item,),
            gc_result={
                "dry_run": True,
                "error_count": 0,
                "planned_deleted_files": 1,
                "deleted_files": 0,
                "deleted_bytes": 0,
                "verified_before_files": 1,
                "planned_deleted_bytes": item.size_bytes,
            },
        )
    finally:
        health_summary._sha256_file = original_sha

    checks = {
        "no_sha_called_for_dry_run_delete_candidate": called_paths == [],
        "status_not_crit": payload.get("status") in {"ok", "warn"},
        "dry_run_basis_is_size_stat_only": payload["last_delete"]["delete_basis"] == "dry_run_size_stat_verified_before_delete_no_hash",
        "dry_run_hash_skip_flag_visible": payload["integrity"]["delete_candidate_hash_verification_skipped_due_dry_run"] is True,
        "dry_run_policy_visible": payload["integrity"]["dry_run_cold_read_policy"] == "stat_size_only_no_content_hash",
        "verified_before_count_reused": payload["last_delete"]["verified_delete_candidates"] == 1,
        "unverified_count_zero": payload["last_delete"]["unverified_delete_candidate_count"] == 0,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    # Real-delete summaries must still be able to hash candidate pairs.
    real_called_paths: list[str] = []

    def _counting_sha(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
        real_called_paths.append(str(path))
        return original_sha(path, chunk_size=chunk_size)

    try:
        health_summary._sha256_file = _counting_sha
        real_payload = build_archive_transfer_health_summary(
            cfg,
            copy_items=(),
            copy_result={"error_count": 0, "copied_files": 0, "copied_bytes": 0},
            gc_items=(item,),
            gc_result={
                "dry_run": False,
                "error_count": 0,
                "planned_deleted_files": 1,
                "deleted_files": 0,
                "deleted_bytes": 0,
                "verified_before_files": 1,
                "planned_deleted_bytes": item.size_bytes,
            },
        )
    finally:
        health_summary._sha256_file = original_sha

    real_checks = {
        "real_delete_still_hashes_pair": len(real_called_paths) == 2,
        "real_delete_basis_hash": real_payload["last_delete"]["delete_basis"] == "verified_on_e_drive_by_size_and_sha256",
        "real_delete_hash_skip_flag_false": real_payload["integrity"]["delete_candidate_hash_verification_skipped_due_dry_run"] is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in real_checks.items() if not ok)

    payload_out = {
        "ok": not failures,
        "phase": "archive_dry_run_gc_health_summary_cold_load_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | real_checks,
        "sample": {
            "dry_run_summary": payload,
            "dry_run_hash_called_paths": called_paths,
            "real_delete_hash_called_paths": real_called_paths,
        },
        "failures": failures,
    }
    print(json.dumps(payload_out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_archive_dry_run_gc_health_summary_does_not_hash_read_cold_candidates() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
