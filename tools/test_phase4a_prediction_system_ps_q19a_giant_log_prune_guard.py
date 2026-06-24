# path: ./tools/test_phase4a_prediction_system_ps_q19a_giant_log_prune_guard.py
# desc: Guard for PS-Q19A giant log pruning tool. Uses only temporary test roots.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import prune_giant_log_candidates_ps_q19a as prune  # noqa: E402


def test_prune_candidates_excludes_active_hot_audit_and_deletes_only_archives(tmp_path: Path, monkeypatch) -> None:
    hot = tmp_path / "D" / "btc_ts_hot"
    cold = tmp_path / "E" / "btc_ts"
    monkeypatch.setattr(prune, "HOT_ROOT", hot.resolve())
    monkeypatch.setattr(prune, "COLD_ROOT", cold.resolve())

    active = hot / "logs" / "audit.jsonl"
    hot_arch = hot / "logs" / "audit" / "archive" / "date=2026-06-24" / "audit_old.jsonl"
    hot_collector_archive = hot / "logs" / "collector_vnext" / "archive_audit.jsonl"
    cold_audit = cold / "logs" / "audit.jsonl"
    for path in (active, hot_arch, hot_collector_archive, cold_audit):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x" * 12, encoding="utf-8")

    dry = prune.prune_candidates(
        hot_root=hot.resolve(),
        cold_root=cold.resolve(),
        include_cold=True,
        min_size_bytes=1,
        execute=False,
        ack="",
    )
    assert dry["ok"] is True
    assert dry["dry_run"] is True
    assert dry["delete_performed"] is False
    assert any(item["reason"] == "active_hot_audit_excluded_rotate_first" for item in dry["candidates"])
    assert dry["eligible_delete_count"] == 3

    run = prune.prune_candidates(
        hot_root=hot.resolve(),
        cold_root=cold.resolve(),
        include_cold=True,
        min_size_bytes=1,
        execute=True,
        ack=prune.ACK,
    )
    assert run["ok"] is True, json.dumps(run, ensure_ascii=False)
    assert active.exists()
    assert not hot_arch.exists()
    assert not hot_collector_archive.exists()
    assert not cold_audit.exists()
    assert run["deleted_count"] == 3
    assert run["active_hot_audit_delete_allowed"] is False
    assert run["would_send_to_broker"] is False


def test_prune_execute_requires_ack(tmp_path: Path, monkeypatch) -> None:
    hot = tmp_path / "D" / "btc_ts_hot"
    cold = tmp_path / "E" / "btc_ts"
    monkeypatch.setattr(prune, "HOT_ROOT", hot.resolve())
    monkeypatch.setattr(prune, "COLD_ROOT", cold.resolve())
    target = hot / "logs" / "audit" / "archive" / "date=2026-06-24" / "audit_old.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x" * 12, encoding="utf-8")

    result = prune.prune_candidates(
        hot_root=hot.resolve(),
        cold_root=cold.resolve(),
        include_cold=False,
        min_size_bytes=1,
        execute=True,
        ack="",
    )
    assert result["ok"] is False
    assert "explicit_ack_required" in result["blockers"]
    assert target.exists()
