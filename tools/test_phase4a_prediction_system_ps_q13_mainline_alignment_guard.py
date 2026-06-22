# path: ./tools/test_phase4a_prediction_system_ps_q13_mainline_alignment_guard.py
# desc: Guard for corrected PS-Q13 mainline alignment before new implementation.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q13_MAINLINE_ALIGNMENT_2026-06-22.md"
PS_Q11 = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q11_SCENARIO_CORE_CLOSEOUT_2026-06-22.md"
PS_Q12 = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q12_THREAD_CLOSEOUT_2026-06-22.md"

REQUIRED_DOC_MARKERS = (
    "PS-Q11 Scenario Prediction Core strengthening is complete",
    "PS-Q12 WarRoom read-only inference display lane is complete",
    "The next mainline is not AutoTrade and not a trigger bridge.",
    "WarRoom operator review usability",
    "real-time human confirmation of predictions",
    "GPT-assisted explanation",
    "parameter-adjustment candidates",
    "Keep parameter adjustment as review/proposal/staging first, not silent live mutation.",
    "Improve other information sources and complete the planned inference features before AutoTrade implementation.",
    "Prediction System owns prediction contracts, evidence, scenario traces, explanation packets, and parameter-adjustment proposal data.",
    "WarRoom owns display, operator review, GPT-assisted explanation surfaces, and check-only UI snapshots.",
    "Collector owns collection and hot/latest runtime data production.",
    "AutoTrade owns trigger consumption, readiness, risk gates, approval/ledger, mode/order, and broker paths, but remains out of scope for the next work.",
    "Do not put AutoTrade trigger logic inside WarRoom components",
    "Do not implement AutoTrade trigger consumption.",
    "Do not append approval, decision, or command ledgers.",
    "Do not add broker/private API calls.",
    "Do not add mode apply or order placement.",
    "Do not add WarRoom runtime artifact writes.",
    "Do not silently mutate live parameters.",
    "PS-Q13A: WarRoom real-time prediction review and parameter-adjustment review preflight.",
)

PS_Q11_MARKERS = (
    "PS-Q11A through PS-Q11H completed through f5ba61a4.",
    "evidence_weighting_trace",
    "invalidation_rewrite_trace",
    "scenario_switch_trace",
    "advisory_output_packet_candidate",
    "operator_review_handoff_shape",
    "scenario_core_closeout_candidate",
    "AutoTrade execution was not resumed.",
)

PS_Q12_MARKERS = (
    "This document closes the PS-Q12 WarRoom read-only inference display lane thread.",
    "read-only/non-executing observation lane",
    "WarRoom UI trigger bridge was not added.",
    "AutoTrade execution was not resumed.",
    "approval_or_authorization_allowed=false",
    "ledger_append_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
)

FORBIDDEN_DOC_MARKERS = (
    "AutoTrade trigger consumption is implemented",
    "broker/private API calls are added",
    "mode apply is added",
    "order placement is added",
    "ledger append is added",
    "silent live parameter mutation is allowed",
    "WarRoom runtime artifact writes are enabled",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    failures: list[str] = []
    for path in (DOC, PS_Q11, PS_Q12):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")

    doc_text = _read(DOC) if DOC.exists() else ""
    q11_text = _read(PS_Q11) if PS_Q11.exists() else ""
    q12_text = _read(PS_Q12) if PS_Q12.exists() else ""

    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing alignment marker: {marker}")
    for marker in PS_Q11_MARKERS:
        if marker not in q11_text:
            failures.append(f"missing PS-Q11 source marker: {marker}")
    for marker in PS_Q12_MARKERS:
        if marker not in q12_text:
            failures.append(f"missing PS-Q12 source marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden enablement marker present: {marker}")

    payload = {
        "ok": not failures,
        "guard": "ps_q13_mainline_alignment",
        "alignment": {
            "ps_q11_treated_as_completed": not any("PS-Q11" in f for f in failures),
            "ps_q12_treated_as_completed": not any("PS-Q12" in f for f in failures),
            "next_mainline": "warroom_real_time_prediction_review_and_parameter_adjustment_review_preflight",
            "autotrade_deferred": True,
            "responsibility_separation_required": True,
            "manual_review_before_parameter_mutation": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q13_mainline_alignment_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
