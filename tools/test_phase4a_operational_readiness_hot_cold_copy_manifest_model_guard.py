# path: ./tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_guard.py
# desc: Phase 4-A Hot/Cold copy manifest model guard. No copy/delete executor.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_COPY_MANIFEST_MODEL_2026-06-02.md"
MODEL_PATH = "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py"
TEST_PATH = "btcts_next/src/btcts/collector_vnext/archive/test_copy_manifest.py"

FORBIDDEN_MODEL_TOKENS = [
    "shutil.copy",
    "copy2(",
    "copytree(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "archive_gc_enable",
    "execute_copy_plan",
    "execute_gc_plan",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_copy_manifest_model"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1200)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold copy manifest model skeleton",
        "COPY_MANIFEST_SCHEMA_VERSION = hot_cold_copy_manifest_v1",
        "COPY_INTENT = hot_to_cold_archive_copy",
        "ALLOWED_REL_PREFIXES = data/market_data, data/collector_raw",
        "FORBIDDEN_REL_PREFIXES = state/collector_vnext, logs/collector_vnext",
        "ALLOWED_HASH_ALGORITHMS = sha256, blake3, none_with_size_only_marker",
        "hot_size_bytes == cold_size_bytes",
        "hot_hash == cold_hash",
        "size_stable_across_two_observations = true",
        "not_copy_executor = true",
        "not_delete_executor = true",
        "not_archive_gc_enablement = true",
        "Do not copy files.",
        "Do not delete files.",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_model_source(failures: list[str]) -> dict[str, Any]:
    text = _read(MODEL_PATH)
    required = [
        "COPY_MANIFEST_SCHEMA_VERSION = \"hot_cold_copy_manifest_v1\"",
        "COPY_INTENT = \"hot_to_cold_archive_copy\"",
        "ALLOWED_REL_PREFIXES",
        "FORBIDDEN_REL_PREFIXES",
        "ALLOWED_HASH_ALGORITHMS",
        "MINIMUM_STABILITY_SECONDS = 60",
        "class HotColdCopyManifestRow",
        "def normalize_rel_file",
        "def rel_prefix_for",
        "def is_allowed_rel_file",
        "def is_complete_file_name",
        "def build_manifest_row",
        "def validate_manifest_row",
        "hot_cold_size_mismatch",
        "hot_cold_hash_mismatch",
        "size_not_stable_across_two_observations",
        "not_copy_executor",
        "not_delete_executor",
        "not_archive_gc_enablement",
        "Does not read files, copy, or delete.",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_MODEL_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"model missing required fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"model contains forbidden executor/delete token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _probe_model(failures: list[str]) -> dict[str, Any]:
    code = """
from btcts.collector_vnext.archive.copy_manifest import build_manifest_row, validate_manifest_row
row = build_manifest_row(
    exchange='bitflyer', symbol='BTC_JPY',
    rel_file='data/market_data/exchange=bitflyer/symbol=BTC_JPY/date=2026-06-01/part-00001.parquet',
    hot_root_resolved='d:/btc_ts_hot', cold_root_resolved='e:/btc_ts',
    hot_size_bytes=100, cold_size_bytes=100,
    hash_algorithm='sha256', hot_hash='h', cold_hash='h',
    source_mtime_utc='2026-06-01T00:00:00Z', cold_mtime_utc='2026-06-01T00:01:00Z',
    copy_completed_at_utc='2026-06-01T00:02:00Z', verification_completed_at_utc='2026-06-01T00:03:00Z',
    size_stable_across_two_observations=True,
)
import json
print(json.dumps(validate_manifest_row(row), sort_keys=True))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO_ROOT / "btcts_next" / "src"), text=True, capture_output=True, timeout=120)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"model probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("copy_verified") is True
    if not ok:
        failures.append("model probe must validate a correct manifest row")
    return {"ok": ok, "returncode": proc.returncode, "parsed": parsed}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_model": _compile(MODEL_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "spec": _check_spec(failures),
        "model_source": _check_model_source(failures),
        "model_probe": _probe_model(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_copy_manifest_model_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
