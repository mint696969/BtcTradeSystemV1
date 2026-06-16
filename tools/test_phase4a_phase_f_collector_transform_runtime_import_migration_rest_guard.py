# path: ./tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_rest_guard.py
# desc: Phase 4-A Phase F REST runtime import migration guard.

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

SELF_PATH = "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_rest_guard.py"
EMIT_REST_PATH = "btcts_next/src/btcts/collector_vnext/emit_rest.py"
FACADE_PATH = "btcts_next/src/btcts/collector_vnext/transforms/facade.py"
FACADE_SKELETON_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_facade_skeleton_guard.py"
USAGE_GUARD_PATH = "tools/test_phase4a_phase_f_collector_transform_usage_audit_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_PHASE_F_COLLECTOR_TRANSFORM_RUNTIME_IMPORT_MIGRATION_REST_2026-06-03.md"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    SELF_PATH,
    EMIT_REST_PATH,
    FACADE_PATH,
    FACADE_SKELETON_GUARD_PATH,
    USAGE_GUARD_PATH,
]

REQUIRED_EMIT_REST_FRAGMENTS = [
    "from .transforms.facade import (",
    "apply_board_structural_hints,",
    "apply_trade_structural_hints,",
    "canonical_board_snapshot,",
    "canonical_trades,",
    "board_payload = canonical_board_snapshot(",
    "apply_board_structural_hints(",
    "trades = canonical_trades(source_payload)",
    "apply_trade_structural_hints(",
    "write_raw(",
    "write_canonical(",
]

FORBIDDEN_EMIT_REST_FRAGMENTS = [
    "from .transforms.board_structural_hints import apply_board_structural_hints",
    "from .transforms.raw_to_canonical import canonical_board_snapshot",
    "from .transforms.raw_to_canonical_trades import canonical_trades",
    "from .transforms.trade_structural_hints import apply_trade_structural_hints",
    "from .transforms.ws_board_to_canonical",
    "from .transforms.ws_trade_to_canonical",
]

FORBIDDEN_UNIFIED_FACADE_IMPORT = "from .transforms.facade import"
UNIFIED_RUNTIME_FILES = [
]

REQUIRED_SPEC_FRAGMENTS = [
    "REST runtime import migration only",
    "replace direct transform imports in emit_rest.py with imports from transforms.facade",
    "keep all existing call sites and arguments unchanged",
    "WS lane runtime import migration",
    "collector capture behavior changes",
    "collector writer/backfill behavior changes",
    "canonical payload field changes",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "phase_f_rest_runtime_import_migration"
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


def _check_unified_lanes_not_migrated(failures: list[str]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for rel_path in UNIFIED_RUNTIME_FILES:
        if FORBIDDEN_UNIFIED_FACADE_IMPORT in _read(rel_path):
            hits.append({"path": rel_path, "fragment": FORBIDDEN_UNIFIED_FACADE_IMPORT})
    for hit in hits:
        failures.append(f"unified WS lane runtime import migration is not allowed in REST slice: {hit['path']}")
    return {"hit_count": len(hits), "hits": hits}


def _check_primary_connection(failures: list[str]) -> dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [SELF_PATH, "phase_f_collector_transform_runtime_import_migration_rest_guard"]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary total guard missing REST migration connection: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "facade_skeleton_source_present": _check_fragments(FACADE_PATH, ["COLLECTOR_TRANSFORM_FACADE_VERSION", "__all__ = ["], [], failures),
        "emit_rest_import_shape": _check_fragments(EMIT_REST_PATH, REQUIRED_EMIT_REST_FRAGMENTS, FORBIDDEN_EMIT_REST_FRAGMENTS, failures),
        "spec": _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, [], failures),
        "unified_lanes_not_migrated": _check_unified_lanes_not_migrated(failures),
        "primary_connection": _check_primary_connection(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_phase_f_collector_transform_runtime_import_migration_rest_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
