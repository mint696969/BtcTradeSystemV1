# path: ./tools/test_phase4a_autotrade_milestone_fl_pre_armed_dry_run_auth_request_execution_gate_status_close_guard.py
# desc: Close guard for S97 Pre-Armed Dry Run authorization request execution gate dry-run/status. Broker-free; non-recording; non-executing; non-authorizing. Short path avoids Windows MAX_PATH.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_autotrade_milestone_fl_pre_armed_dry_run_auth_request_execution_gate_status_close_guard.py"
S97_RUN_PATH = "tools/run_sr_fx_pre_armed_dry_run_auth_request_execution_gate_dry_run_status_s97.py"
S97_GUARD_PATH = "tools/test_phase4a_autotrade_milestone_fl_pre_armed_dry_run_auth_request_execution_gate_status_guard.py"
S96_GUARD_PATH = "tools/test_phase4a_autotrade_milestone_fk_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_dry_run_plan_status_guard.py"
COMMAND_STATUS_PATH = "btcts_next/src/btcts/autotrade/execution/command_status.py"
EXPECTED_SLICE_FILES = {S97_RUN_PATH, S97_GUARD_PATH, SELF_PATH}
FORBIDDEN_RUN_TOKENS = ('place_order(', 'send_order(', 'broker_order(', 'private_api', 'pybitflyer', 'ccxt', 'requests.post', 'httpx.post', 'append_command_ledger_record(', 'validate_and_append_command', 'submit_mode_change_command_request', 'mode_changed=True', 'would_send_to_broker=True', 'pre_armed_dry_run_authorized=True', 'live_authorized=True', 'approval_ledger_appended=True', 'command_ledger_appended=True', 'mode_change_requested=True', 'mode_change_authorized=True', 'approval_record_append_execution_authorized=True', 'authorization_request_recorded=True', 'authorization_request_record_executed=True', 'authorization_request_record_execution_requested=True', 'authorization_request_record_execution_authorized=True', 'authorization_request_execution_gate_authorized=True', 'authorization_request_execution_gate_executed=True', 'while True')
REQUIRED_RUN_FRAGMENTS = ("from S96", "Gate/status only", "non-recording", "non-executing", "non-authorizing", "read_only", "would_send_to_broker", "mode_changed", "dry_run_gate_only", "authorization_request_execution_gate_ready", "authorization_request_execution_gate_blockers", "authorization_request_execution_gate_review_summary", "operator_safety_lock", "separate_explicit_authorization_slice_required_before_any_authorization")


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8") if (REPO_ROOT / rel_path).exists() else ""


def _syntax(rel_path: str, failures: list[str]) -> dict[str, object]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing syntax target: {rel_path}")
        return {"ok": False, "missing": True}
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return {"ok": True}
    except Exception as exc:
        failures.append(f"syntax failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=REPO_ROOT, text=True, capture_output=True, timeout=120)
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1200:]}
    ok = proc.returncode == 0 and payload.get("ok") is True and payload.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": payload.get("phase"), "status": payload.get("status")}


def _run_boundary(failures: list[str]) -> dict[str, object]:
    text = _read(S97_RUN_PATH)
    lower = text.lower()
    missing = [frag for frag in REQUIRED_RUN_FRAGMENTS if frag.lower() not in lower]
    forbidden = [tok for tok in FORBIDDEN_RUN_TOKENS if tok in text]
    false_literals = ['"read_only": True', '"would_send_to_broker": False', '"mode_changed": False', '"dry_run_gate_only": True']
    false_missing = [frag for frag in false_literals if frag not in text]
    failures.extend(f"S97 run missing required fragment: {frag}" for frag in missing)
    failures.extend(f"S97 run contains forbidden token: {tok}" for tok in forbidden)
    failures.extend(f"S97 run missing safety literal: {frag}" for frag in false_missing)
    return {"missing": missing, "forbidden": forbidden, "false_missing": false_missing}


def _git_boundary(failures: list[str]) -> dict[str, object]:
    lines = [line for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines() if line.strip()]
    unexpected = []
    for line in lines:
        rel = (line[3:] if len(line) > 3 else line).replace(chr(92), "/")
        if rel not in EXPECTED_SLICE_FILES:
            unexpected.append(line)
    failures.extend(f"unexpected dirty file during S97 close: {line}" for line in unexpected)
    return {"lines": lines, "unexpected": unexpected, "expected_slice_files": sorted(EXPECTED_SLICE_FILES)}


def main() -> int:
    failures: list[str] = []
    syntax = {p: _syntax(p, failures) for p in (SELF_PATH, S97_RUN_PATH, S97_GUARD_PATH, S96_GUARD_PATH, COMMAND_STATUS_PATH)}
    run_boundary = _run_boundary(failures)
    s97_guard = _run_json_guard(S97_GUARD_PATH, failures)
    s96_guard = _run_json_guard(S96_GUARD_PATH, failures)
    git_boundary = _git_boundary(failures)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_fl_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_gate_dry_run_status_close_guard", "status": "closed" if not failures else "open", "contract": {"s97_authorization_request_execution_gate_status_present": (REPO_ROOT / S97_RUN_PATH).exists(), "s97_focused_guard_closed": s97_guard.get("ok") is True, "s96_fk_guard_closed": s96_guard.get("ok") is True, "syntax_checked_without_pyc": all(item.get("ok") is True for item in syntax.values()), "broker_free_non_recording_non_executing_non_authorizing": not run_boundary.get("forbidden"), "expected_git_boundary_only": not git_boundary.get("unexpected")}, "syntax": syntax, "run_boundary": run_boundary, "guards": {"s97_fl_guard": s97_guard, "s96_fk_guard": s96_guard}, "git_boundary": git_boundary, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
