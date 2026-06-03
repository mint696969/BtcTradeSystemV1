# path: ./tools/test_phase4a_phase_f_collector_transform_migration_prep_entry_criteria_guard.py
# desc: Phase 4-A Phase F collector transform migration prep entry criteria guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_phase_f_collector_transform_migration_prep_entry_criteria_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_PHASE_F_COLLECTOR_TRANSFORM_MIGRATION_PREP_ENTRY_CRITERIA_2026-06-03.md"
ROADMAP_PATH = "tmp/gpt_room/memory/roadmaps/PHASE4A_L3_FREEZE_TO_L2_CANONICAL_BOUNDARY_AND_UI_ROADMAP_2026-04-22.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
PHASEC_TOTAL_GUARD_PATH = "tools/test_phase4a_post_phasec_total_guard.py"
PHASEC_CLOSE_GUARD_PATH = "tools/test_phase4a_phasec_close_bundle.py"
POST_PHASEC_DOWNSTREAM_GUARD_PATH = "tools/test_phase4a_post_phasec_downstream_boundary_check.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    SELF_PATH,
    PHASEC_CLOSE_GUARD_PATH,
    POST_PHASEC_DOWNSTREAM_GUARD_PATH,
    PHASEC_TOTAL_GUARD_PATH,
    "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py",
    "btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/emit_rest.py",
    "btcts_next/src/btcts/collector_vnext/emit_ws.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
]

REQUIRED_SPEC_FRAGMENTS = [
    "Phase4A Phase F collector transform migration prep entry criteria",
    "entry criteria / guard only",
    "usage audit of collector_vnext/transforms call sites",
    "runtime import migration",
    "collector capture behavior changes",
    "collector writer/backfill changes",
    "phase4a_phase_f_collector_transform_usage_audit",
    "tmp/work output only",
]

REQUIRED_ROADMAP_FRAGMENTS = [
    "Phase F  collector transform migration prep and staged cleanup",
    "collector transform migration prep and staged cleanup",
    "usage audit",
    "facade / bridge",
    "staged migration",
    "capture 安定性",
]

REQUIRED_ROOM_FRAGMENTS = [
    "phase4a_phase_f_collector_transform_migration_prep_entry_criteria",
    "return_to_main_phase4a_roadmap_or_phase_f_prep",
    "health_latency_budget_metadata_observability_guard_green_clean_commit_checkpoint_a35e7535",
    "runtime state writer",
    "market_engine integration",
    "collector writer/backfill",
    "broker/order/execution",
    "inference/training",
    "raw D/E scanner",
]

FORBIDDEN_IMPLEMENTATION_PATHS = [
    "btcts_next/src/btcts/collector_vnext/canonical_facade.py",
    "btcts_next/src/btcts/collector_vnext/transform_facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/runtime_bridge.py",
]

FORBIDDEN_PRIMARY_ABSENCE = [
    SELF_PATH,
    "phase_f_collector_transform_migration_prep_entry_criteria_guard",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "phase_f_collector_transform_migration_prep_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=1200,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase")}


def _check_fragments(rel_path: str, required: list[str], failures: list[str]) -> dict[str, Any]:
    text = _read(rel_path)
    if not text:
        failures.append(f"required file missing or empty: {rel_path}")
        return {"missing_file": True, "missing": required}
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing fragment in {rel_path}: {fragment}")
    return {"missing": missing}


def _check_forbidden_paths(failures: list[str]) -> dict[str, Any]:
    existing = [rel for rel in FORBIDDEN_IMPLEMENTATION_PATHS if (REPO_ROOT / rel).exists()]
    for rel in existing:
        failures.append(f"Phase F entry must not create runtime migration/facade implementation yet: {rel}")
    return {"existing": existing}


def _check_primary_connection(failures: list[str]) -> dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    missing = [fragment for fragment in FORBIDDEN_PRIMARY_ABSENCE if fragment not in text]
    for fragment in missing:
        failures.append(f"primary total guard missing Phase F entry connection: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "phasec_total_guard": _run_json_guard(PHASEC_TOTAL_GUARD_PATH, failures),
        "spec": _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, failures),
        "roadmap": _check_fragments(ROADMAP_PATH, REQUIRED_ROADMAP_FRAGMENTS, failures),
        "focus": _check_fragments(FOCUS_PATH, REQUIRED_ROOM_FRAGMENTS, failures),
        "state": _check_fragments(STATE_PATH, REQUIRED_ROOM_FRAGMENTS, failures),
        "no_runtime_migration_files_yet": _check_forbidden_paths(failures),
        "primary_connection": _check_primary_connection(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_phase_f_collector_transform_migration_prep_entry_criteria_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
