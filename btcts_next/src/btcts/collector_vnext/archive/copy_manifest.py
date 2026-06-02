# path: ./btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py
# desc: Data model and validation helpers for Hot/Cold copy correctness manifests. No copy/delete executor.

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any

COPY_MANIFEST_SCHEMA_VERSION = "hot_cold_copy_manifest_v1"
COPY_INTENT = "hot_to_cold_archive_copy"
ALLOWED_REL_PREFIXES: tuple[str, ...] = ("data/market_data", "data/collector_raw")
FORBIDDEN_REL_PREFIXES: tuple[str, ...] = ("state/collector_vnext", "logs/collector_vnext")
ALLOWED_HASH_ALGORITHMS: tuple[str, ...] = ("sha256", "blake3", "none_with_size_only_marker")
MINIMUM_STABILITY_SECONDS = 60
COMPLETED_SUFFIXES: tuple[str, ...] = (".jsonl", ".parquet")
INCOMPLETE_SUFFIX_MARKERS: tuple[str, ...] = (".tmp", ".partial", ".inprogress", ".writing")


def normalize_rel_file(value: str) -> str:
    """Normalize a manifest relative file path to POSIX form and reject root escape."""
    raw = str(value or "").strip().replace("\\", "/")
    if not raw:
        raise ValueError("rel_file_empty")
    path = PurePosixPath(raw)
    if path.is_absolute():
        raise ValueError("rel_file_absolute")
    parts = path.parts
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("rel_file_parent_or_empty_part")
    return path.as_posix()


def rel_prefix_for(rel_file: str) -> str:
    normalized = normalize_rel_file(rel_file)
    parts = normalized.split("/")
    if len(parts) < 2:
        return normalized
    return "/".join(parts[:2])


def is_allowed_rel_file(rel_file: str) -> bool:
    try:
        normalized = normalize_rel_file(rel_file)
    except ValueError:
        return False
    prefix = rel_prefix_for(normalized)
    if prefix not in ALLOWED_REL_PREFIXES:
        return False
    return not any(normalized == item or normalized.startswith(item + "/") for item in FORBIDDEN_REL_PREFIXES)


def is_complete_file_name(rel_file: str) -> bool:
    normalized = normalize_rel_file(rel_file)
    lower_name = PurePosixPath(normalized).name.lower()
    if any(marker in lower_name for marker in INCOMPLETE_SUFFIX_MARKERS):
        return False
    return any(lower_name.endswith(suffix) for suffix in COMPLETED_SUFFIXES)


@dataclass(frozen=True)
class HotColdCopyManifestRow:
    schema_version: str
    copy_intent: str
    exchange: str
    symbol: str
    rel_file: str
    rel_prefix: str
    hot_root_resolved: str
    cold_root_resolved: str
    hot_size_bytes: int
    cold_size_bytes: int
    hash_algorithm: str
    hot_hash: str | None
    cold_hash: str | None
    source_mtime_utc: str
    cold_mtime_utc: str
    copy_completed_at_utc: str
    verification_completed_at_utc: str
    size_stable_across_two_observations: bool
    minimum_stability_seconds: int
    completed_file_marker: str
    writer_state: str = "completed"
    not_copy_executor: bool = True
    not_delete_executor: bool = True
    not_archive_gc_enablement: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_manifest_row(
    *,
    exchange: str,
    symbol: str,
    rel_file: str,
    hot_root_resolved: str,
    cold_root_resolved: str,
    hot_size_bytes: int,
    cold_size_bytes: int,
    hash_algorithm: str,
    hot_hash: str | None,
    cold_hash: str | None,
    source_mtime_utc: str,
    cold_mtime_utc: str,
    copy_completed_at_utc: str,
    verification_completed_at_utc: str,
    size_stable_across_two_observations: bool,
    minimum_stability_seconds: int = MINIMUM_STABILITY_SECONDS,
    completed_file_marker: str = "suffix",
) -> HotColdCopyManifestRow:
    normalized = normalize_rel_file(rel_file)
    return HotColdCopyManifestRow(
        schema_version=COPY_MANIFEST_SCHEMA_VERSION,
        copy_intent=COPY_INTENT,
        exchange=str(exchange),
        symbol=str(symbol),
        rel_file=normalized,
        rel_prefix=rel_prefix_for(normalized),
        hot_root_resolved=str(hot_root_resolved),
        cold_root_resolved=str(cold_root_resolved),
        hot_size_bytes=int(hot_size_bytes),
        cold_size_bytes=int(cold_size_bytes),
        hash_algorithm=str(hash_algorithm),
        hot_hash=hot_hash,
        cold_hash=cold_hash,
        source_mtime_utc=str(source_mtime_utc),
        cold_mtime_utc=str(cold_mtime_utc),
        copy_completed_at_utc=str(copy_completed_at_utc),
        verification_completed_at_utc=str(verification_completed_at_utc),
        size_stable_across_two_observations=bool(size_stable_across_two_observations),
        minimum_stability_seconds=int(minimum_stability_seconds),
        completed_file_marker=str(completed_file_marker),
    )


