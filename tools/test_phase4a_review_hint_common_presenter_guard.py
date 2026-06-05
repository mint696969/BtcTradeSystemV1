# path: ./tools/test_phase4a_review_hint_common_presenter_guard.py
# desc: Guard widget-friendly review hint presenter. No Streamlit/UI layout/runtime/broker wiring.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_SOURCE_GUARD = "tools/test_phase4a_review_hint_ai_display_source_bridge_guard.py"
FILES = [
    "btcts_next/src/btcts/apps/operator_ui/components/review_hint_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_review_hint_presenter.py",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "review_hint_common_presenter"
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
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_source(failures: list[str]) -> dict[str, object]:
    presenter = _read("btcts_next/src/btcts/apps/operator_ui/components/review_hint_presenter.py")
    test_text = _read("btcts_next/src/btcts/apps/operator_ui/tests/test_review_hint_presenter.py")
    required = [
        "review_hint_compact_reading_line",
        "review_hint_snapshot_lines",
        "review_hint_display_sections",
        "prediction_review_hint_display_context",
        "widget_reusable",
        "not_runtime_wiring",
        "not_ui_rendering",
    ]
    missing = [fragment for fragment in required if fragment not in presenter]
    for fragment in missing:
        failures.append(f"presenter missing fragment: {fragment}")

    source_for_scan = presenter + "\n" + test_text
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if token in source_for_scan]
    for token in forbidden_hits:
        failures.append(f"review hint presenter contains forbidden token: {token}")

    return {"missing": missing, "forbidden_hits": forbidden_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile("tools/test_phase4a_review_hint_common_presenter_guard.py", failures),
        "compile_files": {rel: _compile(rel, failures) for rel in FILES},
        "ai_source_guard": _run_json_guard(AI_SOURCE_GUARD, failures),
        "plain_test": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_review_hint_presenter.py", failures),
        "source": _check_source(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_review_hint_common_presenter_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
