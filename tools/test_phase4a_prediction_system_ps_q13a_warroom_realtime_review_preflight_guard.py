# path: ./tools/test_phase4a_prediction_system_ps_q13a_warroom_realtime_review_preflight_guard.py
# desc: Close guard for PS-Q13A WarRoom real-time prediction review / parameter-adjustment review preflight.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_contract.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_realtime_review_preflight_contract.py"
ALIGNMENT = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q13_MAINLINE_ALIGNMENT_2026-06-22.md"

REQUIRED_COMPONENT_MARKERS = (
    "PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION",
    "prediction_warroom_realtime_review_preflight.ps_q13a.v1",
    "realtime_prediction_delta_review",
    "gpt_assisted_explanation_context",
    "parameter_adjustment_candidate_review",
    "RESPONSIBILITY_BOUNDARY",
    "PARAMETER_REVIEW_STATES",
    "FORBIDDEN_NEXT_BEHAVIOR",
    "silent_live_parameter_mutation",
    "autotrade_trigger_consumption",
    "broker_private_api",
    "warroom_runtime_artifact_write",
    "streamlit_import_required: bool = False",
    "would_mutate_live_parameters: bool = False",
    "would_append_parameter_version: bool = False",
    "command_ledger_append_requested: bool = False",
    "decision_ledger_append_requested: bool = False",
    "autotrade_trigger_enabled: bool = False",
    "broker_execution_requested: bool = False",
)

FORBIDDEN_COMPONENT_MARKERS = (
    "import streamlit",
    "from streamlit",
    "st.",
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "call_private_api(",
    "mode_apply(",
    "apply_live_parameters(",
    "mutate_live_parameters(",
)

REQUIRED_TEST_MARKERS = (
    "test_prediction_warroom_realtime_review_preflight_contract",
    "blocked_waiting_for_latest_prediction_source",
    "ready_for_future_warroom_ui_slice",
    "proposal_only_declared",
    "would_mutate_live_parameters",
    "autotrade_trigger_enabled",
    "broker_execution_requested",
)

REQUIRED_ALIGNMENT_MARKERS = (
    "PS-Q13A: WarRoom real-time prediction review and parameter-adjustment review preflight.",
    "Prediction System owns prediction contracts, evidence, scenario traces, explanation packets, and parameter-adjustment proposal data.",
    "WarRoom owns display, operator review, GPT-assisted explanation surfaces, and check-only UI snapshots.",
    "AutoTrade owns trigger consumption, readiness, risk gates, approval/ledger, mode/order, and broker paths, but remains out of scope for the next work.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    failures: list[str] = []
    for path in (COMPONENT, TEST, ALIGNMENT):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")

    component_text = _read(COMPONENT) if COMPONENT.exists() else ""
    test_text = _read(TEST) if TEST.exists() else ""
    alignment_text = _read(ALIGNMENT) if ALIGNMENT.exists() else ""

    for marker in REQUIRED_COMPONENT_MARKERS:
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for marker in FORBIDDEN_COMPONENT_MARKERS:
        if marker in component_text:
            failures.append(f"forbidden component marker present: {marker}")
    for marker in REQUIRED_TEST_MARKERS:
        if marker not in test_text:
            failures.append(f"missing test marker: {marker}")
    for marker in REQUIRED_ALIGNMENT_MARKERS:
        if marker not in alignment_text:
            failures.append(f"missing alignment marker: {marker}")

    payload = {
        "ok": not failures,
        "guard": "ps_q13a_warroom_realtime_review_preflight",
        "contract": {
            "component_present": COMPONENT.exists(),
            "test_present": TEST.exists(),
            "alignment_doc_present": ALIGNMENT.exists(),
            "warroom_review_preflight_only": True,
            "responsibility_separation_guarded": True,
            "parameter_adjustment_review_only": True,
            "autotrade_deferred": True,
            "no_broker_or_ledger_or_runtime_write": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q13a_warroom_realtime_review_preflight_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
