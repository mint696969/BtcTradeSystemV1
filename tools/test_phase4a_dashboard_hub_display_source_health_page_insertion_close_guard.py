# path: ./tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_close_guard.py
# desc: Close guard for Health page dashboard hub source panel insertion. No app.py/sidebar/runtime/broker mutation.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

from btcts.apps.operator_ui.hub.display_source_page_connection_entry import (
    dashboard_hub_display_source_page_connection_entry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FOCUSED_GUARDS = [
    "tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_guard.py",
]
COMPILE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_health_page_insertion.py",
    "tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_guard.py",
]
SOURCE_SHAPE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_health_page_insertion.py",
]
PLAIN_TESTS = [
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_health_page_insertion.py",
]
FORBIDDEN_SOURCE_TOKENS = [
    "order_size",
    "order_price",
    "leverage",
    "broker_account",
    "place_order",
    "broker_order",
    "live_order_placement",
    "auto_trade",
    "account_mutation",
    "broker_adapter_operation",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_health_page_insertion_close"
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


def _check_page_connection_entry(failures: list[str]) -> dict[str, object]:
    entry = dashboard_hub_display_source_page_connection_entry()
    expected = {
        "page_connection_ready": True,
        "selected_page_key": "health",
        "allowed_next_surface": "existing_view_component_call",
        "app_py_wiring_allowed": False,
        "page_routing_mutation_allowed": False,
        "runtime_wiring_allowed": False,
    }
    mismatches: dict[str, object] = {}
    for key, value in expected.items():
        if entry.get(key) != value:
            mismatches[key] = {"actual": entry.get(key), "expected": value}
            failures.append(f"page connection entry mismatch: {key}: expected {value!r}, got {entry.get(key)!r}")
    return {"entry": entry, "mismatches": mismatches}


def _check_source_shape(failures: list[str]) -> dict[str, object]:
    joined = "\n".join(_read(rel) for rel in SOURCE_SHAPE_FILES)
    required = [
        "from btcts.apps.operator_ui.components.dashboard_hub_source_panel import (",
        "render_dashboard_hub_display_source_panel",
        "health_widget_slot(\"dashboard_hub_source_panel\")",
        "def _render_dashboard_hub_source_panel_section() -> None:",
        "dashboard_hub_source_panel",
        "priority\": 118",
        "zone_id\": \"detail\"",
        "refresh_mode\": \"poll_normal\"",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"health page dashboard hub source panel insertion close missing fragment: {fragment}")
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if token in joined]
    for token in forbidden_hits:
        failures.append(f"health page dashboard hub source panel insertion close contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_existing_boundary(failures: list[str]) -> dict[str, object]:
    forbidden = [
        "dashboard_hub_source_panel",
        "render_dashboard_hub_display_source_panel",
    ]
    app_text = _read("btcts_next/src/btcts/apps/operator_ui/app.py")
    app_hits = [token for token in forbidden if token in app_text]
    for token in app_hits:
        failures.append(f"app.py must not be wired by health page insertion close slice: {token}")

    page_hits: list[dict[str, str]] = []
    for rel in [
        "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    ]:
        text = _read(rel)
        for token in forbidden:
            if token in text:
                page_hits.append({"path": rel, "token": token})
                failures.append(f"non-selected view must not be wired by health page insertion close slice: {rel}: {token}")
    return {"app_hits": app_hits, "non_selected_view_hits": page_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_close_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "focused_guards": {rel: _run_json_guard(rel, failures) for rel in FOCUSED_GUARDS},
        "page_connection_entry": _check_page_connection_entry(failures),
        "plain_tests": {rel: _run_plain_ok(rel, failures) for rel in PLAIN_TESTS},
        "source_shape": _check_source_shape(failures),
        "existing_boundary": _check_existing_boundary(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_health_page_insertion_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
