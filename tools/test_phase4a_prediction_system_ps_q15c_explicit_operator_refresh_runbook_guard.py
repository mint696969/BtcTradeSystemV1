# path: ./tools/test_phase4a_prediction_system_ps_q15c_explicit_operator_refresh_runbook_guard.py
# desc: Guard for PS-Q15C explicit operator-shell refresh runbook. Docs/check only; does not execute refresh or write runtime artifacts.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q15C_EXPLICIT_OPERATOR_REFRESH_RUNBOOK_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q15C_EXPLICIT_OPERATOR_REFRESH_RUNBOOK_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q15c_explicit_operator_refresh_runbook_guard.py",
}
REQUIRED_MARKERS = (
    "PS-Q15A primary_root_cause=latest_prediction_artifact_stale",
    "PS-Q15B primary_conclusion=operator_shell_refresh_path_exists_but_is_not_scheduler",
    "manual_operator_runner=tmp/work/ps_q12d_refresh_latest_prediction/run_ps_q12d_export_and_smoke.py",
    "actual_export_runner_version=prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1",
    "latest_payload_export_runner_version=prediction_warroom_latest_payload_export_runner.ps_q9y.v1",
    "warroom_page_export_runner_mounted=false",
    "python .\\tmp\\work\\ps_q12d_refresh_latest_prediction\\run_ps_q12d_export_and_smoke.py",
    "export.runner_state=latest_payload_actual_export_runner_exported",
    "export.target_file_written=true",
    "export.safe_flags.warroom_page_mutation_allowed_false=true",
    "export.safe_flags.ui_triggered_runner_execution_false=true",
    "export.safe_flags.approval_or_authorization_allowed_false=true",
    "export.safe_flags.ledger_append_allowed_false=true",
    "export.safe_flags.autotrade_trigger_allowed_false=true",
    "export.safe_flags.broker_private_api_allowed_false=true",
    "smoke.adapter_state=latest_prediction_source_ready",
    "python .\\tools\\check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause.py",
    "python .\\tools\\check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke.py",
    "It does not approve WarRoom UI export controls.",
    "It does not approve scheduler creation.",
    "It does not approve repeated automatic refresh.",
    "It does not approve freshness bypass.",
    "It does not approve force-ready behavior.",
    "It does not approve AutoTrade.",
    "It does not approve broker/private API.",
    "It does not approve parameter apply.",
    "It does not approve parameter staging write.",
    "runbook_only=true",
    "guard_only=true",
    "human_shell_action_required=true",
    "warroom_ui_trigger=false",
    "parameter_staging_write_allowed=false",
    "Option A: human explicitly runs the one-shot operator-shell refresh command",
    "Option B: design a separate non-UI scheduled producer",
    "Option C: keep current state blocked/not_ready",
)
FORBIDDEN_GUARD_TOKENS = (
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "run_ps_q12d_export_and_smoke.main(",
    "os.system(",
    "target.write_text(",
    "replace(target)",
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
)
FORBIDDEN_DOC_ENABLEMENT = (
    "It approves WarRoom UI export controls.",
    "It approves scheduler creation.",
    "It approves repeated automatic refresh.",
    "It approves freshness bypass.",
    "It approves force-ready behavior.",
    "It approves AutoTrade.",
    "It approves broker/private API.",
    "It approves parameter apply.",
    "It approves parameter staging write.",
    "warroom_ui_trigger=true",
    "ui_controls_added=true",
    "approval_or_authorization_allowed=true",
    "ledger_append_allowed=true",
    "autotrade_trigger_allowed=true",
    "broker_private_api_allowed=true",
    "parameter_apply_allowed=true",
    "parameter_staging_write_allowed=true",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _guard_search_text(text: str) -> str:
    start = text.find("FORBIDDEN_GUARD_TOKENS = (")
    end = text.find("FORBIDDEN_DOC_ENABLEMENT = (", start)
    if start >= 0 and end > start:
        text = text[:start] + text[end:]
    return text


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    doc = _read(DOC) if DOC.exists() else ""
    guard = _read(Path(__file__))
    guard_search = _guard_search_text(guard)
    if not DOC.exists():
        failures.append(f"missing doc: {DOC.relative_to(REPO_ROOT)}")
    for marker in REQUIRED_MARKERS:
        if marker not in doc:
            failures.append(f"missing runbook marker: {marker}")
    for token in FORBIDDEN_GUARD_TOKENS:
        if token in guard_search:
            failures.append(f"forbidden guard execution token present: {token}")
    for token in FORBIDDEN_DOC_ENABLEMENT:
        if token in doc:
            failures.append(f"forbidden doc enablement marker present: {token}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q15c_explicit_operator_refresh_runbook",
        "contract": {
            "explicit_human_refresh_runbook_present": DOC.exists(),
            "does_not_execute_refresh_in_guard": not any(token in guard_search for token in FORBIDDEN_GUARD_TOKENS),
            "does_not_approve_scheduler_or_warroom_export_trigger": not any(token in doc for token in FORBIDDEN_DOC_ENABLEMENT),
            "post_refresh_validation_commands_present": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q15c_explicit_operator_refresh_runbook_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
