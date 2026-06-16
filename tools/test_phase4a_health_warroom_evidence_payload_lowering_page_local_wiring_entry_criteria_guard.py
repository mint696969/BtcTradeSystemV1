# path: ./tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_entry_criteria_guard.py
# desc: Phase 4-A Health/WarRoom evidence payload lowering page-local wiring entry criteria guard.

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

SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PAYLOAD_LOWERING_PAGE_LOCAL_WIRING_ENTRY_CRITERIA_2026-05-31.md"
SELF_PATH = "tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_entry_criteria_guard.py"
BRIDGE_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard.py"
BRIDGE_PATH = "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_lowering_bridge.py"
IMPLEMENTATION_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PAYLOAD_LOWERING_PAGE_LOCAL_WIRING_IMPLEMENTATION_2026-05-31.md"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"

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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_page_local_wiring_entry"
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
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Health / WarRoom evidence payload lowering page-local wiring entry criteria",
        "entry criteria only",
        "lower_health_snapshot_evidence_presentation_for_ui",
        "lower_warroom_session_state_evidence_presentation_for_ui",
        "accept already-built evidence presentation payloads only",
        "Do not add Health page bridge calls yet.",
        "Do not add WarRoom page bridge calls yet.",
        "Do not add route wiring.",
        "Do not add runtime state writer behavior.",
        "Do not scan D/E.",
        "Do not call market_engine.",
        "Do not call broker/order/execution.",
        "Do not feed inference/training.",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _check_bridge(failures: list[str]) -> dict[str, Any]:
    text = _read(BRIDGE_PATH)
    missing = [name for name in BRIDGE_HELPERS if f"def {name}" not in text]
    for name in missing:
        failures.append(f"bridge helper missing: {name}")
    for fragment in [
        "already-built evidence payload fields",
        "not_runtime_wiring",
        "not_runtime_signal",
        "not_market_engine_input",
        "not_collector_writer",
        "not_broker_or_order_automation",
        "not_inference_or_training",
    ]:
        if fragment not in text:
            failures.append(f"bridge missing boundary fragment: {fragment}")
    return {"missing_helpers": missing}


def _check_pages_still_pre_entry(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    warroom = _read(WARROOM_PAGE_PATH)
    implementation_open = (REPO_ROOT / IMPLEMENTATION_SPEC_PATH).exists()
    health_hits = [] if implementation_open else [name for name in BRIDGE_HELPERS if name in health]
    warroom_hits = [] if implementation_open else [name for name in BRIDGE_HELPERS if name in warroom]
    for name in health_hits:
        failures.append(f"Health page must not call bridge in entry slice: {name}")
    for name in warroom_hits:
        failures.append(f"WarRoom page must not call bridge in entry slice: {name}")

    required_health = [
        "def _snapshot_evidence_presentation_payload",
        "render_evidence_presentation_panel(evidence_payload",
    ]
    required_warroom = [
        "def _warroom_evidence_presentation_payload",
        "render_evidence_presentation_panel(evidence_payload",
    ]
    if implementation_open:
        required_health.append("Return bridge-normalized evidence presentation payload from the Health snapshot only.")
        required_warroom.append("Return bridge-normalized evidence presentation payload from session_state only.")
    else:
        required_health.append("Return already-provided evidence presentation payload from the Health snapshot only.")
        required_warroom.append("Return an already-provided evidence presentation payload from session_state only.")
    for fragment in required_health:
        if fragment not in health:
            failures.append(f"Health page missing pre-entry payload-consumption fragment: {fragment}")
    for fragment in required_warroom:
        if fragment not in warroom:
            failures.append(f"WarRoom page missing pre-entry payload-consumption fragment: {fragment}")

    forbidden_tokens = [
        "build_real_data_validation_evidence_summary(",
        "load_health_snapshot(",
        "D:" + "\\",
        "E:" + "\\",
        "market_engine_signal",
        "collector_write_path",
        "place" + "_" + "order(",
        "broker" + "_" + "order(",
        "training_dataset",
        "inference_job",
    ]
    health_forbidden_hits = [token for token in forbidden_tokens if token in health]
    warroom_forbidden_hits = [token for token in forbidden_tokens if token in warroom]
    # Health page may import/use load_health_snapshot as the existing page data source.
    health_forbidden_hits = [x for x in health_forbidden_hits if x != "load_health_snapshot("]
    for token in health_forbidden_hits:
        failures.append(f"Health page contains forbidden page-local wiring token: {token}")
    for token in warroom_forbidden_hits:
        failures.append(f"WarRoom page contains forbidden page-local wiring token: {token}")

    return {
        "health_bridge_hits": health_hits,
        "warroom_bridge_hits": warroom_hits,
        "health_forbidden_hits": health_forbidden_hits,
        "warroom_forbidden_hits": warroom_forbidden_hits,
    }


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
                failures.append(f"runtime path references page-local wiring bridge: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_bridge": _compile(BRIDGE_PATH, failures),
        "bridge_guard": _run_json_guard(BRIDGE_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "bridge": _check_bridge(failures),
        "pages_still_pre_entry": _check_pages_still_pre_entry(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_entry_criteria_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
