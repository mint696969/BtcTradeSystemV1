# path: ./tools/test_phase4a_phase_f_collector_transform_facade_migration_close_audit_guard.py
# desc: Phase 4-A Phase F collector transform facade migration close audit guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import ast
import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_phase_f_collector_transform_facade_migration_close_audit_guard.py"
FACADE_PATH = "btcts_next/src/btcts/collector_vnext/transforms/facade.py"
REST_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_rest_guard.py"
EMIT_WS_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_emit_ws_guard.py"
BOARD_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_unified_ws_board_guard.py"
EXECUTIONS_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_unified_ws_executions_guard.py"
POST_PHASEC_GUARD_PATH = "tools/test_phase4a_post_phasec_downstream_boundary_check.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_PHASE_F_COLLECTOR_TRANSFORM_FACADE_MIGRATION_CLOSE_AUDIT_2026-06-04.md"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

RUNTIME_CALLERS = {
    "btcts_next/src/btcts/collector_vnext/emit_rest.py": [
        "apply_board_structural_hints",
        "apply_trade_structural_hints",
        "canonical_board_snapshot",
        "canonical_trades",
    ],
    "btcts_next/src/btcts/collector_vnext/emit_ws.py": [
        "apply_board_structural_hints",
        "apply_trade_structural_hints",
        "canonical_board_event",
        "canonical_ws_trade",
    ],
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py": [
        "apply_board_structural_hints",
        "canonical_board_event",
    ],
    "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py": [
        "apply_trade_structural_hints",
        "canonical_ws_trade",
    ],
}

APPROVED_FACADE_EXPORTS = [
    "COLLECTOR_TRANSFORM_FACADE_VERSION",
    "BoardLevelsAdapter",
    "canonical_board_snapshot",
    "canonical_board_event",
    "canonical_trades",
    "canonical_ws_trade",
    "apply_board_structural_hints",
    "apply_trade_structural_hints",
]

APPROVED_RUNTIME_SYMBOLS = [
    "canonical_board_snapshot",
    "canonical_board_event",
    "canonical_trades",
    "canonical_ws_trade",
    "apply_board_structural_hints",
    "apply_trade_structural_hints",
]

FORBIDDEN_DIRECT_IMPORTS = [
    "from .transforms.board_structural_hints import apply_board_structural_hints",
    "from .transforms.trade_structural_hints import apply_trade_structural_hints",
    "from .transforms.raw_to_canonical import canonical_board_snapshot",
    "from .transforms.raw_to_canonical_trades import canonical_trades",
    "from .transforms.ws_board_to_canonical import canonical_board_event",
    "from .transforms.ws_trade_to_canonical import canonical_ws_trade",
]

FORBIDDEN_FACADE_FRAGMENTS = [
    "write_raw(",
    "write_canonical(",
    "connect_and_stream_",
    "fetch_board(",
    "fetch_executions(",
    "load_config(",
    "make_record(",
    "market_engine",
    "broker",
    "place_order",
]

REQUIRED_SPEC_FRAGMENTS = [
    "close audit / guard only",
    "all known collector runtime transform callers use the stable facade import surface",
    "The facade is a stable collector runtime adapter import surface only",
    "L2 canonical remains the owner of canonical payload builders and schema meaning",
    "all known runtime callers use transforms.facade",
    "no known runtime caller imports direct transform implementation modules",
    "collector capture behavior changes",
    "collector writer/backfill behavior changes",
    "canonical payload field changes",
]

