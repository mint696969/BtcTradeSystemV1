# path: ./tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard.py
# desc: Phase 4-A Health/WarRoom evidence presentation upstream payload production entry criteria guard.

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
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PRESENTATION_UPSTREAM_PAYLOAD_PRODUCTION_ENTRY_CRITERIA_2026-05-30.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
WARROOM_WIRING_GUARD_PATH = "tools/test_phase4a_warroom_evidence_presentation_page_wiring_guard.py"
UPSTREAM_ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
PRESENTATION_MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py"
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_upstream_payload_entry"
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


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        SPEC_PATH: [
            "upstream payload production entry criteria / guard only",
            "real_data_validation_evidence_presentation_upstream.py",
            "no filesystem scan",
            "no D/E path read",
            "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard.py",
        ],
        INDEX_PATH: [
            "PHASE4A_HEALTH_WARROOM_EVIDENCE_PRESENTATION_UPSTREAM_PAYLOAD_PRODUCTION_ENTRY_CRITERIA_2026-05-30.md",
            "raw D/E scanner",
        ],
        STATE_PATH: [
            "warroom_evidence_presentation_page_wiring_closed_primary_guard_green",
            "health_warroom_evidence_presentation_upstream_payload_production_entry_criteria",
        "health_warroom_evidence_presentation_upstream_payload_producer",
            "runtime state writer",
            "market_engine integration",
            "collector writer/backfill",
            "broker/order/execution",
            "inference/training",
            "raw D/E scanner",
        ],
        PRESENTATION_MODULE_PATH: [
            "def health_warroom_evidence_presentation_payload",
            "not_runtime_signal",
            "not_collector_writer",
            "not_inference_or_training",
        ],
        HEALTH_PAGE_PATH: [
            "def _snapshot_evidence_presentation_payload",
            "render_evidence_presentation_panel(evidence_payload",
        ],
        WARROOM_PAGE_PATH: [
            "def _warroom_evidence_presentation_payload",
            "render_evidence_presentation_panel(evidence_payload",
        ],
        PRIMARY_GUARD_PATH: [
            UPSTREAM_ENTRY_GUARD_PATH,
            "health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard",
        ],
    }
    missing: list[dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read(rel_path)
        if not text:
            failures.append(f"required file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"missing required fragment: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing}


def _probe_existing_payload_builder(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
            health_warroom_evidence_presentation_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import build_real_data_validation_evidence_summary
        payload = health_warroom_evidence_presentation_payload(
            build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        )
    except Exception as exc:
        failures.append(f"existing payload builder probe failed: {type(exc).__name__}: {exc}")
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
        failures.append(f"existing payload boundary flag not true: {key}")
    if payload.get("presentation_kind") != "health_warroom_evidence_consumption_presentation":
        failures.append("presentation_kind mismatch")
    return {"ok": not bad, "presentation_kind": payload.get("presentation_kind"), "status_key": payload.get("status_key"), "bad": bad}


def _check_consumers_are_already_provided_only(failures: List[str]) -> Dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    warroom = _read(WARROOM_PAGE_PATH)
    forbidden_health = [
        "health_warroom_evidence_presentation_payload(",
        "health_warroom_evidence_presentation_model(",
        "build_real_data_validation_evidence_summary(",
        "D:" + "\\",
        "E:" + "\\",
    ]
    forbidden_warroom = [
        *forbidden_health,
        "load_health_snapshot",
    ]
    health_hits = [token for token in forbidden_health if token in health]
    warroom_hits = [token for token in forbidden_warroom if token in warroom]
    for token in health_hits:
        failures.append(f"Health page must consume already-provided payload only: {token}")
    for token in warroom_hits:
        failures.append(f"WarRoom page must consume already-provided payload only: {token}")
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
                failures.append(f"runtime path references upstream payload production: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_self": _compile(UPSTREAM_ENTRY_GUARD_PATH, failures),
        "compile_presentation_module": _compile(PRESENTATION_MODULE_PATH, failures),
        "warroom_wiring_guard": _run_json_guard(WARROOM_WIRING_GUARD_PATH, failures),
        "docs": _check_docs(failures),
        "existing_payload_builder": _probe_existing_payload_builder(failures),
        "consumers_already_provided_only": _check_consumers_are_already_provided_only(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
