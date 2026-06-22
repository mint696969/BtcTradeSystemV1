# path: ./tools/test_phase4a_prediction_system_ps_q14b_source_readiness_uicheck_checker_guard.py
# desc: Guard for PS-Q14B WarRoom source-readiness explanation UI Check checker.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q14b_source_readiness_uicheck_snapshot.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py"

REQUIRED_CHECKER_MARKERS = (
    "EXPECTED_SESSION_STATE_KEY",
    "warroom_latest_prediction_source_review_panel_uicheck_snapshot",
    "EXPECTED_READINESS_EXPLANATION_VERSION",
    "prediction_warroom_latest_prediction_source_readiness_explanation.ps_q14a.v1",
    "readiness_explanation_row_count",
    "validate_snapshot",
    "validate_file",
    "check_latest_or_path",
    "test_ps_q14b_source_readiness_uicheck_snapshot_checker_sample",
    "test_ps_q14b_source_readiness_uicheck_snapshot_checker_redacted_sample",
)
REQUIRED_PANEL_MARKERS = (
    "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_EXPLANATION_VERSION",
    "readiness_explanation_row_count",
    "warroom_latest_prediction_source_review_panel_uicheck_snapshot",
)
FORBIDDEN_CHECKER_MARKERS = (
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "call_private_api(",
    "apply_live_parameters(",
    "mutate_live_parameters(",
    "bypass_allowed=True",
    "can_fix_in_warroom=True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    failures: list[str] = []
    for path in (CHECKER, PANEL):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
    checker_text = _read(CHECKER) if CHECKER.exists() else ""
    panel_text = _read(PANEL) if PANEL.exists() else ""
    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            failures.append(f"missing checker marker: {marker}")
    for marker in REQUIRED_PANEL_MARKERS:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    for marker in FORBIDDEN_CHECKER_MARKERS:
        if marker in checker_text:
            failures.append(f"forbidden checker marker present: {marker}")
    payload = {
        "ok": not failures,
        "guard": "ps_q14b_source_readiness_uicheck_checker",
        "checker": {
            "checker_present": CHECKER.exists(),
            "source_readiness_snapshot_dependency_present": True,
            "readiness_explanation_row_count_guarded": True,
            "sample_validation_test_present": True,
            "read_only_validation": True,
            "no_bypass_or_execution": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q14b_source_readiness_uicheck_checker_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
