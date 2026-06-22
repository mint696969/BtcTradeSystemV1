# path: ./tools/test_phase4a_prediction_system_ps_q13c_warroom_realtime_review_readability_guard.py
# desc: Guard for PS-Q13C WarRoom realtime review readability rows and proposal-only parameter review surfaces.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_realtime_review_preflight_panel.py"

REQUIRED_PANEL_MARKERS = (
    "PREDICTION_WARROOM_REALTIME_REVIEW_READABILITY_VERSION",
    "prediction_warroom_realtime_review_readability.ps_q13c.v1",
    "prediction_warroom_realtime_review_summary_cards",
    "prediction_warroom_gpt_review_checklist_rows",
    "prediction_warroom_parameter_adjustment_candidate_rows",
    "summary_cards",
    "gpt_review_checklist_rows",
    "parameter_adjustment_candidate_rows",
    "apply_allowed",
    "staging_write_allowed",
    "PS-Q13C parameter candidates are proposal/review only",
)

REQUIRED_TEST_MARKERS = (
    "PREDICTION_WARROOM_REALTIME_REVIEW_READABILITY_VERSION",
    "prediction_warroom_realtime_review_summary_cards",
    "prediction_warroom_gpt_review_checklist_rows",
    "prediction_warroom_parameter_adjustment_candidate_rows",
    "source_quality_sensitivity",
    "signal_strength_threshold",
    "scenario_trace_required_fields",
    "apply_allowed",
    "staging_write_allowed",
)

FORBIDDEN_PANEL_MARKERS = (
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "call_private_api(",
    "apply_live_parameters(",
    "mutate_live_parameters(",
    "staging_write_allowed=True",
    "apply_allowed=True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
    panel_text = _read(PANEL) if PANEL.exists() else ""
    test_text = _read(TEST) if TEST.exists() else ""
    for marker in REQUIRED_PANEL_MARKERS:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    for marker in REQUIRED_TEST_MARKERS:
        if marker not in test_text:
            failures.append(f"missing test marker: {marker}")
    for marker in FORBIDDEN_PANEL_MARKERS:
        if marker in panel_text:
            failures.append(f"forbidden panel marker present: {marker}")
    payload = {
        "ok": not failures,
        "guard": "ps_q13c_warroom_realtime_review_readability",
        "readability": {
            "summary_cards": True,
            "gpt_review_checklist": True,
            "parameter_adjustment_candidates_proposal_only": True,
            "apply_allowed": False,
            "staging_write_allowed": False,
            "display_only": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q13c_warroom_realtime_review_readability_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
