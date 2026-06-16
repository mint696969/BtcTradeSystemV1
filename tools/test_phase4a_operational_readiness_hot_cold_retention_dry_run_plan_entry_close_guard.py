# path: ./tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_close_guard.py
# desc: Close guard for Phase 4-A Hot/Cold retention explicit dry-run plan entry criteria. No delete/GC/runtime mutation.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_close_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_criteria_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_DRY_RUN_PLAN_ENTRY_CRITERIA_2026-06-01.md"
PLANNER_PATH = "tmp/work/operator_operational_readiness/build_explicit_hot_cold_delete_plan_dry_run_v1.py"
ROADMAP_PATH = "tmp/gpt_room/memory/roadmaps/2026-05-28_phase4a_operational_readiness_hot_retention_and_ui_latency_gate.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
STATE_PATH = "tmp/gpt_room/11_STATE.json"

COMPILE_FILES = [
    SELF_PATH,
    ENTRY_GUARD_PATH,
    PLANNER_PATH,
]

FORBIDDEN_PLANNER_TOKENS = [
    ".unlink(",
    ".rmdir(",
    "shutil.rmtree(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "send2trash",
    "archive_gc_enable",
    "--execute",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operational_readiness_hot_cold_dry_run_entry_close"
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
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "phase": parsed.get("phase"),
        "json": parsed,
        "stdout_tail": (proc.stdout or "")[-1800:],
        "stderr_tail": (proc.stderr or "")[-1800:],
    }


def _check_spec(failures: list[str]) -> dict[str, Any]:
    text = _read(SPEC_PATH)
    required = [
        "Operational readiness hot/cold retention explicit dry-run plan entry criteria",
        "D:\\btc_ts_hot",
        "E:\\btc_ts",
        "dry_run = true",
        "build_delete_plan_only_no_delete_no_unlink_no_rmdir",
        "Do not unlink files.",
        "Do not rmdir directories.",
        "Do not enable archive GC.",
        "Do not mutate collector state.",
        "Do not run guarded small-batch delete without a separate operator confirmation and plan hash slice.",
        ENTRY_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"retention dry-run plan close spec missing fragment: {fragment}")
    return {"missing": missing}


def _check_roadmap_and_room(failures: list[str]) -> dict[str, Any]:
    roadmap = _read(ROADMAP_PATH)
    focus = _read(FOCUS_PATH)
    state = _read(STATE_PATH)
    required = [
        "Create explicit D-hot / E-cold dry-run delete plan.",
        "D:\\btc_ts_hot",
        "E:\\btc_ts",
        "destructive hot storage delete",
    ]
    missing: list[str] = []
    for fragment in required:
        if fragment not in roadmap and fragment not in focus and fragment not in state:
            missing.append(fragment)
            failures.append(f"roadmap/room missing dry-run plan close fragment: {fragment}")
    return {"missing": missing}


def _check_planner_source(failures: list[str]) -> dict[str, Any]:
    text = _read(PLANNER_PATH)
    required = [
        "SCHEMA_VERSION = \"build_explicit_hot_cold_delete_plan_dry_run_v1\"",
    "DEFAULT_HOT_ROOT",
    "BTCTS_PLAN_HOT_ROOT",
    "D:\\btc_ts_hot",
    "DEFAULT_COLD_ROOT",
    "BTCTS_PLAN_COLD_ROOT",
    "E:\\btc_ts",
        "ALLOWED_PREFIXES = [",
        "\"data/market_data\"",
        "\"data/collector_raw\"",
        "FORBIDDEN_PREFIXES = [",
        "\"state/collector_vnext\"",
        "\"logs/collector_vnext\"",
        "build_delete_plan_only_no_delete_no_unlink_no_rmdir",
        "cold_size_bytes == hot_size_bytes only",
        "plan_hash",
        "operator_review_required_before_any_delete",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_PLANNER_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"planner missing dry-run close fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"planner contains forbidden delete/config token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_entry_boundary(entry_result: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    parsed = entry_result.get("json") if isinstance(entry_result, dict) else None
    checks = parsed.get("checks") if isinstance(parsed, dict) else None
    planner_source = checks.get("planner_source") if isinstance(checks, dict) else None
    probe = checks.get("planner_empty_roots_probe") if isinstance(checks, dict) else None
    forbidden_hits = planner_source.get("forbidden_hits") if isinstance(planner_source, dict) else None
    probe_ok = probe.get("ok") if isinstance(probe, dict) else None
    dry_run = probe.get("dry_run") if isinstance(probe, dict) else None
    filesystem_unchanged = probe.get("filesystem_unchanged") if isinstance(probe, dict) else None
    action = probe.get("action") if isinstance(probe, dict) else None
    ok = (
        forbidden_hits == []
        and probe_ok is True
        and dry_run is True
        and filesystem_unchanged is True
        and action == "build_delete_plan_only_no_delete_no_unlink_no_rmdir"
    )
    if not ok:
        failures.append("retention dry-run entry guard must prove dry-run/no-delete planner boundary")
    return {
        "ok": ok,
        "verified_by_entry_guard": True,
        "forbidden_hits": forbidden_hits,
        "probe_ok": probe_ok,
        "dry_run": dry_run,
        "filesystem_unchanged": filesystem_unchanged,
        "action": action,
        "path": ENTRY_GUARD_PATH,
    }


def main() -> int:
    failures: list[str] = []
    entry_guard = _run_json_guard(ENTRY_GUARD_PATH, failures)
    checks = {
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "entry_guard": entry_guard,
        "spec": _check_spec(failures),
        "roadmap_and_room": _check_roadmap_and_room(failures),
        "planner_source": _check_planner_source(failures),
        "entry_boundary": _check_entry_boundary(entry_guard, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
