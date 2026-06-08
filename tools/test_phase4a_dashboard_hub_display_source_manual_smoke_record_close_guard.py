# path: ./tools/test_phase4a_dashboard_hub_display_source_manual_smoke_record_close_guard.py
# desc: Close guard for manual Streamlit smoke pass record of dashboard hub source panel.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

from btcts.apps.operator_ui.hub.display_source_presenter import (
    dashboard_hub_display_source_presenter,
)
from btcts.apps.operator_ui.hub.display_source_ui_entry_criteria import (
    dashboard_hub_display_source_ui_entry_criteria,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MANUAL_SMOKE_GUARD = "tools/test_phase4a_dashboard_hub_display_source_manual_smoke_record_guard.py"
EXPECTED_SMOKE_STEP = "manual_streamlit_smoke_passed_health_page_panel_visible"
COMPILE_FILES = [
    MANUAL_SMOKE_GUARD,
    "tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_close_guard.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py",
]
PLAIN_TESTS = [
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py",
]
SOURCE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py",
]
STALE_TOKENS: list[str] = []


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_manual_smoke_record_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=900)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    smoke = parsed.get("manual_smoke") or {}
    smoke_ok = (
        smoke.get("environment") == "hot"
        and smoke.get("ui_launch_method") == "python -m streamlit"
        and smoke.get("page") == "Health"
        and smoke.get("panel_visible") is True
        and smoke.get("details_expander_opened") is True
        and smoke.get("hot_cold_metadata_table_visible") is True
        and smoke.get("hot_cold_status_label_visible") == "catalog_ready_payload_not_opened"
        and smoke.get("hot_cold_payload_loader_visible") == "not_opened"
        and smoke.get("hot_cold_dataset_reader_visible") == "not_opened"
        and smoke.get("hot_cold_copy_executor_visible") == "not_opened"
        and smoke.get("streamlit_exception_observed") is False
    )
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    if not smoke_ok:
        failures.append(f"{rel_path} manual_smoke payload must record hot Health pass")
    return {
        "ok": ok,
        "manual_smoke_ok": smoke_ok,
        "returncode": proc.returncode,
        "phase": parsed.get("phase"),
        "manual_smoke": smoke,
        "stdout_tail": (proc.stdout or "")[-1000:],
        "stderr_tail": (proc.stderr or "")[-1000:],
    }


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1000:], "stderr_tail": (proc.stderr or "")[-1000:]}


def _check_guard_shape(failures: list[str]) -> dict[str, object]:
    text = _read(MANUAL_SMOKE_GUARD)
    required = [
        "phase4a_dashboard_hub_display_source_manual_smoke_record_guard",
        "manual_smoke",
        "environment",
        "hot",
        "ui_launch_method",
        "python -m streamlit",
        "page",
        "Health",
        "panel_visible",
        "details_expander_opened",
        "hot_cold_metadata_table_visible",
        "hot_cold_status_label_visible",
        "catalog_ready_payload_not_opened",
        "hot_cold_payload_loader_visible",
        "hot_cold_dataset_reader_visible",
        "hot_cold_copy_executor_visible",
        "not_opened",
        "streamlit_exception_observed",
        EXPECTED_SMOKE_STEP,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"manual smoke record guard missing fragment: {fragment}")
    return {"missing": missing}


def _check_runtime_payload(failures: list[str]) -> dict[str, object]:
    entry = dashboard_hub_display_source_ui_entry_criteria()
    presenter = dashboard_hub_display_source_presenter(entry)
    detail_steps = [row.get("value") for row in presenter.get("detail_rows", ()) if row.get("label") == "next_required_step"]
    mismatches: dict[str, object] = {}
    expected_pairs = {
        "entry.next_required_step": (entry.get("next_required_step"), EXPECTED_SMOKE_STEP),
        "entry.ui_entry_ready": (entry.get("ui_entry_ready"), True),
        "presenter.status_label": (presenter.get("status_label"), "ready"),
        "presenter.detail_next_required_step": (tuple(detail_steps), (EXPECTED_SMOKE_STEP,)),
    }
    for key, (actual, expected) in expected_pairs.items():
        if actual != expected:
            mismatches[key] = {"actual": actual, "expected": expected}
            failures.append(f"manual smoke close mismatch: {key}: expected {expected!r}, got {actual!r}")
    return {"entry": entry, "detail_steps": detail_steps, "presenter_status_label": presenter.get("status_label"), "mismatches": mismatches}


def _check_source_shape(failures: list[str]) -> dict[str, object]:
    joined = "\n".join(_read(rel) for rel in SOURCE_FILES)
    required = [
        EXPECTED_SMOKE_STEP,
        "next_required_step",
        "diagnostics_read_only_panel",
        "catalog_ready_payload_not_opened",
        "not_opened",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"manual smoke record close source missing fragment: {fragment}")
    stale_hits = [token for token in STALE_TOKENS if token in joined]
    for token in stale_hits:
        failures.append(f"manual smoke record close source still contains stale token: {token}")
    return {"missing": missing, "stale_hits": stale_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_manual_smoke_record_close_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "manual_smoke_guard": _run_json_guard(MANUAL_SMOKE_GUARD, failures),
        "plain_tests": {rel: _run_plain_ok(rel, failures) for rel in PLAIN_TESTS},
        "guard_shape": _check_guard_shape(failures),
        "runtime_payload": _check_runtime_payload(failures),
        "source_shape": _check_source_shape(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_manual_smoke_record_close_guard",
        "close_status": "closed" if not failures else "open",
        "manual_smoke_status": "passed_hot_health_page" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
