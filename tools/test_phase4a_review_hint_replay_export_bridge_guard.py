# path: ./tools/test_phase4a_review_hint_replay_export_bridge_guard.py
# desc: Guard Position/Execution review hint snapshots through replay session/export/report. No UI/runtime/broker wiring.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_review_hint_replay_export_bridge_guard.py"
POSITION_ARTIFACT_GUARD = "tools/test_phase4a_position_review_hint_replay_artifact_snapshot_guard.py"
EXECUTION_ARTIFACT_GUARD = "tools/test_phase4a_execution_review_hint_replay_artifact_snapshot_guard.py"
FILES = [
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
]
PLAIN_TESTS = [
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "review_hint_replay_export_bridge"
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
    required = {
        "btcts_next/src/btcts/replay/replay_session.py": [
            "prediction_position_review_hint_snapshots",
            "prediction_execution_review_hint_snapshots",
            "add_prediction_position_review_hint_snapshot",
            "add_prediction_execution_review_hint_snapshot",
        ],
        "btcts_next/src/btcts/replay/replay_runner.py": [
            "prediction_position_review_hint_snapshot",
            "prediction_execution_review_hint_snapshot",
        ],
        "btcts_next/src/btcts/replay/replay_export.py": [
            "prediction_position_review_hint_snapshot_path",
            "prediction_execution_review_hint_snapshot_path",
            "prediction_position_review_hint_snapshot_count",
            "prediction_execution_review_hint_snapshot_count",
        ],
        "btcts_next/src/btcts/replay/replay_report.py": [
            "prediction_position_review_hint_summary",
            "prediction_execution_review_hint_summary",
            "broker_link_free",
            "account_side_effect_free",
        ],
    }
    missing: list[str] = []
    forbidden_hits: list[str] = []
    for rel, fragments in required.items():
        text = _read(rel)
        for fragment in fragments:
            if fragment not in text:
                missing.append(f"{rel}: {fragment}")
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
                forbidden_hits.append(f"{rel}: {token}")
    for item in missing:
        failures.append(f"missing bridge fragment: {item}")
    for item in forbidden_hits:
        failures.append(f"forbidden token in bridge source: {item}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_files": {rel: _compile(rel, failures) for rel in FILES},
        "position_artifact_guard": _run_json_guard(POSITION_ARTIFACT_GUARD, failures),
        "execution_artifact_guard": _run_json_guard(EXECUTION_ARTIFACT_GUARD, failures),
        "plain_tests": {rel: _run_plain_ok(rel, failures) for rel in PLAIN_TESTS},
        "source": _check_source(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_review_hint_replay_export_bridge_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
