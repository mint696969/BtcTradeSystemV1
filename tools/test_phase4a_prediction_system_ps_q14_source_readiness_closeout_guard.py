# path: ./tools/test_phase4a_prediction_system_ps_q14_source_readiness_closeout_guard.py
# desc: Guard for PS-Q14 WarRoom source-readiness explanation closeout documentation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q14_SOURCE_READINESS_CLOSEOUT_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q14_SOURCE_READINESS_CLOSEOUT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q14_source_readiness_closeout_guard.py",
}

REQUIRED_MARKERS = (
    "Head at closeout candidate: 73197904",
    "da3ae9d7 PS-Q14A source-readiness explanation rows",
    "1d086349 PS-Q14B source-readiness UI Check JSON checker",
    "73197904 PS-Q14C source-readiness layout polish",
    "readiness_explanation_rows",
    "readiness_explanation_display_rows",
    "safe_flags=read_only;no_exec;no_warroom_fix;no_bypass",
    "observed_uicheck_json=tmp/uicheck/uicheck_20260622_165424_452889_warroom.json",
    "checker=ps_q14b_source_readiness_uicheck_snapshot",
    "checker=ps_q13e_warroom_realtime_review_uicheck_snapshot",
    "ok=true",
    "snapshot_version=prediction_warroom_latest_prediction_source_uicheck_snapshot.ps_q12h.v1",
    "readiness_explanation_version=prediction_warroom_latest_prediction_source_readiness_explanation.ps_q14a.v1",
    "panel_state=latest_prediction_source_review_panel_blocked",
    "adapter_state=latest_prediction_source_blocked",
    "readability_row_count=6",
    "issue_row_count=13",
    "readiness_explanation_row_count=13",
    "blocker_count=10",
    "warning_count=3",
    "parameter_apply_allowed_any=false",
    "parameter_staging_write_allowed_any=false",
    "Freshness bypass was not added.",
    "Force-ready behavior was not added.",
    "Loader/readiness behavior was not changed.",
    "WarRoom runtime artifact writes were not added.",
    "Approval, decision, or command ledger append was not added.",
    "Broker/private API calls were not added.",
    "Mode apply was not added.",
    "Order placement was not added.",
    "AutoTrade trigger consumption was not implemented.",
    "Parameter apply was not added.",
    "Parameter staging write was not added.",
    "Silent live parameter mutation was not added.",
    "read_only=true",
    "non_executing=true",
    "display_only=true",
    "review_only=true",
    "can_fix_in_warroom=false",
    "bypass_allowed=false",
    "would_write_runtime_artifact=false",
    "would_send_to_broker=false",
    "autotrade_trigger_enabled=false",
    "broker_execution_requested=false",
    "mode_apply_requested=false",
    "requires a separate explicit human scope and approval",
)

FORBIDDEN_ENABLEMENT_MARKERS = (
    "Freshness bypass was added",
    "Force-ready behavior was added",
    "Loader/readiness behavior was changed",
    "WarRoom runtime artifact writes were added",
    "ledger append was added",
    "Broker/private API calls were added",
    "Mode apply was added",
    "Order placement was added",
    "AutoTrade trigger consumption was implemented",
    "Parameter apply was added",
    "Parameter staging write was added",
    "Silent live parameter mutation was added",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    if not DOC.exists():
        failures.append(f"missing doc: {DOC.relative_to(REPO_ROOT)}")
        text = ""
    else:
        text = _read(DOC)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing closeout marker: {marker}")
    for marker in FORBIDDEN_ENABLEMENT_MARKERS:
        if marker in text:
            failures.append(f"forbidden enablement marker present: {marker}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q14_source_readiness_closeout",
        "phase": "phase3_prediction_system_warroom_source_readiness_explanation_closeout",
        "contract": {
            "thread_closeout_doc_present": DOC.exists(),
            "ps_q14_a_to_c_lineage_recorded": not failures,
            "actual_ui_observation_recorded": not failures,
            "uicheck_checker_results_recorded": not failures,
            "read_only_non_executing_boundary_recorded": not failures,
            "no_execution_surface_enabled": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q14_source_readiness_closeout_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
