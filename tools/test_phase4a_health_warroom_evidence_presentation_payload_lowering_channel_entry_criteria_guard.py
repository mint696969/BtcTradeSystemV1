# path: ./tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_entry_criteria_guard.py
# desc: Phase 4-A Health/WarRoom evidence presentation payload lowering channel entry criteria guard.

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

SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PRESENTATION_PAYLOAD_LOWERING_CHANNEL_ENTRY_CRITERIA_2026-05-31.md"
UPSTREAM_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py"
SELF_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_entry_criteria_guard.py"
UPSTREAM_MODULE_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_presentation_upstream.py"
IMPLEMENTATION_SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_PRESENTATION_PAYLOAD_LOWERING_CHANNEL_IMPLEMENTATION_2026-05-31.md"
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

EXPECTED_HEALTH_KEYS = {
    "evidence_presentation_payload",
    "health_warroom_evidence_presentation_payload",
    "real_data_validation_evidence_presentation",
}

EXPECTED_WARROOM_KEYS = {
    "warroom_evidence_presentation_payload",
    "health_warroom_evidence_presentation_payload",
    "real_data_validation_evidence_presentation",
    "evidence_presentation_payload",
}

REQUIRED_BOUNDARY_TRUE = [
    "read_only_consumption",
    "diagnostic_evidence_only",
    "operator_support_only",
    "not_runtime_signal",
    "not_runtime_wiring",
    "not_market_engine_input",
    "not_collector_writer",
    "not_broker_or_order_automation",
    "not_inference_or_training",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_payload_lowering_channel_entry"
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
        return {
            "ok": False,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-2000:],
            "stderr_tail": (proc.stderr or "")[-2000:],
        }
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "phase": parsed.get("phase"),
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Health / WarRoom evidence presentation payload lowering channel entry criteria",
        "guard-only entry criteria",
        "health_snapshot_evidence_presentation_payload_fields",
        "warroom_session_state_evidence_presentation_payload_fields",
        "lower_health_warroom_evidence_presentation_payload",
        "evidence_presentation_payload",
        "health_warroom_evidence_presentation_payload",
        "real_data_validation_evidence_presentation",
        "warroom_evidence_presentation_payload",
        "not_runtime_wiring = true",
        "not_market_engine_input = true",
        "not_collector_writer = true",
        "not_broker_or_order_automation = true",
        "not_inference_or_training = true",
        "Do not implement actual Health snapshot mutation yet.",
        "Do not implement actual WarRoom session_state mutation yet.",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _probe_existing_lowering(failures: list[str]) -> dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_presentation_upstream import (
            lower_health_warroom_evidence_presentation_payload,
        )
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
            build_real_data_validation_evidence_summary,
        )
        lowered = lower_health_warroom_evidence_presentation_payload(
            build_real_data_validation_evidence_summary(
                source_output_ref="source.json",
                review_output_ref="review.json",
            )
        )
    except Exception as exc:
        failures.append(f"lowering probe failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": str(exc)}

    health_fields = dict(lowered.get("health_snapshot_fields") or {})
    warroom_fields = dict(lowered.get("warroom_session_state_fields") or {})
    boundary = dict(lowered.get("boundary") or {})
    bad: list[str] = []

    if set(health_fields) != EXPECTED_HEALTH_KEYS:
        bad.append(f"health keys mismatch: {sorted(health_fields)}")
    if set(warroom_fields) != EXPECTED_WARROOM_KEYS:
        bad.append(f"warroom keys mismatch: {sorted(warroom_fields)}")
    for key in REQUIRED_BOUNDARY_TRUE:
        if boundary.get(key) is not True:
            bad.append(f"boundary flag not true: {key}")

    if lowered.get("lowering_kind") != "health_warroom_evidence_presentation_payload_lowering":
        bad.append("lowering_kind mismatch")
    if lowered.get("not_runtime_wiring") is not True:
        bad.append("top-level not_runtime_wiring must be true")

    for item in bad:
        failures.append(f"existing lowering probe failed: {item}")

    return {
        "ok": not bad,
        "bad": bad,
        "health_keys": sorted(health_fields),
        "warroom_keys": sorted(warroom_fields),
        "lowering_kind": lowered.get("lowering_kind"),
    }


def _check_pages_do_not_call_producer(failures: list[str]) -> dict[str, Any]:
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
        failures.append(f"Health page must not call upstream producer in entry slice: {token}")
    for token in warroom_hits:
        failures.append(f"WarRoom page must not call upstream producer in entry slice: {token}")
    return {"health_hits": health_hits, "warroom_hits": warroom_hits}


def _scan_runtime_references(failures: list[str]) -> dict[str, Any]:
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
                failures.append(f"runtime path references upstream lowering producer: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def _check_no_new_lowering_implementation(failures: list[str]) -> dict[str, Any]:
    # This entry slice should add only this guard and the spec.  Existing module may already
    # define the pure lowering function, but no new adapter names should appear yet.
    module_text = _read(UPSTREAM_MODULE_PATH)
    forbidden_new_adapter_names = [
        "lower_health_snapshot_evidence_presentation_fields",
        "lower_warroom_session_state_evidence_presentation_fields",
        "apply_health_warroom_evidence_presentation_payload",
    ]
    implementation_open = (REPO_ROOT / IMPLEMENTATION_SPEC_PATH).exists()
    hits = [] if implementation_open else [name for name in forbidden_new_adapter_names if name in module_text]
    for name in hits:
        failures.append(f"entry slice must not add implementation adapter yet: {name}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_upstream_module": _compile(UPSTREAM_MODULE_PATH, failures),
        "upstream_producer_guard": _run_json_guard(UPSTREAM_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "existing_lowering_probe": _probe_existing_lowering(failures),
        "pages_do_not_call_producer": _check_pages_do_not_call_producer(failures),
        "runtime_references": _scan_runtime_references(failures),
        "no_new_lowering_implementation": _check_no_new_lowering_implementation(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_health_warroom_evidence_presentation_payload_lowering_channel_entry_criteria_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())