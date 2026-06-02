# path: ./tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_guard.py
# desc: Phase 4-A guard for Hot/Cold copy manifest JSONL dry-run serializer. No copy/delete executor.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_guard.py"
MODEL_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_COPY_MANIFEST_WRITER_DRY_RUN_2026-06-02.md"
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
    "open(",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_copy_manifest_writer_dry_run"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str], *, timeout: int = 1200) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=timeout)
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
        "Hot/Cold copy manifest writer dry-run serializer",
        "COPY_MANIFEST_JSONL_WRITER_SCHEMA_VERSION = hot_cold_copy_manifest_jsonl_writer_v1",
        "manifest_row_to_jsonl",
        "manifest_rows_to_jsonl",
        "parse_manifest_jsonl_text",
        "build_manifest_writer_dry_run_payload",
        "validates every manifest row before serialization",
        "would_write = false",
        "append_only = true",
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
        "COPY_MANIFEST_JSONL_WRITER_SCHEMA_VERSION = \"hot_cold_copy_manifest_jsonl_writer_v1\"",
        "def manifest_row_to_jsonl",
        "def manifest_rows_to_jsonl",
        "def parse_manifest_jsonl_text",
        "def build_manifest_writer_dry_run_payload",
        "Does not copy/delete or touch roots.",
        "Does not write files.",
        "would_write",
        "append_only",
        "not_copy_executor",
        "not_delete_executor",
        "not_archive_gc_enablement",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_MODEL_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"model missing dry-run writer fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"model contains forbidden executor/io token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _probe_writer(failures: list[str]) -> dict[str, Any]:
    code = """
from btcts.collector_vnext.archive.copy_manifest import build_manifest_row, build_manifest_writer_dry_run_payload
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
payload = build_manifest_writer_dry_run_payload([row], target_manifest_path='state/collector_vnext/hot_cold_copy_manifest.jsonl')
print(json.dumps(payload, sort_keys=True))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO_ROOT / "btcts_next" / "src"), text=True, capture_output=True, timeout=120)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"writer probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    boundary = parsed.get("boundary") or {}
    ok = (
        proc.returncode == 0
        and parsed.get("dry_run") is True
        and parsed.get("would_write") is False
        and parsed.get("append_only") is True
        and parsed.get("row_count") == 1
        and parsed.get("total_hot_size_bytes") == 100
        and "jsonl_text" in parsed
        and boundary.get("not_copy_executor") is True
        and boundary.get("not_delete_executor") is True
        and boundary.get("not_archive_gc_enablement") is True
    )
    if not ok:
        failures.append("writer probe must produce dry-run append-only payload without executor boundaries")
    return {"ok": ok, "returncode": proc.returncode, "row_count": parsed.get("row_count"), "boundary": boundary}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_model": _compile(MODEL_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "model_close_guard": _run_json_guard(MODEL_CLOSE_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "spec": _check_spec(failures),
        "model_source": _check_model_source(failures),
        "writer_probe": _probe_writer(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
