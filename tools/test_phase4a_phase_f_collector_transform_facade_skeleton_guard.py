# path: ./tools/test_phase4a_phase_f_collector_transform_facade_skeleton_guard.py
# desc: Phase 4-A Phase F collector transform facade skeleton guard.

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

SELF_PATH = "tools/test_phase4a_phase_f_collector_transform_facade_skeleton_guard.py"
FACADE_PATH = "btcts_next/src/btcts/collector_vnext/transforms/facade.py"
FACADE_TEST_PATH = "btcts_next/src/btcts/collector_vnext/transforms/test_facade.py"
USAGE_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_usage_audit_guard.py"
DECISION_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_facade_decision_entry_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_PHASE_F_COLLECTOR_TRANSFORM_FACADE_SKELETON_2026-06-03.md"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    SELF_PATH,
    FACADE_PATH,
    FACADE_TEST_PATH,
    USAGE_GUARD_PATH,
    DECISION_GUARD_PATH,
]

REQUIRED_FACADE_FRAGMENTS = [
    'COLLECTOR_TRANSFORM_FACADE_VERSION = "collector_transform_facade.v1"',
    "from btcts.collector_vnext.transforms.raw_to_canonical import (",
    "from btcts.collector_vnext.transforms.ws_board_to_canonical import (",
    "from btcts.collector_vnext.transforms.raw_to_canonical_trades import (",
    "from btcts.collector_vnext.transforms.ws_trade_to_canonical import (",
    "from btcts.collector_vnext.transforms.board_structural_hints import (",
    "from btcts.collector_vnext.transforms.trade_structural_hints import (",
    "def canonical_board_snapshot(",
    "def canonical_board_event(",
    "def canonical_trades(",
    "def canonical_ws_trade(",
    "def apply_board_structural_hints(",
    "def apply_trade_structural_hints(",
    "__all__ = [",
]

FORBIDDEN_FACADE_FRAGMENTS = [
    "make_orderbook_snapshot_payload",
    "make_orderbook_event_payload",
    "make_trade_event_payload",
    "open(",
    "Path(",
    "os.",
    "subprocess",
    "requests",
    "websocket",
    "place_order",
    "market_engine",
]

REQUIRED_TEST_FRAGMENTS = [
    "_assert_facade_contract",
    "_assert_board_snapshot_delegation",
    "_assert_board_event_delegation",
    "_assert_trade_delegation",
    "_assert_structural_hint_delegation",
    'print("ok")',
]

REQUIRED_SPEC_FRAGMENTS = [
    "facade skeleton only",
    "stable collector runtime adapter import surface only",
    "re-export/delegate the existing six transform/hint functions",
    "runtime import migration",
    "collector capture behavior changes",
    "collector writer/backfill changes",
    "canonical payload field changes",
]

FORBIDDEN_RUNTIME_MIGRATION_PATHS = [
    "btcts_next/src/btcts/collector_vnext/canonical_facade.py",
    "btcts_next/src/btcts/collector_vnext/transform_facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/runtime_bridge.py",
]

RUNTIME_FILES = [
    "btcts_next/src/btcts/collector_vnext/emit_rest.py",
    "btcts_next/src/btcts/collector_vnext/emit_ws.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
]

FORBIDDEN_RUNTIME_IMPORT = "btcts.collector_vnext.transforms.facade"


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "phase_f_collector_transform_facade_skeleton"
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


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    ok = proc.returncode == 0 and proc.stdout.strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_fragments(rel_path: str, required: list[str], forbidden: list[str], failures: list[str]) -> dict[str, Any]:
    text = _read(rel_path)
    if not text:
        failures.append(f"required file missing or empty: {rel_path}")
        return {"missing_file": True, "missing": required, "forbidden_hits": []}
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [fragment for fragment in forbidden if fragment in text]
    for fragment in missing:
        failures.append(f"missing fragment in {rel_path}: {fragment}")
    for fragment in forbidden_hits:
        failures.append(f"forbidden fragment in {rel_path}: {fragment}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_no_runtime_import_migration(failures: list[str]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for rel_path in RUNTIME_FILES:
        text = _read(rel_path)
        if FORBIDDEN_RUNTIME_IMPORT in text:
            hits.append({"path": rel_path, "fragment": FORBIDDEN_RUNTIME_IMPORT})
    for hit in hits:
        failures.append(f"runtime import migration is not allowed in facade skeleton: {hit['path']}")
    return {"hit_count": len(hits), "hits": hits}


def _check_forbidden_paths(failures: list[str]) -> dict[str, Any]:
    existing = [rel for rel in FORBIDDEN_RUNTIME_MIGRATION_PATHS if (REPO_ROOT / rel).exists()]
    for rel in existing:
        failures.append(f"facade skeleton must not create extra migration/bridge path: {rel}")
    return {"existing": existing}


def _check_primary_connection(failures: list[str]) -> dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [SELF_PATH, "phase_f_collector_transform_facade_skeleton_guard"]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary total guard missing facade skeleton connection: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "usage_audit_source_present": _check_fragments(USAGE_GUARD_PATH, ["phase4a_phase_f_collector_transform_usage_audit_guard"], [], failures),
        "decision_entry_source_present": _check_fragments(DECISION_GUARD_PATH, ["phase4a_phase_f_collector_transform_facade_decision_entry_guard"], [], failures),
        "facade_source": _check_fragments(FACADE_PATH, REQUIRED_FACADE_FRAGMENTS, FORBIDDEN_FACADE_FRAGMENTS, failures),
        "facade_test_source": _check_fragments(FACADE_TEST_PATH, REQUIRED_TEST_FRAGMENTS, [], failures),
        "facade_plain_test": _run_plain_ok(FACADE_TEST_PATH, failures),
        "spec": _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, [], failures),
        "runtime_import_migration_historical_boundary": {"closed_at_skeleton_slice": True},
        "no_extra_facade_or_bridge_paths": _check_forbidden_paths(failures),
        "primary_connection": _check_primary_connection(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_phase_f_collector_transform_facade_skeleton_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
