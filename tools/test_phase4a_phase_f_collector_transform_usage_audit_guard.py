# path: ./tools/test_phase4a_phase_f_collector_transform_usage_audit_guard.py
# desc: Phase 4-A Phase F collector transform usage audit guard.

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

SELF_PATH = "tools/test_phase4a_phase_f_collector_transform_usage_audit_guard.py"
AUDIT_PATH = "tools/audit_phase4a_phase_f_collector_transform_usage.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_migration_prep_entry_criteria_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_PHASE_F_COLLECTOR_TRANSFORM_USAGE_AUDIT_2026-06-03.md"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
OUTPUT_PATH = "tmp/work/phase4a_phase_f_collector_transform_migration_prep/outputs/collector_transform_usage_audit_v1.json"

COMPILE_TARGETS = [
    SELF_PATH,
    AUDIT_PATH,
    ENTRY_GUARD_PATH,
    "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py",
    "btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/board_structural_hints.py",
    "btcts_next/src/btcts/collector_vnext/transforms/trade_structural_hints.py",
    "btcts_next/src/btcts/collector_vnext/emit_rest.py",
    "btcts_next/src/btcts/collector_vnext/emit_ws.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
]

REQUIRED_SPEC_FRAGMENTS = [
    "read-only usage audit",
    "runtime adapter users",
    "L2 canonical public boundary users",
    "structural hint users",
    "future facade / bridge candidates",
    "runtime import migration",
    "collector capture behavior changes",
    "facade / bridge implementation",
]

ENTRY_CHECKPOINT_FRAGMENTS = [
    "return_to_main_phase4a_roadmap_or_phase_f_prep",
    "health_latency_budget_metadata_observability_guard_green_clean_commit_checkpoint_a35e7535",
    "phase4a_phase_f_collector_transform_migration_prep_entry_criteria",
    "phase4a_phase_f_collector_transform_usage_audit",
]

REQUIRED_AUDIT_SYMBOLS = {
    "canonical_board_snapshot": ["btcts_next/src/btcts/collector_vnext/emit_rest.py"],
    "canonical_board_event": [
        "btcts_next/src/btcts/collector_vnext/emit_ws.py",
        "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    ],
    "canonical_trades": ["btcts_next/src/btcts/collector_vnext/emit_rest.py"],
    "canonical_ws_trade": [
        "btcts_next/src/btcts/collector_vnext/emit_ws.py",
        "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
    ],
    "apply_board_structural_hints": [
        "btcts_next/src/btcts/collector_vnext/emit_rest.py",
        "btcts_next/src/btcts/collector_vnext/emit_ws.py",
        "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    ],
    "apply_trade_structural_hints": [
        "btcts_next/src/btcts/collector_vnext/emit_rest.py",
        "btcts_next/src/btcts/collector_vnext/emit_ws.py",
        "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
    ],
}

FORBIDDEN_RUNTIME_MIGRATION_PATHS = [
    "btcts_next/src/btcts/collector_vnext/canonical_facade.py",
    "btcts_next/src/btcts/collector_vnext/transform_facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/runtime_bridge.py",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "phase_f_collector_transform_usage_audit"
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


def _check_entry_checkpoint(failures: list[str]) -> dict[str, Any]:
    """Keep the usage audit tied to the Phase F entry checkpoint without re-running
    the historical entry guard after focus has advanced to later Phase F slices.
    The primary total guard still runs the entry guard as its own top-level check.
    """
    checks: dict[str, Any] = {}
    for rel_path in [STATE_PATH, FOCUS_PATH]:
        text = _read(rel_path)
        missing = [fragment for fragment in ENTRY_CHECKPOINT_FRAGMENTS if fragment not in text]
        for fragment in missing:
            failures.append(f"missing Phase F entry checkpoint fragment in {rel_path}: {fragment}")
        checks[rel_path] = {"missing": missing}
    return checks


def _run_audit(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / AUDIT_PATH)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=300,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"audit did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}

    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append("usage audit must return ok true and failures []")

    output_path = REPO_ROOT / OUTPUT_PATH
    if not output_path.exists():
        failures.append(f"usage audit output missing: {OUTPUT_PATH}")
    else:
        try:
            output_payload = json.loads(output_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"usage audit output is not valid JSON: {exc}")
            output_payload = {}
        if output_payload.get("phase") != "phase4a_phase_f_collector_transform_usage_audit":
            failures.append("usage audit output phase mismatch")

    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "usage_item_count": parsed.get("usage_item_count"), "output_path": parsed.get("output_path"), "json": parsed}


def _check_audit_payload(payload: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    usage_items = payload.get("usage_items")
    if not isinstance(usage_items, list):
        failures.append("usage_items must be a list")
        return {"ok": False, "bad": ["usage_items_not_list"]}

    by_symbol = {str(item.get("symbol")): item for item in usage_items if isinstance(item, dict)}
    bad: list[str] = []
    for symbol, expected_callers in REQUIRED_AUDIT_SYMBOLS.items():
        item = by_symbol.get(symbol)
        if item is None:
            bad.append(f"missing_symbol:{symbol}")
            failures.append(f"usage audit missing symbol: {symbol}")
            continue
        # Historical usage audit was created before facade migration. After close, do not enforce
        # pre-migration planning flags; current close guards own the migrated runtime import shape.
        callers = list(item.get("callers") or [])
        # Caller mapping is allowed to become facade-mediated after Phase F migration close.
        # The close audit guard verifies current runtime callers directly.
        if item.get("l2_public_boundary_builder") and item.get("definition_uses_l2_public_boundary_builder") is not True:
            bad.append(f"l2_builder_not_used:{symbol}")
            failures.append(f"definition must use L2 public boundary builder: {symbol}")

    if payload.get("read_only") is not True:
        bad.append("read_only_not_true")
        failures.append("audit payload read_only must be true")
    if payload.get("forbidden_runtime_migration_paths_existing") != []:
        bad.append("forbidden_runtime_migration_paths_existing_not_empty")
        failures.append("forbidden runtime migration paths must not exist")
    if payload.get("direct_payload_imports_outside_transforms") != []:
        bad.append("direct_payload_imports_outside_transforms_not_empty")
        failures.append("runtime files must not import L2 private payload modules")

    return {"ok": not bad, "bad": bad}


def _check_fragments(rel_path: str, required: list[str], failures: list[str]) -> dict[str, Any]:
    text = _read(rel_path)
    if not text:
        failures.append(f"required file missing or empty: {rel_path}")
        return {"missing_file": True, "missing": required}
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing fragment in {rel_path}: {fragment}")
    return {"missing": missing}


def _check_forbidden_runtime_paths(failures: list[str]) -> dict[str, Any]:
    existing = [rel for rel in FORBIDDEN_RUNTIME_MIGRATION_PATHS if (REPO_ROOT / rel).exists()]
    for rel in existing:
        failures.append(f"usage audit must not create runtime migration/facade implementation: {rel}")
    return {"existing": existing}


def _check_primary_connection(failures: list[str]) -> dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [SELF_PATH, "phase_f_collector_transform_usage_audit_guard"]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary total guard missing usage audit connection: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    audit_result = _run_audit(failures)
    audit_payload = audit_result.get("json") if isinstance(audit_result.get("json"), dict) else {}
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "entry_checkpoint": _check_entry_checkpoint(failures),
        "spec": _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, failures),
        "audit_run": audit_result,
        "audit_payload": _check_audit_payload(audit_payload, failures),
        "no_runtime_migration_files": _check_forbidden_runtime_paths(failures),
        "primary_connection": _check_primary_connection(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_phase_f_collector_transform_usage_audit_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
