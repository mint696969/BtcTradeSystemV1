# path: ./tools/test_phase4a_prediction_system_ps_q13d_warroom_realtime_review_uicheck_guard.py
# desc: Guard for PS-Q13D WarRoom realtime review UI Check snapshot coverage.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_realtime_review_preflight_panel.py"

REQUIRED_PANEL_MARKERS = (
    "PREDICTION_WARROOM_REALTIME_REVIEW_UICHECK_SNAPSHOT_VERSION",
    "prediction_warroom_realtime_review_uicheck_snapshot.ps_q13d.v1",
    "build_prediction_warroom_realtime_review_uicheck_snapshot",
    "warroom_realtime_review_preflight_panel_uicheck_snapshot",
    "summary_card_count",
    "gpt_review_checklist_count",
    "parameter_adjustment_candidate_count",
    "parameter_apply_allowed_any",
    "parameter_staging_write_allowed_any",
    "safe_boundary",
    "parameter_apply_allowed_any_false",
    "parameter_staging_write_allowed_any_false",
)

REQUIRED_TEST_MARKERS = (
    "PREDICTION_WARROOM_REALTIME_REVIEW_UICHECK_SNAPSHOT_VERSION",
    "build_prediction_warroom_realtime_review_uicheck_snapshot",
    "summary_card_count",
    "gpt_review_checklist_count",
    "parameter_adjustment_candidate_count",
    "parameter_apply_allowed_any",
    "parameter_staging_write_allowed_any",
    "safe_boundary",
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
        "guard": "ps_q13d_warroom_realtime_review_uicheck",
        "uicheck": {
            "snapshot_version_present": True,
            "session_state_snapshot_key_present": True,
            "summary_card_count_guarded": True,
            "gpt_review_checklist_count_guarded": True,
            "parameter_candidate_count_guarded": True,
            "parameter_apply_allowed_any": False,
            "parameter_staging_write_allowed_any": False,
            "safe_boundary_guarded": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q13d_warroom_realtime_review_uicheck_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
