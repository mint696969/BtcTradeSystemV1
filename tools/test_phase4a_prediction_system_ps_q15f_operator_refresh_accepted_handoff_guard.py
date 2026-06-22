# path: ./tools/test_phase4a_prediction_system_ps_q15f_operator_refresh_accepted_handoff_guard.py
# desc: Guard for PS-Q15F final handoff after Option A accepted; docs/check only.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q15F_OPERATOR_REFRESH_ACCEPTED_HANDOFF_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q15F_OPERATOR_REFRESH_ACCEPTED_HANDOFF_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q15f_operator_refresh_accepted_handoff_guard.py",
}
REQUIRED_MARKERS = (
    "Option A chosen explicitly by @mint=true",
    "one_shot_operator_shell_refresh_executed=true",
    "acceptance_gate.accepted=true",
    "acceptance_gate.state=operator_refresh_accepted",
    "generated_at=2026-06-22T09:37:06Z",
    "prediction_run_id=prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-22T09:37:06Z",
    "target_file_size_bytes=2995734",
    "latest_payload_actual_export_runner=prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1",
    "q9y_state=latest_payload_export_runner_exported",
    "adapter_state=latest_prediction_source_ready",
    "payload_decode_succeeded=true",
    "loaded_payload_count=1",
    "review_packet_ready=true",
    "session_state_updated=true",
    "q15a_primary_root_cause=no_blocking_root_cause_detected_by_ps_q15a",
    "q15b_primary_conclusion=operator_shell_refresh_path_exists_but_is_not_scheduler",
    "The current remaining gap is not the loader path itself; it is ongoing production/freshness of the latest prediction artifact.",
    "Option B: design non-UI scheduled producer contract/guard/visibility",
    "contract_only=true",
    "guard_only=true",
    "visibility_design_required=true",
    "scheduler_enabled=false",
    "runtime_artifact_write_enabled=false",
    "operator_visibility_required=true",
    "freshness_policy_explicit=true",
    "warnings_visible=true",
    "rollback_or_disable_path_required=true",
    "Do not start by enabling scheduler.",
    "Do not start by adding runtime write automation.",
)
FORBIDDEN_MARKERS = (
    "scheduler_enabled=true",
    "runtime_artifact_write_enabled=true",
    "warroom_ui_trigger=true",
    "freshness_bypass=true",
    "force_ready=true",
    "ledger_append=true",
    "broker_private_api=true",
    "mode_order_execution=true",
    "autotrade=true",
    "parameter_apply=true",
    "parameter_staging_write=true",
    "silent_live_parameter_mutation=true",
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _guard_search_text(text: str) -> str:
    start = text.find("FORBIDDEN_GUARD_TOKENS = (")
    end = text.find("def _read", start)
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
    guard_search = _guard_search_text(_read(Path(__file__)))
    if not DOC.exists():
        failures.append(f"missing doc: {DOC.relative_to(REPO_ROOT)}")
    for marker in REQUIRED_MARKERS:
        if marker not in doc:
            failures.append(f"missing handoff marker: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in doc:
            failures.append(f"forbidden handoff marker present: {marker}")
    for token in FORBIDDEN_GUARD_TOKENS:
        if token in guard_search:
            failures.append(f"forbidden guard execution token present: {token}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q15f_operator_refresh_accepted_handoff",
        "contract": {
            "option_a_accepted_handoff_present": DOC.exists(),
            "next_thread_option_b_first_task_recorded": "Option B: design non-UI scheduled producer contract/guard/visibility" in doc,
            "no_scheduler_or_runtime_write_enabled": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q15f_operator_refresh_accepted_handoff_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
