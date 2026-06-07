# path: ./tools/test_phase4a_dashboard_hub_display_source_panel_close_guard.py
# desc: Close guard for component-only Streamlit dashboard hub display source panel. No app.py/non-health page routing/runtime/broker wiring.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FOCUSED_GUARDS = [
    "tools/test_phase4a_dashboard_hub_display_source_panel_guard.py",
]
COMPILE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_panel.py",
    "tools/test_phase4a_dashboard_hub_display_source_panel_guard.py",
]
SOURCE_SHAPE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_panel.py",
]
PLAIN_TESTS = [
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_panel.py",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_panel_close"
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


def _check_source_shape(failures: list[str]) -> dict[str, object]:
    joined = "\n".join(_read(rel) for rel in SOURCE_SHAPE_FILES)
    required = [
        "dashboard_hub_display_source_panel",
        "DASHBOARD_HUB_SOURCE_PANEL_CONTRACT",
        "dashboard_hub_source_panel=",
        "hot_cold_row_count",
        "hot_cold_status_label",
        "hot_cold_metadata_detail_status",
        "hot_cold_rows_present",
        "hot_cold_status:",
        "catalog_ready_payload_not_opened",
        "render_dashboard_hub_display_source_panel",
        "import streamlit as st",
        "live_shell.panel_container",
        "st.table",
        "component_only_rendering",
        "not_app_py_wiring",
        "not_page_routing",
        "not_runtime_wiring",
        "not_broker_or_order_wiring",
        "read_only_contract",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"dashboard hub source panel bundle missing fragment: {fragment}")
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if token in joined]
    for token in forbidden_hits:
        failures.append(f"dashboard hub source panel bundle contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_app_py_untouched_boundary(failures: list[str]) -> dict[str, object]:
    app_text = _read("btcts_next/src/btcts/apps/operator_ui/app.py")
    forbidden = [
        "dashboard_hub_source_panel",
        "render_dashboard_hub_display_source_panel",
        "DASHBOARD_HUB_SOURCE_PANEL_CONTRACT",
    ]
    hits = [token for token in forbidden if token in app_text]
    for token in hits:
        failures.append(f"app.py must not be wired to dashboard hub source panel in this slice: {token}")
    return {"hits": hits}


def _check_view_routing_boundary(failures: list[str]) -> dict[str, object]:
    """Allow the existing Health page component slot; ban app/page spread elsewhere."""
    health_rel = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
    health_text = _read(health_rel)
    required_health_tokens = [
        "render_dashboard_hub_display_source_panel",
        'health_widget_slot("dashboard_hub_source_panel")',
    ]
    missing_health_tokens = [token for token in required_health_tokens if token not in health_text]
    for token in missing_health_tokens:
        failures.append(f"health page must retain dashboard hub source panel slot wiring: {token}")

    paths = [
        "btcts_next/src/btcts/apps/operator_ui/views/__init__.py",
        "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    ]
    forbidden = [
        "dashboard_hub_source_panel",
        "render_dashboard_hub_display_source_panel",
        "DASHBOARD_HUB_SOURCE_PANEL_CONTRACT",
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
                failures.append(f"non-health view/page routing must not be wired to dashboard hub source panel: {rel}: {token}")
    return {"missing_health_tokens": missing_health_tokens, "non_health_hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_panel_close_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "focused_guards": {rel: _run_json_guard(rel, failures) for rel in FOCUSED_GUARDS},
        "plain_tests": {rel: _run_plain_ok(rel, failures) for rel in PLAIN_TESTS},
        "source_shape": _check_source_shape(failures),
        "app_py_untouched_boundary": _check_app_py_untouched_boundary(failures),
        "view_routing_boundary": _check_view_routing_boundary(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_panel_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
