# path: ./tools/test_phase4a_prediction_system_ps_q13_warroom_review_loop_closeout_guard.py
# desc: Guard for PS-Q13 WarRoom realtime review loop closeout documentation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q13_WARROOM_REVIEW_LOOP_CLOSEOUT_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q13_WARROOM_REVIEW_LOOP_CLOSEOUT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q13_warroom_review_loop_closeout_guard.py",
}

REQUIRED_MARKERS = (
    "Head at closeout candidate: 960d8bc1",
    "ea3494f9 PS-Q13A WarRoom real-time prediction review / GPT explanation / parameter-adjustment review preflight contract",
    "b08169ae PS-Q13B WarRoom display/readability/check-only panel integration",
    "234c091c PS-Q13C quick summary cards, GPT review checklist, and proposal-only parameter candidate rows",
    "635e0cc4 PS-Q13D WarRoom realtime review UI Check snapshot",
    "3c4227f8 PS-Q13E WarRoom realtime review UI Check JSON checker",
    "960d8bc1 PS-Q13F redaction-aware UI Check checker tolerance",
    "warroom_realtime_review_preflight_panel_uicheck_snapshot",
    "observed_uicheck_json=tmp/uicheck/uicheck_20260622_160937_663177_warroom.json",
    "latest_prediction_source_panel_state=latest_prediction_source_review_panel_blocked",
    "blocker_count=10",
    "warning_count=3",
    "checker=ps_q13e_warroom_realtime_review_uicheck_snapshot",
    "ok=true",
    "summary_card_count=4",
    "gpt_review_checklist_count=3",
    "parameter_adjustment_candidate_count=3",
    "parameter_apply_allowed_any=false",
    "parameter_staging_write_allowed_any=false",
    "redacted_safe_boundary_keys=[approval_or_authorization_allowed_false, authorization_grant_requested_false, broker_private_api_allowed_false]",
    "PS-Q13C quick summary cards are visible",
    "PS-Q13C GPT review checklist is visible",
    "PS-Q13C parameter candidates are visible as proposal/review-only",
    "PS-Q13B boundary rows are visible and show read_only=true and execution=false",
    "AutoTrade trigger consumption was not implemented.",
    "PredictionSystemResult-to-AutoTrade bridge execution was not implemented.",
    "Approval, decision, or command ledger append was not added.",
    "Broker/private API calls were not added.",
    "Mode apply was not added.",
    "Order placement was not added.",
    "WarRoom runtime artifact writes were not added.",
    "Freshness bypass was not added.",
    "Silent live parameter mutation was not added.",
    "Parameter apply was not added.",
    "Parameter staging write was not added.",
    "read_only=true",
    "non_executing=true",
    "display_only=true",
    "review_only=true",
    "would_send_to_broker=false",
    "would_write_runtime_artifact=false",
    "autotrade_trigger_enabled=false",
    "broker_execution_requested=false",
    "mode_apply_requested=false",
    "requires a separate explicit human scope and approval",
)

FORBIDDEN_ENABLEMENT_MARKERS = (
    "AutoTrade trigger consumption was implemented",
    "bridge execution was implemented",
    "ledger append was added",
    "Broker/private API calls were added",
    "Mode apply was added",
    "Order placement was added",
    "WarRoom runtime artifact writes were added",
    "Freshness bypass was added",
    "Silent live parameter mutation was added",
    "Parameter apply was added",
    "Parameter staging write was added",
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
        "guard": "ps_q13_warroom_review_loop_closeout",
        "phase": "phase3_prediction_system_warroom_realtime_review_loop",
        "contract": {
            "thread_closeout_doc_present": DOC.exists(),
            "ps_q13_a_to_f_lineage_recorded": not failures,
            "actual_ui_observation_recorded": not failures,
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


def test_ps_q13_warroom_review_loop_closeout_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
