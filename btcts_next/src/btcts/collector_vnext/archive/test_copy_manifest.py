# path: ./btcts_next/src/btcts/collector_vnext/archive/test_copy_manifest.py
# desc: Plain test for Hot/Cold copy manifest model. No copy/delete.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.collector_vnext.archive.copy_manifest import (  # noqa: E402
    COPY_MANIFEST_SCHEMA_VERSION,
    build_manifest_row,
    normalize_rel_file,
    validate_manifest_row,
)


def _valid_row():
    return build_manifest_row(
        exchange="bitflyer",
        symbol="BTC_JPY",
        rel_file="data/collector_raw/exchange=bitflyer/symbol=BTC_JPY/channel=executions/date=2026-06-01/part-00001.jsonl",
        hot_root_resolved="d:/btc_ts_hot",
        cold_root_resolved="e:/btc_ts",
        hot_size_bytes=123,
        cold_size_bytes=123,
        hash_algorithm="sha256",
        hot_hash="abc",
        cold_hash="abc",
        source_mtime_utc="2026-06-01T00:00:00Z",
        cold_mtime_utc="2026-06-01T00:01:00Z",
        copy_completed_at_utc="2026-06-01T00:02:00Z",
        verification_completed_at_utc="2026-06-01T00:03:00Z",
        size_stable_across_two_observations=True,
        minimum_stability_seconds=60,
    )


def main() -> int:
    assert normalize_rel_file("data\\collector_raw\\x.jsonl") == "data/collector_raw/x.jsonl"
    for bad in ["", "/absolute/file.jsonl", "data/../escape.jsonl"]:
        try:
            normalize_rel_file(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected invalid rel_file: {bad}")

    row = _valid_row()
    assert row.schema_version == COPY_MANIFEST_SCHEMA_VERSION
    result = validate_manifest_row(row)
    assert result["ok"] is True
    assert result["failures"] == []
    assert result["rel_prefix"] == "data/collector_raw"
    assert result["copy_verified"] is True

    size_only = _valid_row().to_dict()
    size_only["hash_algorithm"] = "none_with_size_only_marker"
    size_only["hot_hash"] = None
    size_only["cold_hash"] = None
    assert validate_manifest_row(size_only)["ok"] is True

    mismatch = _valid_row().to_dict()
    mismatch["cold_hash"] = "different"
    assert "hot_cold_hash_mismatch" in validate_manifest_row(mismatch)["failures"]

    bad_size = _valid_row().to_dict()
    bad_size["cold_size_bytes"] = 122
    assert "hot_cold_size_mismatch" in validate_manifest_row(bad_size)["failures"]

    not_stable = _valid_row().to_dict()
    not_stable["size_stable_across_two_observations"] = False
    assert "size_not_stable_across_two_observations" in validate_manifest_row(not_stable)["failures"]

    incomplete = _valid_row().to_dict()
    incomplete["rel_file"] = "data/collector_raw/exchange=bitflyer/symbol=BTC_JPY/channel=executions/date=2026-06-01/part-00001.jsonl.tmp"
    assert "rel_file_not_completed_suffix_or_has_incomplete_marker" in validate_manifest_row(incomplete)["failures"]

    forbidden = _valid_row().to_dict()
    forbidden["rel_file"] = "state/collector_vnext/state.json"
    forbidden["rel_prefix"] = "state/collector_vnext"
    failures = validate_manifest_row(forbidden)["failures"]
    assert "rel_prefix_not_allowed" in failures
    assert "rel_file_under_forbidden_prefix" in failures

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
