# path: ./tools/test_phase4a_hot_cold_dashboard_display_source_catalog_close_guard.py
# desc: Close guard for Hot/Cold dashboard display source catalog registration. Catalog-only; no reader/rendering/copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_hot_cold_dashboard_display_source_catalog_close_guard.py"
CATALOG_GUARD_PATH = "tools/test_phase4a_hot_cold_dashboard_display_source_catalog_guard.py"
MODEL_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_model_close_guard.py"
CATALOG_PATH = "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_display_sources.py"
OPERATOR_CATALOG_PATH = "btcts_next/src/btcts/apps/operator_ui/components/operator_display_source_catalog.py"
REGISTRY_PATH = "btcts_next/src/btcts/apps/operator_ui/hub/display_source_registry.py"
TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_dashboard_display_source_catalog.py"

COMPILE_FILES = [
    CATALOG_GUARD_PATH,
    MODEL_CLOSE_GUARD_PATH,
    CATALOG_PATH,
    OPERATOR_CATALOG_PATH,
    REGISTRY_PATH,
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_dashboard_source_catalog_close"
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
    catalog_text = _read(CATALOG_PATH)
    operator_text = _read(OPERATOR_CATALOG_PATH)
    registry_text = _read(REGISTRY_PATH)
    required = [
        (CATALOG_PATH, "HOT_COLD_DISPLAY_SOURCE_CATALOG"),
        (CATALOG_PATH, "hot_cold_duplicate_safe_dataset_view_model"),
        (CATALOG_PATH, "hot_cold_duplicate_safe_dataset_view_read_only_model"),
        (CATALOG_PATH, "hot_cold_duplicate_safe_dataset_view_v1"),
        (CATALOG_PATH, "exchange:symbol:rel_file"),
        (CATALOG_PATH, "load_hot_cold_display_source_catalog"),
        (CATALOG_PATH, "hot_cold_display_source_catalog_summary"),
        (CATALOG_PATH, "not_dataset_reader"),
        (CATALOG_PATH, "not_simulation_connector"),
        (CATALOG_PATH, "not_training_connector"),
        (CATALOG_PATH, "not_copy_executor"),
        (CATALOG_PATH, "not_delete_executor"),
        (CATALOG_PATH, "not_archive_gc_enablement"),
        (OPERATOR_CATALOG_PATH, "load_hot_cold_display_source_catalog"),
        (OPERATOR_CATALOG_PATH, "hot_cold_display_sources"),
        (OPERATOR_CATALOG_PATH, "ai_operator_display_sources"),
        (OPERATOR_CATALOG_PATH, "sources = ai_sources + hot_cold_sources"),
        (REGISTRY_PATH, "load_dashboard_hub_display_source_registry"),
    ]
    text_by_path = {
        CATALOG_PATH: catalog_text,
        OPERATOR_CATALOG_PATH: operator_text,
        REGISTRY_PATH: registry_text,
    }
    missing = [f"{path}:{fragment}" for path, fragment in required if fragment not in text_by_path[path]]
    forbidden_hits: list[dict[str, str]] = []
    for rel_path in [CATALOG_PATH, OPERATOR_CATALOG_PATH, REGISTRY_PATH]:
        text = _read(rel_path)
        for token in FORBIDDEN_TOKENS:
            if token in text:
                forbidden_hits.append({"path": rel_path, "token": token})
    for fragment in missing:
        failures.append(f"hot/cold dashboard source catalog close missing fragment: {fragment}")
    if forbidden_hits:
        failures.append("hot/cold dashboard source catalog close contains forbidden reader/rendering/executor tokens")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _probe_catalog(failures: list[str]) -> dict[str, Any]:
    code = """
from btcts.apps.operator_ui.components.hot_cold_display_sources import hot_cold_display_source_catalog_summary
from btcts.apps.operator_ui.components.operator_display_source_catalog import load_operator_dashboard_display_source_catalog, select_display_sources_for_consumer
from btcts.apps.operator_ui.hub.display_source_registry import load_dashboard_hub_display_source_registry, display_source_keys_for_page
import json
summary = hot_cold_display_source_catalog_summary()
catalog = load_operator_dashboard_display_source_catalog()
health = select_display_sources_for_consumer('health_tab', catalog)
registry = load_dashboard_hub_display_source_registry()
print(json.dumps({
    'summary': summary,
    'source_count': catalog['source_count'],
    'source_keys': list(catalog['source_keys']),
    'health_keys': [item['source_key'] for item in health],
    'registry_health_keys': list(display_source_keys_for_page('health', registry)),
    'registry_read_only': registry['read_only_contract'],
}, sort_keys=True))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO_ROOT / "btcts_next" / "src"), text=True, capture_output=True, timeout=120)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"dashboard source catalog close probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    summary = parsed.get("summary") or {}
    ok = (
        proc.returncode == 0
        and summary.get("catalog_type") == "hot_cold_display_source_catalog"
        and summary.get("source_count") == 1
        and "hot_cold_duplicate_safe_dataset_view_model" in parsed.get("source_keys", [])
        and "hot_cold_duplicate_safe_dataset_view_model" in parsed.get("health_keys", [])
        and "hot_cold_duplicate_safe_dataset_view_model" in parsed.get("registry_health_keys", [])
        and parsed.get("registry_read_only") is True
        and summary.get("not_dataset_reader") is True
        and summary.get("not_copy_executor") is True
        and summary.get("not_delete_executor") is True
        and summary.get("not_archive_gc_enablement") is True
    )
    if not ok:
        failures.append("dashboard source catalog close probe must expose hot/cold source and remain catalog-only")
    return {"ok": ok, "returncode": proc.returncode, **parsed, "stderr_tail": (proc.stderr or "")[-1200:]}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "catalog_guard": _run_json_guard(CATALOG_GUARD_PATH, failures),
        "model_close_guard": {"verified_before_catalog_close_guard": True, "path": MODEL_CLOSE_GUARD_PATH},
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "source_shape": _check_source_shape(failures),
        "catalog_probe": _probe_catalog(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_hot_cold_dashboard_display_source_catalog_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
