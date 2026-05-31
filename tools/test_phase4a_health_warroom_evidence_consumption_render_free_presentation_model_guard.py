# path: ./tools/test_phase4a_health_warroom_evidence_consumption_render_free_presentation_model_guard.py
# desc: Phase 4-A Health/WarRoom evidence consumption render-free presentation model guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_RENDER_FREE_PRESENTATION_MODEL_2026-05-29.md"
ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_consumption_presentation_entry_criteria_guard.py"
MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py"
TEST_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence_consumption.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
FORBIDDEN_PATHS = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "error": "missing"}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_render_free_presentation"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace('/', '__') + '.pyc')), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=300)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}


def _run_plain_ok(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        SPEC_PATH: [
            "render-free presentation model only",
            "HealthWarRoomEvidencePresentationModel",
            "health_warroom_evidence_presentation_model",
            "health_warroom_evidence_presentation_payload",
            "not_ui_rendering = true",
        ],
        MODULE_PATH: [
            "class HealthWarRoomEvidencePresentationModel",
            "def health_warroom_evidence_presentation_model",
            "def health_warroom_evidence_presentation_payload",
            "not_ui_rendering",
        ],
        PRIMARY_GUARD_PATH: [
            "tools/test_phase4a_health_warroom_evidence_consumption_render_free_presentation_model_guard.py",
            "health_warroom_evidence_consumption_render_free_presentation_model_guard",
        ],
    }
    missing: list[dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"missing required fragment: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing}


def _probe_presentation(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
            health_warroom_evidence_presentation_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import build_real_data_validation_evidence_summary
        payload = health_warroom_evidence_presentation_payload(
            build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        )
    except Exception as exc:
        failures.append(f"presentation payload probe failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": str(exc)}
    boundary = dict(payload.get("boundary") or {})
    required_true = [
        "read_only_consumption",
        "diagnostic_evidence_only",
        "operator_support_only",
        "not_runtime_signal",
        "not_runtime_wiring",
        "not_ui_rendering",
        "not_market_engine_input",
        "not_collector_writer",
        "not_broker_or_order_automation",
        "not_inference_or_training",
    ]
    bad = [key for key in required_true if boundary.get(key) is not True]
    for key in bad:
        failures.append(f"presentation boundary flag not true: {key}")
    if payload.get("presentation_kind") != "health_warroom_evidence_consumption_presentation":
        failures.append("presentation_kind mismatch")
    if payload.get("status_key") not in {"available", "available_with_notes", "missing", "unknown"}:
        failures.append("status_key unexpected")
    return {"ok": not bad, "presentation_kind": payload.get("presentation_kind"), "status_key": payload.get("status_key"), "bad": bad}


def _scan_forbidden_paths(failures: List[str]) -> Dict[str, Any]:
    patterns = ["HealthWarRoomEvidencePresentationModel", "health_warroom_evidence_presentation_payload", "health_warroom_evidence_presentation_model"]
    approved = {
        "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_panel.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_evidence_presentation_panel.py",
        "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_evidence_presentation_wiring.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_evidence_presentation_wiring.py",
    }
    hits: list[str] = []
    for rel_root in FORBIDDEN_PATHS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in approved:
                continue
            if any(pattern in text for pattern in patterns):
                hits.append(rel)
                failures.append(f"forbidden runtime/UI path references render-free presentation model: {rel}")
    return {"hit_count": len(hits), "hits": hits, "approved_count": len(approved)}


def _check_module_forbidden(failures: List[str]) -> Dict[str, Any]:
    text = _read(MODULE_PATH)
    forbidden = ["import streamlit", "from streamlit", " st.", "\nst.", "place_order(", ".place_order", "broker_order(", "D:\\", "E:\\"]
    hits = [fragment for fragment in forbidden if fragment in text]
    for fragment in hits:
        failures.append(f"module contains forbidden render/runtime/path fragment: {fragment}")
    return {"hits": hits}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_module": _compile(MODULE_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "compile_self": _compile("tools/test_phase4a_health_warroom_evidence_consumption_render_free_presentation_model_guard.py", failures),
        "presentation_entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "docs": _check_docs(failures),
        "presentation_probe": _probe_presentation(failures),
        "module_forbidden": _check_module_forbidden(failures),
        "forbidden_path_scan": _scan_forbidden_paths(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_consumption_render_free_presentation_model_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
