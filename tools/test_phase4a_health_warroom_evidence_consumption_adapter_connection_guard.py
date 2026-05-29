# path: ./tools/test_phase4a_health_warroom_evidence_consumption_adapter_connection_guard.py
# desc: Phase 4-A Health/WarRoom evidence consumption adapter connection guard.

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
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_ADAPTER_CONNECTION_GUARD_2026-05-29.md"
MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py"
TEST_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence_consumption.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_read_only_evidence_consumption_entry_criteria_guard.py"
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_adapter_connection"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace('/', '__') + '.pyc')), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_plain_ok(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-2000:], "stderr_tail": (proc.stderr or "")[-2000:]}


def _probe_payload(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
            health_warroom_evidence_consumption_status_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
            build_real_data_validation_evidence_summary,
        )
        summary = build_real_data_validation_evidence_summary(source_output_ref="source.json", review_output_ref="review.json")
        payload = health_warroom_evidence_consumption_status_payload(summary)
    except Exception as exc:
        failures.append(f"payload probe failed: {type(exc).__name__}: {exc}")
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
        failures.append(f"payload boundary flag not true: {key}")
    forbidden_keys = [
        "component",
        "widget",
        "route",
        "streamlit",
        "runtime_state_path",
        "market_engine_signal",
        "collector_write_path",
        "order_size",
        "order_price",
        "place_order",
        "broker_order",
        "live_order_placement",
        "auto_trade",
        "training_dataset",
        "inference_job",
        "raw_data_path",
        "hot_root",
        "cold_root",
    ]
    forbidden_present = [key for key in forbidden_keys if key in payload]
    for key in forbidden_present:
        failures.append(f"payload contains forbidden key: {key}")
    return {"ok": not bad and not forbidden_present, "payload_kind": payload.get("payload_kind"), "bad": bad, "forbidden_present": forbidden_present}


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        SPEC_PATH: [
            "status payload adapter connection only",
            "health_warroom_evidence_consumption_status_payload",
            "not_runtime_signal = true",
            "not_ui_rendering = true",
        ],
        MODULE_PATH: [
            "health_warroom_evidence_consumption_status_payload",
            "layout-free, read-only Health/WarRoom evidence status payload",
            "not_runtime_signal",
            "not_ui_rendering",
        ],
        ENTRY_GUARD_PATH: [
            "CONSUMER_SKELETON_PATH",
            "consumer_skeleton_test",
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


def _check_module_forbidden(failures: List[str]) -> Dict[str, Any]:
    text = _read(MODULE_PATH)
    forbidden = [
        "import streamlit",
        "from streamlit",
        " st.",
        "\nst.",
        "runtime_state_path =",
        "market_engine_signal =",
        "collector_write_path =",
        "place_order(",
        ".place_order",
        "broker_order(",
        "training_dataset =",
        "inference_job =",
        "D:\\",
        "E:\\",
        "r\"D:",
        "r\"E:",
    ]
    hits = [fragment for fragment in forbidden if fragment in text]
    for fragment in hits:
        failures.append(f"adapter module contains forbidden runtime/UI/path fragment: {fragment}")
    return {"hits": hits}


def _check_no_forbidden_path_usage(failures: List[str]) -> Dict[str, Any]:
    patterns = ["health_warroom_evidence_consumption_status_payload", "HealthWarRoomEvidenceConsumptionModel", "real_data_validation_evidence_consumption"]
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
            if any(pattern in text for pattern in patterns):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(rel)
                failures.append(f"forbidden path references evidence consumption adapter: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_module": _compile(MODULE_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "test": _run_plain_ok(TEST_PATH, failures),
        "payload_probe": _probe_payload(failures),
        "docs": _check_docs(failures),
        "module_forbidden": _check_module_forbidden(failures),
        "forbidden_path_usage": _check_no_forbidden_path_usage(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_consumption_adapter_connection_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
