# path: ./tools/test_phase4a_position_review_hint_replay_artifact_snapshot_guard.py
# desc: Guard Position review hint read-only replay artifact snapshot entry. No UI/runtime/broker wiring.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_position_review_hint_replay_artifact_snapshot_guard.py"
POSITION_HELPER_GUARD = "tools/test_phase4a_position_review_hint_builder_skeleton_guard.py"
ARTIFACTS_PATH = "btcts_next/src/btcts/replay/replay_prediction_artifacts.py"
TEST_PATH = "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py"

FORBIDDEN_ARTIFACT_TOKENS = [
    "PredictionPositionHint",
    "build_prediction_position",
    "PredictionExecutionHint",
    "build_prediction_execution",
    "position_size",
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
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "position_review_hint_replay_artifact_snapshot"
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
    artifacts = _read(ARTIFACTS_PATH)
    test_text = _read(TEST_PATH)
    required_artifacts = [
        "PositionReviewHintBuildInput",
        "make_position_review_hint",
        "position_review_hint_to_snapshot",
        "prediction_position_review_hint_snapshot",
        "position_review_hint_read_only_snapshot",
        "replay_artifact_only",
        "not_runtime_wiring",
        "not_ui_wiring",
        "not_market_engine_wiring",
    ]
    missing = [fragment for fragment in required_artifacts if fragment not in artifacts]
    for fragment in missing:
        failures.append(f"artifact source missing fragment: {fragment}")

    forbidden_hits = [token for token in FORBIDDEN_ARTIFACT_TOKENS if token in artifacts]
    for token in forbidden_hits:
        failures.append(f"artifact source contains forbidden token: {token}")

    test_required = [
        "prediction_position_review_hint_snapshot",
        "position_context.review_only.row_1",
        "direction_snapshot.row_1",
    ]
    test_missing = [fragment for fragment in test_required if fragment not in test_text]
    for fragment in test_missing:
        failures.append(f"test missing fragment: {fragment}")

    return {
        "missing": missing,
        "forbidden_hits": forbidden_hits,
        "test_missing": test_missing,
    }


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_artifacts": _compile(ARTIFACTS_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "position_helper_guard": _run_json_guard(POSITION_HELPER_GUARD, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "source": _check_source(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_position_review_hint_replay_artifact_snapshot_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
