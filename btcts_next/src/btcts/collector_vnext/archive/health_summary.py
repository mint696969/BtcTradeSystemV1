# path: ./btcts_next/src/btcts/collector_vnext/archive/health_summary.py
# desc: Bounded D/E archive transfer health summary producer for Health dashboard payload input.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import ArchiveConfig

SUMMARY_SCHEMA_VERSION = "archive_transfer_health_summary.v1"
DEFAULT_BAD_FILES_PREVIEW_LIMIT = 20
DELETE_CANDIDATE_HASH_MISMATCH_REASON_LITERAL = "delete_candidate_hash_mismatch"


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _same_resolved_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve(strict=False) == right.resolve(strict=False)
    except Exception:
        return str(left.absolute()).casefold() == str(right.absolute()).casefold()


def archive_transfer_health_summary_path(cfg: ArchiveConfig) -> Path:
    return cfg.hot_root / "state" / "collector_vnext" / "archive_transfer_health_summary.json"


def _sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _safe_stat(path: Path) -> dict[str, Any]:
    try:
        st = path.stat()
        return {"exists": True, "size_bytes": int(st.st_size), "mtime_ns": int(st.st_mtime_ns)}
    except Exception as exc:
        return {"exists": False, "error": f"{type(exc).__name__}: {exc}"}


def _append_bad_file(
    bad_files: list[dict[str, Any]],
    *,
    preview_limit: int,
    relative_path: str,
    d_path: Path,
    e_path: Path,
    reason: str,
    d_size: int | None = None,
    e_size: int | None = None,
    d_hash: str | None = None,
    e_hash: str | None = None,
    detail: str | None = None,
) -> None:
    if len(bad_files) >= preview_limit:
        return
    row: dict[str, Any] = {
        "relative_path": relative_path,
        "d_path": str(d_path),
        "e_path": str(e_path),
        "reason": reason,
    }
    if d_size is not None:
        row["d_size"] = int(d_size)
    if e_size is not None:
        row["e_size"] = int(e_size)
    if d_hash is not None:
        row["d_hash"] = d_hash
    if e_hash is not None:
        row["e_hash"] = e_hash
    if detail:
        row["detail"] = detail
    bad_files.append(row)


def _relative_to_hot(cfg: ArchiveConfig, path: Path) -> str:
    try:
        return path.relative_to(cfg.hot_root).as_posix()
    except Exception:
        return path.as_posix()


def _verify_pair(
    cfg: ArchiveConfig,
    *,
    hot_path: Path,
    cold_path: Path,
    bad_files: list[dict[str, Any]],
    preview_limit: int,
    reason_prefix: str,
) -> dict[str, int]:
    counts = {
        "checked_files": 1,
        "verified_files": 0,
        "missing_count": 0,
        "size_mismatch_count": 0,
        "hash_mismatch_count": 0,
        "stat_error_count": 0,
    }
    rel = _relative_to_hot(cfg, hot_path)

    if _same_resolved_path(hot_path, cold_path):
        counts["stat_error_count"] += 1
        _append_bad_file(
            bad_files,
            preview_limit=preview_limit,
            relative_path=rel,
            d_path=hot_path,
            e_path=cold_path,
            reason=f"{reason_prefix}_same_resolved_path",
        )
        return counts

    hot_stat = _safe_stat(hot_path)
    cold_stat = _safe_stat(cold_path)
    if not hot_stat.get("exists"):
        counts["missing_count"] += 1
        _append_bad_file(
            bad_files,
            preview_limit=preview_limit,
            relative_path=rel,
            d_path=hot_path,
            e_path=cold_path,
            reason=f"{reason_prefix}_missing_on_d",
            detail=str(hot_stat.get("error") or ""),
        )
        return counts
    if not cold_stat.get("exists"):
        counts["missing_count"] += 1
        _append_bad_file(
            bad_files,
            preview_limit=preview_limit,
            relative_path=rel,
            d_path=hot_path,
            e_path=cold_path,
            reason=f"{reason_prefix}_missing_on_e",
            d_size=_as_int(hot_stat.get("size_bytes")),
            detail=str(cold_stat.get("error") or ""),
        )
        return counts

    hot_size = _as_int(hot_stat.get("size_bytes"))
    cold_size = _as_int(cold_stat.get("size_bytes"))
    if hot_size != cold_size:
        counts["size_mismatch_count"] += 1
        _append_bad_file(
            bad_files,
            preview_limit=preview_limit,
            relative_path=rel,
            d_path=hot_path,
            e_path=cold_path,
            reason=f"{reason_prefix}_size_mismatch",
            d_size=hot_size,
            e_size=cold_size,
        )
        return counts

    try:
        hot_hash = _sha256_file(hot_path)
        cold_hash = _sha256_file(cold_path)
    except Exception as exc:
        counts["stat_error_count"] += 1
        _append_bad_file(
            bad_files,
            preview_limit=preview_limit,
            relative_path=rel,
            d_path=hot_path,
            e_path=cold_path,
            reason=f"{reason_prefix}_hash_failed",
            d_size=hot_size,
            e_size=cold_size,
            detail=f"{type(exc).__name__}: {exc}",
        )
        return counts

    if hot_hash != cold_hash:
        counts["hash_mismatch_count"] += 1
        _append_bad_file(
            bad_files,
            preview_limit=preview_limit,
            relative_path=rel,
            d_path=hot_path,
            e_path=cold_path,
            reason=f"{reason_prefix}_hash_mismatch",
            d_size=hot_size,
            e_size=cold_size,
            d_hash=hot_hash,
            e_hash=cold_hash,
        )
        return counts

    counts["verified_files"] += 1
    return counts


