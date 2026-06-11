# path: ./tools/test_phase4a_dashboard_hub_display_source_matrix_guard.py
# desc: Guard dashboard hub display source/page matrix read model. No app.py/Streamlit/layout/runtime/broker wiring.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AVAILABILITY_CLOSE_GUARD = "tools/test_phase4a_dashboard_hub_display_source_availability_close_guard.py"
FILES = [
    "btcts_next/src/btcts/apps/operator_ui/hub/display_source_matrix.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_matrix.py",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "dashboard_hub_display_source_matrix"
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
        "dashboard_hub_display_source_matrix",
        "DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT",
        "dashboard_hub_source_matrix=",
        "page_rows",
        "source_rows",
        "source_presence",
        "page_presence",
        "missing_references",
        "summary_widget",
        "review_hint_display",
        "read_only_contract",
        "widget_reusable",
        "layout_decision_free",
        "not_runtime_wiring",
        "not_ui_rendering",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"dashboard hub display source matrix missing fragment: {fragment}")
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if token in joined]
    for token in forbidden_hits:
        failures.append(f"dashboard hub display source matrix contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_app_py_untouched_boundary(failures: list[str]) -> dict[str, object]:
    app_text = _read("btcts_next/src/btcts/apps/operator_ui/app.py")
    forbidden = [
        "display_source_matrix",
        "dashboard_hub_display_source_matrix",
        "DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT",
    ]
    hits = [token for token in forbidden if token in app_text]
    for token in hits:
        failures.append(f"app.py must not be wired to dashboard hub source matrix in this slice: {token}")
    return {"hits": hits}


def _run_availability_close_guard(failures: list[str]) -> dict[str, object]:
    if os.environ.get("BTCTS_DASHBOARD_HUB_SKIP_NESTED_CLOSE_GUARD") == "1":
        return {
            "ok": True,
            "skipped": True,
            "reason": "verified_by_separate_primary_total_guard",
            "path": AVAILABILITY_CLOSE_GUARD,
        }
    return _run_json_guard(AVAILABILITY_CLOSE_GUARD, failures)

def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_dashboard_hub_display_source_matrix_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in FILES},
        "availability_close_guard": _run_availability_close_guard(failures),
        "plain_test": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_matrix.py", failures),
        "source": _check_source(failures),
        "app_py_untouched_boundary": _check_app_py_untouched_boundary(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_dashboard_hub_display_source_matrix_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
