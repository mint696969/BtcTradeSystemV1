# path: ./tools/test_phase4a_operator_display_source_catalog_guard.py
# desc: Guard operator-wide display source catalog facade. No Streamlit/UI layout/runtime/broker wiring.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_DISPLAY_SOURCE_CATALOG_GUARD = "tools/test_phase4a_ai_display_source_catalog_guard.py"
FILES = [
    "btcts_next/src/btcts/apps/operator_ui/components/operator_display_source_catalog.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_operator_display_source_catalog.py",
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
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_display_source_catalog"
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
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1000:], "stderr_tail": (proc.stderr or "")[-1000:]}


def _check_source(failures: list[str]) -> dict[str, object]:
    joined = "\n".join(_read(rel) for rel in FILES)
    required = [
        "OPERATOR_DASHBOARD_HUB_CONTRACT",
        "operator_dashboard_display_source_catalog",
        "dashboard_role",
        "current_tab_layout_is_temporary",
        "load_operator_dashboard_display_source_catalog",
        "select_display_sources_for_consumer",
        "review_hint_display",
        "future_widget",
        "widget_reusable",
        "layout_decision_free",
        "not_runtime_wiring",
        "not_ui_rendering",
    ]
    missing = [fragment for fragment in required if fragment not in joined]
    for fragment in missing:
        failures.append(f"operator display source catalog missing fragment: {fragment}")
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if token in joined]
    for token in forbidden_hits:
        failures.append(f"operator display source catalog contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_operator_display_source_catalog_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in FILES},
        "ai_display_source_catalog_guard": _run_json_guard(AI_DISPLAY_SOURCE_CATALOG_GUARD, failures),
        "plain_test": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_operator_display_source_catalog.py", failures),
        "source": _check_source(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_display_source_catalog_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