def validate_manifest_row(row: HotColdCopyManifestRow | dict[str, Any]) -> dict[str, Any]:
    """Validate a manifest row using row metadata only. Does not read files, copy, or delete."""
    data = row.to_dict() if isinstance(row, HotColdCopyManifestRow) else dict(row)
    failures: list[str] = []
    warnings: list[str] = []

    if data.get("schema_version") != COPY_MANIFEST_SCHEMA_VERSION:
        failures.append("schema_version_mismatch")
    if data.get("copy_intent") != COPY_INTENT:
        failures.append("copy_intent_mismatch")
    if data.get("exchange") != "bitflyer":
        failures.append("exchange_must_be_bitflyer")
    if data.get("symbol") != "BTC_JPY":
        failures.append("symbol_must_be_BTC_JPY")

    try:
        rel_file = normalize_rel_file(str(data.get("rel_file") or ""))
    except ValueError as exc:
        failures.append(str(exc))
        rel_file = ""

    if rel_file:
        expected_prefix = rel_prefix_for(rel_file)
        if data.get("rel_prefix") != expected_prefix:
            failures.append("rel_prefix_mismatch")
        if expected_prefix not in ALLOWED_REL_PREFIXES:
            failures.append("rel_prefix_not_allowed")
        if any(rel_file == item or rel_file.startswith(item + "/") for item in FORBIDDEN_REL_PREFIXES):
            failures.append("rel_file_under_forbidden_prefix")
        try:
            if not is_complete_file_name(rel_file):
                failures.append("rel_file_not_completed_suffix_or_has_incomplete_marker")
        except ValueError as exc:
            failures.append(str(exc))

    hot_root = str(data.get("hot_root_resolved") or "").strip().casefold()
    cold_root = str(data.get("cold_root_resolved") or "").strip().casefold()
    if not hot_root or not cold_root:
        failures.append("hot_or_cold_root_missing")
    elif hot_root == cold_root:
        failures.append("hot_cold_root_same_resolved")

    hot_size = int(data.get("hot_size_bytes") or 0)
    cold_size = int(data.get("cold_size_bytes") or 0)
    if hot_size <= 0:
        failures.append("hot_size_not_positive")
    if cold_size <= 0:
        failures.append("cold_size_not_positive")
    if hot_size != cold_size:
        failures.append("hot_cold_size_mismatch")

    hash_algorithm = str(data.get("hash_algorithm") or "")
    hot_hash = data.get("hot_hash")
    cold_hash = data.get("cold_hash")
    if hash_algorithm not in ALLOWED_HASH_ALGORITHMS:
        failures.append("hash_algorithm_not_allowed")
    elif hash_algorithm == "none_with_size_only_marker":
        if hot_hash or cold_hash:
            warnings.append("size_only_marker_should_not_include_hash_values")
    else:
        if not hot_hash or not cold_hash:
            failures.append("hash_required_for_algorithm")
        elif str(hot_hash) != str(cold_hash):
            failures.append("hot_cold_hash_mismatch")

    for key in (
        "source_mtime_utc",
        "cold_mtime_utc",
        "copy_completed_at_utc",
        "verification_completed_at_utc",
    ):
        if not str(data.get(key) or "").strip():
            failures.append(f"{key}_missing")

    if data.get("size_stable_across_two_observations") is not True:
        failures.append("size_not_stable_across_two_observations")
    if int(data.get("minimum_stability_seconds") or 0) < MINIMUM_STABILITY_SECONDS:
        failures.append("minimum_stability_seconds_too_low")
    if str(data.get("writer_state") or "") != "completed":
        failures.append("writer_state_not_completed")

    for boundary_key in ("not_copy_executor", "not_delete_executor", "not_archive_gc_enablement"):
        if data.get(boundary_key) is not True:
            failures.append(f"{boundary_key}_must_be_true")

    return {
        "ok": not failures,
        "schema_version": COPY_MANIFEST_SCHEMA_VERSION,
        "failures": failures,
        "warnings": warnings,
        "rel_file": rel_file,
        "rel_prefix": data.get("rel_prefix"),
        "hash_algorithm": hash_algorithm,
        "size_bytes": hot_size,
        "copy_verified": not failures,
    }
