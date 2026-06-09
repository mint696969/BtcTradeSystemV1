# path: ./tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_criteria_guard.py
# desc: Phase 4-A operational readiness hot/cold retention explicit dry-run plan entry criteria guard.

from __future__ import annotations

import json
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_criteria_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_DRY_RUN_PLAN_ENTRY_CRITERIA_2026-06-01.md"
PLANNER_PATH = "tmp/work/operator_operational_readiness/build_explicit_hot_cold_delete_plan_dry_run_v1.py"
ROADMAP_PATH = "tmp/gpt_room/memory/roadmaps/2026-05-28_phase4a_operational_readiness_hot_retention_and_ui_latency_gate.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
STATE_PATH = "tmp/gpt_room/11_STATE.json"

REQUIRED_PLANNER_FRAGMENTS = [
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
    "dry_run",
    "build_delete_plan_only_no_delete_no_unlink_no_rmdir",
    "No delete, unlink, rmdir, config update, archive GC enablement, runtime change, UI change, or collector state mutation is performed.",
    "cold_size_bytes == hot_size_bytes only",
    "plan_hash",
    "operator_review_required_before_any_delete",
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
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operational_readiness_hot_cold_dry_run_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Operational readiness hot/cold retention explicit dry-run plan entry criteria",
        "D:\\btc_ts_hot",
        "E:\\btc_ts",
        "D:\\btc_ts_hot\\data\\market_data",
        "D:\\btc_ts_hot\\data\\collector_raw",
        "dry_run = true",
        "build_delete_plan_only_no_delete_no_unlink_no_rmdir",
        "Do not unlink files.",
        "Do not rmdir directories.",
        "Do not enable archive GC.",
        "Do not mutate collector state.",
        "Do not run guarded small-batch delete without a separate operator confirmation and plan hash slice.",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


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
            failures.append(f"roadmap/room missing fragment: {fragment}")
            missing.append(fragment)
    return {"missing": missing}


def _check_planner_source(failures: list[str]) -> dict[str, Any]:
    text = _read(PLANNER_PATH)
    missing = [fragment for fragment in REQUIRED_PLANNER_FRAGMENTS if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_PLANNER_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"planner missing required dry-run fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"planner contains forbidden delete/config token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _probe_planner_empty_roots(failures: list[str]) -> dict[str, Any]:
    probe_root = REPO_ROOT / "tmp" / "_guard_probe" / "hot_cold_dry_run_entry"
    hot = probe_root / "D_hot"
    cold = probe_root / "E_cold"
    if probe_root.exists():
        shutil.rmtree(probe_root)
    (hot / "data" / "market_data").mkdir(parents=True, exist_ok=True)
    (hot / "data" / "collector_raw").mkdir(parents=True, exist_ok=True)
    (cold / "data" / "market_data").mkdir(parents=True, exist_ok=True)
    (cold / "data" / "collector_raw").mkdir(parents=True, exist_ok=True)

    before = sorted(str(p.relative_to(probe_root)).replace("\\", "/") for p in probe_root.rglob("*"))
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / PLANNER_PATH),
            "--hot-root",
            str(hot),
            "--cold-root",
            str(cold),
            "--stdout-only",
            "--max-files-per-prefix",
            "1000",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    after = sorted(str(p.relative_to(probe_root)).replace("\\", "/") for p in probe_root.rglob("*"))
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"planner stdout-only probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}

    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("dry_run") is True
    if not ok:
        failures.append("planner stdout-only probe must return ok true and dry_run true")
    if before != after:
        failures.append("planner stdout-only probe changed probe filesystem contents")
    if parsed.get("action") != "build_delete_plan_only_no_delete_no_unlink_no_rmdir":
        failures.append("planner action must remain build_delete_plan_only_no_delete_no_unlink_no_rmdir")
    constraints = parsed.get("constraints") or {}
    if constraints.get("allowed_prefixes") != ["data/market_data", "data/collector_raw"]:
        failures.append("planner allowed prefixes mismatch")
    if constraints.get("forbidden_prefixes") != ["state/collector_vnext", "logs/collector_vnext"]:
        failures.append("planner forbidden prefixes mismatch")

    return {
        "ok": ok,
        "returncode": proc.returncode,
        "dry_run": parsed.get("dry_run"),
        "action": parsed.get("action"),
        "candidate_delete_files": ((parsed.get("counts") or {}).get("candidate_delete_files")),
        "plan_hash_present": bool(parsed.get("plan_hash")),
        "filesystem_unchanged": before == after,
    }


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_planner": _compile(PLANNER_PATH, failures),
        "spec": _check_spec(failures),
        "roadmap_and_room": _check_roadmap_and_room(failures),
        "planner_source": _check_planner_source(failures),
        "planner_empty_roots_probe": _probe_planner_empty_roots(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_criteria_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
