# path: ./tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_guard.py
# desc: Integration guard for dashboard hub source panel in Operator UI Health page before manual Streamlit smoke.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

from btcts.apps.operator_ui.components.dashboard_hub_source_panel import (
    DASHBOARD_HUB_SOURCE_PANEL_CONTRACT,
)
from btcts.apps.operator_ui.components.slot_definitions import (
    health_widget_ids,
    health_widget_slot,
)
from btcts.apps.operator_ui.hub.display_source_page_connection_entry import (
    dashboard_hub_display_source_page_connection_entry,
)
from btcts.apps.operator_ui.hub.display_source_presenter import (
    dashboard_hub_display_source_presenter,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HEALTH_INSERTION_CLOSE_GUARD = "tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_close_guard.py"
COMPILE_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/app.py",
    "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_page_connection_entry.py",
    "tools/test_phase4a_dashboard_hub_display_source_health_page_insertion_close_guard.py",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_operator_ui_integration"
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


def _check_app_route_boundary(failures: list[str]) -> dict[str, object]:
    text = _read("btcts_next/src/btcts/apps/operator_ui/app.py")
    required = [
        "(\"health\", get_text(lang, \"page_health\"), health_page)",
        "page_module = pages[selected_page_key]",
        "page_module.render()",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"app.py route boundary missing expected existing route fragment: {fragment}")
    forbidden = [
        "dashboard_hub_source_panel",
        "render_dashboard_hub_display_source_panel",
        "display_source_page_connection_entry",
    ]
    hits = [token for token in forbidden if token in text]
    for token in hits:
        failures.append(f"app.py must not directly wire dashboard hub source panel: {token}")
    return {"missing": missing, "forbidden_hits": hits}


def _check_health_page_connection(failures: list[str]) -> dict[str, object]:
    text = _read("btcts_next/src/btcts/apps/operator_ui/views/health_page.py")
    required = [
        "from btcts.apps.operator_ui.components.dashboard_hub_source_panel import (",
        "render_dashboard_hub_display_source_panel",
        "def _render_dashboard_hub_source_panel_section() -> None:",
        "health_widget_slot(\"dashboard_hub_source_panel\")",
        "render_dashboard_hub_display_source_panel()",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"health_page dashboard hub source panel wiring missing fragment: {fragment}")
    counts = {
        "render_call_count": text.count("render_dashboard_hub_display_source_panel()"),
        "slot_count": text.count("health_widget_slot(\"dashboard_hub_source_panel\")"),
    }
    if counts["render_call_count"] != 1:
        failures.append(f"health_page must render dashboard hub source panel exactly once: {counts['render_call_count']}")
    if counts["slot_count"] != 1:
        failures.append(f"health_page must register dashboard hub source panel slot exactly once: {counts['slot_count']}")
    return {"missing": missing, "counts": counts}


def _check_slot_and_presenter_contracts(failures: list[str]) -> dict[str, object]:
    entry = dashboard_hub_display_source_page_connection_entry()
    presenter = dashboard_hub_display_source_presenter()
    slot = health_widget_slot("dashboard_hub_source_panel")
    contract = dict(DASHBOARD_HUB_SOURCE_PANEL_CONTRACT)

    mismatches: dict[str, object] = {}
    expected_pairs = {
        "entry.selected_page_key": (entry.get("selected_page_key"), "health"),
        "entry.page_connection_ready": (entry.get("page_connection_ready"), True),
        "entry.app_py_wiring_allowed": (entry.get("app_py_wiring_allowed"), False),
        "entry.page_routing_mutation_allowed": (entry.get("page_routing_mutation_allowed"), False),
        "slot.page_id": (slot.get("page_id"), "health"),
        "slot.widget_id": (slot.get("widget_id"), "dashboard_hub_source_panel"),
        "slot.zone_id": (slot.get("zone_id"), "detail"),
        "panel.read_only_contract": (contract.get("read_only_contract"), True),
        "panel.streamlit_rendering": (contract.get("streamlit_rendering"), True),
        "panel.not_app_py_wiring": (contract.get("not_app_py_wiring"), True),
        "panel.not_runtime_wiring": (contract.get("not_runtime_wiring"), True),
        "presenter.not_app_py_wiring": (presenter.get("not_app_py_wiring"), True),
        "presenter.not_runtime_wiring": (presenter.get("not_runtime_wiring"), True),
    }
    for key, (actual, expected) in expected_pairs.items():
        if actual != expected:
            mismatches[key] = {"actual": actual, "expected": expected}
            failures.append(f"integration contract mismatch: {key}: expected {expected!r}, got {actual!r}")

    widget_ids = health_widget_ids()
    if "dashboard_hub_source_panel" not in widget_ids:
        mismatches["health_widget_ids"] = "dashboard_hub_source_panel missing"
        failures.append("health_widget_ids must include dashboard_hub_source_panel")

    return {
        "entry": entry,
        "slot": slot,
        "presenter_status_label": presenter.get("status_label"),
        "panel_contract": contract,
        "mismatches": mismatches,
    }


def _check_runtime_boundary(failures: list[str]) -> dict[str, object]:
    paths = [
        "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
        "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
        "btcts_next/src/btcts/apps/operator_ui/hub/display_source_presenter.py",
        "btcts_next/src/btcts/apps/operator_ui/hub/display_source_page_connection_entry.py",
    ]
    hits: list[dict[str, str]] = []
    for rel in paths:
        text = _read(rel)
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                hits.append({"path": rel, "token": token})
                failures.append(f"operator UI integration must not open runtime/broker/order token: {rel}: {token}")
    return {"hits": hits}


def _check_non_selected_views(failures: list[str]) -> dict[str, object]:
    forbidden = [
        "dashboard_hub_source_panel",
        "render_dashboard_hub_display_source_panel",
    ]
    hits: list[dict[str, str]] = []
    for rel in [
        "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
        "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    ]:
        text = _read(rel)
        for token in forbidden:
            if token in text:
                hits.append({"path": rel, "token": token})
                failures.append(f"non-selected view must not be wired to dashboard hub source panel: {rel}: {token}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_operator_ui_integration_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "health_insertion_close_guard": _run_json_guard(HEALTH_INSERTION_CLOSE_GUARD, failures),
        "app_route_boundary": _check_app_route_boundary(failures),
        "health_page_connection": _check_health_page_connection(failures),
        "slot_and_presenter_contracts": _check_slot_and_presenter_contracts(failures),
        "runtime_boundary": _check_runtime_boundary(failures),
        "non_selected_views": _check_non_selected_views(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_operator_ui_integration_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
