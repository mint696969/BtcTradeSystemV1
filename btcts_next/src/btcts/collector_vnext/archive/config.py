# path: ./btcts_next/src/btcts/collector_vnext/archive/config.py
# desc: Archive worker configuration for Collector vNext.

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from btcts.collector_vnext._env_utils import env_int
from btcts.collector_vnext.config import load_config


DEFAULT_COPY_PREFIXES = [
    "data/market_data",
    "data/collector_raw",
    "data/market_state",
    "state/collector_vnext",
    "logs/collector_vnext",
]

DEFAULT_GC_PREFIXES = [
    "data/market_data",
    "data/collector_raw",
    "data/market_state",
]


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
    relative_prefixes: list[str] = field(default_factory=list)
    copy_prefixes: list[str] = field(default_factory=list)
    gc_prefixes: list[str] = field(default_factory=list)
    scan_interval_sec: int = 30
    stable_age_sec: int = 3600
    copy_min_age_days: int = 1
    gc_min_age_days: int = 10
    max_files_per_cycle: int = 64
    max_bytes_per_cycle: int = 256 * 1024 * 1024
    gc_enabled: bool = False
    gc_dry_run: bool = True
    max_delete_files_per_cycle: int = 32
    max_delete_bytes_per_cycle: int = 25 * 1024 * 1024 * 1024

    def resolved_copy_prefixes(self) -> list[str]:
        if self.copy_prefixes:
            return list(self.copy_prefixes)
        if self.relative_prefixes:
            return list(self.relative_prefixes)
        return list(DEFAULT_COPY_PREFIXES)

    def resolved_gc_prefixes(self) -> list[str]:
        if self.gc_prefixes:
            return list(self.gc_prefixes)
        if self.relative_prefixes:
            legacy = [x for x in self.relative_prefixes if str(x).startswith("data/")]
            if legacy:
                return legacy
        return list(DEFAULT_GC_PREFIXES)


def load_archive_config() -> ArchiveConfig:
    collector_cfg = load_config()
    hot_base = collector_cfg.data_root.parent
    cold_root = Path(str(os.getenv("BTCTS_ARCHIVE_COLD_ROOT", r"E:\btc_ts")).strip() or r"E:\btc_ts")

    return ArchiveConfig(
        hot_root=hot_base,
        cold_root=cold_root,
        relative_prefixes=_env_list("BTCTS_ARCHIVE_RELATIVE_PREFIXES", []),
        copy_prefixes=_env_list("BTCTS_ARCHIVE_COPY_PREFIXES", []),
        gc_prefixes=_env_list("BTCTS_ARCHIVE_GC_PREFIXES", []),
        scan_interval_sec=max(10, env_int("BTCTS_ARCHIVE_SCAN_INTERVAL_SEC", 30)),
        stable_age_sec=max(1800, env_int("BTCTS_ARCHIVE_STABLE_AGE_SEC", 3600)),
        copy_min_age_days=max(1, env_int("BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS", 1)),
        gc_min_age_days=max(7, env_int("BTCTS_ARCHIVE_GC_MIN_AGE_DAYS", 10)),
        max_files_per_cycle=max(1, env_int("BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE", 64)),
        max_bytes_per_cycle=max(1024 * 1024, env_int("BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE", 256 * 1024 * 1024)),
        gc_enabled=_env_bool("BTCTS_ARCHIVE_GC_ENABLED", False),
        gc_dry_run=_env_bool("BTCTS_ARCHIVE_GC_DRY_RUN", True),
        max_delete_files_per_cycle=max(1, env_int("BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE", 32)),
        max_delete_bytes_per_cycle=max(1024 * 1024, env_int("BTCTS_ARCHIVE_MAX_DELETE_BYTES_PER_CYCLE", 25 * 1024 * 1024 * 1024)),
    )