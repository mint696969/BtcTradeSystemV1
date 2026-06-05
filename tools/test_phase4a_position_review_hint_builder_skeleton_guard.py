# path: ./tools/test_phase4a_position_review_hint_builder_skeleton_guard.py
# desc: Phase 4-A Position review hint read-only helper skeleton guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_position_review_hint_builder_skeleton_guard.py"
CONTRACT_GUARD_PATH = "tools/test_phase4a_position_review_hint_entry_criteria_guard.py"
BUILDER_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_position_review_hint_builder.py"
TEST_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_builder.py"
SHARED_INIT_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py"

FORBIDDEN_TOKENS = [
    "build_prediction_position",
    "position_size",
    "order_size",
    "order_price",
    "leverage",
    "broker_account",
    "place_order",
    "broker_order",
    "live_order_placement",
    "auto_trade",
    "import streamlit",
    "from streamlit",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "position_review_hint_builder_skeleton"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
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


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_source(failures: list[str]) -> dict[str, Any]:
    builder = _read(BUILDER_PATH)
    test_text = _read(TEST_PATH)
    init_text = _read(SHARED_INIT_PATH)
    required = [
        "class PositionReviewHintBuildInput",
        "def make_position_review_hint",
        "def position_review_hint_to_snapshot",
        "read_only_contract",
        "not_live_position_mutation",
        "not_execution_instruction",
        "not_broker_or_order_automation",
        "not_runtime_wiring",
        "not_replay_wiring",
        "not_ui_wiring",
    ]
    missing = [fragment for fragment in required if fragment not in builder]
    for fragment in missing:
        failures.append(f"builder missing fragment: {fragment}")

    scanned_text = "\n".join((builder, test_text, init_text))
    forbidden_hits = [token for token in FORBIDDEN_TOKENS if token in scanned_text]
    for token in forbidden_hits:
        failures.append(f"new Position helper files contain forbidden token: {token}")

    init_missing = [
        fragment for fragment in [
            "PositionReviewHintBuildInput",
            "make_position_review_hint",
            "position_review_hint_to_snapshot",
        ]
        if fragment not in init_text
    ]
    for fragment in init_missing:
        failures.append(f"shared __init__ missing export fragment: {fragment}")

    return {"missing": missing, "forbidden_hits": forbidden_hits, "init_missing": init_missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_builder": _compile(BUILDER_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "contract_guard": _run_json_guard(CONTRACT_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "source": _check_source(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_position_review_hint_builder_skeleton_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
