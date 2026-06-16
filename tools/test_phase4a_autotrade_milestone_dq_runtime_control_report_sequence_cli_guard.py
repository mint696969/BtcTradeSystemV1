# path: ./tools/test_phase4a_autotrade_milestone_dq_runtime_control_report_sequence_cli_guard.py
# desc: Guard S51 runtime_control report sequence CLI wrapper remains broker-free, read-only, and non-authorizing.

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_sr_fx_runtime_control_report_sequence_once.py"
SEQUENCE_APP = REPO_ROOT / "btcts_next/src/btcts/apps/sr_fx_runtime_control_report_sequence_once.py"
SEQUENCE_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/tests/test_sr_fx_runtime_control_report_sequence_once.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s51_runtime_control_report_sequence_cli_guard"
OUT_PATH = TMP_ROOT / "wrapper_out.json"
CHECK_FILES = (
    RUNNER,
    SEQUENCE_APP,
    SEQUENCE_TEST,
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
    "mode_changed=True",
    "would_send_to_broker=True",
    "while True",
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _seed_state(state_root: Path) -> None:
    state = state_root / "collector_vnext"
    _write_json(
        state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json",
        {
            "ok": True,
            "data_ui_integrity_ready_for_final_human_review": True,
            "autotrade_resume_authorized": False,
            "blocked_by": [],
            "summary": {"primary_lineage": "continuous_ws", "service_stale": False},
            "context": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"},
            "read_only": True,
            "would_send_to_broker": False,
        },
    )
    _write_json(
        state / "public" / "bitflyer_fx_public_market_readiness.json",
        {
            "public_market_readiness": {
                "ok": True,
                "product_code": "FX_BTC_JPY",
                "market_uid": "bitflyer.fx.FX_BTC_JPY",
                "blocked_by": [],
                "warnings": [],
                "read_only": True,
                "would_send_to_broker": False,
            }
        },
    )
    _write_json(
        state / "private" / "bitflyer_fx_readiness.json",
        {
            "readiness": {
                "product_code": "FX_BTC_JPY",
                "market_uid": "bitflyer.fx.FX_BTC_JPY",
                "private_state_known_and_fresh": True,
                "account_clear_for_new_auto_entry": True,
                "blocked_by": [],
                "read_only": True,
                "would_send_to_broker": False,
            }
        },
    )
    _write_json(
        state / "private" / "bitflyer_fx_live_readiness_contract.json",
        {
            "live_readiness_contract": {
                "ready": False,
                "product_code": "FX_BTC_JPY",
                "market_uid": "bitflyer.fx.FX_BTC_JPY",
                "blocked_by": ["order_sender_not_implemented"],
                "read_only": True,
                "would_send_to_broker": False,
            }
        },
    )


def _run_wrapper() -> dict[str, Any]:
    if TMP_ROOT.exists():
        shutil.rmtree(TMP_ROOT)
    data_root = TMP_ROOT / "data"
    logs_root = TMP_ROOT / "logs"
    state_root = TMP_ROOT / "state"
    runtime_root = TMP_ROOT / "runtime_hot"
    for path in (data_root, logs_root, state_root, runtime_root):
        path.mkdir(parents=True, exist_ok=True)
    _seed_state(state_root)

    proc = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--data-root",
            str(data_root),
            "--logs-root",
            str(logs_root),
            "--state-root",
            str(state_root),
            "--runtime-root",
            str(runtime_root),
            "--now",
            "2026-06-17T00:00:10Z",
            "--out",
            str(OUT_PATH),
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        return {"ok": False, "returncode": proc.returncode, "error": f"stdout was not JSON: {exc}", "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
    payload["_returncode"] = proc.returncode
    payload["_stdout_tail"] = proc.stdout[-2000:]
    payload["_stderr_tail"] = proc.stderr[-2000:]
    return payload


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")
        blocked_imports = _imports_from(path).intersection({"requests", "httpx", "ccxt", "pybitflyer"})
        if blocked_imports:
            failures.append(f"forbidden imports in {path.relative_to(REPO_ROOT)}: {sorted(blocked_imports)}")

    runner_text = RUNNER.read_text(encoding="utf-8") if RUNNER.exists() else ""
    for token in (
        "Operator-facing broker-free CLI wrapper",
        "non_authorizing",
        "run_sr_fx_runtime_control_report_sequence",
        "BTC_TS_AUTOTRADE_RUNTIME_ROOT",
        "BTCTS_RUNTIME_CONTROL_NOW",
        '"would_send_to_broker": False',
    ):
        if str(token) not in runner_text:
            failures.append(f"runner missing required token: {token}")

    wrapper = _run_wrapper()
    sequence = wrapper.get("sequence") if isinstance(wrapper.get("sequence"), dict) else {}
    steps = sequence.get("steps") if isinstance(sequence.get("steps"), list) else []
    step_names = [str(step.get("name")) for step in steps if isinstance(step, dict)]
    runtime_control = wrapper.get("runtime_control") if isinstance(wrapper.get("runtime_control"), dict) else {}
    safety_lock = wrapper.get("operator_safety_lock") if isinstance(wrapper.get("operator_safety_lock"), dict) else {}
    paths = wrapper.get("paths") if isinstance(wrapper.get("paths"), dict) else {}

    checks = {
        "wrapper_returncode_zero": wrapper.get("_returncode") == 0,
        "wrapper_ok_true": wrapper.get("ok") is True,
        "sequence_complete": sequence.get("sequence_complete") is True,
        "runtime_control_first": step_names[:1] == ["runtime_control_snapshot_refresh"],
        "all_expected_steps_present": step_names == [
            "runtime_control_snapshot_refresh",
            "execution_safety_harness_report",
            "pre_live_blocker_report",
            "final_review_package",
            "data_ui_gate_handoff",
        ],
        "runtime_control_exists": runtime_control.get("exists") is True,
        "final_review_runtime_present": bool((sequence.get("summary") or {}).get("final_review_runtime_control_present")) if isinstance(sequence.get("summary"), dict) else False,
        "handoff_runtime_present": bool((sequence.get("summary") or {}).get("handoff_runtime_control_present")) if isinstance(sequence.get("summary"), dict) else False,
        "operator_safety_lock": safety_lock.get("non_authorizing") is True and safety_lock.get("read_only") is True and safety_lock.get("would_send_to_broker") is False and safety_lock.get("mode_changed") is False,
        "top_level_safety_flags": wrapper.get("read_only") is True and wrapper.get("would_send_to_broker") is False and wrapper.get("mode_changed") is False and wrapper.get("autotrade_resume_authorized") is False,
        "out_file_written": OUT_PATH.exists(),
        "runtime_control_state_written": Path(str(paths.get("runtime_control_state") or "")).exists(),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DQ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dq_runtime_control_report_sequence_cli_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "cli_wrapper_present": RUNNER.exists(),
            "sequence_invoked": checks.get("sequence_complete", False),
            "runtime_control_refreshed_first": checks.get("runtime_control_first", False),
            "read_only_no_broker_non_authorizing": checks.get("operator_safety_lock", False) and checks.get("top_level_safety_flags", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "wrapper_summary": {
            "returncode": wrapper.get("_returncode"),
            "ok": wrapper.get("ok"),
            "step_names": step_names,
            "runtime_control_ok": runtime_control.get("ok"),
            "runtime_control_blocked_by": runtime_control.get("blocked_by"),
            "paths": paths,
        },
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
