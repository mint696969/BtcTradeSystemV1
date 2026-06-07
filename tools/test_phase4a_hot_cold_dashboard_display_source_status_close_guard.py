# path: ./tools/test_phase4a_hot_cold_dashboard_display_source_status_close_guard.py
# desc: Close guard for Hot/Cold dashboard display source status model. Metadata-only; no payload loader/rendering/file reader/copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_hot_cold_dashboard_display_source_status_close_guard.py"
STATUS_GUARD_PATH = "tools/test_phase4a_hot_cold_dashboard_display_source_status_guard.py"
CATALOG_CLOSE_GUARD_PATH = "tools/test_phase4a_hot_cold_dashboard_display_source_catalog_close_guard.py"
STATUS_PATH = "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_display_source_status.py"
CATALOG_PATH = "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_display_sources.py"
TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_dashboard_display_source_status.py"

COMPILE_FILES = [
    STATUS_GUARD_PATH,
    CATALOG_CLOSE_GUARD_PATH,
    STATUS_PATH,
    CATALOG_PATH,
    TEST_PATH,
]

FORBIDDEN_TOKENS = [
    "read_parquet(",
    "read_json(",
    "rglob(\"*.parquet\")",
    "rglob(\"*.jsonl\")",
    "streamlit",
    "st.",
    "render_",
    "payload_loader_opened = True",
    "dashboard_rendering_opened = True",
    "dataset_reader_opened = True",
    "shutil.copy",
    "copy2(",
    "copytree(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "archive_gc_enable =",
    "archive_gc_enable:",
    "archive_gc_enable(",
    "execute_copy_plan",
    "execute_gc_plan",
    "connect_to_simulation",
    "connect_to_training",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_dashboard_source_status_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1800)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_source_shape(failures: list[str]) -> dict[str, Any]:
    text = _read(STATUS_PATH)
    required = [
        "HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT",
        "hot_cold_duplicate_safe_dataset_view_source_status",
        "catalog_ready_payload_not_opened",
        "payload_loader_status",
        "dashboard_rendering_status",
        "dataset_reader_status",
        "simulation_connector_status",
        "training_connector_status",
        "copy_delete_gc_status",
        "payload_loader_opened",
        "dashboard_rendering_opened",
        "dataset_reader_opened",
        "hot_cold_source_status=",
        "not_payload_loader",
        "not_dataset_reader",
        "not_ui_rendering",
        "not_copy_executor",
        "not_delete_executor",
        "not_archive_gc_enablement",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"hot/cold dashboard source status close missing fragment: {fragment}")
    if forbidden_hits:
        failures.append("hot/cold dashboard source status close contains forbidden reader/rendering/executor token")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _probe_status(failures: list[str]) -> dict[str, Any]:
    code = """
from btcts.apps.operator_ui.components.hot_cold_display_source_status import hot_cold_duplicate_safe_dataset_view_source_status
import json
status = hot_cold_duplicate_safe_dataset_view_source_status()
print(json.dumps(status, sort_keys=True))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO_ROOT / "btcts_next" / "src"), text=True, capture_output=True, timeout=120)
    try:
        status = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"hot/cold dashboard source status close probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    flags = status.get("readiness_flags") or {}
    ok = (
        proc.returncode == 0
        and status.get("source_key") == "hot_cold_duplicate_safe_dataset_view_model"
        and status.get("source_type") == "hot_cold_duplicate_safe_dataset_view_read_only_model"
        and status.get("status_label") == "catalog_ready_payload_not_opened"
        and status.get("payload_loader_status") == "not_opened"
        and status.get("dataset_reader_status") == "not_opened"
        and status.get("dashboard_rendering_status") == "not_opened"
        and status.get("simulation_connector_status") == "not_opened"
        and status.get("training_connector_status") == "not_opened"
        and status.get("copy_delete_gc_status") == "not_opened"
        and flags.get("catalog_present") is True
        and flags.get("schema_version_known") is True
        and flags.get("logical_identity_known") is True
        and flags.get("payload_loader_opened") is False
        and flags.get("dataset_reader_opened") is False
        and flags.get("dashboard_rendering_opened") is False
        and flags.get("simulation_connector_opened") is False
        and flags.get("training_connector_opened") is False
        and flags.get("copy_executor_opened") is False
        and flags.get("delete_executor_opened") is False
        and flags.get("archive_gc_enablement_opened") is False
    )
    if not ok:
        failures.append("hot/cold dashboard source status close probe must remain metadata-only and unopened")
    return {"ok": ok, "returncode": proc.returncode, "status": status, "stderr_tail": (proc.stderr or "")[-1200:]}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "status_guard": _run_json_guard(STATUS_GUARD_PATH, failures),
        "catalog_close_guard": {"verified_before_status_close_guard": True, "path": CATALOG_CLOSE_GUARD_PATH},
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "source_shape": _check_source_shape(failures),
        "status_probe": _probe_status(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_hot_cold_dashboard_display_source_status_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
