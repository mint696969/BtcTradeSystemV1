# path: ./btcts_next/src/btcts/collector_vnext/archive/config.py
# desc: Archive worker configuration for Collector vNext.

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from btcts.collector_vnext.config import load_config


def _env_int(name: str, default: int) -> int:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return list(default)
    return [x.strip() for x in raw.split(",") if x.strip()]


def _env_bool(name: str, default: bool) -> bool:
    raw = str(os.getenv(name, "") or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ArchiveConfig:
    hot_root: Path
    cold_root: Path
    relative_prefixes: list[str] = field(
        default_factory=lambda: [
            "data/market_data",
            "data/collector_raw",
            "state/collector_vnext",
            "logs/collector_vnext",
        ]
    )
    scan_interval_sec: int = 30
    stable_age_sec: int = 600
    copy_min_age_days: int = 1
    gc_min_age_days: int = 2
    max_files_per_cycle: int = 64
    max_bytes_per_cycle: int = 256 * 1024 * 1024
    gc_enabled: bool = False
    gc_dry_run: bool = True
    max_delete_files_per_cycle: int = 32


def load_archive_config() -> ArchiveConfig:
    collector_cfg = load_config()
    hot_base = collector_cfg.data_root.parent
    cold_root = Path(str(os.getenv("BTCTS_ARCHIVE_COLD_ROOT", r"E:\btc_ts")).strip() or r"E:\btc_ts")

    return ArchiveConfig(
        hot_root=hot_base,
        cold_root=cold_root,
        relative_prefixes=_env_list(
            "BTCTS_ARCHIVE_RELATIVE_PREFIXES",
            [
                "data/market_data",
                "data/collector_raw",
                "state/collector_vnext",
                "logs/collector_vnext",
            ],
        ),
        scan_interval_sec=max(10, _env_int("BTCTS_ARCHIVE_SCAN_INTERVAL_SEC", 30)),
        stable_age_sec=max(60, _env_int("BTCTS_ARCHIVE_STABLE_AGE_SEC", 600)),
        copy_min_age_days=max(1, _env_int("BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS", 1)),
        gc_min_age_days=max(2, _env_int("BTCTS_ARCHIVE_GC_MIN_AGE_DAYS", 2)),
        max_files_per_cycle=max(1, _env_int("BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE", 64)),
        max_bytes_per_cycle=max(1024 * 1024, _env_int("BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE", 256 * 1024 * 1024)),
        gc_enabled=_env_bool("BTCTS_ARCHIVE_GC_ENABLED", False),
        gc_dry_run=_env_bool("BTCTS_ARCHIVE_GC_DRY_RUN", True),
        max_delete_files_per_cycle=max(1, _env_int("BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE", 32)),
    )