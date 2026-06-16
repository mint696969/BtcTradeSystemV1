# path: ./tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_close_guard.py
# desc: Close guard for dashboard hub source Operator UI integration guard before manual Streamlit smoke.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_GUARD = "tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_guard.py"
FOCUSED_GUARDS = [
    INTEGRATION_GUARD,
]
COMPILE_FILES = [
    INTEGRATION_GUARD,
    "tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_close_guard.py",
    "btcts_next/src/btcts/apps/operator_ui/app.py",
    "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_page_connection_entry.py",
]
SOURCE_SHAPE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/app.py",
    "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py",
]
FORBIDDEN_RUNTIME_TOKENS = [
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_operator_ui_integration_close"
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


def _check_guard_shape(failures: list[str]) -> dict[str, object]:
    text = _read(INTEGRATION_GUARD)
    required = [
        "phase4a_dashboard_hub_display_source_operator_ui_integration_guard",
        "health_insertion_close_guard",
        "app_route_boundary",
        "health_page_connection",
        "slot_and_presenter_contracts",
        "runtime_boundary",
        "non_selected_views",
        "_check_app_route_boundary",
        "_check_health_page_connection",
        "_check_slot_and_presenter_contracts",
        "_check_runtime_boundary",
        "_check_non_selected_views",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"operator UI integration guard missing fragment: {fragment}")
    return {"missing": missing}


def _check_source_shape(failures: list[str]) -> dict[str, object]:
    joined = "\n".join(_read(rel) for rel in SOURCE_SHAPE_FILES)
    required = [
        "(\"health\", get_text(lang, \"page_health\"), health_page)",
        "page_module = pages[selected_page_key]",
        "page_module.render()",
        "from btcts.apps.operator_ui.components.dashboard_hub_source_panel import (",
        "health_widget_slot(\"dashboard_hub_source_panel\")",
        "render_dashboard_hub_display_source_panel()",
        "dashboard_hub_source_panel",
        "priority\": 118",
        "zone_id\": \"detail\"",
        "refresh_mode\": \"poll_normal\"",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"operator UI integration close source missing fragment: {fragment}")
    forbidden_hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in joined]
    for token in forbidden_hits:
        failures.append(f"operator UI integration close source contains forbidden runtime token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_route_boundaries(failures: list[str]) -> dict[str, object]:
    app_text = _read("btcts_next/src/btcts/apps/operator_ui/app.py")
    health_text = _read("btcts_next/src/btcts/apps/operator_ui/views/health_page.py")
    app_forbidden = [
        "dashboard_hub_source_panel",
        "render_dashboard_hub_display_source_panel",
        "display_source_page_connection_entry",
    ]
    app_hits = [token for token in app_forbidden if token in app_text]
    for token in app_hits:
        failures.append(f"app.py must not directly wire dashboard hub source panel in integration close: {token}")

    health_counts = {
        "render_call_count": health_text.count("render_dashboard_hub_display_source_panel()"),
        "slot_count": health_text.count("health_widget_slot(\"dashboard_hub_source_panel\")"),
    }
    if health_counts["render_call_count"] != 1:
        failures.append(f"health_page render call count must be 1: {health_counts['render_call_count']}")
    if health_counts["slot_count"] != 1:
        failures.append(f"health_page slot count must be 1: {health_counts['slot_count']}")

    non_selected_hits: list[dict[str, str]] = []
    for rel in [
        "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    ]:
        text = _read(rel)
        for token in ["dashboard_hub_source_panel", "render_dashboard_hub_display_source_panel"]:
            if token in text:
                non_selected_hits.append({"path": rel, "token": token})
                failures.append(f"non-selected view must not be wired in integration close: {rel}: {token}")
    return {"app_hits": app_hits, "health_counts": health_counts, "non_selected_hits": non_selected_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_close_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "focused_guards": {rel: _run_json_guard(rel, failures) for rel in FOCUSED_GUARDS},
        "guard_shape": _check_guard_shape(failures),
        "source_shape": _check_source_shape(failures),
        "route_boundaries": _check_route_boundaries(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_operator_ui_integration_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
