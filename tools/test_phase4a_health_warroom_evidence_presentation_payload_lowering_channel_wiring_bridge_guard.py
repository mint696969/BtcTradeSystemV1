# path: ./tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard.py
# desc: Phase 4-A Health/WarRoom evidence presentation payload lowering channel wiring bridge guard.

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

SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PRESENTATION_PAYLOAD_LOWERING_CHANNEL_WIRING_BRIDGE_IMPLEMENTATION_2026-05-31.md"
SELF_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_entry_criteria_guard.py"
LOWERING_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_guard.py"
BRIDGE_PATH = "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_lowering_bridge.py"
TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_evidence_presentation_lowering_bridge.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PAGE_LOCAL_IMPLEMENTATION_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PAYLOAD_LOWERING_PAGE_LOCAL_WIRING_IMPLEMENTATION_2026-05-31.md"

FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]

BRIDGE_NAMES = [
    "lower_health_snapshot_evidence_presentation_for_ui",
    "lower_warroom_session_state_evidence_presentation_for_ui",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_payload_lowering_wiring_bridge"
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


def _check_fragments(failures: list[str]) -> dict[str, Any]:
    required_by_file = {
        SPEC_PATH: [
            "lower_health_snapshot_evidence_presentation_for_ui",
            "lower_warroom_session_state_evidence_presentation_for_ui",
            "already-built evidence presentation payload",
            "Health page and WarRoom page are still not modified",
        ],
        BRIDGE_PATH: [
            "def lower_health_snapshot_evidence_presentation_for_ui",
            "def lower_warroom_session_state_evidence_presentation_for_ui",
            "lower_health_snapshot_evidence_presentation_fields",
            "lower_warroom_session_state_evidence_presentation_fields",
            "not_runtime_wiring",
            "not_market_engine_input",
            "not_collector_writer",
            "not_broker_or_order_automation",
            "not_inference_or_training",
        ],
        TEST_PATH: [
            "assert health_in ==",
            "assert warroom_in ==",
            "evidence_presentation_wiring_bridge",
            "not_runtime_wiring",
        ],
    }
    missing: list[dict[str, str]] = []
    for rel_path, fragments in required_by_file.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"missing required fragment: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing}


def _probe_bridge(failures: list[str]) -> dict[str, Any]:
    try:
        from btcts.apps.operator_ui.components.evidence_presentation_lowering_bridge import (
            lower_health_snapshot_evidence_presentation_for_ui,
            lower_warroom_session_state_evidence_presentation_for_ui,
        )
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_presentation_upstream import build_health_warroom_evidence_presentation_upstream_payload
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import build_real_data_validation_evidence_summary
        payload = build_health_warroom_evidence_presentation_upstream_payload(
            build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        )
        health_in = {"existing": "health"}
        warroom_in = {"existing": "warroom"}
        health_out = lower_health_snapshot_evidence_presentation_for_ui(health_in, payload)
        warroom_out = lower_warroom_session_state_evidence_presentation_for_ui(warroom_in, payload)
    except Exception as exc:
        failures.append(f"bridge probe failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": str(exc)}

    bad: list[str] = []
    if health_in != {"existing": "health"}:
        bad.append("health input mutated")
    if warroom_in != {"existing": "warroom"}:
        bad.append("warroom input mutated")
    if health_out.get("evidence_presentation_wiring_bridge") != "health_snapshot_ui_bridge":
        bad.append("health bridge marker mismatch")
    if warroom_out.get("evidence_presentation_wiring_bridge") != "warroom_session_state_ui_bridge":
        bad.append("warroom bridge marker mismatch")
    for out_name, out in (("health", health_out), ("warroom", warroom_out)):
        for key in ["not_runtime_wiring", "not_runtime_signal", "not_market_engine_input", "not_collector_writer", "not_broker_or_order_automation", "not_inference_or_training"]:
            if out.get(key) is not True:
                bad.append(f"{out_name} boundary false: {key}")
    for item in bad:
        failures.append(f"bridge probe failed: {item}")
    return {"ok": not bad, "bad": bad}


def _check_pages_still_not_call_bridge(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    warroom = _read(WARROOM_PAGE_PATH)
    page_local_open = (REPO_ROOT / PAGE_LOCAL_IMPLEMENTATION_SPEC_PATH).exists()
    health_hits = [] if page_local_open else [name for name in BRIDGE_NAMES if name in health]
    warroom_hits = [] if page_local_open else [name for name in BRIDGE_NAMES if name in warroom]
    for name in health_hits:
        failures.append(f"Health page must not call bridge in bridge-only slice: {name}")
    for name in warroom_hits:
        failures.append(f"WarRoom page must not call bridge in bridge-only slice: {name}")
    return {"health_hits": health_hits, "warroom_hits": warroom_hits}


def _scan_runtime_references(failures: list[str]) -> dict[str, Any]:
    hits: list[str] = []
    patterns = [*BRIDGE_NAMES, "evidence_presentation_lowering_bridge"]
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
                failures.append(f"runtime path references evidence presentation bridge: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_bridge": _compile(BRIDGE_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "lowering_guard": _run_json_guard(LOWERING_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "fragments": _check_fragments(failures),
        "bridge_probe": _probe_bridge(failures),
        "pages_still_not_call_bridge": _check_pages_still_not_call_bridge(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
