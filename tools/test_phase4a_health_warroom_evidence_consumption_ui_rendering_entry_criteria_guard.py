# path: ./tools/test_phase4a_health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard.py
# desc: Phase 4-A Health/WarRoom evidence consumption UI rendering entry criteria guard.

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
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_UI_RENDERING_ENTRY_CRITERIA_2026-05-30.md"
RENDER_FREE_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_RENDER_FREE_PRESENTATION_MODEL_2026-05-29.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
RENDER_FREE_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_consumption_render_free_presentation_model_guard.py"
UI_RENDERING_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
PRESENTATION_MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py"
APP_UI_ROOT = "btcts_next/src/btcts/apps/operator_ui"
FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]
EVIDENCE_PRESENTATION_PATTERNS = [
    "HealthWarRoomEvidencePresentationModel",
    "health_warroom_evidence_presentation_model",
    "health_warroom_evidence_presentation_payload",
    "health_warroom_evidence_consumption_presentation",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "error": "missing"}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_ui_rendering_entry"
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


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        SPEC_PATH: [
            "UI rendering entry criteria / guard only",
            "actual Streamlit rendering implementation ではない",
            "apps/operator_ui has no premature evidence presentation reference",
            "tools/test_phase4a_health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard.py",
        ],
        RENDER_FREE_SPEC_PATH: [
            "render-free presentation model only",
            "health_warroom_evidence_presentation_payload",
        ],
        INDEX_PATH: [
            "PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_UI_RENDERING_ENTRY_CRITERIA_2026-05-30.md",
            "actual Streamlit rendering",
        ],
        STATE_PATH: [
            "health_warroom_evidence_consumption",
            "route wiring",
            "runtime state writer",
            "market_engine integration",
            "collector writer/backfill",
            "broker/order/execution",
            "inference/training",
            "raw D/E scanner",
        ],
        PRESENTATION_MODULE_PATH: [
            "class HealthWarRoomEvidencePresentationModel",
            "def health_warroom_evidence_presentation_payload",
            "not_ui_rendering",
            "not_runtime_signal",
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


def _probe_render_free_payload(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
            health_warroom_evidence_presentation_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import build_real_data_validation_evidence_summary
        payload = health_warroom_evidence_presentation_payload(
            build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        )
    except Exception as exc:
        failures.append(f"render-free presentation payload probe failed: {type(exc).__name__}: {exc}")
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
        failures.append(f"render-free payload boundary flag not true: {key}")
    if payload.get("presentation_kind") != "health_warroom_evidence_consumption_presentation":
        failures.append("render-free payload presentation_kind mismatch")
    return {"ok": not bad, "presentation_kind": payload.get("presentation_kind"), "status_key": payload.get("status_key"), "bad": bad}


def _scan_paths_for_patterns(root_rel: str, patterns: list[str]) -> list[str]:
    root = REPO_ROOT / root_rel
    if not root.exists():
        return []
    hits: list[str] = []
    for path in root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if any(pattern in text for pattern in patterns):
            hits.append(path.relative_to(REPO_ROOT).as_posix())
    return sorted(hits)


def _check_no_premature_ui_rendering(failures: List[str]) -> Dict[str, Any]:
    approved = {
        "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_panel.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_evidence_presentation_panel.py",
        "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_evidence_presentation_wiring.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_evidence_presentation_wiring.py",
    }
    hits = [path for path in _scan_paths_for_patterns(APP_UI_ROOT, EVIDENCE_PRESENTATION_PATTERNS) if path not in approved]
    for path in hits:
        failures.append(f"premature apps/operator_ui evidence presentation reference found: {path}")
    return {"hit_count": len(hits), "hits": hits, "approved_count": len(approved)}


def _check_no_runtime_reference(failures: List[str]) -> Dict[str, Any]:
    all_hits: list[str] = []
    for rel_root in FORBIDDEN_RUNTIME_ROOTS:
        all_hits.extend(_scan_paths_for_patterns(rel_root, EVIDENCE_PRESENTATION_PATTERNS))
    all_hits = sorted(set(all_hits))
    for path in all_hits:
        failures.append(f"forbidden runtime path references evidence presentation: {path}")
    return {"hit_count": len(all_hits), "hits": all_hits}


def _check_primary_connected(failures: List[str]) -> Dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [
        UI_RENDERING_GUARD_PATH,
        "health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary guard missing UI rendering entry connection fragment: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_self": _compile(UI_RENDERING_GUARD_PATH, failures),
        "compile_presentation_module": _compile(PRESENTATION_MODULE_PATH, failures),
        "render_free_guard": _run_json_guard(RENDER_FREE_GUARD_PATH, failures),
        "docs": _check_docs(failures),
        "render_free_payload": _probe_render_free_payload(failures),
        "premature_ui_rendering": _check_no_premature_ui_rendering(failures),
        "runtime_reference": _check_no_runtime_reference(failures),
        "primary_connection": _check_primary_connected(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
