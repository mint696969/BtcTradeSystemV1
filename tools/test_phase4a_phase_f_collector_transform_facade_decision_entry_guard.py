# path: ./tools/test_phase4a_phase_f_collector_transform_facade_decision_entry_guard.py
# desc: Phase 4-A Phase F collector transform facade decision entry guard.

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

SELF_PATH = "tools/test_phase4a_phase_f_collector_transform_facade_decision_entry_guard.py"
USAGE_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_usage_audit_guard.py"
AUDIT_OUTPUT_PATH = "tmp/work/phase4a_phase_f_collector_transform_migration_prep/outputs/collector_transform_usage_audit_v1.json"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_PHASE_F_COLLECTOR_TRANSFORM_FACADE_DECISION_ENTRY_CRITERIA_2026-06-03.md"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    SELF_PATH,
    USAGE_GUARD_PATH,
    "tools/audit_phase4a_phase_f_collector_transform_usage.py",
]

REQUIRED_SPEC_FRAGMENTS = [
    "B: add a collector transform facade later as a stable runtime adapter import surface",
    "This decision does not create the facade implementation yet.",
    "future facade = stable collector runtime adapter import surface only",
    "create a facade skeleton in a later guarded slice",
    "facade must re-export/delegate existing transform functions only",
    "facade must not change payload shape",
    "facade must not change capture behavior",
    "runtime import migration",
    "collector writer/backfill changes",
    "phase4a_phase_f_collector_transform_facade_skeleton",
]

REQUIRED_DECISION_CHECKPOINT_FRAGMENTS = [
    "phase4a_phase_f_collector_transform_usage_audit_clean_commit_checkpoint_d01213bc",
    "phase4a_phase_f_collector_transform_facade_decision_entry_criteria",
    "phase4a_phase_f_collector_transform_facade_decision_entry_clean_commit_checkpoint_8505c443",
    "phase4a_phase_f_collector_transform_facade_skeleton",
]

FORBIDDEN_RUNTIME_MIGRATION_PATHS = [
    "btcts_next/src/btcts/collector_vnext/canonical_facade.py",
    "btcts_next/src/btcts/collector_vnext/transform_facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/runtime_bridge.py",
]

REQUIRED_AUDIT_SYMBOLS = [
    "canonical_board_snapshot",
    "canonical_board_event",
    "canonical_trades",
    "canonical_ws_trade",
    "apply_board_structural_hints",
    "apply_trade_structural_hints",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "phase_f_collector_transform_facade_decision_entry"
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


def _check_audit_output(failures: list[str]) -> dict[str, Any]:
    text = _read(AUDIT_OUTPUT_PATH)
    if not text:
        failures.append(f"audit output missing: {AUDIT_OUTPUT_PATH}")
        return {"ok": False, "missing": REQUIRED_AUDIT_SYMBOLS}
    try:
        payload = json.loads(text)
    except Exception as exc:
        failures.append(f"audit output invalid JSON: {exc}")
        return {"ok": False, "error": str(exc)}
    usage_items = payload.get("usage_items") if isinstance(payload, dict) else None
    by_symbol = {str(item.get("symbol")): item for item in usage_items or [] if isinstance(item, dict)}
    missing = [symbol for symbol in REQUIRED_AUDIT_SYMBOLS if symbol not in by_symbol]
    for symbol in missing:
        failures.append(f"audit output missing required symbol: {symbol}")
    if payload.get("ok") is not True or payload.get("failures") != []:
        failures.append("audit output must be ok true and failures []")
    if payload.get("forbidden_runtime_migration_paths_existing") != []:
        failures.append("audit output must not have runtime migration paths")
    if payload.get("direct_payload_imports_outside_transforms") != []:
        failures.append("audit output must not have direct payload imports outside transforms")
    return {"missing": missing, "usage_item_count": len(by_symbol), "ok": not missing}


def _check_forbidden_paths(failures: list[str]) -> dict[str, Any]:
    existing = [rel for rel in FORBIDDEN_RUNTIME_MIGRATION_PATHS if (REPO_ROOT / rel).exists()]
    for rel in existing:
        failures.append(f"decision entry must not create facade/runtime bridge yet: {rel}")
    return {"existing": existing}


def _check_primary_connection(failures: list[str]) -> dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [SELF_PATH, "phase_f_collector_transform_facade_decision_entry_guard"]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary total guard missing facade decision entry connection: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "usage_audit_guard": _run_json_guard(USAGE_GUARD_PATH, failures),
        "spec": _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, failures),
        "state_decision_checkpoint": _check_fragments(STATE_PATH, REQUIRED_DECISION_CHECKPOINT_FRAGMENTS, failures),
        "focus_decision_checkpoint": _check_fragments(FOCUS_PATH, REQUIRED_DECISION_CHECKPOINT_FRAGMENTS, failures),
        "audit_output": _check_audit_output(failures),
        "no_facade_or_bridge_implementation_yet": _check_forbidden_paths(failures),
        "primary_connection": _check_primary_connection(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_phase_f_collector_transform_facade_decision_entry_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
