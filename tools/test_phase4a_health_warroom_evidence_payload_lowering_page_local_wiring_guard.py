# path: ./tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_guard.py
# desc: Phase 4-A Health/WarRoom evidence payload lowering page-local wiring implementation guard.

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

SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PAYLOAD_LOWERING_PAGE_LOCAL_WIRING_IMPLEMENTATION_2026-05-31.md"
SELF_PATH = "tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_entry_criteria_guard.py"
BRIDGE_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
HEALTH_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_evidence_presentation_wiring.py"
WARROOM_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_evidence_presentation_wiring.py"

BRIDGE_HELPERS = [
    "lower_health_snapshot_evidence_presentation_for_ui",
    "lower_warroom_session_state_evidence_presentation_for_ui",
]

FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_page_local_wiring_impl"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1200)
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


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Health / WarRoom evidence payload lowering page-local wiring implementation",
        "lower_health_snapshot_evidence_presentation_for_ui",
        "lower_warroom_session_state_evidence_presentation_for_ui",
        "does not make pages build evidence from source artifacts",
        "does not",
        "scan D/E",
        "add route wiring",
        "write runtime state",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _check_pages(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    warroom = _read(WARROOM_PAGE_PATH)
    required_health = [
        "from btcts.apps.operator_ui.components.evidence_presentation_lowering_bridge import",
        "lower_health_snapshot_evidence_presentation_for_ui",
        "lower_health_snapshot_evidence_presentation_for_ui(snapshot, payload)",
        "Return bridge-normalized evidence presentation payload from the Health snapshot only.",
        "render_evidence_presentation_panel(evidence_payload",
    ]
    required_warroom = [
        "from btcts.apps.operator_ui.components.evidence_presentation_lowering_bridge import",
        "lower_warroom_session_state_evidence_presentation_for_ui",
        "lower_warroom_session_state_evidence_presentation_for_ui(st.session_state, payload)",
        "Return bridge-normalized evidence presentation payload from session_state only.",
        "render_evidence_presentation_panel(evidence_payload",
    ]
    missing: list[dict[str, str]] = []
    for fragment in required_health:
        if fragment not in health:
            failures.append(f"Health page missing page-local bridge wiring fragment: {fragment}")
            missing.append({"path": HEALTH_PAGE_PATH, "fragment": fragment})
    for fragment in required_warroom:
        if fragment not in warroom:
            failures.append(f"WarRoom page missing page-local bridge wiring fragment: {fragment}")
            missing.append({"path": WARROOM_PAGE_PATH, "fragment": fragment})

    forbidden_health = [
        "build_real_data_validation_evidence_summary(",
        "D:" + "\\",
        "E:" + "\\",
        "market_engine_signal",
        "collector_write_path",
        "place" + "_" + "order(",
        "broker" + "_" + "order(",
        "training_dataset",
        "inference_job",
    ]
    forbidden_warroom = [*forbidden_health, "load_health_snapshot("]
    health_hits = [token for token in forbidden_health if token in health]
    warroom_hits = [token for token in forbidden_warroom if token in warroom]
    for token in health_hits:
        failures.append(f"Health page contains forbidden page-local wiring token: {token}")
    for token in warroom_hits:
        failures.append(f"WarRoom page contains forbidden page-local wiring token: {token}")
    return {"missing": missing, "health_forbidden_hits": health_hits, "warroom_forbidden_hits": warroom_hits}


def _scan_runtime_references(failures: list[str]) -> dict[str, Any]:
    hits: list[str] = []
    patterns = [*BRIDGE_HELPERS, "evidence_presentation_lowering_bridge"]
    for rel_root in FORBIDDEN_RUNTIME_ROOTS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if any(pattern in text for pattern in patterns):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(rel)
                failures.append(f"runtime path references page-local bridge wiring: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_health_page": _compile(HEALTH_PAGE_PATH, failures),
        "compile_warroom_page": _compile(WARROOM_PAGE_PATH, failures),
        "compile_health_test": _compile(HEALTH_TEST_PATH, failures),
        "compile_warroom_test": _compile(WARROOM_TEST_PATH, failures),
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "bridge_guard": _run_json_guard(BRIDGE_GUARD_PATH, failures),
        "health_plain_test": _run_plain_ok(HEALTH_TEST_PATH, failures),
        "warroom_plain_test": _run_plain_ok(WARROOM_TEST_PATH, failures),
        "spec": _check_spec(failures),
        "pages": _check_pages(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
