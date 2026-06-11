# path: ./tools/test_phase4a_dashboard_hub_display_source_page_connection_entry_guard.py
# desc: Guard dashboard hub source panel page connection entry criteria. No app.py/view routing/layout/runtime/broker mutation.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_CLOSE_GUARD = "tools/test_phase4a_dashboard_hub_display_source_panel_close_guard.py"
FILES = [
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_page_connection_entry.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_page_connection_entry.py",
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
    "import streamlit",
    "from streamlit",
    "st.",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_page_connection_entry"
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


def _check_source(failures: list[str]) -> dict[str, object]:
    joined = "\n".join(_read(rel) for rel in FILES)
    required = [
        "dashboard_hub_display_source_page_connection_entry",
        "DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT",
        "dashboard_hub_source_page_connection=",
        "page_connection_ready",
        "selected_page_key",
        "connectable_page_keys",
        "existing_view_component_call",
        "create_guarded_existing_view_component_insertion_slice",
        "not_app_py_wiring",
        "not_page_routing_mutation",
        "not_layout_decision",
        "not_runtime_wiring",
        "not_broker_or_order_wiring",
        "health_tab",
        "collector_tab",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"dashboard hub source page connection entry missing fragment: {fragment}")
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if token in joined]
    for token in forbidden_hits:
        failures.append(f"dashboard hub source page connection entry contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_existing_ui_untouched_boundary(failures: list[str]) -> dict[str, object]:
    """Current truth: Health page insertion is closed; app.py and non-selected views stay untouched."""
    paths = [
        "btcts_next/src/btcts/apps/operator_ui/app.py",
        "btcts_next/src/btcts/apps/operator_ui/views/__init__.py",
        "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    ]
    forbidden = [
        "display_source_page_connection_entry",
        "dashboard_hub_display_source_page_connection_entry",
        "DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT",
        "render_dashboard_hub_display_source_panel",
    ]
    hits: list[dict[str, str]] = []
    for rel in paths:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                hits.append({"path": rel, "token": token})
                failures.append(f"app.py and non-selected UI must not be wired in page connection entry slice: {rel}: {token}")

    health_text = _read("btcts_next/src/btcts/apps/operator_ui/views/health_page.py")
    allowed_health_tokens = [
        "render_dashboard_hub_display_source_panel",
        'health_widget_slot("dashboard_hub_source_panel")',
    ]
    missing_allowed_health_tokens = [token for token in allowed_health_tokens if token not in health_text]
    for token in missing_allowed_health_tokens:
        failures.append(f"closed health page insertion must retain dashboard hub source panel token: {token}")

    return {"hits": hits, "missing_allowed_health_tokens": missing_allowed_health_tokens}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_page_connection_entry_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in FILES},
        "panel_close_guard": _run_json_guard(PANEL_CLOSE_GUARD, failures),
        "plain_test": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_page_connection_entry.py", failures),
        "source": _check_source(failures),
        "existing_ui_untouched_boundary": _check_existing_ui_untouched_boundary(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_page_connection_entry_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
