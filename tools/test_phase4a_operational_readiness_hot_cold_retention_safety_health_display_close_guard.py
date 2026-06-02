# path: ./tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_display_close_guard.py
# desc: Phase 4-A close guard for Hot/Cold retention safety Health display. No D/E scan, no copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_display_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_SAFETY_HEALTH_DISPLAY_CLOSE_2026-06-02.md"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_guard.py"
PANEL_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_panel_guard.py"
WIRING_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_wiring_guard.py"
PRODUCER_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_snapshot_producer_guard.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/health_data_service.py"
SAFETY_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py"
PANEL_PATH = "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py"
SERVICE_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_service.py"
PANEL_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_panel.py"
HEALTH_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_evidence_presentation_wiring.py"
PRIMARY_COMPACT_PATH = "tmp/work/phase4a_health_warroom_evidence_consumption_ui_rendering/run_primary_guard_compact_v1.py"

FORBIDDEN_SOURCE_TOKENS = [
    "shutil.rmtree(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "send2trash",
    "archive_gc_enable",
    "run_explicit_hot_cold_small_batch_delete",
]

FORBIDDEN_HEALTH_RENDER_TOKENS = [
    "rglob(",
    "glob(",
    "os.scandir(",
    "build_explicit_hot_cold_delete_plan",
    "D:" + "\\",
    "E:" + "\\",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_retention_safety_health_display_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str], *, timeout: int = 1200) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=timeout)
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


def _run_primary_compact(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / PRIMARY_COMPACT_PATH)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=3600)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"primary compact did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failed_guard_count") == 0 and parsed.get("top_failure_count") == 0
    if not ok:
        failures.append("primary compact must be ok with no failed guards")
    return {"ok": ok, "returncode": proc.returncode, "failed_guard_count": parsed.get("failed_guard_count"), "top_failure_count": parsed.get("top_failure_count"), "failed_guards": parsed.get("failed_guards"), "json_path": parsed.get("json_path"), "log_path": parsed.get("log_path")}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold retention safety Health display close",
        "10-day hot retention policy entry",
        "display-only panel component",
        "Health page snapshot-only wiring",
        "Health snapshot lightweight payload producer",
        "hot_retention_days = 10",
        "min_delete_age_hours = 240",
        "previous 48h-style first batch is abandoned for execute",
        "scan D/E from Health render path",
        "copy files",
        "delete files",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_closed_chain_source(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    service = _read(SAFETY_SERVICE_PATH)
    health_service = _read(HEALTH_SERVICE_PATH)
    panel = _read(PANEL_PATH)

    required_fragments = {
        HEALTH_PAGE_PATH: [
            "render_hot_cold_retention_safety_panel",
            "_snapshot_hot_cold_retention_safety_payload",
            'health_widget_slot("hot_cold_retention_safety_panel")',
        ],
        HEALTH_SERVICE_PATH: [
            "load_hot_cold_retention_safety_payload",
            "hot_cold_retention_safety_payload = load_hot_cold_retention_safety_payload()",
            '"operational_readiness_hot_cold_retention_safety": hot_cold_retention_safety_payload',
        ],
        SAFETY_SERVICE_PATH: [
            "HOT_RETENTION_DAYS = 10",
            "MIN_DELETE_AGE_HOURS = 240.0",
            "\"candidate_files\": 0",
            "previous_plan_abandoned_for_execute",
            "Rebuild dry-run plan with min_age_hours=240 before any delete.",
        ],
        PANEL_PATH: [
            "render_hot_cold_retention_safety_panel",
            "not_filesystem_scan",
            "not_copy_executor",
            "not_delete_executor",
        ],
    }
    text_by_path = {HEALTH_PAGE_PATH: health, HEALTH_SERVICE_PATH: health_service, SAFETY_SERVICE_PATH: service, PANEL_PATH: panel}
    missing: list[dict[str, str]] = []
    for rel_path, fragments in required_fragments.items():
        text = text_by_path[rel_path]
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"closed chain missing fragment: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    forbidden_hits: list[dict[str, str]] = []
    for rel_path, text in [(HEALTH_PAGE_PATH, health), (HEALTH_SERVICE_PATH, health_service), (SAFETY_SERVICE_PATH, service), (PANEL_PATH, panel)]:
        tokens = list(FORBIDDEN_SOURCE_TOKENS)
        if rel_path in {HEALTH_PAGE_PATH, PANEL_PATH}:
            tokens.extend(FORBIDDEN_HEALTH_RENDER_TOKENS)
        for token in tokens:
            if token in text:
                failures.append(f"closed chain contains forbidden token: {rel_path}: {token}")
                forbidden_hits.append({"path": rel_path, "token": token})

    evidence_idx = health.find('health_widget_slot("evidence_presentation_panel")')
    safety_idx = health.find('health_widget_slot("hot_cold_retention_safety_panel")')
    if safety_idx < 0 or evidence_idx < 0 or safety_idx > evidence_idx:
        failures.append("Health safety panel must exist before evidence panel")

    return {"missing": missing, "forbidden_hits": forbidden_hits, "safety_slot_index": safety_idx, "evidence_slot_index": evidence_idx}


def _check_payload_shape(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-c", "from btcts.apps.operator_ui.hot_cold_retention_safety_service import load_hot_cold_retention_safety_payload; import json; print(json.dumps(load_hot_cold_retention_safety_payload(), ensure_ascii=False, sort_keys=True))"],
        cwd=str(REPO_ROOT / "btcts_next" / "src"),
        text=True,
        capture_output=True,
        timeout=120,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"payload shape probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    checks_ok = (
        parsed.get("title") == "Hot/Cold retention safety"
        and parsed.get("hot_retention_days") == 10
        and float(parsed.get("min_delete_age_hours") or 0.0) == 240.0
        and parsed.get("delete_readiness_key") in {"blocked_previous_plan_younger_than_10_days", "no_recent_preflight_summary", "blocked_rebuild_10day_plan"}
        and (parsed.get("counts") or {}).get("candidate_files") == 0
        and (parsed.get("boundary") or {}).get("not_filesystem_scan") is True
        and (parsed.get("boundary") or {}).get("not_delete_executor") is True
    )
    if not checks_ok:
        failures.append("payload shape must represent 10-day blocked/no-execute safety state")
    return {"ok": checks_ok, "returncode": proc.returncode, "status_key": parsed.get("status_key"), "delete_readiness_key": parsed.get("delete_readiness_key"), "candidate_files": (parsed.get("counts") or {}).get("candidate_files")}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_health_page": _compile(HEALTH_PAGE_PATH, failures),
        "compile_health_service": _compile(HEALTH_SERVICE_PATH, failures),
        "compile_safety_service": _compile(SAFETY_SERVICE_PATH, failures),
        "compile_panel": _compile(PANEL_PATH, failures),
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "panel_guard": _run_json_guard(PANEL_GUARD_PATH, failures),
        "wiring_guard": _run_json_guard(WIRING_GUARD_PATH, failures),
        "producer_guard": _run_json_guard(PRODUCER_GUARD_PATH, failures),
        "service_plain_test": _run_plain_ok(SERVICE_TEST_PATH, failures),
        "panel_plain_test": _run_plain_ok(PANEL_TEST_PATH, failures),
        "health_plain_test": _run_plain_ok(HEALTH_TEST_PATH, failures),
        "spec": _check_spec(failures),
        "closed_chain_source": _check_closed_chain_source(failures),
        "payload_shape": _check_payload_shape(failures),
        "primary_compact": _run_primary_compact(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_retention_safety_health_display_close_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
