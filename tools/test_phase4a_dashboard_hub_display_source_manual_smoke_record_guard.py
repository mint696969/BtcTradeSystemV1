# path: ./tools/test_phase4a_dashboard_hub_display_source_manual_smoke_record_guard.py
# desc: Guard manual Streamlit smoke pass record for dashboard hub source panel on Health page.

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
INTEGRATION_CLOSE_GUARD = "tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_close_guard.py"
EXPECTED_SMOKE_STEP = "manual_streamlit_smoke_passed_health_page_panel_visible"
COMPILE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py",
]
PLAIN_TESTS = [
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py",
]
FORBIDDEN_STALE_TOKENS = [
    "create_separate_render_free_presenter_entry",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_manual_smoke_record"
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
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1000:], "stderr_tail": (proc.stderr or "")[-1000:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1000:], "stderr_tail": (proc.stderr or "")[-1000:]}


def _check_runtime_payload(failures: list[str]) -> dict[str, object]:
    entry = dashboard_hub_display_source_ui_entry_criteria()
    presenter = dashboard_hub_display_source_presenter(entry)
    detail_steps = [row.get("value") for row in presenter.get("detail_rows", ()) if row.get("label") == "next_required_step"]
    mismatches: dict[str, object] = {}
    if entry.get("next_required_step") != EXPECTED_SMOKE_STEP:
        mismatches["entry.next_required_step"] = {"actual": entry.get("next_required_step"), "expected": EXPECTED_SMOKE_STEP}
        failures.append("ui entry next_required_step must record manual smoke pass")
    if detail_steps != [EXPECTED_SMOKE_STEP]:
        mismatches["presenter.detail_next_required_step"] = {"actual": detail_steps, "expected": [EXPECTED_SMOKE_STEP]}
        failures.append("presenter details must expose manual smoke pass step exactly once")
    if presenter.get("status_label") != "ready":
        mismatches["presenter.status_label"] = {"actual": presenter.get("status_label"), "expected": "ready"}
        failures.append("presenter must remain ready after smoke record")
    return {"entry": entry, "detail_steps": detail_steps, "presenter_status_label": presenter.get("status_label"), "mismatches": mismatches}


def _check_source_shape(failures: list[str]) -> dict[str, object]:
    paths = [
        "btcts_next/src/btcts/apps/operator_ui/hub/display_source_ui_entry_criteria.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py",
        "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py",
    ]
    joined = "\n".join(_read(rel) for rel in paths)
    required = [EXPECTED_SMOKE_STEP, "next_required_step", "diagnostics_read_only_panel"]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"manual smoke record source missing fragment: {fragment}")
    stale_hits = [token for token in FORBIDDEN_STALE_TOKENS if token in joined]
    for token in stale_hits:
        failures.append(f"manual smoke record source still contains stale token: {token}")
    return {"missing": missing, "stale_hits": stale_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_manual_smoke_record_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "integration_close_guard": _run_json_guard(INTEGRATION_CLOSE_GUARD, failures),
        "plain_tests": {rel: _run_plain_ok(rel, failures) for rel in PLAIN_TESTS},
        "runtime_payload": _check_runtime_payload(failures),
        "source_shape": _check_source_shape(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_manual_smoke_record_guard",
        "manual_smoke": {
            "environment": "hot",
            "ui_launch_method": "python -m streamlit",
            "page": "Health",
            "panel_visible": True,
            "details_expander_opened": True,
            "streamlit_exception_observed": False,
        },
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