def _merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for k, v in source.items():
        target[k] = int(target.get(k, 0)) + int(v)


def _verify_items(
    cfg: ArchiveConfig,
    items: Iterable[Any],
    *,
    kind: str,
    bad_files: list[dict[str, Any]],
    preview_limit: int,
) -> dict[str, int]:
    counts = {
        "checked_files": 0,
        "verified_files": 0,
        "missing_count": 0,
        "size_mismatch_count": 0,
        "hash_mismatch_count": 0,
        "stat_error_count": 0,
    }
    for item in items:
        hot_path = Path(getattr(item, "src", getattr(item, "hot_path", "")))
        cold_path = Path(getattr(item, "dst", getattr(item, "cold_path", "")))
        if not str(hot_path) or not str(cold_path):
            continue
        _merge_counts(
            counts,
            _verify_pair(
                cfg,
                hot_path=hot_path,
                cold_path=cold_path,
                bad_files=bad_files,
                preview_limit=preview_limit,
                reason_prefix=kind,
            ),
        )
    return counts


def build_archive_transfer_health_summary(
    cfg: ArchiveConfig,
    *,
    copy_items: Iterable[Any] = (),
    copy_result: dict[str, Any] | None = None,
    gc_items: Iterable[Any] = (),
    gc_result: dict[str, Any] | None = None,
    bad_files_preview_limit: int = DEFAULT_BAD_FILES_PREVIEW_LIMIT,
) -> dict[str, Any]:
    """Build a compact, render-free D/E archive transfer health summary.

    The verifier hashes bounded copy and delete-candidate item pairs while the
    hot-side file still exists. It is intended to be called by the archive
    worker immediately after copy and before/around GC execution, not by UI.
    """
    copy_result = dict(copy_result or {})
    gc_result = dict(gc_result or {})
    bad_files: list[dict[str, Any]] = []

    copy_counts = _verify_items(
        cfg,
        copy_items,
        kind="copy",
        bad_files=bad_files,
        preview_limit=bad_files_preview_limit,
    )
    delete_basis_counts = _verify_items(
        cfg,
        gc_items,
        kind="delete_candidate",
        bad_files=bad_files,
        preview_limit=bad_files_preview_limit,
    )

    copy_error_count = _as_int(copy_result.get("error_count"))
    gc_error_count = _as_int(gc_result.get("error_count"))
    mismatch_count = (
        copy_counts["size_mismatch_count"]
        + copy_counts["hash_mismatch_count"]
        + delete_basis_counts["size_mismatch_count"]
        + delete_basis_counts["hash_mismatch_count"]
    )
    missing_count = copy_counts["missing_count"] + delete_basis_counts["missing_count"]
    unverified_delete_candidate_count = max(
        0,
        delete_basis_counts["checked_files"] - delete_basis_counts["verified_files"],
    )

    crit_reasons: list[str] = []
    warn_reasons: list[str] = []
    if copy_error_count:
        crit_reasons.append("copy_job_error")
    if gc_error_count:
        crit_reasons.append("gc_job_error")
    if mismatch_count:
        crit_reasons.append("d_e_size_or_hash_mismatch")
    if missing_count:
        crit_reasons.append("d_or_e_missing_for_transfer_pair")
    if unverified_delete_candidate_count:
        crit_reasons.append("delete_candidate_not_hash_verified_on_e")

    copied_files = _as_int(copy_result.get("copied_files"))
    planned_deleted_files = _as_int(gc_result.get("planned_deleted_files"))
    deleted_files = _as_int(gc_result.get("deleted_files"))
    if not crit_reasons and copied_files == 0 and planned_deleted_files == 0 and deleted_files == 0:
        warn_reasons.append("no_copy_or_delete_activity_in_this_cycle")

    if crit_reasons:
        status = "crit"
        severity = "crit"
        reasons = crit_reasons
    elif warn_reasons:
        status = "warn"
        severity = "warn"
        reasons = warn_reasons
    else:
        status = "ok"
        severity = "info"
        reasons = ["copy_and_delete_candidates_hash_verified"]

    path = archive_transfer_health_summary_path(cfg)
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "status": status,
        "severity": severity,
        "generated_at": _now_iso_utc(),
        "source": {
            "producer": "btcts.collector_vnext.archive.health_summary",
            "hot_root": str(cfg.hot_root),
            "cold_root": str(cfg.cold_root),
            "event_driven": True,
            "ui_must_not_scan_d_or_e": True,
        },
        "reasons": reasons,
        "last_copy": {
            "planned_files": copy_counts["checked_files"],
            "copied_files": copied_files,
            "copied_bytes": _as_int(copy_result.get("copied_bytes")),
            "verified_files": copy_counts["verified_files"],
            "mismatch_count": copy_counts["size_mismatch_count"] + copy_counts["hash_mismatch_count"],
            "missing_count": copy_counts["missing_count"],
            "error_count": copy_error_count,
        },
        "last_delete": {
            "planned_deleted_files": planned_deleted_files,
            "deleted_files": deleted_files,
            "deleted_bytes": _as_int(gc_result.get("deleted_bytes")),
            "delete_basis": "verified_on_e_drive_by_size_and_sha256",
            "verified_delete_candidates": delete_basis_counts["verified_files"],
            "unverified_delete_candidate_count": unverified_delete_candidate_count,
            "error_count": gc_error_count,
            "dry_run": bool(gc_result.get("dry_run", False)),
        },
        "integrity": {
            "hash_algorithm": "sha256",
            "checked_files": copy_counts["checked_files"] + delete_basis_counts["checked_files"],
            "verified_files": copy_counts["verified_files"] + delete_basis_counts["verified_files"],
            "mismatch_count": mismatch_count,
            "missing_count": missing_count,
            "hash_mismatch_count": copy_counts["hash_mismatch_count"] + delete_basis_counts["hash_mismatch_count"],
            "size_mismatch_count": copy_counts["size_mismatch_count"] + delete_basis_counts["size_mismatch_count"],
        },
        "policy": {
            "status_colors": {"ok": "green", "warn": "amber", "crit": "red", "unknown": "gray"},
            "normal_ok_shows_all_files": False,
            "warn_crit_bad_files_include_paths": True,
            "target_hot_retention_days": 10,
            "minimum_hot_retention_days": 7,
        },
        "bad_files_preview_limit": int(bad_files_preview_limit),
        "bad_files_truncated": len(bad_files) >= int(bad_files_preview_limit),
        "bad_files": bad_files,
        "full_report_path": str(path),
    }


def write_archive_transfer_health_summary(cfg: ArchiveConfig, payload: dict[str, Any]) -> Path:
    path = archive_transfer_health_summary_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path