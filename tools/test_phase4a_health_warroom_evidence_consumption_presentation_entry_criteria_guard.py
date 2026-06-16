# path: ./tools/test_phase4a_health_warroom_evidence_consumption_presentation_entry_criteria_guard.py
# desc: Phase 4-A Health/WarRoom evidence consumption presentation entry criteria guard.

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

PRESENTATION_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_PRESENTATION_ENTRY_CRITERIA_2026-05-29.md"
ADAPTER_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_ADAPTER_CONNECTION_GUARD_2026-05-29.md"
ENTRY_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_READ_ONLY_EVIDENCE_CONSUMPTION_ENTRY_CRITERIA_2026-05-29.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
ADAPTER_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_consumption_adapter_connection_guard.py"
PRESENTATION_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_consumption_presentation_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
ADAPTER_MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py"

FORBIDDEN_APP_UI_ROOT = "btcts_next/src/btcts/apps/operator_ui"
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


def _compile(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "error": "missing"}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_presentation_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace('/', '__') + '.pyc')), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"guard missing: {rel_path}")
        return {"ok": False, "returncode": None, "json": None, "stdout_tail": "", "stderr_tail": ""}
    proc = subprocess.run([sys.executable, str(path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=300)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "json": None, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase") if isinstance(parsed, dict) else None, "json": parsed, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        PRESENTATION_SPEC_PATH: [
            "Health / WarRoom evidence consumption presentation entry criteria",
            "presentation entry criteria / guard only",
            "Streamlit rendering",
            "btcts_next/src/btcts/apps/operator_ui/* を変更してはいけない",
            "tools/test_phase4a_health_warroom_evidence_consumption_presentation_entry_criteria_guard.py",
        ],
        ADAPTER_SPEC_PATH: [
            "status payload adapter connection only",
            "health_warroom_evidence_consumption_status_payload",
        ],
        ENTRY_SPEC_PATH: [
            "read-only consumer skeleton close",
            "Still forbidden",
        ],
        INDEX_PATH: [
            "PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_PRESENTATION_ENTRY_CRITERIA_2026-05-29.md",
            "apps/operator_ui implementation",
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



def _check_state_progression(failures: List[str]) -> Dict[str, Any]:
    text = _read(STATE_PATH)
    allowed_fragments = [
        "health_warroom_evidence_consumption_adapter_connection_closed_primary_guard_green",
        "health_warroom_evidence_consumption_presentation_entry_criteria",
        "health_warroom_evidence_consumption_presentation_entry_closed_primary_guard_green",
        "health_warroom_evidence_consumption_render_free_presentation_model",
        "health_warroom_evidence_consumption_render_free_presentation_model_closed_primary_guard_green",
        "health_warroom_evidence_consumption_ui_rendering_entry_criteria",
        "health_warroom_evidence_consumption_ui_rendering_entry_closed_primary_guard_green",
        "health_warroom_evidence_consumption_shared_ui_rendering_component",
        "health_warroom_evidence_consumption_shared_ui_rendering_component_closed_primary_guard_green",
        "health_warroom_evidence_consumption_health_page_wiring",
        "health_warroom_evidence_consumption_health_page_wiring_closed_primary_guard_green",
        "health_warroom_evidence_consumption_warroom_page_wiring",
        "health_warroom_evidence_presentation_upstream_payload_production_entry_criteria",
        "health_warroom_evidence_presentation_upstream_payload_producer",
        "health_warroom_evidence_consumption_warroom_page_wiring_closed_primary_guard_green",
    ]
    matched = [fragment for fragment in allowed_fragments if fragment in text]
    if not matched:
        failures.append("state is not on an allowed Health/WarRoom evidence presentation progression point")

    required_closed_boundary = [
        "route wiring",
        "runtime state writer",
        "market_engine integration",
        "collector writer/backfill",
        "broker/order/execution",
        "inference/training",
        "raw D/E scanner",
    ]
    missing_boundary = [fragment for fragment in required_closed_boundary if fragment not in text]
    for fragment in missing_boundary:
        failures.append(f"state missing closed presentation boundary fragment: {fragment}")

    return {
        "matched": matched,
        "allowed_count": len(allowed_fragments),
        "missing_boundary": missing_boundary,
    }

def _check_adapter_payload_available(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
            health_warroom_evidence_consumption_status_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import build_real_data_validation_evidence_summary
        payload = health_warroom_evidence_consumption_status_payload(
            build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        )
    except Exception as exc:
        failures.append(f"adapter payload import/probe failed: {type(exc).__name__}: {exc}")
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
        failures.append(f"adapter payload boundary flag not true: {key}")
    return {"ok": not bad, "payload_kind": payload.get("payload_kind"), "bad": bad}


def _scan_forbidden_paths(failures: List[str]) -> Dict[str, Any]:
    patterns = [
        "health_warroom_evidence_consumption_status_payload",
        "HealthWarRoomEvidenceConsumptionModel",
        "real_data_validation_evidence_consumption",
    ]
    hits: list[str] = []
    for rel_root in [FORBIDDEN_APP_UI_ROOT, *FORBIDDEN_RUNTIME_ROOTS]:
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
                failures.append(f"premature presentation/runtime evidence consumption reference found: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def _check_primary_connected(failures: List[str]) -> Dict[str, Any]:
    text = _read(PRIMARY_GUARD_PATH)
    required = [
        PRESENTATION_GUARD_PATH,
        "health_warroom_evidence_consumption_presentation_entry_criteria_guard",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"primary guard missing presentation entry connection fragment: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_self": _compile(PRESENTATION_GUARD_PATH, failures),
        "compile_adapter_module": _compile(ADAPTER_MODULE_PATH, failures),
        "docs": _check_docs(failures),
        "state_progression": _check_state_progression(failures),
        "adapter_payload": _check_adapter_payload_available(failures),
        "adapter_guard": _run_json_guard(ADAPTER_GUARD_PATH, failures),
        "forbidden_path_scan": _scan_forbidden_paths(failures),
        "primary_connection": _check_primary_connected(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_consumption_presentation_entry_criteria_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
