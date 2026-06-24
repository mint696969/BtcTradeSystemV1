# path: ./tools/prune_giant_log_candidates_ps_q19a.py
# desc: PS-Q19A guarded giant log pruning tool. Dry-run by default. Deletes only whitelisted log JSONL candidates from D-hot archive/log paths and, when explicitly requested, E-cold log paths. Never deletes active D-hot logs/audit.jsonl.

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ACK = "PS_Q19A_DELETE_GIANT_LOG_CANDIDATES"
HOT_ROOT = Path(r"D:\btc_ts_hot")
COLD_ROOT = Path(r"E:\btc_ts")
DEFAULT_MIN_SIZE_BYTES = 500 * 1024 * 1024


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _resolve(text: str) -> Path:
    return Path(text).expanduser().resolve()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _iter_jsonl(root: Path) -> Iterable[Path]:
    logs = root / "logs"
    if not logs.exists():
        return []
    return logs.rglob("*.jsonl")


def _classify(path: Path, *, root: Path, role: str) -> tuple[bool, str]:
    rel = _rel(path, root)
    rel_l = rel.lower()
    if role == "hot" and rel_l == "logs/audit.jsonl":
        return False, "active_hot_audit_excluded_rotate_first"
    if role == "hot":
        allowed = (
            rel_l.startswith("logs/audit/archive/")
            or rel_l == "logs/collector_vnext/archive_audit.jsonl"
            or rel_l.startswith("logs/collector_vnext/archive/")
        )
        return (allowed, "hot_log_archive_candidate" if allowed else "hot_non_archive_log_excluded")
    if role == "cold":
        allowed = rel_l.startswith("logs/")
        return (allowed, "cold_log_candidate" if allowed else "cold_non_log_excluded")
    return False, "unknown_role"


def build_candidates(*, hot_root: Path, cold_root: Path, include_cold: bool, min_size_bytes: int) -> list[dict]:
    roots: list[tuple[str, Path]] = [("hot", hot_root)]
    if include_cold:
        roots.append(("cold", cold_root))
    rows: list[dict] = []
    for role, root in roots:
        for path in _iter_jsonl(root):
            if not _is_relative_to(path, root):
                continue
            try:
                size = int(path.stat().st_size)
            except Exception:
                continue
            allowed, reason = _classify(path, root=root, role=role)
            if size < int(min_size_bytes) and allowed:
                continue
            if allowed or reason.startswith("active_hot_audit"):
                rows.append(
                    {
                        "role": role,
                        "path": str(path),
                        "relative_path": _rel(path, root),
                        "size_bytes": size,
                        "eligible": bool(allowed and size >= int(min_size_bytes)),
                        "reason": reason if size >= int(min_size_bytes) else "below_min_size_bytes",
                    }
                )
    rows.sort(key=lambda item: int(item["size_bytes"]), reverse=True)
    return rows


def prune_candidates(*, hot_root: Path, cold_root: Path, include_cold: bool, min_size_bytes: int, execute: bool, ack: str) -> dict:
    blockers: list[str] = []
    if hot_root.resolve() != HOT_ROOT.resolve():
        blockers.append(f"hot_root_must_be_D_btc_ts_hot: {hot_root}")
    if include_cold and cold_root.resolve() != COLD_ROOT.resolve():
        blockers.append(f"cold_root_must_be_E_btc_ts: {cold_root}")
    if execute and ack != ACK:
        blockers.append("explicit_ack_required")
    candidates = build_candidates(hot_root=hot_root, cold_root=cold_root, include_cold=include_cold, min_size_bytes=min_size_bytes)
    eligible = [item for item in candidates if item.get("eligible") is True]
    deleted: list[dict] = []
    failed: list[dict] = []
    if execute and not blockers:
        for item in eligible:
            path = Path(str(item["path"]))
            try:
                path.unlink()
                deleted.append(item)
            except Exception as exc:
                failed.append({**item, "error": f"{type(exc).__name__}: {exc}"})
    ok = not blockers and not failed
    return {
        "ok": ok,
        "tool": "prune_giant_log_candidates_ps_q19a",
        "ts": _utc_iso(),
        "dry_run": not execute,
        "execute_requested": execute,
        "hot_root": str(hot_root),
        "cold_root": str(cold_root),
        "include_cold": include_cold,
        "min_size_bytes": int(min_size_bytes),
        "candidate_count": len(candidates),
        "eligible_delete_count": len(eligible),
        "deleted_count": len(deleted),
        "failed_count": len(failed),
        "delete_performed": bool(deleted),
        "compress_performed": False,
        "active_hot_audit_delete_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "blockers": blockers,
        "candidates": candidates,
        "deleted": deleted,
        "failed": failed,
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PS-Q19A giant log prune dry-run/execute")
    p.add_argument("--hot-root", default=str(HOT_ROOT))
    p.add_argument("--cold-root", default=str(COLD_ROOT))
    p.add_argument("--include-cold", action="store_true")
    p.add_argument("--min-size-bytes", type=int, default=DEFAULT_MIN_SIZE_BYTES)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--ack", default="")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = prune_candidates(
        hot_root=_resolve(args.hot_root),
        cold_root=_resolve(args.cold_root),
        include_cold=bool(args.include_cold),
        min_size_bytes=int(args.min_size_bytes),
        execute=bool(args.execute),
        ack=str(args.ack or ""),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
