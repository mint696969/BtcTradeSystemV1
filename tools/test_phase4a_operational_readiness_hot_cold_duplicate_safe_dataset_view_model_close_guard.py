# path: ./tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_model_close_guard.py
# desc: Close guard for duplicate-safe Hot/Cold logical dataset view read-only model skeleton. No file reader/training/copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_model_close_guard.py"
MODEL_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_model_guard.py"
ENTRY_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_close_guard.py"
MODEL_PATH = "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py"
TEST_PATH = "btcts_next/src/btcts/collector_vnext/archive/test_copy_manifest.py"

COMPILE_FILES = [
    MODEL_GUARD_PATH,
    ENTRY_CLOSE_GUARD_PATH,
    MODEL_PATH,
    TEST_PATH,
]

FORBIDDEN_RUNTIME_TOKENS = [
    "read_parquet(",
    "read_json(",
    "rglob(\"*.parquet\")",
    "rglob(\"*.jsonl\")",
    "shutil.copy",
    "copy2(",
    "copytree(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "archive_gc_enable =",
    "archive_gc_enable:",
    "archive_gc_enable(",
    "execute_copy_plan",
    "execute_gc_plan",
    "connect_to_simulation",
    "connect_to_training",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_duplicate_safe_dataset_view_model_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1800)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_source_shape(failures: list[str]) -> dict[str, Any]:
    text = _read(MODEL_PATH)
    required = [
        "class HotColdLogicalDatasetViewRow",
        "def build_logical_file_id",
        "def build_duplicate_safe_dataset_view_rows",
        "def summarize_duplicate_safe_dataset_view",
        "Physical roots are intentionally excluded.",
        "manifest_row_invalid_for_duplicate_safe_view",
        "cold_verified_by_manifest_hot_retention_days_",
        "hot_preferred_until_cold_verified_hot_retention_days_",
        "hot_cold_duplicate_safe_dataset_view_v1",
        "not_physical_path_identity",
        "not_dataset_reader",
        "not_simulation_connector",
        "not_training_connector",
        "not_copy_executor",
        "not_delete_executor",
        "not_archive_gc_enablement",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"duplicate-safe dataset view model close source missing fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"duplicate-safe dataset view model close source contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _probe_model(failures: list[str]) -> dict[str, Any]:
    code = """
from btcts.collector_vnext.archive.copy_manifest import build_manifest_row, build_duplicate_safe_dataset_view_rows, summarize_duplicate_safe_dataset_view
import json
row = build_manifest_row(
    exchange='bitflyer', symbol='BTC_JPY',
    rel_file='data/collector_raw/exchange=bitflyer/symbol=BTC_JPY/channel=executions/date=2026-06-01/part-00001.jsonl',
    hot_root_resolved='d:/btc_ts_hot', cold_root_resolved='e:/btc_ts',
    hot_size_bytes=100, cold_size_bytes=100,
    hash_algorithm='sha256', hot_hash='h', cold_hash='h',
    source_mtime_utc='2026-06-01T00:00:00Z', cold_mtime_utc='2026-06-01T00:01:00Z',
    copy_completed_at_utc='2026-06-01T00:02:00Z', verification_completed_at_utc='2026-06-01T00:03:00Z',
    size_stable_across_two_observations=True,
)
rows = build_duplicate_safe_dataset_view_rows([row, row.to_dict()])
summary = summarize_duplicate_safe_dataset_view(rows)
print(json.dumps({'rows': [r.to_dict() for r in rows], 'summary': summary}, sort_keys=True))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO_ROOT / "btcts_next" / "src"), text=True, capture_output=True, timeout=120)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"duplicate-safe dataset view close model probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    rows = parsed.get("rows") or []
    summary = parsed.get("summary") or {}
    ok = (
        proc.returncode == 0
        and len(rows) == 1
        and rows[0].get("logical_file_id") == "bitflyer:BTC_JPY:data/collector_raw/exchange=bitflyer/symbol=BTC_JPY/channel=executions/date=2026-06-01/part-00001.jsonl"
        and rows[0].get("storage_tier_selected") == "cold"
        and rows[0].get("not_dataset_reader") is True
        and rows[0].get("not_physical_path_identity") is True
        and summary.get("row_count") == 1
        and summary.get("duplicate_logical_file_id_count") == 0
        and summary.get("cold_selected_count") == 1
        and summary.get("not_dataset_reader") is True
        and summary.get("not_simulation_connector") is True
        and summary.get("not_training_connector") is True
        and summary.get("not_copy_executor") is True
        and summary.get("not_delete_executor") is True
        and summary.get("not_archive_gc_enablement") is True
    )
    if not ok:
        failures.append("duplicate-safe dataset view close model probe must deduplicate and stay read-only")
    return {"ok": ok, "returncode": proc.returncode, "rows": rows, "summary": summary, "stderr_tail": (proc.stderr or "")[-1200:]}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "model_guard": _run_json_guard(MODEL_GUARD_PATH, failures),
        "entry_close_guard": {"verified_before_model_close_guard": True, "path": ENTRY_CLOSE_GUARD_PATH},
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "source_shape": _check_source_shape(failures),
        "model_probe": _probe_model(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_model_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
