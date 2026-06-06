# path: ./tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_close_guard.py
# desc: Phase 4-A close guard for Hot/Cold copy manifest model skeleton. No copy/delete executor.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_COPY_MANIFEST_MODEL_CLOSE_2026-06-02.md"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_guard.py"
MODEL_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_guard.py"
HEALTH_PAYLOAD_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
MODEL_PATH = "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py"
TEST_PATH = "btcts_next/src/btcts/collector_vnext/archive/test_copy_manifest.py"
PRIMARY_COMPACT_PATH = "tmp/work/phase4a_health_warroom_evidence_consumption_ui_rendering/run_primary_guard_compact_v1.py"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

FORBIDDEN_MODEL_TOKENS = [
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
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_copy_manifest_model_close"
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
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _run_primary_compact(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / PRIMARY_COMPACT_PATH)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=3600)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"primary compact did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failed_guard_count") == 0 and parsed.get("top_failure_count") == 0
    if not ok:
        failures.append("primary compact must be ok with no failed guards")
    return {"ok": ok, "returncode": proc.returncode, "failed_guard_count": parsed.get("failed_guard_count"), "top_failure_count": parsed.get("top_failure_count"), "failed_guards": parsed.get("failed_guards"), "json_path": parsed.get("json_path"), "log_path": parsed.get("log_path")}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold copy manifest model close",
        "copy correctness / manifest entry criteria",
        "copy manifest row data model",
        "manifest row validation helper",
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
        "candidate_delete_files = 0",
        "No delete is required now.",
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


def _check_latest_10day_plan(failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / PLAN_SUMMARY_PATH
    if not path.exists():
        failures.append(f"latest 10-day plan summary missing: {PLAN_SUMMARY_PATH}")
        return {"exists": False}
    data = json.loads(path.read_text(encoding="utf-8"))
    too_new = ((data.get("review_exclusions") or {}).get("too_new") or {})
    ok = (
        data.get("ok") is True
        and data.get("plan_hash") == EXPECTED_PLAN_HASH
        and int(data.get("candidate_delete_files") or 0) == 0
        and float(data.get("candidate_delete_gb") or 0.0) == 0.0
        and int(too_new.get("files") or 0) == 56
        and data.get("no_delete_no_unlink_no_rmdir") is True
    )
    if not ok:
        failures.append("latest 10-day plan summary must remain zero-candidate/no-delete")
    return {"ok": ok, "plan_hash": data.get("plan_hash"), "candidate_delete_files": data.get("candidate_delete_files"), "too_new": too_new}


def _probe_model(failures: list[str]) -> dict[str, Any]:
    code = """
from btcts.collector_vnext.archive.copy_manifest import build_manifest_row, validate_manifest_row
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
        "model_guard": _run_json_guard(MODEL_GUARD_PATH, failures),
        "health_payload_guard": _run_json_guard(HEALTH_PAYLOAD_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "spec": _check_spec(failures),
        "model_source": _check_model_source(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
        "model_probe": _probe_model(failures),
        "primary_compact": _run_primary_compact(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_copy_manifest_model_close_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
