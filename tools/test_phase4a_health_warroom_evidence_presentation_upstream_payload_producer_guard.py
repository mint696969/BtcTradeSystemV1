# path: ./tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py
# desc: Phase 4-A Health/WarRoom evidence presentation upstream payload producer implementation guard.

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
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PRESENTATION_UPSTREAM_PAYLOAD_PRODUCER_IMPLEMENTATION_2026-05-30.md"
ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard.py"
MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_presentation_upstream.py"
INIT_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/__init__.py"
TEST_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence_presentation_upstream.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]
UPSTREAM_PATTERNS = [
    "real_data_validation_evidence_presentation_upstream",
    "build_health_warroom_evidence_presentation_upstream_payload",
    "lower_health_warroom_evidence_presentation_payload",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_upstream_payload_producer"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace('/', '__') + '.pyc')), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1200)
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
            "upstream payload producer module only",
            "real_data_validation_evidence_presentation_upstream.py",
            "lower_health_warroom_evidence_presentation_payload",
            "no D/E path read",
            "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py",
        ],
        MODULE_PATH: [
            "def build_health_warroom_evidence_presentation_upstream_payload",
            "def health_snapshot_evidence_presentation_payload_fields",
            "def warroom_session_state_evidence_presentation_payload_fields",
            "def lower_health_warroom_evidence_presentation_payload",
            "not_runtime_wiring",
            "not_collector_writer",
        ],
        INIT_PATH: [
            "build_health_warroom_evidence_presentation_upstream_payload",
            "lower_health_warroom_evidence_presentation_payload",
        ],
        PRIMARY_GUARD_PATH: [
            "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py",
            "health_warroom_evidence_presentation_upstream_payload_producer_guard",
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


def _probe_payload_lowering(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_presentation_upstream import (
            lower_health_warroom_evidence_presentation_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import build_real_data_validation_evidence_summary
        lowered = lower_health_warroom_evidence_presentation_payload(
            build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        )
    except Exception as exc:
        failures.append(f"payload producer probe failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": str(exc)}
    payload = dict(lowered.get("payload") or {})
    boundary = dict(lowered.get("boundary") or {})
    health_fields = dict(lowered.get("health_snapshot_fields") or {})
    warroom_fields = dict(lowered.get("warroom_session_state_fields") or {})
    required_health = {"evidence_presentation_payload", "health_warroom_evidence_presentation_payload", "real_data_validation_evidence_presentation"}
    required_warroom = {"warroom_evidence_presentation_payload", "health_warroom_evidence_presentation_payload", "real_data_validation_evidence_presentation", "evidence_presentation_payload"}
    bad: list[str] = []
    if set(health_fields) != required_health:
        bad.append("health field keys mismatch")
    if set(warroom_fields) != required_warroom:
        bad.append("warroom field keys mismatch")
    for key in ["read_only_consumption", "diagnostic_evidence_only", "operator_support_only", "not_runtime_signal", "not_runtime_wiring", "not_market_engine_input", "not_collector_writer", "not_broker_or_order_automation", "not_inference_or_training"]:
        if boundary.get(key) is not True:
            bad.append(f"boundary not true: {key}")
    if payload.get("status_key") != "available":
        bad.append("payload status_key mismatch")
    for item in bad:
        failures.append(f"payload lowering probe failed: {item}")
    return {"ok": not bad, "bad": bad, "health_keys": sorted(health_fields), "warroom_keys": sorted(warroom_fields)}


def _check_consumers_unchanged(failures: List[str]) -> Dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    warroom = _read(WARROOM_PAGE_PATH)
    forbidden = [
        "build_health_warroom_evidence_presentation_upstream_payload",
        "lower_health_warroom_evidence_presentation_payload",
        "real_data_validation_evidence_presentation_upstream",
    ]
    health_hits = [token for token in forbidden if token in health]
    warroom_hits = [token for token in forbidden if token in warroom]
    for token in health_hits:
        failures.append(f"Health page must not call upstream producer in this slice: {token}")
    for token in warroom_hits:
        failures.append(f"WarRoom page must not call upstream producer in this slice: {token}")
    return {"health_hits": health_hits, "warroom_hits": warroom_hits}


def _scan_runtime_references(failures: List[str]) -> Dict[str, Any]:
    hits: list[str] = []
    for rel_root in FORBIDDEN_RUNTIME_ROOTS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if any(pattern in text for pattern in UPSTREAM_PATTERNS):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(rel)
                failures.append(f"runtime path references upstream payload producer: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_module": _compile(MODULE_PATH, failures),
        "compile_init": _compile(INIT_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "compile_self": _compile("tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py", failures),
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "docs": _check_docs(failures),
        "payload_lowering_probe": _probe_payload_lowering(failures),
        "consumers_unchanged": _check_consumers_unchanged(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
