# path: ./tools/test_phase4a_prediction_system_ps_q15e_refresh_decision_checkpoint_guard.py
# desc: Guard for PS-Q15E human decision checkpoint. Docs/check only; does not choose refresh/scheduler/blocked path.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q15E_REFRESH_DECISION_CHECKPOINT_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q15E_REFRESH_DECISION_CHECKPOINT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q15e_refresh_decision_checkpoint_guard.py",
}
REQUIRED_MARKERS = (
    "PS-Q15A commit=3f187fa6 primary_root_cause=latest_prediction_artifact_stale",
    "PS-Q15B commit=50ff7231 primary_conclusion=operator_shell_refresh_path_exists_but_is_not_scheduler",
    "PS-Q15C commit=3ec7c95e explicit operator refresh runbook added; no refresh executed",
    "PS-Q15D commit=855e11a3 operator refresh acceptance gate added; current stale state rejected",
    "acceptance_gate.state=operator_refresh_not_accepted",
    "Option A: explicit one-shot operator-shell refresh",
    "Option B: non-UI scheduled producer design",
    "Option C: keep blocked/not_ready and continue diagnostics",
    "This checkpoint does not choose Option A.",
    "This checkpoint does not choose Option B.",
    "This checkpoint does not choose Option C.",
    "This checkpoint does not run refresh.",
    "This checkpoint does not write D-hot runtime artifacts.",
    "This checkpoint does not create a scheduler.",
    "This checkpoint does not add WarRoom export controls.",
    "This checkpoint does not bypass freshness.",
    "This checkpoint does not force readiness.",
    "This checkpoint does not trigger AutoTrade.",
    "human_decision_required=true",
    "thread_crossing_decision_human_controlled=true",
    "refresh_executed=false",
    "runtime_artifact_write=false",
    "scheduler_created=false",
    "warroom_ui_trigger=false",
    "parameter_staging_write=false",
    "If @mint does not choose A/B/C explicitly, do not infer the choice.",
)
FORBIDDEN_MARKERS = (
    "This checkpoint chooses Option A.",
    "This checkpoint chooses Option B.",
    "This checkpoint chooses Option C.",
    "This checkpoint runs refresh.",
    "This checkpoint writes D-hot runtime artifacts.",
    "This checkpoint creates a scheduler.",
    "This checkpoint adds WarRoom export controls.",
    "This checkpoint bypasses freshness.",
    "This checkpoint forces readiness.",
    "human_decision_required=false",
    "refresh_executed=true",
    "runtime_artifact_write=true",
    "scheduler_created=true",
    "warroom_ui_trigger=true",
    "warroom_export_controls=true",
    "freshness_bypass=true",
    "force_ready=true",
    "ledger_append=true",
    "broker_private_api=true",
    "autotrade=true",
    "parameter_apply=true",
    "parameter_staging_write=true",
    "silent_live_parameter_mutation=true",
)
FORBIDDEN_EXACT_LINES = (
    "broker_private_api=true",
    "autotrade=true",
    "parameter_apply=true",
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
            failures.append(f"missing checkpoint marker: {marker}")
    doc_lines = set(doc.splitlines())
    broad_forbidden = tuple(
        marker for marker in FORBIDDEN_MARKERS if marker not in FORBIDDEN_EXACT_LINES
    )
    for marker in broad_forbidden:
        if marker in doc:
            failures.append(f"forbidden checkpoint marker present: {marker}")
    for marker in FORBIDDEN_EXACT_LINES:
        if marker in doc_lines:
            failures.append(f"forbidden checkpoint exact line present: {marker}")
    for token in FORBIDDEN_GUARD_TOKENS:
        if token in guard_search:
            failures.append(f"forbidden guard execution token present: {token}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q15e_refresh_decision_checkpoint",
        "contract": {
            "decision_checkpoint_present": DOC.exists(),
            "abc_options_recorded_without_choice": not failures,
            "human_decision_required": "human_decision_required=true" in doc,
            "does_not_execute_refresh_or_scheduler": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q15e_refresh_decision_checkpoint_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
