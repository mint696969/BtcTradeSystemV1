# path: ./btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py
# desc: Data model and validation helpers for Hot/Cold copy correctness manifests. No copy/delete executor.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any

COPY_MANIFEST_SCHEMA_VERSION = "hot_cold_copy_manifest_v1"
COPY_MANIFEST_JSONL_WRITER_SCHEMA_VERSION = "hot_cold_copy_manifest_jsonl_writer_v1"
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



def manifest_row_to_jsonl(row: HotColdCopyManifestRow | dict[str, Any]) -> str:
    """Serialize one validated manifest row to one JSONL line. Does not copy/delete or touch roots."""
    data = row.to_dict() if isinstance(row, HotColdCopyManifestRow) else dict(row)
    result = validate_manifest_row(data)
    if not result.get("ok"):
        raise ValueError("manifest_row_invalid: " + ",".join(result.get("failures") or []))
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def manifest_rows_to_jsonl(rows: list[HotColdCopyManifestRow | dict[str, Any]]) -> str:
    """Serialize validated manifest rows to append-only JSONL text. Does not write files."""
    return "".join(manifest_row_to_jsonl(row) for row in rows)


def parse_manifest_jsonl_text(text: str) -> list[dict[str, Any]]:
    """Parse and validate manifest JSONL text. Does not read files."""
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(str(text or "").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except Exception as exc:
            raise ValueError(f"manifest_jsonl_invalid_json_line_{line_number}: {type(exc).__name__}: {exc}") from exc
        result = validate_manifest_row(row)
        if not result.get("ok"):
            raise ValueError(
                f"manifest_jsonl_invalid_row_{line_number}: " + ",".join(result.get("failures") or [])
            )
        rows.append(row)
    return rows


def build_manifest_writer_dry_run_payload(
    rows: list[HotColdCopyManifestRow | dict[str, Any]],
    *,
    target_manifest_path: str,
) -> dict[str, Any]:
    """Build a dry-run append payload for a future manifest writer. Does not write files."""
    jsonl_text = manifest_rows_to_jsonl(rows)
    parsed = parse_manifest_jsonl_text(jsonl_text)
    total_bytes = sum(int(row.get("hot_size_bytes") or 0) for row in parsed)
    return {
        "schema_version": COPY_MANIFEST_JSONL_WRITER_SCHEMA_VERSION,
        "dry_run": True,
        "append_only": True,
        "would_write": False,
        "target_manifest_path": str(target_manifest_path),
        "row_count": len(parsed),
        "total_hot_size_bytes": total_bytes,
        "jsonl_text": jsonl_text,
        "boundary": {
            "not_copy_executor": True,
            "not_delete_executor": True,
            "not_archive_gc_enablement": True,
            "not_runtime_state_writer": True,
            "not_collector_state_mutation": True,
            "not_health_render_path_scan": True,
        },
    }


@dataclass(frozen=True)
class HotColdLogicalDatasetViewRow:
    """Duplicate-safe logical dataset row built from manifest metadata only."""

    logical_file_id: str
    exchange: str
    symbol: str
    rel_file: str
    storage_tier_selected: str
    hot_present: bool
    cold_present: bool
    cold_verified_by_manifest: bool
    selected_size_bytes: int
    selected_hash_algorithm: str
    selected_hash: str | None
    selection_reason: str
    not_physical_path_identity: bool = True
    not_dataset_reader: bool = True
    not_copy_executor: bool = True
    not_delete_executor: bool = True
    not_archive_gc_enablement: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_logical_file_id(*, exchange: str, symbol: str, rel_file: str) -> str:
    """Build the duplicate-safe logical identity. Physical roots are intentionally excluded."""
    normalized = normalize_rel_file(rel_file)
    return f"{str(exchange)}:{str(symbol)}:{normalized}"


def build_duplicate_safe_dataset_view_rows(
    rows: list[HotColdCopyManifestRow | dict[str, Any]],
    *,
    hot_retention_days: int = 10,
) -> list[HotColdLogicalDatasetViewRow]:
    """Build duplicate-safe logical dataset rows from manifest rows only.

    This function does not read D/E data files, scan directories, connect to
    simulation/training, copy files, delete files, or enable archive GC.
    """
    selected_by_id: dict[str, HotColdLogicalDatasetViewRow] = {}

    for row in rows:
        data = row.to_dict() if isinstance(row, HotColdCopyManifestRow) else dict(row)
        validation = validate_manifest_row(data)
        if not validation.get("ok"):
            raise ValueError("manifest_row_invalid_for_duplicate_safe_view: " + ",".join(validation.get("failures") or []))

        exchange = str(data.get("exchange") or "")
        symbol = str(data.get("symbol") or "")
        rel_file = normalize_rel_file(str(data.get("rel_file") or ""))
        logical_file_id = build_logical_file_id(exchange=exchange, symbol=symbol, rel_file=rel_file)
        hot_present = int(data.get("hot_size_bytes") or 0) > 0
        cold_present = int(data.get("cold_size_bytes") or 0) > 0
        cold_verified = bool(validation.get("copy_verified")) and cold_present

        # Manifest rows represent verified cold copies. Until a future catalog provides
        # partition age, select cold when verified; otherwise keep hot. This keeps the
        # skeleton deterministic without opening file reads or retention-date parsing.
        storage_tier_selected = "cold" if cold_verified else "hot"
        selected_size_bytes = int(data.get("cold_size_bytes") if storage_tier_selected == "cold" else data.get("hot_size_bytes"))
        selected_hash = data.get("cold_hash") if storage_tier_selected == "cold" else data.get("hot_hash")
        view_row = HotColdLogicalDatasetViewRow(
            logical_file_id=logical_file_id,
            exchange=exchange,
            symbol=symbol,
            rel_file=rel_file,
            storage_tier_selected=storage_tier_selected,
            hot_present=hot_present,
            cold_present=cold_present,
            cold_verified_by_manifest=cold_verified,
            selected_size_bytes=selected_size_bytes,
            selected_hash_algorithm=str(data.get("hash_algorithm") or ""),
            selected_hash=selected_hash,
            selection_reason=(
                f"cold_verified_by_manifest_hot_retention_days_{int(hot_retention_days)}"
                if cold_verified
                else f"hot_preferred_until_cold_verified_hot_retention_days_{int(hot_retention_days)}"
            ),
        )

        existing = selected_by_id.get(logical_file_id)
        if existing is None:
            selected_by_id[logical_file_id] = view_row
            continue
        if existing.storage_tier_selected != "cold" and view_row.storage_tier_selected == "cold":
            selected_by_id[logical_file_id] = view_row

    return [selected_by_id[key] for key in sorted(selected_by_id)]


def summarize_duplicate_safe_dataset_view(rows: list[HotColdLogicalDatasetViewRow]) -> dict[str, Any]:
    """Summarize duplicate-safe view rows without reading dataset files."""
    logical_ids = [row.logical_file_id for row in rows]
    duplicate_count = len(logical_ids) - len(set(logical_ids))
    return {
        "schema_version": "hot_cold_duplicate_safe_dataset_view_v1",
        "row_count": len(rows),
        "duplicate_logical_file_id_count": duplicate_count,
        "cold_selected_count": sum(1 for row in rows if row.storage_tier_selected == "cold"),
        "hot_selected_count": sum(1 for row in rows if row.storage_tier_selected == "hot"),
        "not_dataset_reader": True,
        "not_simulation_connector": True,
        "not_training_connector": True,
        "not_copy_executor": True,
        "not_delete_executor": True,
        "not_archive_gc_enablement": True,
    }