COMPILE_TARGETS = [
    SELF_PATH,
    FACADE_PATH,
    *RUNTIME_CALLERS.keys(),
    REST_GUARD_PATH,
    EMIT_WS_GUARD_PATH,
    BOARD_GUARD_PATH,
    EXECUTIONS_GUARD_PATH,
    POST_PHASEC_GUARD_PATH,
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "phase_f_facade_migration_close_audit"
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


def _imported_names_from_facade(rel_path: str) -> list[str]:
    tree = ast.parse(_read(rel_path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "transforms.facade" and node.level == 1:
            names.extend(alias.name for alias in node.names)
    return sorted(names)


def _check_runtime_callers(failures: list[str]) -> dict[str, Any]:
    bad: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    for rel_path, expected_names in RUNTIME_CALLERS.items():
        text = _read(rel_path)
        imported = _imported_names_from_facade(rel_path)
        missing = [name for name in expected_names if name not in imported]
        direct_hits = [fragment for fragment in FORBIDDEN_DIRECT_IMPORTS if fragment in text]
        for name in missing:
            failures.append(f"runtime caller missing facade import: {rel_path}: {name}")
            bad.append({"path": rel_path, "missing_facade_import": name})
        for fragment in direct_hits:
            failures.append(f"runtime caller must not import direct transform implementation: {rel_path}: {fragment}")
            bad.append({"path": rel_path, "direct_import": fragment})
        details[rel_path] = {"expected": expected_names, "imported": imported, "missing": missing, "direct_hits": direct_hits}
    return {"bad_count": len(bad), "bad": bad, "details": details}


def _check_facade_contract(failures: list[str]) -> dict[str, Any]:
    text = _read(FACADE_PATH)
    tree = ast.parse(text)
    defined_functions = sorted(node.name for node in tree.body if isinstance(node, ast.FunctionDef))
    missing_functions = [name for name in APPROVED_RUNTIME_SYMBOLS if name not in defined_functions]
    extra_functions = [name for name in defined_functions if name not in APPROVED_RUNTIME_SYMBOLS]

    all_value: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__" and isinstance(node.value, ast.List):
                    all_value = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]
    missing_all = [name for name in APPROVED_FACADE_EXPORTS if name not in all_value]
    extra_all = [name for name in all_value if name not in APPROVED_FACADE_EXPORTS]
    forbidden_hits = [fragment for fragment in FORBIDDEN_FACADE_FRAGMENTS if fragment in text]

    for name in missing_functions:
        failures.append(f"facade missing approved function: {name}")
    for name in extra_functions:
        failures.append(f"facade has unapproved function export implementation: {name}")
    for name in missing_all:
        failures.append(f"facade __all__ missing export: {name}")
    for name in extra_all:
        failures.append(f"facade __all__ has unapproved export: {name}")
    for fragment in forbidden_hits:
        failures.append(f"facade must remain adapter import surface only; forbidden fragment: {fragment}")

    return {
        "defined_functions": defined_functions,
        "missing_functions": missing_functions,
        "extra_functions": extra_functions,
        "all": all_value,
        "missing_all": missing_all,
        "extra_all": extra_all,
        "forbidden_hits": forbidden_hits,
    }



def _check_spec_source(rel_path: str, marker: str, failures: list[str]) -> dict[str, Any]:
    text = _read(rel_path)
    missing = [] if marker in text else [marker]
    for fragment in missing:
        failures.append(f"historical migration guard source missing marker: {rel_path}: {fragment}")
    return {"missing": missing}

def _check_spec(failures: list[str]) -> dict[str, Any]:
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in REQUIRED_SPEC_FRAGMENTS if fragment not in text]
    for fragment in missing:
        failures.append(f"close audit spec missing fragment: {fragment}")
    return {"missing": missing}


def _check_primary_connection(failures: list[str]) -> dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [SELF_PATH, "phase_f_collector_transform_facade_migration_close_audit_guard"]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary total guard missing facade migration close audit connection: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "runtime_migration_guard_sources": {
            "rest": _check_spec_source(REST_GUARD_PATH, "phase4a_phase_f_collector_transform_runtime_import_migration_rest_guard", failures),
            "emit_ws": _check_spec_source(EMIT_WS_GUARD_PATH, "phase4a_phase_f_collector_transform_runtime_import_migration_emit_ws_guard", failures),
            "unified_ws_board": _check_spec_source(BOARD_GUARD_PATH, "phase4a_phase_f_collector_transform_runtime_import_migration_unified_ws_board_guard", failures),
            "unified_ws_executions": _check_spec_source(EXECUTIONS_GUARD_PATH, "phase4a_phase_f_collector_transform_runtime_import_migration_unified_ws_executions_guard", failures),
        },
        "post_phasec_downstream_boundary": _run_json_guard(POST_PHASEC_GUARD_PATH, failures),
        "runtime_callers": _check_runtime_callers(failures),
        "facade_contract": _check_facade_contract(failures),
        "spec": _check_spec(failures),
        "primary_connection": _check_primary_connection(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_phase_f_collector_transform_facade_migration_close_audit_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
